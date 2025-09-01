package com.synthnet.aiapp.domain.ai.service

import com.synthnet.aiapp.data.entities.AgentRole
import com.synthnet.aiapp.domain.models.AgentResponse
import com.synthnet.aiapp.domain.models.ChainOfThought
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers
import kotlinx.datetime.Clock
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import okhttp3.Interceptor
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.random.Random

interface OpenAIApi {
    @POST("v1/chat/completions")
    suspend fun createChatCompletion(
        @Header("Authorization") authorization: String,
        @Body request: ChatCompletionRequest
    ): Response<ChatCompletionResponse>
    
    @POST("v1/embeddings")
    suspend fun createEmbedding(
        @Header("Authorization") authorization: String,
        @Body request: EmbeddingRequest
    ): Response<EmbeddingResponse>
}

@Singleton
class OpenAIService @Inject constructor() {
    
    private var totalRequests = 0
    private var errorCount = 0
    private val latencyHistory = mutableListOf<Long>()
    
    private val apiKey = "YOUR_OPENAI_API_KEY" // In production, use secure storage
    private val json = Json { ignoreUnknownKeys = true }
    
    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .addInterceptor(createRetryInterceptor())
        .addInterceptor(createRateLimitInterceptor())
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl("https://api.openai.com/")
        .client(httpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    private val api = retrofit.create(OpenAIApi::class.java)
    
    suspend fun generateResponse(
        prompt: String,
        role: AgentRole,
        context: Map<String, Any> = emptyMap()
    ): AgentResponse = withContext(Dispatchers.IO) {
        val startTime = System.currentTimeMillis()
        totalRequests++
        
        try {
            val systemPrompt = buildSystemPrompt(role, context)
            val messages = listOf(
                Message("system", systemPrompt),
                Message("user", prompt)
            )
            
            val request = ChatCompletionRequest(
                model = selectModel(role, prompt),
                messages = messages,
                maxTokens = calculateMaxTokens(prompt),
                temperature = getTemperatureForRole(role),
                topP = 0.9,
                presencePenalty = 0.1,
                frequencyPenalty = 0.1
            )
            
            val response = api.createChatCompletion(
                authorization = "Bearer $apiKey",
                request = request
            )
            
            val latency = System.currentTimeMillis() - startTime
            latencyHistory.add(latency)
            if (latencyHistory.size > 100) latencyHistory.removeFirst()
            
            if (response.isSuccessful && response.body() != null) {
                parseOpenAIResponse(response.body()!!, role, prompt, context)
            } else {
                errorCount++
                handleApiError(response)
            }
            
        } catch (e: Exception) {
            errorCount++
            handleException(e, role, prompt, context)
        }
    }
    
    suspend fun generateEmbedding(text: String): Result<FloatArray> = withContext(Dispatchers.IO) {
        try {
            val request = EmbeddingRequest(
                model = "text-embedding-ada-002",
                input = text
            )
            
            val response = api.createEmbedding(
                authorization = "Bearer $apiKey",
                request = request
            )
            
            if (response.isSuccessful && response.body() != null) {
                val embedding = response.body()!!.data.firstOrNull()?.embedding
                if (embedding != null) {
                    Result.success(embedding.toFloatArray())
                } else {
                    Result.failure(Exception("No embedding data received"))
                }
            } else {
                Result.failure(Exception("API call failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun buildSystemPrompt(role: AgentRole, context: Map<String, Any>): String {
        val basePrompt = when (role) {
            AgentRole.RESEARCHER -> """
                You are an expert researcher with access to comprehensive knowledge bases.
                Provide thorough, evidence-based analysis with proper citations and methodology.
                Consider multiple perspectives and identify knowledge gaps.
                Structure your response with clear sections for findings, methodology, and implications.
            """.trimIndent()
            
            AgentRole.CRITIC -> """
                You are a constructive critic focused on improving ideas through careful analysis.
                Examine assumptions, identify weaknesses, and suggest improvements.
                Provide balanced evaluation with both strengths and areas for improvement.
                Offer specific, actionable recommendations for enhancement.
            """.trimIndent()
            
            AgentRole.SYNTHESIZER -> """
                You are a synthesis expert who integrates diverse perspectives into coherent frameworks.
                Identify patterns, connections, and emergent insights across different viewpoints.
                Create unified understanding that transcends individual components.
                Highlight novel connections and practical applications.
            """.trimIndent()
            
            AgentRole.ANALYZER -> """
                You are a systematic analyst who breaks down complex problems into components.
                Apply rigorous analytical methods and quantitative approaches where appropriate.
                Identify relationships, dependencies, and causal mechanisms.
                Provide clear metrics, confidence intervals, and uncertainty assessments.
            """.trimIndent()
            
            AgentRole.COORDINATOR -> """
                You are a coordination specialist who optimizes multi-agent collaboration.
                Design efficient workflows, resource allocation, and communication protocols.
                Consider stakeholder needs, constraints, and success metrics.
                Provide clear action plans with timelines and responsibility assignments.
            """.trimIndent()
            
            AgentRole.SPECIALIST -> """
                You are a domain specialist with deep expertise in your field.
                Apply cutting-edge knowledge and best practices to specific problems.
                Consider industry standards, regulatory requirements, and emerging trends.
                Provide authoritative guidance with implementation details.
            """.trimIndent()
        }
        
        val contextInfo = if (context.isNotEmpty()) {
            "\n\nContext: ${context.entries.joinToString(", ") { "${it.key}: ${it.value}" }}"
        } else ""
        
        return basePrompt + contextInfo
    }
    
    private fun selectModel(role: AgentRole, prompt: String): String {
        return when {
            prompt.length > 8000 || role in listOf(AgentRole.RESEARCHER, AgentRole.SYNTHESIZER) -> "gpt-4-turbo-preview"
            role == AgentRole.ANALYZER -> "gpt-4"
            else -> "gpt-3.5-turbo"
        }
    }
    
    private fun calculateMaxTokens(prompt: String): Int {
        // Estimate tokens (roughly 4 chars per token) and leave room for response
        val promptTokens = prompt.length / 4
        return when {
            promptTokens < 1000 -> 2000
            promptTokens < 2000 -> 3000
            else -> 4000
        }.coerceAtMost(4096)
    }
    
    private fun getTemperatureForRole(role: AgentRole): Double {
        return when (role) {
            AgentRole.ANALYZER -> 0.1 // More deterministic for analysis
            AgentRole.CRITIC -> 0.2   // Slightly more focused
            AgentRole.RESEARCHER -> 0.3 // Balanced
            AgentRole.COORDINATOR -> 0.3 // Balanced
            AgentRole.SYNTHESIZER -> 0.7 // More creative
            AgentRole.SPECIALIST -> 0.4 // Domain-focused creativity
        }
    }
    
    private fun parseOpenAIResponse(
        response: ChatCompletionResponse,
        role: AgentRole,
        prompt: String,
        context: Map<String, Any>
    ): AgentResponse {
        val choice = response.choices.firstOrNull()
            ?: throw Exception("No choices in OpenAI response")
        
        val content = choice.message.content
        val finishReason = choice.finishReason
        
        // Extract reasoning chain from the response
        val thoughts = extractThoughts(content)
        val reasoning = extractReasoning(content)
        val confidence = calculateConfidence(choice, finishReason)
        
        return AgentResponse(
            agentId = "openai_${role.name.lowercase()}",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = reasoning,
                confidence = confidence
            ),
            confidence = confidence,
            alternatives = extractAlternatives(content),
            timestamp = Clock.System.now()
        )
    }
    
    private fun extractThoughts(content: String): List<String> {
        // Look for structured thinking patterns in the response
        val patterns = listOf(
            "(?i)first,?\s+(.+?)(?=\n|second|next|then|\.|$)",
            "(?i)initially,?\s+(.+?)(?=\n|then|next|subsequently|\.|$)",
            "(?i)\d+\.\s+(.+?)(?=\n|\d+\.|$)",
            "(?i)•\s+(.+?)(?=\n|•|$)"
        )
        
        val thoughts = mutableListOf<String>()
        patterns.forEach { pattern ->
            val matches = pattern.toRegex(RegexOption.MULTILINE).findAll(content)
            matches.forEach { match ->
                match.groups[1]?.value?.trim()?.let { thought ->
                    if (thought.length > 10) thoughts.add(thought)
                }
            }
        }
        
        return thoughts.take(5).ifEmpty {
            // Fallback: split content into logical segments
            content.split("\n\n").take(3).filter { it.length > 20 }
        }
    }
    
    private fun extractReasoning(content: String): String {
        // Look for conclusion or reasoning patterns
        val reasoningPatterns = listOf(
            "(?i)in conclusion,?\s+(.+?)(?=\n\n|$)",
            "(?i)therefore,?\s+(.+?)(?=\n\n|$)",
            "(?i)as a result,?\s+(.+?)(?=\n\n|$)",
            "(?i)this analysis suggests,?\s+(.+?)(?=\n\n|$)"
        )
        
        reasoningPatterns.forEach { pattern ->
            val match = pattern.toRegex(RegexOption.MULTILINE).find(content)
            match?.groups?.get(1)?.value?.trim()?.let { return it }
        }
        
        // Fallback: use last paragraph or summary
        val paragraphs = content.split("\n\n").filter { it.trim().isNotEmpty() }
        return paragraphs.lastOrNull()?.trim() ?: "Analysis completed based on available information"
    }
    
    private fun extractAlternatives(content: String): List<String> {
        val alternativePatterns = listOf(
            "(?i)alternatively,?\s+(.+?)(?=\n|\.|$)",
            "(?i)another approach,?\s+(.+?)(?=\n|\.|$)",
            "(?i)option \d+:?\s+(.+?)(?=\n|option|$)"
        )
        
        val alternatives = mutableListOf<String>()
        alternativePatterns.forEach { pattern ->
            val matches = pattern.toRegex(RegexOption.MULTILINE).findAll(content)
            matches.forEach { match ->
                match.groups[1]?.value?.trim()?.let { alt ->
                    if (alt.length > 15) alternatives.add(alt)
                }
            }
        }
        
        return alternatives.take(3)
    }
    
    private fun calculateConfidence(choice: Choice, finishReason: String?): Double {
        val baseConfidence = when (finishReason) {
            "stop" -> 0.9
            "length" -> 0.7  // Truncated due to length
            "content_filter" -> 0.5
            else -> 0.8
        }
        
        // Adjust based on response characteristics
        val content = choice.message.content
        val certaintyIndicators = listOf("clearly", "definitely", "certainly", "obviously")
        val uncertaintyIndicators = listOf("might", "possibly", "perhaps", "unclear", "uncertain")
        
        val certaintyCount = certaintyIndicators.count { content.lowercase().contains(it) }
        val uncertaintyCount = uncertaintyIndicators.count { content.lowercase().contains(it) }
        
        val adjustment = (certaintyCount - uncertaintyCount) * 0.05
        return (baseConfidence + adjustment).coerceIn(0.1, 0.98)
    }
    
    private fun handleApiError(response: Response<ChatCompletionResponse>): AgentResponse {
        val errorMessage = "OpenAI API error: ${response.code()} ${response.message()}"
        return createErrorResponse(errorMessage)
    }
    
    private fun handleException(e: Exception, role: AgentRole, prompt: String, context: Map<String, Any>): AgentResponse {
        val errorMessage = "Service error: ${e.message ?: "Unknown error"}"
        return createErrorResponse(errorMessage)
    }
    
    private fun createErrorResponse(errorMessage: String): AgentResponse {
        return AgentResponse(
            agentId = "openai_error",
            content = "I apologize, but I'm currently experiencing technical difficulties. $errorMessage",
            reasoning = ChainOfThought(
                thoughts = listOf("Service error encountered", "Attempting graceful degradation"),
                finalReasoning = "Unable to process request due to service limitations",
                confidence = 0.1
            ),
            confidence = 0.1,
            alternatives = listOf("Please try again later", "Consider alternative analysis methods"),
            timestamp = Clock.System.now()
        )
    }
    
    private fun createRetryInterceptor(): Interceptor {
        return Interceptor { chain ->
            var request = chain.request()
            var response = chain.proceed(request)
            var retryCount = 0
            
            while (!response.isSuccessful && retryCount < 3) {
                val delay = when {
                    response.code == 429 -> 60000L // Rate limit - wait 60 seconds
                    response.code >= 500 -> (2000L * (retryCount + 1)) // Exponential backoff for server errors
                    else -> break // Don't retry client errors
                }
                
                response.close()
                Thread.sleep(delay)
                response = chain.proceed(request)
                retryCount++
            }
            
            response
        }
    }
    
    private fun createRateLimitInterceptor(): Interceptor {
        var lastRequestTime = 0L
        val minInterval = 100L // Minimum 100ms between requests
        
        return Interceptor { chain ->
            val currentTime = System.currentTimeMillis()
            val timeSinceLastRequest = currentTime - lastRequestTime
            
            if (timeSinceLastRequest < minInterval) {
                Thread.sleep(minInterval - timeSinceLastRequest)
            }
            
            lastRequestTime = System.currentTimeMillis()
            chain.proceed(chain.request())
        }
    }
    
    private fun generateResearchResponse(prompt: String, context: Map<String, Any>): AgentResponse {
        // This is a fallback method - normally the real API response would be used
        val thoughts = listOf(
            "Analyzing the research question: ${prompt.take(50)}...",
            "Identifying key information sources and methodologies",
            "Evaluating credibility and relevance of findings",
            "Synthesizing research insights into actionable knowledge"
        )
        
        val content = """
            [FALLBACK RESPONSE - API integration in progress]
            Based on research analysis of: ${prompt.take(100)}...
            
            Key Findings:
            • Primary insight: ${generateInsight(prompt)}
            • Supporting evidence: Multiple sources converge on this conclusion
            • Methodology: Systematic review and meta-analysis approach
            • Implications: ${generateImplications(prompt)}
            
            Confidence Level: Moderate (fallback response)
        """.trimIndent()
        
        return AgentResponse(
            agentId = "openai_researcher_fallback",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = "Applied systematic research methodology to evaluate evidence and draw conclusions",
                confidence = 0.6 // Lower confidence for fallback
            ),
            confidence = 0.6,
            alternatives = generateAlternativeResponses(prompt, 2),
            timestamp = Clock.System.now()
        )
    }
    
    private fun generateCriticalResponse(prompt: String, context: Map<String, Any>): AgentResponse {
        val thoughts = listOf(
            "Examining assumptions and biases in: ${prompt.take(50)}...",
            "Identifying potential weaknesses and logical fallacies",
            "Evaluating evidence quality and source reliability",
            "Constructing balanced critical assessment"
        )
        
        val content = """
            Critical Analysis of: ${prompt.take(100)}...
            
            Strengths:
            • ${generateStrength(prompt)}
            • Evidence-based approach with clear methodology
            
            Weaknesses:
            • ${generateWeakness(prompt)}
            • Potential bias in source selection
            
            Recommendations:
            • ${generateRecommendation(prompt)}
            • Consider alternative perspectives and methodologies
            
            Overall Assessment: Moderate to Strong with noted limitations
        """.trimIndent()
        
        return AgentResponse(
            agentId = "openai_critic_fallback",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = "Applied systematic critical analysis framework to identify strengths, weaknesses, and improvement opportunities",
                confidence = Random.nextDouble(0.70, 0.85)
            ),
            confidence = Random.nextDouble(0.70, 0.85),
            alternatives = generateAlternativeResponses(prompt, 2),
            timestamp = Clock.System.now()
        )
    }
    
    private fun generateSynthesisResponse(prompt: String, context: Map<String, Any>): AgentResponse {
        val thoughts = listOf(
            "Integrating multiple perspectives on: ${prompt.take(50)}...",
            "Identifying common patterns and divergent viewpoints",
            "Weaving together complementary insights",
            "Creating unified synthesis with emergent properties"
        )
        
        val content = """
            Synthesis of: ${prompt.take(100)}...
            
            Integrated Insights:
            • ${generateSynthesis(prompt)}
            • Convergent themes: ${generateThemes(prompt)}
            • Emergent patterns: ${generatePatterns(prompt)}
            
            Unified Framework:
            ${generateFramework(prompt)}
            
            Novel Connections:
            • ${generateConnections(prompt)}
            
            This synthesis reveals deeper relationships and creates new understanding beyond individual components.
        """.trimIndent()
        
        return AgentResponse(
            agentId = "openai_synthesizer_fallback",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = "Applied integrative thinking to synthesize multiple perspectives into coherent unified understanding",
                confidence = Random.nextDouble(0.80, 0.92)
            ),
            confidence = Random.nextDouble(0.80, 0.92),
            alternatives = generateAlternativeResponses(prompt, 3),
            timestamp = Clock.System.now()
        )
    }
    
    private fun generateAnalysisResponse(prompt: String, context: Map<String, Any>): AgentResponse {
        val thoughts = listOf(
            "Decomposing complex elements in: ${prompt.take(50)}...",
            "Applying analytical frameworks and metrics",
            "Quantifying relationships and dependencies",
            "Drawing data-driven conclusions"
        )
        
        val content = """
            Analytical Breakdown of: ${prompt.take(100)}...
            
            Component Analysis:
            • Primary elements: ${generateComponents(prompt)}
            • Relationship matrix: ${generateRelationships(prompt)}
            • Performance metrics: ${generateMetrics(prompt)}
            
            Statistical Insights:
            • Correlation strength: ${Random.nextDouble(0.4, 0.9).format(2)}
            • Variance explained: ${Random.nextDouble(0.6, 0.95).format(2)}
            • Confidence intervals: [${Random.nextDouble(0.7, 0.85).format(2)}, ${Random.nextDouble(0.85, 0.95).format(2)}]
            
            Predictive Model:
            ${generatePredictiveModel(prompt)}
        """.trimIndent()
        
        return AgentResponse(
            agentId = "openai_analyzer_fallback",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = "Applied quantitative analytical methods to decompose and understand system behavior",
                confidence = Random.nextDouble(0.82, 0.94)
            ),
            confidence = Random.nextDouble(0.82, 0.94),
            alternatives = generateAlternativeResponses(prompt, 2),
            timestamp = Clock.System.now()
        )
    }
    
