package com.synthnet.aiapp.domain.ai

import com.synthnet.aiapp.domain.ai.embeddings.VectorEmbeddingService
import com.synthnet.aiapp.domain.ai.embeddings.EmbeddingType
import com.synthnet.aiapp.domain.ai.knowledge.KnowledgeGraphService
import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.repository.ThoughtRepository
import com.synthnet.aiapp.data.entities.ThoughtType
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext
import kotlinx.datetime.Clock
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.*

/**
 * Semantic Vector-of-Thought (VoT) Engine
 * 
 * Advanced reasoning system that combines:
 * - Tree of Thought exploration
 * - Semantic vector representations
 * - Knowledge graph integration
 * - Multi-dimensional reasoning paths
 * - Confidence-weighted synthesis
 */
@Singleton
class SemanticVoTEngine @Inject constructor(
    private val thoughtRepository: ThoughtRepository,
    private val embeddingService: VectorEmbeddingService,
    private val knowledgeGraphService: KnowledgeGraphService
) {
    
    suspend fun executeSemanticVoTWorkflow(
        projectId: String,
        prompt: String,
        agents: List<Agent>,
        context: ProjectContext
    ): Result<SemanticThoughtVector> = withContext(Dispatchers.Default) {
        try {
            coroutineScope {
                // Phase 1: Multi-dimensional thought generation
                val initialVectorThoughts = async { 
                    generateInitialVectorThoughts(projectId, prompt, agents, context) 
                }
                
                // Phase 2: Semantic clustering and analysis
                val semanticClusters = async { 
                    val thoughts = initialVectorThoughts.await()
                    clusterThoughtsBySemantics(thoughts)
                }
                
                // Phase 3: Knowledge graph augmentation
                val augmentedThoughts = async {
                    val thoughts = initialVectorThoughts.await()
                    augmentWithKnowledgeGraph(thoughts, context)
                }
                
                // Phase 4: Multi-path exploration
                val explorationPaths = async {
                    val thoughts = initialVectorThoughts.await()
                    exploreSemanticPaths(thoughts, context)
                }
                
                // Phase 5: Confidence-weighted synthesis
                val clusters = semanticClusters.await()
                val augmented = augmentedThoughts.await()
                val paths = explorationPaths.await()
                
                val synthesizedVector = synthesizeSemanticVector(
                    originalThoughts = initialVectorThoughts.await(),
                    clusters = clusters,
                    augmentedThoughts = augmented,
                    explorationPaths = paths
                )
                
                Result.success(synthesizedVector)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private suspend fun generateInitialVectorThoughts(
        projectId: String,
        prompt: String,
        agents: List<Agent>,
        context: ProjectContext
    ): List<VectorThought> {
        return agents.mapIndexed { index, agent ->
            val agentPerspective = generateAgentPerspective(agent, prompt, context)
            val embedding = embeddingService.generateEmbedding(
                text = "$prompt ${agentPerspective.reasoning}",
                type = EmbeddingType.SEMANTIC
            ).getOrThrow()
            
            VectorThought(
                id = generateThoughtId(),
                projectId = projectId,
                agentId = agent.id,
                content = agentPerspective.content,
                reasoning = agentPerspective.reasoning,
                confidence = agentPerspective.confidence,
                embedding = embedding,
                semanticDimensions = extractSemanticDimensions(agentPerspective, agent),
                thoughtType = ThoughtType.INITIAL,
                createdAt = Clock.System.now(),
                metadata = mapOf(
                    "agent_role" to agent.role.name,
                    "generation_order" to index.toString(),
                    "perspective_type" to agentPerspective.perspectiveType
                )
            )
        }
    }
    
    private suspend fun clusterThoughtsBySemantics(
        thoughts: List<VectorThought>
    ): List<SemanticCluster> {
        val embeddings = thoughts.map { it.embedding }
        val clusters = embeddingService.clusterEmbeddings(embeddings, numClusters = min(5, thoughts.size))
            .getOrElse { emptyList() }
        
        return clusters.mapIndexed { index, cluster ->
            val clusterThoughts = thoughts.filter { thought ->
                cluster.members.contains(thought.embedding)
            }
            
            SemanticCluster(
                id = "cluster_$index",
                thoughts = clusterThoughts,
                centroid = cluster.centroid,
                coherenceScore = calculateCoherenceScore(clusterThoughts),
                dominantTheme = extractDominantTheme(clusterThoughts),
                semanticDensity = calculateSemanticDensity(clusterThoughts)
            )
        }
    }
    
    private suspend fun augmentWithKnowledgeGraph(
        thoughts: List<VectorThought>,
        context: ProjectContext
    ): List<AugmentedVectorThought> {
        return thoughts.map { thought ->
            // Find related knowledge entities
            val relatedEntities = knowledgeGraphService.semanticSearch(
                query = thought.content,
                maxResults = 10,
                threshold = 0.7
            ).getOrElse { emptyList() }
            
            // Extract relevant context from project memory
            val relevantContext = context.getItemsByRelevance(0.6)
                .filter { contextItem ->
                    val contextEmbedding = embeddingService.generateEmbedding(
                        contextItem.content, EmbeddingType.CONTEXTUAL
                    ).getOrNull()
                    
                    contextEmbedding?.let { embedding ->
                        thought.embedding.cosineSimilarity(embedding) > 0.7
                    } ?: false
                }
            
            AugmentedVectorThought(
                originalThought = thought,
                relatedKnowledge = relatedEntities.map { it.entity },
                contextualConnections = relevantContext,
                knowledgeConfidence = calculateKnowledgeConfidence(relatedEntities),
                contextRelevance = calculateContextRelevance(relevantContext, thought)
            )
        }
    }
    
    private suspend fun exploreSemanticPaths(
        thoughts: List<VectorThought>,
        context: ProjectContext
    ): List<SemanticPath> {
        val paths = mutableListOf<SemanticPath>()
        
        // Generate paths by following semantic similarities
        thoughts.forEach { startThought ->
            val path = mutableListOf<VectorThought>(startThought)
            var currentThought = startThought
            
            // Follow semantic trail for up to 5 steps
            repeat(5) {
                val nextThought = findMostSimilarUnvisitedThought(
                    currentThought, 
                    thoughts, 
                    visited = path.map { it.id }.toSet()
                )
                
                if (nextThought != null && 
                    currentThought.embedding.cosineSimilarity(nextThought.embedding) > 0.6) {
                    path.add(nextThought)
                    currentThought = nextThought
                } else {
                    // Generate new thought to continue path
                    val syntheticThought = generateSyntheticThought(
                        currentThought, 
                        context,
                        step = path.size
                    )
                    if (syntheticThought != null) {
                        path.add(syntheticThought)
                        currentThought = syntheticThought
                    }
                }
            }
            
            if (path.size > 1) {
                paths.add(SemanticPath(
                    id = "path_${startThought.id}",
                    thoughts = path,
                    coherence = calculatePathCoherence(path),
                    novelty = calculatePathNovelty(path),
                    completeness = calculatePathCompleteness(path, context),
                    totalConfidence = path.map { it.confidence }.average()
                ))
            }
        }
        
        return paths.sortedByDescending { it.coherence * it.totalConfidence }
    }
    
    private suspend fun synthesizeSemanticVector(
        originalThoughts: List<VectorThought>,
        clusters: List<SemanticCluster>,
        augmentedThoughts: List<AugmentedVectorThought>,
        explorationPaths: List<SemanticPath>
    ): SemanticThoughtVector {
        
        // Weight different sources of information
        val clusterContributions = clusters.map { cluster ->
            VectorContribution(
                source = "cluster_${cluster.id}",
                weight = cluster.coherenceScore * cluster.semanticDensity,
                confidence = cluster.thoughts.map { it.confidence }.average(),
                reasoning = "Semantic cluster with theme: ${cluster.dominantTheme}"
            )
        }
        
        val knowledgeContributions = augmentedThoughts.map { augmented ->
            VectorContribution(
                source = "knowledge_${augmented.originalThought.id}",
                weight = augmented.knowledgeConfidence * augmented.contextRelevance,
                confidence = augmented.originalThought.confidence,
                reasoning = "Knowledge-augmented insight with ${augmented.relatedKnowledge.size} connections"
            )
        }
        
        val pathContributions = explorationPaths.take(3).map { path ->
            VectorContribution(
                source = "path_${path.id}",
                weight = path.coherence * path.novelty * path.completeness,
                confidence = path.totalConfidence,
                reasoning = "Semantic exploration path with ${path.thoughts.size} steps"
            )
        }
        
        val allContributions = clusterContributions + knowledgeContributions + pathContributions
        val totalWeight = allContributions.sumOf { it.weight }
        
        // Synthesize final embedding
        val synthesizedEmbedding = synthesizeWeightedEmbeddings(
            originalThoughts.map { it.embedding },
            allContributions.map { it.weight }
        )
        
        // Generate synthesis reasoning
        val synthesisReasoning = generateSynthesisReasoning(
            originalThoughts, clusters, explorationPaths, allContributions
        )
        
        // Calculate final confidence
        val finalConfidence = calculateFinalConfidence(allContributions, totalWeight)
        
        return SemanticThoughtVector(
            id = generateVectorId(),
            originalThoughts = originalThoughts,
            semanticClusters = clusters,
            explorationPaths = explorationPaths,
            contributions = allContributions,
            synthesizedEmbedding = synthesizedEmbedding,
            finalReasoning = synthesisReasoning,
            confidence = finalConfidence,
            noveltyScore = calculateOverallNovelty(explorationPaths),
            coherenceScore = calculateOverallCoherence(clusters),
            completenessScore = calculateOverallCompleteness(explorationPaths),
            createdAt = Clock.System.now()
        )
    }
    
    // Helper methods for perspective generation
    private fun generateAgentPerspective(
        agent: Agent,
        prompt: String,
        context: ProjectContext
    ): AgentPerspective {
        val roleBasedPrompt = adaptPromptToRole(prompt, agent.role)
        val contextualInsights = extractContextualInsights(context, agent)
        
        return when (agent.role) {
            com.synthnet.aiapp.data.entities.AgentRole.CONDUCTOR -> 
                generateConductorPerspective(roleBasedPrompt, contextualInsights)
            com.synthnet.aiapp.data.entities.AgentRole.STRATEGY -> 
                generateStrategyPerspective(roleBasedPrompt, contextualInsights)
            com.synthnet.aiapp.data.entities.AgentRole.IMPLEMENTATION -> 
                generateImplementationPerspective(roleBasedPrompt, contextualInsights)
            com.synthnet.aiapp.data.entities.AgentRole.TESTING -> 
                generateTestingPerspective(roleBasedPrompt, contextualInsights)
            com.synthnet.aiapp.data.entities.AgentRole.DOCUMENTATION -> 
                generateDocumentationPerspective(roleBasedPrompt, contextualInsights)
            com.synthnet.aiapp.data.entities.AgentRole.REVIEW -> 
                generateReviewPerspective(roleBasedPrompt, contextualInsights)
        }
    }
    
    private fun generateConductorPerspective(prompt: String, insights: List<String>): AgentPerspective {
        return AgentPerspective(
            content = "Orchestrating approach: $prompt",
            reasoning = "As conductor, I focus on coordination, resource allocation, and ensuring all agents work harmoniously toward the goal. ${insights.joinToString(" ")}",
            confidence = 0.85,
            perspectiveType = "orchestration"
        )
    }
    
    private fun generateStrategyPerspective(prompt: String, insights: List<String>): AgentPerspective {
        return AgentPerspective(
            content = "Strategic analysis: $prompt",
            reasoning = "From a strategic standpoint, I analyze long-term implications, competitive advantages, and optimal pathways. ${insights.joinToString(" ")}",
            confidence = 0.82,
            perspectiveType = "strategic"
        )
    }
    
    private fun generateImplementationPerspective(prompt: String, insights: List<String>): AgentPerspective {
        return AgentPerspective(
            content = "Implementation approach: $prompt",
            reasoning = "Focusing on technical feasibility, architecture decisions, and practical implementation steps. ${insights.joinToString(" ")}",
            confidence = 0.88,
            perspectiveType = "technical"
        )
    }
    
    private fun generateTestingPerspective(prompt: String, insights: List<String>): AgentPerspective {
        return AgentPerspective(
            content = "Quality assurance view: $prompt",
            reasoning = "Examining testability, edge cases, quality metrics, and validation strategies. ${insights.joinToString(" ")}",
            confidence = 0.80,
            perspectiveType = "quality"
        )
    }
    
    private fun generateDocumentationPerspective(prompt: String, insights: List<String>): AgentPerspective {
        return AgentPerspective(
            content = "Documentation analysis: $prompt",
            reasoning = "Considering clarity, completeness, maintainability, and knowledge transfer aspects. ${insights.joinToString(" ")}",
            confidence = 0.75,
            perspectiveType = "documentation"
        )
    }
    
    private fun generateReviewPerspective(prompt: String, insights: List<String>): AgentPerspective {
        return AgentPerspective(
            content = "Critical review: $prompt",
            reasoning = "Evaluating strengths, weaknesses, potential issues, and improvement opportunities. ${insights.joinToString(" ")}",
            confidence = 0.83,
            perspectiveType = "review"
        )
    }
    
    // Semantic analysis helper methods
    private fun extractSemanticDimensions(perspective: AgentPerspective, agent: Agent): SemanticDimensions {
        return SemanticDimensions(
            abstraction = calculateAbstractionLevel(perspective.content),
            complexity = calculateComplexityLevel(perspective.reasoning),
            creativity = calculateCreativityLevel(perspective.content, agent.metrics.innovationScore),
            practicality = calculatePracticalityLevel(perspective.content, agent.role),
            confidence = perspective.confidence,
            novelty = calculateNoveltyLevel(perspective.content)
        )
    }
    
    private fun calculateAbstractionLevel(content: String): Double {
        val abstractWords = listOf("concept", "theory", "principle", "framework", "paradigm", "model")
        val matches = abstractWords.count { content.lowercase().contains(it) }
        return minOf(1.0, matches / 3.0)
    }
    
    private fun calculateComplexityLevel(reasoning: String): Double {
        val complexityIndicators = listOf("however", "therefore", "consequently", "furthermore", "nevertheless")
        val matches = complexityIndicators.count { reasoning.lowercase().contains(it) }
        return minOf(1.0, matches / 2.0 + reasoning.split(" ").size / 50.0)
    }
    
    private fun calculateCreativityLevel(content: String, agentInnovation: Double): Double {
        val creativeWords = listOf("innovative", "novel", "creative", "unique", "breakthrough", "revolutionary")
        val matches = creativeWords.count { content.lowercase().contains(it) }
        return (agentInnovation + minOf(1.0, matches / 2.0)) / 2.0
    }
    
    private fun calculatePracticalityLevel(content: String, role: com.synthnet.aiapp.data.entities.AgentRole): Double {
        val practicalWords = listOf("implement", "execute", "build", "create", "deploy", "configure")
        val matches = practicalWords.count { content.lowercase().contains(it) }
        val roleBonus = when (role) {
            com.synthnet.aiapp.data.entities.AgentRole.IMPLEMENTATION -> 0.3
            com.synthnet.aiapp.data.entities.AgentRole.TESTING -> 0.2
            else -> 0.0
        }
        return minOf(1.0, (matches / 3.0) + roleBonus)
    }
    
    private fun calculateNoveltyLevel(content: String): Double {
        // Simple novelty calculation based on unique word combinations
        val words = content.split(" ").map { it.lowercase().replace(Regex("[^a-z]"), "") }
        val uniquePairs = words.zipWithNext().toSet()
        return minOf(1.0, uniquePairs.size / 10.0)
    }
    
    // Additional helper methods for clustering, path finding, and synthesis...
    private fun calculateCoherenceScore(thoughts: List<VectorThought>): Double {
        if (thoughts.size < 2) return 1.0
        
        val similarities = mutableListOf<Double>()
        for (i in thoughts.indices) {
            for (j in i + 1 until thoughts.size) {
                similarities.add(thoughts[i].embedding.cosineSimilarity(thoughts[j].embedding))
            }
        }
        return similarities.average()
    }
    
    private fun extractDominantTheme(thoughts: List<VectorThought>): String {
        val allWords = thoughts.flatMap { it.content.split(" ") }
            .map { it.lowercase().replace(Regex("[^a-z]"), "") }
            .filter { it.length > 3 }
        
        val wordCounts = allWords.groupingBy { it }.eachCount()
        return wordCounts.maxByOrNull { it.value }?.key ?: "mixed_themes"
    }
    
    private fun calculateSemanticDensity(thoughts: List<VectorThought>): Double {
        if (thoughts.isEmpty()) return 0.0
        
        val avgDimensions = thoughts.map { thought ->
            listOf(
                thought.semanticDimensions.abstraction,
                thought.semanticDimensions.complexity,
                thought.semanticDimensions.creativity,
                thought.semanticDimensions.practicality,
                thought.semanticDimensions.novelty
            ).average()
        }.average()
        
        return avgDimensions
    }
    
    private suspend fun generateSyntheticThought(
        baseThought: VectorThought,
        context: ProjectContext,
        step: Int
    ): VectorThought? {
        // Generate a synthetic thought that continues the semantic path
        val syntheticContent = "Building on ${baseThought.content.take(50)}... [synthetic step $step]"
        val syntheticReasoning = "Synthetic reasoning derived from previous thought with confidence ${baseThought.confidence}"
        
        val embedding = embeddingService.generateEmbedding(
            syntheticContent, EmbeddingType.SEMANTIC
        ).getOrNull() ?: return null
        
        return VectorThought(
            id = generateThoughtId(),
            projectId = baseThought.projectId,
            agentId = "synthetic_${baseThought.agentId}",
            content = syntheticContent,
            reasoning = syntheticReasoning,
            confidence = baseThought.confidence * 0.8, // Reduced confidence for synthetic thoughts
            embedding = embedding,
            semanticDimensions = baseThought.semanticDimensions.copy(novelty = 0.9),
            thoughtType = ThoughtType.SYNTHESIS,
            createdAt = Clock.System.now(),
            metadata = mapOf(
                "synthetic" to "true",
                "base_thought" to baseThought.id,
                "step" to step.toString()
            )
        )
    }
    
    // More helper methods would be implemented here...
    
    private fun adaptPromptToRole(prompt: String, role: com.synthnet.aiapp.data.entities.AgentRole): String {
        return when (role) {
            com.synthnet.aiapp.data.entities.AgentRole.CONDUCTOR -> "As a conductor, coordinate: $prompt"
            com.synthnet.aiapp.data.entities.AgentRole.STRATEGY -> "Strategically analyze: $prompt"
            com.synthnet.aiapp.data.entities.AgentRole.IMPLEMENTATION -> "How to implement: $prompt"
            com.synthnet.aiapp.data.entities.AgentRole.TESTING -> "Testing approach for: $prompt"
            com.synthnet.aiapp.data.entities.AgentRole.DOCUMENTATION -> "Document and explain: $prompt"
            com.synthnet.aiapp.data.entities.AgentRole.REVIEW -> "Critical review of: $prompt"
        }
    }
    
    private fun extractContextualInsights(context: ProjectContext, agent: Agent): List<String> {
        return context.getAllItems()
            .filter { it.relevanceScore > 0.7 }
            .take(3)
            .map { "Context: ${it.content.take(100)}" }
    }
    
    private fun calculateKnowledgeConfidence(relatedEntities: List<com.synthnet.aiapp.domain.ai.knowledge.SemanticSearchResult>): Double {
        return if (relatedEntities.isEmpty()) 0.0 else relatedEntities.map { it.similarity }.average()
    }
    
    private fun calculateContextRelevance(contextItems: List<ContextItem>, thought: VectorThought): Double {
        return contextItems.map { it.relevanceScore }.average()
    }
    
    private fun findMostSimilarUnvisitedThought(
        currentThought: VectorThought,
        allThoughts: List<VectorThought>,
        visited: Set<String>
    ): VectorThought? {
        return allThoughts
            .filter { it.id !in visited }
            .maxByOrNull { currentThought.embedding.cosineSimilarity(it.embedding) }
    }
    
    private fun calculatePathCoherence(path: List<VectorThought>): Double {
        if (path.size < 2) return 1.0
        val similarities = path.zipWithNext { a, b -> a.embedding.cosineSimilarity(b.embedding) }
        return similarities.average()
    }
    
    private fun calculatePathNovelty(path: List<VectorThought>): Double {
        return path.map { it.semanticDimensions.novelty }.average()
    }
    
    private fun calculatePathCompleteness(path: List<VectorThought>, context: ProjectContext): Double {
        // Measure how well the path addresses the original context
        val pathContent = path.joinToString(" ") { it.content }
        val contextContent = context.getAllItems().joinToString(" ") { it.content }
        
        // Simple overlap measure (could be enhanced with embeddings)
        val pathWords = pathContent.split(" ").map { it.lowercase() }.toSet()
        val contextWords = contextContent.split(" ").map { it.lowercase() }.toSet()
        
        return if (contextWords.isEmpty()) 1.0 
               else pathWords.intersect(contextWords).size.toDouble() / contextWords.size
    }
    
    private fun synthesizeWeightedEmbeddings(
        embeddings: List<VectorEmbeddingService.Embedding>,
        weights: List<Double>
    ): VectorEmbeddingService.Embedding {
        val dimension = embeddings.firstOrNull()?.dimension ?: 384
        val synthesizedVector = FloatArray(dimension) { 0f }
        
        val totalWeight = weights.sum()
        if (totalWeight > 0) {
            embeddings.zip(weights).forEach { (embedding, weight) ->
                val normalizedWeight = (weight / totalWeight).toFloat()
                embedding.vector.forEachIndexed { i, value ->
                    synthesizedVector[i] += value * normalizedWeight
                }
            }
        }
        
        return VectorEmbeddingService.Embedding(
            vector = synthesizedVector,
            metadata = mapOf(
                "synthesis_type" to "weighted_combination",
                "source_count" to embeddings.size,
                "total_weight" to totalWeight
            )
        )
    }
    
    private fun generateSynthesisReasoning(
        originalThoughts: List<VectorThought>,
        clusters: List<SemanticCluster>,
        paths: List<SemanticPath>,
        contributions: List<VectorContribution>
    ): String {
        val topContributions = contributions.sortedByDescending { it.weight }.take(3)
        
        return buildString {
            append("Semantic Vector-of-Thought synthesis from ${originalThoughts.size} initial thoughts. ")
            append("Key insights: ")
            
            topContributions.forEach { contribution ->
                append("${contribution.reasoning} (confidence: ${(contribution.confidence * 100).toInt()}%). ")
            }
            
            append("Semantic coherence across ${clusters.size} clusters. ")
            append("Explored ${paths.size} reasoning paths. ")
            append("Final synthesis represents weighted integration of all semantic dimensions.")
        }
    }
    
    private fun calculateFinalConfidence(contributions: List<VectorContribution>, totalWeight: Double): Double {
        return if (totalWeight > 0) {
            contributions.sumOf { it.weight * it.confidence } / totalWeight
        } else {
            0.5
        }
    }
    
    private fun calculateOverallNovelty(paths: List<SemanticPath>): Double {
        return paths.map { it.novelty }.average()
    }
    
    private fun calculateOverallCoherence(clusters: List<SemanticCluster>): Double {
        return clusters.map { it.coherenceScore }.average()
    }
    
    private fun calculateOverallCompleteness(paths: List<SemanticPath>): Double {
        return paths.map { it.completeness }.average()
    }
    
    private fun generateThoughtId(): String = "thought_${System.currentTimeMillis()}_${kotlin.random.Random.nextInt(1000)}"
    private fun generateVectorId(): String = "vector_${System.currentTimeMillis()}_${kotlin.random.Random.nextInt(1000)}"
}

// Data models for Semantic VoT
data class VectorThought(
    val id: String,
    val projectId: String,
    val agentId: String,
    val content: String,
    val reasoning: String,
    val confidence: Double,
    val embedding: VectorEmbeddingService.Embedding,
    val semanticDimensions: SemanticDimensions,
    val thoughtType: ThoughtType,
    val createdAt: kotlinx.datetime.Instant,
    val metadata: Map<String, String> = emptyMap()
)

data class SemanticDimensions(
    val abstraction: Double,
    val complexity: Double,
    val creativity: Double,
    val practicality: Double,
    val confidence: Double,
    val novelty: Double
)

data class AgentPerspective(
    val content: String,
    val reasoning: String,
    val confidence: Double,
    val perspectiveType: String
)

data class SemanticCluster(
    val id: String,
    val thoughts: List<VectorThought>,
    val centroid: VectorEmbeddingService.Embedding,
    val coherenceScore: Double,
    val dominantTheme: String,
    val semanticDensity: Double
)

data class AugmentedVectorThought(
    val originalThought: VectorThought,
    val relatedKnowledge: List<com.synthnet.aiapp.domain.ai.knowledge.KnowledgeEntity>,
    val contextualConnections: List<ContextItem>,
    val knowledgeConfidence: Double,
    val contextRelevance: Double
)

data class SemanticPath(
    val id: String,
    val thoughts: List<VectorThought>,
    val coherence: Double,
    val novelty: Double,
    val completeness: Double,
    val totalConfidence: Double
)

data class VectorContribution(
    val source: String,
    val weight: Double,
    val confidence: Double,
    val reasoning: String
)

data class SemanticThoughtVector(
    val id: String,
    val originalThoughts: List<VectorThought>,
    val semanticClusters: List<SemanticCluster>,
    val explorationPaths: List<SemanticPath>,
    val contributions: List<VectorContribution>,
    val synthesizedEmbedding: VectorEmbeddingService.Embedding,
    val finalReasoning: String,
    val confidence: Double,
    val noveltyScore: Double,
    val coherenceScore: Double,
    val completenessScore: Double,
    val createdAt: kotlinx.datetime.Instant
)