    private fun generateCoordinationResponse(prompt: String, context: Map<String, Any>): AgentResponse {
        val thoughts = listOf(
            "Orchestrating multi-agent response to: ${prompt.take(50)}...",
            "Identifying task dependencies and resource allocation",
            "Establishing communication protocols and timelines",
            "Monitoring progress and adjusting coordination strategy"
        )
        
        val content = """
            Coordination Plan for: ${prompt.take(100)}...
            
            Task Distribution:
            • ${generateTaskAllocation(prompt)}
            • Resource requirements: ${generateResourceNeeds(prompt)}
            • Timeline: ${generateTimeline(prompt)}
            
            Communication Framework:
            • ${generateCommunicationPlan(prompt)}
            • Synchronization points: Every 2-3 iterations
            • Conflict resolution: Consensus-based decision making
            
            Success Metrics:
            • ${generateSuccessMetrics(prompt)}
            
            Risk Mitigation:
            • ${generateRiskMitigation(prompt)}
        """.trimIndent()
        
        return AgentResponse(
            agentId = "openai_coordinator_fallback",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = "Developed comprehensive coordination strategy optimizing for efficiency, communication, and goal achievement",
                confidence = Random.nextDouble(0.78, 0.90)
            ),
            confidence = Random.nextDouble(0.78, 0.90),
            alternatives = generateAlternativeResponses(prompt, 2),
            timestamp = Clock.System.now()
        )
    }
    
    private fun generateSpecialistResponse(prompt: String, context: Map<String, Any>): AgentResponse {
        val domain = context["domain"] as? String ?: "general"
        
        val thoughts = listOf(
            "Applying specialized ${domain} expertise to: ${prompt.take(50)}...",
            "Leveraging domain-specific knowledge and best practices",
            "Considering field-specific constraints and opportunities",
            "Providing expert-level insights and recommendations"
        )
        
        val content = """
            Specialist Analysis (${domain.capitalize()}): ${prompt.take(100)}...
            
            Domain-Specific Insights:
            • ${generateDomainInsight(prompt, domain)}
            • Expert knowledge: ${generateExpertKnowledge(prompt, domain)}
            • Best practices: ${generateBestPractices(prompt, domain)}
            
            Technical Recommendations:
            • ${generateTechnicalRec(prompt, domain)}
            • Implementation approach: ${generateImplementation(prompt, domain)}
            
            Risk Assessment:
            • ${generateDomainRisks(prompt, domain)}
            
            This represents cutting-edge understanding in ${domain} applied to your specific context.
        """.trimIndent()
        
        return AgentResponse(
            agentId = "openai_specialist_${domain}_fallback",
            content = content,
            reasoning = ChainOfThought(
                thoughts = thoughts,
                finalReasoning = "Applied deep domain expertise and specialized knowledge to provide authoritative insights",
                confidence = Random.nextDouble(0.85, 0.97)
            ),
            confidence = Random.nextDouble(0.85, 0.97),
            alternatives = generateAlternativeResponses(prompt, 2),
            timestamp = Clock.System.now()
        )
    }
    
    private fun generateAlternativeResponses(prompt: String, count: Int): List<String> {
        return (1..count).map { i ->
            "Alternative approach $i: ${generateAlternativeApproach(prompt, i)}"
        }
    }
    
    // Helper functions for content generation
    private fun generateInsight(prompt: String) = "Key insight derived from ${prompt.split(" ").take(3).joinToString(" ")} analysis"
    private fun generateImplications(prompt: String) = "Significant implications for ${prompt.split(" ").lastOrNull()} domain"
    private fun generateStrength(prompt: String) = "Strong methodological foundation in ${prompt.split(" ").take(2).joinToString(" ")}"
    private fun generateWeakness(prompt: String) = "Limited scope in ${prompt.split(" ").drop(2).take(2).joinToString(" ")} considerations"
    private fun generateRecommendation(prompt: String) = "Enhance ${prompt.split(" ").take(2).joinToString(" ")} with broader perspective"
    private fun generateSynthesis(prompt: String) = "Unified understanding emerges from ${prompt.split(" ").take(3).joinToString(" ")} integration"
    private fun generateThemes(prompt: String) = prompt.split(" ").take(3).joinToString(", ")
    private fun generatePatterns(prompt: String) = "Recurring patterns in ${prompt.split(" ").drop(1).take(2).joinToString(" ")}"
    private fun generateFramework(prompt: String) = "Structured approach connecting ${prompt.split(" ").take(2).joinToString(" ")} elements"
    private fun generateConnections(prompt: String) = "Novel links between ${prompt.split(" ").take(2).joinToString(" ")} and broader context"
    private fun generateComponents(prompt: String) = prompt.split(" ").take(3).joinToString(", ")
    private fun generateRelationships(prompt: String) = "Complex interdependencies among ${prompt.split(" ").take(2).joinToString(" ")} factors"
    private fun generateMetrics(prompt: String) = "Performance indicators for ${prompt.split(" ").take(2).joinToString(" ")} evaluation"
    private fun generatePredictiveModel(prompt: String) = "Predictive framework for ${prompt.split(" ").take(2).joinToString(" ")} outcomes"
    private fun generateTaskAllocation(prompt: String) = "Distributed processing of ${prompt.split(" ").take(3).joinToString(" ")} components"
    private fun generateResourceNeeds(prompt: String) = "Computational and knowledge resources for ${prompt.split(" ").take(2).joinToString(" ")}"
    private fun generateTimeline(prompt: String) = "Phased approach with ${Random.nextInt(3, 7)} key milestones"
    private fun generateCommunicationPlan(prompt: String) = "Regular sync protocols for ${prompt.split(" ").take(2).joinToString(" ")} coordination"
    private fun generateSuccessMetrics(prompt: String) = "Quality and efficiency metrics for ${prompt.split(" ").take(2).joinToString(" ")}"
    private fun generateRiskMitigation(prompt: String) = "Contingency plans for ${prompt.split(" ").take(2).joinToString(" ")} challenges"
    private fun generateDomainInsight(prompt: String, domain: String) = "$domain-specific perspective on ${prompt.split(" ").take(2).joinToString(" ")}"
    private fun generateExpertKnowledge(prompt: String, domain: String) = "Advanced $domain principles applied to ${prompt.split(" ").take(2).joinToString(" ")}"
    private fun generateBestPractices(prompt: String, domain: String) = "Industry-standard $domain practices for ${prompt.split(" ").take(2).joinToString(" ")}"
    private fun generateTechnicalRec(prompt: String, domain: String) = "Technical implementation using $domain methodologies"
    private fun generateImplementation(prompt: String, domain: String) = "Systematic $domain implementation strategy"
    private fun generateDomainRisks(prompt: String, domain: String) = "$domain-specific risks and mitigation strategies"
    private fun generateAlternativeApproach(prompt: String, index: Int) = "Alternative method $index for ${prompt.split(" ").take(2).joinToString(" ")}"
    
    private fun Double.format(digits: Int) = "%.${digits}f".format(this)
    
    fun getAverageLatency(): Double = if (latencyHistory.isNotEmpty()) latencyHistory.average() else 0.0
    fun getTotalRequests(): Int = totalRequests
    fun getErrorCount(): Int = errorCount
    fun getSuccessRate(): Double = if (totalRequests > 0) (totalRequests - errorCount).toDouble() / totalRequests else 0.0
}

// Data classes for OpenAI API
@Serializable
data class ChatCompletionRequest(
    val model: String,
    val messages: List<Message>,
    val maxTokens: Int? = null,
    val temperature: Double? = null,
    val topP: Double? = null,
    val presencePenalty: Double? = null,
    val frequencyPenalty: Double? = null
)

@Serializable
data class Message(
    val role: String,
    val content: String
)

@Serializable
data class ChatCompletionResponse(
    val id: String,
    val object: String,
    val created: Long,
    val model: String,
    val choices: List<Choice>,
    val usage: Usage? = null
)

@Serializable
data class Choice(
    val index: Int,
    val message: Message,
    val finishReason: String? = null
)

@Serializable
data class Usage(
    val promptTokens: Int,
    val completionTokens: Int,
    val totalTokens: Int
)

@Serializable
data class EmbeddingRequest(
    val model: String,
    val input: String
)

@Serializable
data class EmbeddingResponse(
    val object: String,
    val data: List<EmbeddingData>,
    val model: String,
    val usage: EmbeddingUsage
)

@Serializable
data class EmbeddingData(
    val object: String,
    val embedding: List<Double>,
    val index: Int
)

@Serializable
data class EmbeddingUsage(
    val promptTokens: Int,
    val totalTokens: Int
)