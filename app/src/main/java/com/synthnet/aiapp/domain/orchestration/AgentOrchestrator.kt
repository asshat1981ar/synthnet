package com.synthnet.aiapp.domain.orchestration

import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine
import com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting
import com.synthnet.aiapp.domain.services.CollaborationManager
import com.synthnet.aiapp.domain.services.AntifragileSystem
import com.synthnet.aiapp.domain.repository.AgentRepository
import com.synthnet.aiapp.domain.repository.ThoughtRepository
import com.synthnet.aiapp.domain.repository.CollaborationRepository
import com.synthnet.aiapp.domain.ai.service.AIServiceIntegration
import com.synthnet.aiapp.data.entities.AgentStatus
import com.synthnet.aiapp.data.entities.AgentRole
import com.synthnet.aiapp.data.entities.SessionType
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.datetime.Clock
import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.exp
import kotlin.math.max

/**
 * Central orchestration system for managing multi-agent AI workflows.
 * 
 * This orchestrator coordinates between multiple AI agents, facilitating:
 * - Intelligent agent selection based on task requirements
 * - Tree-of-Thought reasoning workflows
 * - Multi-agent collaboration and consensus building
 * - Recursive meta-prompting for response optimization
 * - Antifragile error recovery and system adaptation
 * 
 * @param agentRepository Repository for agent data and operations
 * @param thoughtRepository Repository for thought tree persistence
 * @param collaborationRepository Repository for collaboration session management
 * @param totEngine Tree of Thought reasoning engine
 * @param rmpEngine Recursive Meta-Prompting optimization engine
 * @param collaborationManager Real-time collaboration coordination
 * @param antifragileSystem Error recovery and system resilience
 * @param aiServiceIntegration AI service integration layer
 * @param applicationScope A CoroutineScope tied to the application's lifecycle for background tasks.
 */
@Singleton
class AgentOrchestrator @Inject constructor(
    private val agentRepository: AgentRepository,
    private val thoughtRepository: ThoughtRepository,
    private val collaborationRepository: CollaborationRepository,
    private val totEngine: TreeOfThoughtEngine,
    private val rmpEngine: RecursiveMetaPrompting,
    private val collaborationManager: CollaborationManager,
    private val antifragileSystem: AntifragileSystem,
    private val aiServiceIntegration: AIServiceIntegration,
    private val applicationScope: CoroutineScope // Injected application-level scope
) {
    private val _orchestrationState = MutableStateFlow(OrchestrationState())
    val orchestrationState: StateFlow<OrchestrationState> = _orchestrationState.asStateFlow()
    
    /**
     * Processes user input through the complete multi-agent workflow
     * 
     * @param projectId ID of the project context
     * @param input User's input/query
     * @param context Current project context and memory
     * @return Comprehensive AI response from multi-agent collaboration
     */
    suspend fun processUserInput(
        projectId: String,
        input: String,
        context: ProjectContext
    ): Result<AgentResponse> = antifragileSystem.executeWithFallback("processUserInput") {
        _orchestrationState.value = _orchestrationState.value.copy(
            isProcessing = true,
            currentTask = "Processing user input"
        )
        
        try {
            Log.d(TAG, "Processing user input: ${input.take(100)}...")
            
            // Step 1: Activate relevant agents
            val startTime = Clock.System.now()
            _orchestrationState.value = _orchestrationState.value.copy(
                processingStartTime = startTime,
                currentTask = "Selecting relevant agents"
            )
            
            val agents = agentRepository.getAgentsByProject(projectId)
            val activeAgentsResult = withContext(Dispatchers.Default) { // Offload computation
                selectRelevantAgents(agents, input, context)
            }
            
            val activeAgents = activeAgentsResult.getOrElse { throw it }
            
            if (activeAgents.isEmpty()) {
                throw IllegalStateException("No suitable agents available for project $projectId")
            }
            
            // Update agent statuses to THINKING
            coroutineScope { // Use coroutineScope to ensure all updates complete before proceeding
                activeAgents.map { agent ->
                    async {
                        updateAgentStatus(agent.id, AgentStatus.THINKING)
                    }
                }.awaitAll()
            }
            
            _orchestrationState.value = _orchestrationState.value.copy(
                activeAgents = activeAgents,
                currentTask = "Executing Tree of Thought workflow"
            )
            
            // Step 2: Execute Tree of Thought workflow
            Log.d(TAG, "Executing ToT workflow with ${activeAgents.size} agents")
            val thoughtTree = totEngine.executeToTWorkflow(
                projectId = projectId,
                prompt = input,
                agents = activeAgents,
                context = context
            )
            
            _orchestrationState.value = _orchestrationState.value.copy(
                thoughtTreesActive = 1,
                currentTask = "Starting collaboration session"
            )
            
            // Step 3: Facilitate agent collaboration
            Log.d(TAG, "Starting collaboration with agents: ${activeAgents.map { it.id }}")
            val collaboration = collaborationManager.startCollaboration(
                projectId = projectId,
                participants = activeAgents.map { it.id },
                thoughtTree = thoughtTree,
                sessionType = SessionType.PROBLEM_SOLVING
            )
            
            _orchestrationState.value = _orchestrationState.value.copy(
                collaborationSessions = 1,
                activeCollaborations = listOf(collaboration),
                currentTask = "Synthesizing response"
            )
            
            // Step 4: Generate synthesized response
            Log.d(TAG, "Synthesizing response from thought tree and collaboration")
            val responseResult = withContext(Dispatchers.Default) { // Offload computation
                synthesizeResponse(thoughtTree, collaboration)
            }
            
            val response = responseResult.getOrElse { throw it }
            
            _orchestrationState.value = _orchestrationState.value.copy(
                currentTask = "Optimizing response quality"
            )
            
            // Step 5: Apply recursive meta-prompting for improvement
            Log.d(TAG, "Applying meta-prompting optimization")
            val optimizedResponse = rmpEngine.optimizeResponse(response, context)
            
            // Update agent statuses back to IDLE
            coroutineScope { // Use coroutineScope to ensure all updates complete before proceeding
                activeAgents.map { agent ->
                    async {
                        updateAgentStatus(agent.id, AgentStatus.IDLE)
                    }
                }.awaitAll()
            }
            
            val processingTime = Clock.System.now().toEpochMilliseconds() - startTime.toEpochMilliseconds()
            Log.d(TAG, "Successfully processed input in ${processingTime}ms")
            
            _orchestrationState.value = _orchestrationState.value.copy(
                isProcessing = false,
                currentTask = "Completed",
                lastResponse = optimizedResponse,
                error = null
            )
            
            Result.success(optimizedResponse)
        } catch (e: Exception) {
            Log.e(TAG, "Error processing user input", e)
            
            // Reset agent statuses on error
            applicationScope.launch { // Launch in applicationScope as it's a fire-and-forget cleanup
                _orchestrationState.value.activeAgents.forEach { agent ->
                    try {
                        updateAgentStatus(agent.id, AgentStatus.ERROR)
                    } catch (resetError: Exception) {
                        Log.e(TAG, "Error resetting agent statuses", resetError)
                    }
                }
            }
            
            _orchestrationState.value = _orchestrationState.value.copy(
                isProcessing = false,
                currentTask = "Error occurred",
                error = e.message ?: "Unknown error occurred",
                activeAgents = emptyList(),
                thoughtTreesActive = 0,
                collaborationSessions = 0
            )
            Result.failure(e)
        }
    }
    
    /**
     * Selects and follows a specific reasoning path through the thought tree
     * 
     * @param thoughtTree The thought tree to select from
     * @param selectedPath List of thought IDs representing the path
     * @return Response based on the selected reasoning path
     */
    suspend fun selectThoughtPath(
        thoughtTree: ThoughtTree,
        selectedPath: List<String>
    ): Result<AgentResponse> = antifragileSystem.executeWithFallback("selectThoughtPath") {
        Log.d(TAG, "Selecting thought path: $selectedPath")
        
        if (selectedPath.isEmpty()) {
            return@executeWithFallback Result.failure(
                IllegalArgumentException("Selected path cannot be empty")
            )
        }
        
        _orchestrationState.value = _orchestrationState.value.copy(
            isProcessing = true,
            currentTask = "Selecting thought path"
        )
        
        val selectedThoughts = selectedPath.mapNotNull { thoughtId ->
            thoughtRepository.getThoughtById(thoughtId)
        }
        
        if (selectedThoughts.size != selectedPath.size) {
            Log.w(TAG, "Some thoughts in path not found. Expected: ${selectedPath.size}, Found: ${selectedThoughts.size}")
        }
        
        // Validate path coherence
        val pathValidation = withContext(Dispatchers.Default) { // Offload computation
            validateThoughtPath(selectedThoughts)
        }
        if (!pathValidation.isValid) {
            return@executeWithFallback Result.failure(
                IllegalArgumentException("Invalid thought path: ${pathValidation.reason}")
            )
        }
        
        // Mark thoughts as selected in the repository
        selectedThoughts.forEach { thought ->
            applicationScope.launch { // Launch in applicationScope as it's a fire-and-forget update
                try {
                    thoughtRepository.selectThought(thought.id)
                } catch (e: Exception) {
                    Log.w(TAG, "Failed to mark thought ${thought.id} as selected", e)
                }
            }
        }
        
        // Generate response based on selected path
        val responseResult = withContext(Dispatchers.Default) { // Offload computation
            generatePathResponse(selectedThoughts)
        }
        
        val response = responseResult.getOrElse { throw it }
        
        _orchestrationState.value = _orchestrationState.value.copy(
            isProcessing = false,
            currentTask = "Path selection completed",
            lastResponse = response
        )
        
        Log.d(TAG, "Successfully selected thought path with ${selectedThoughts.size} thoughts")
        Result.success(response)
    }
    
    /**
     * Selects the most relevant agents for a given task based on:
     * - Agent capabilities and roles
     * - Input complexity and domain
     * - Current agent availability and load
     * - Historical performance metrics
     * - Context relevance scores
     */
    private suspend fun selectRelevantAgents(
        agents: Flow<List<Agent>>,
        input: String,
        context: ProjectContext
    ): Result<List<Agent>> = withContext(Dispatchers.Default) { // Ensure this computation is offloaded
        return@withContext try {
            val allAgents = agents.first()
            val availableAgents = allAgents.filter { agent ->
                agent.status in listOf(AgentStatus.IDLE, AgentStatus.THINKING)
            }
            
            if (availableAgents.isEmpty()) {
                Log.w(TAG, "No available agents found, using all agents")
                return@withContext Result.success(allAgents.take(MAX_CONCURRENT_AGENTS))
            }
            
            // Calculate relevance scores for each agent
            val agentScores = availableAgents.map { agent ->
                val score = calculateAgentRelevanceScore(agent, input, context)
                AgentScore(agent, score)
            }.sortedByDescending { it.score }
            
            // Select diverse set of high-scoring agents
            val selectedAgents = selectDiverseAgentSet(agentScores)
            
            Log.d(TAG, "Selected ${selectedAgents.size} agents: ${selectedAgents.map { "${it.role}(${it.metrics.successRate})" }}")
            
            Result.success(selectedAgents)
        } catch (e: Exception) {
            Log.e(TAG, "Error selecting agents", e)
            // Fallback to default agent selection
            Result.failure(e)
        }
    }
    
    /**
     * Calculates relevance score for an agent based on multiple factors
     */
    private suspend fun calculateAgentRelevanceScore(
        agent: Agent,
        input: String,
        context: ProjectContext
    ): Double = withContext(Dispatchers.Default) { // Ensure this computation is offloaded
        val roleWeight = getRoleWeight(agent.role, input)
        val performanceScore = agent.metrics.successRate
        val loadScore = 1.0 - (agent.metrics.averageResponseTime / MAX_RESPONSE_TIME)
        val contextRelevance = calculateContextRelevance(agent, context)
        val capabilityMatch = calculateCapabilityMatch(agent.capabilities, input)
        
        return@withContext (roleWeight * 0.3 + 
                performanceScore * 0.25 + 
                loadScore.coerceIn(0.0, 1.0) * 0.15 + 
                contextRelevance * 0.15 + 
                capabilityMatch * 0.15)
    }
    
    /**
     * Determines role importance based on input characteristics
     */
    private fun getRoleWeight(role: AgentRole, input: String): Double {
        val inputLower = input.lowercase()
        return when (role) {
            AgentRole.CONDUCTOR -> if (inputLower.contains("coordinate") || inputLower.contains("manage")) 0.9 else 0.6
            AgentRole.STRATEGY -> if (inputLower.contains("plan") || inputLower.contains("strategy")) 0.9 else 0.7
            AgentRole.IMPLEMENTATION -> if (inputLower.contains("implement") || inputLower.contains("build")) 0.9 else 0.8
            AgentRole.TESTING -> if (inputLower.contains("test") || inputLower.contains("verify")) 0.9 else 0.5
            AgentRole.DOCUMENTATION -> if (inputLower.contains("document") || inputLower.contains("explain")) 0.9 else 0.4
            AgentRole.REVIEW -> if (inputLower.contains("review") || inputLower.contains("analyze")) 0.9 else 0.6
        }
    }
    
    /**
     * Calculates how relevant an agent is to the current project context
     */
    private fun calculateContextRelevance(agent: Agent, context: ProjectContext): Double {
        val relevantItems = context.getItemsByRelevance(0.5)
        if (relevantItems.isEmpty()) return 0.5
        
        val agentCapabilityText = agent.capabilities.joinToString(" ").lowercase()
        val contextText = relevantItems.joinToString(" ") { it.content }.lowercase()
        
        // Simple keyword matching - in production, use semantic similarity
        val commonTerms = agentCapabilityText.split(" ").intersect(
            contextText.split(" ").toSet()
        )
        
        return (commonTerms.size.toDouble() / agent.capabilities.size.coerceAtLeast(1)).coerceAtMost(1.0)
    }
    
    /**
     * Calculates how well agent capabilities match the input requirements
     */
    private fun calculateCapabilityMatch(capabilities: List<String>, input: String): Double {
        if (capabilities.isEmpty()) return 0.0
        
        val inputLower = input.lowercase()
        val matchingCapabilities = capabilities.count { capability ->
            inputLower.contains(capability.lowercase())
        }
        
        return matchingCapabilities.toDouble() / capabilities.size
    }
    
    /**
     * Selects a diverse set of agents to avoid redundancy
     */
    private fun selectDiverseAgentSet(agentScores: List<AgentScore>): List<Agent> {
        val selected = mutableListOf<Agent>()
        val usedRoles = mutableSetOf<AgentRole>()
        
        // First pass: select highest scoring agent for each unique role
        for (agentScore in agentScores) {
            if (agentScore.agent.role !in usedRoles && selected.size < MAX_CONCURRENT_AGENTS) {
                selected.add(agentScore.agent)
                usedRoles.add(agentScore.agent.role)
            }
        }
        
        // Second pass: fill remaining slots with highest scoring agents
        for (agentScore in agentScores) {
            if (agentScore.agent !in selected && selected.size < MAX_CONCURRENT_AGENTS) {
                selected.add(agentScore.agent)
            }
        }
        
        return selected.ifEmpty { 
            // Emergency fallback
            agentScores.take(3).map { it.agent }
        }
    }
    
    /**
     * Synthesizes a comprehensive response from multiple sources:
     * - Best thoughts from the thought tree
     * - Collaborative insights and consensus
     * - Agent-specific contributions
     * - Confidence-weighted evidence
     */
    private suspend fun synthesizeResponse(
        thoughtTree: ThoughtTree,
        collaboration: Collaboration
    ): Result<AgentResponse> = withContext(Dispatchers.Default) { // Ensure this computation is offloaded
        return@withContext try {
            // Extract best thoughts from the tree
            val bestThoughts = extractBestThoughts(thoughtTree)
            val collaborativeInsights = extractCollaborativeInsights(collaboration)
            
            // Combine insights with confidence weighting
            val synthesizedContent = synthesizeContent(bestThoughts, collaborativeInsights)
            val synthesizedReasoning = synthesizeReasoning(bestThoughts, collaboration)
            val overallConfidence = calculateSynthesizedConfidence(bestThoughts, collaboration)
            val alternatives = generateSynthesizedAlternatives(bestThoughts)
            
            Result.success(AgentResponse(
                agentId = "orchestrator",
                content = synthesizedContent,
                reasoning = synthesizedReasoning,
                confidence = overallConfidence,
                alternatives = alternatives,
                metadata = mapOf(
                    "synthesis_method" to "multi_agent_collaboration",
                    "thought_count" to bestThoughts.size.toString(),
                    "collaboration_participants" to collaboration.participants.size.toString(),
                    "consensus_reached" to collaboration.consensusReached.toString()
                ),
                timestamp = Clock.System.now()
            ))
        } catch (e: Exception) {
            Log.e(TAG, "Error synthesizing response", e)
            // Fallback to simple synthesis
            Result.failure(e)
        }
    }
    
    /**
     * Extracts the highest quality thoughts from the tree
     */
    private fun extractBestThoughts(thoughtTree: ThoughtTree): List<Thought> {
        return thoughtTree.branches
            .flatMap { it.thoughts }
            .sortedByDescending { it.confidence }
            .take(5) // Top 5 thoughts
    }
    
    /**
     * Extracts collaborative insights and consensus points
     */
    private fun extractCollaborativeInsights(collaboration: Collaboration): List<String> {
        return collaboration.sharedContext.commonUnderstanding +
               collaboration.sharedContext.agreedDecisions.map { "Decision: ${it.description} (${it.rationale})" }
    }
    
    /**
     * Synthesizes content from multiple thought sources
     */
    private suspend fun synthesizeContent(
        thoughts: List<Thought>,
        collaborativeInsights: List<String>
    ): String = withContext(Dispatchers.Default) { // Ensure this computation is offloaded
        if (thoughts.isEmpty()) return@withContext "Unable to generate comprehensive response."
        
        val primaryThought = thoughts.maxByOrNull { it.confidence }
            ?: return@withContext "No high-confidence thoughts available."
        
        val supportingThoughts = thoughts.filter { it.id != primaryThought.id }
            .take(3)
        
        val synthesisBuilder = StringBuilder()
        
        // Primary response
        synthesisBuilder.appendLine("Primary Analysis:")
        synthesisBuilder.appendLine(primaryThought.content)
        synthesisBuilder.appendLine()
        
        // Supporting perspectives
        if (supportingThoughts.isNotEmpty()) {
            synthesisBuilder.appendLine("Supporting Perspectives:")
            supportingThoughts.forEachIndexed { index, thought ->
                synthesisBuilder.appendLine("${index + 1}. ${thought.content}")
            }
            synthesisBuilder.appendLine()
        }
        
        // Collaborative insights
        if (collaborativeInsights.isNotEmpty()) {
            synthesisBuilder.appendLine("Collaborative Insights:")
            collaborativeInsights.take(3).forEach { insight ->
                synthesisBuilder.appendLine("• $insight")
            }
        }
        
        return@withContext synthesisBuilder.toString().trim()
    }
    
    /**
     * Synthesizes reasoning chain from multiple sources
     */
    private fun synthesizeReasoning(
        thoughts: List<Thought>,
        collaboration: Collaboration
    ): ChainOfThought {
        val reasoningSteps = mutableListOf<ThoughtStep>()
        
        // Add steps from best thoughts
        thoughts.take(3).forEachIndexed { index, thought ->
            reasoningSteps.add(
                ThoughtStep(
                    id = "synthesis_step_${index + 1}",
                    description = "Analysis from ${thought.agentId}",
                    reasoning = thought.reasoning,
                    evidence = listOf(thought.content),
                    assumptions = listOf("Agent expertise: confidence ${thought.confidence}")
                )
            )
        }
        
        // Add collaborative consensus step if available
        if (collaboration.consensusReached) {
            reasoningSteps.add(
                ThoughtStep(
                    id = "consensus_step",
                    description = "Collaborative consensus",
                    reasoning = "Multiple agents reached consensus through structured collaboration",
                    evidence = collaboration.sharedContext.agreedDecisions.map { it.description },
                    assumptions = listOf("Collaborative validation increases reliability")
                )
            )
        }
        
        val finalReasoning = if (reasoningSteps.isNotEmpty()) {
            "Synthesized from ${reasoningSteps.size} reasoning sources with collaborative validation"
        } else {
            "Limited reasoning available"
        }
        
        val confidence = calculateSynthesizedConfidence(thoughts, collaboration)
        
        return ChainOfThought(
            steps = reasoningSteps,
            conclusion = finalReasoning,
            confidence = confidence
        )
    }
    
    /**
     * Calculates overall confidence based on thought quality and collaboration consensus
     */
    private fun calculateSynthesizedConfidence(
        thoughts: List<Thought>,
        collaboration: Collaboration
    ): Double {
        if (thoughts.isEmpty()) return 0.1
        
        val avgThoughtConfidence = thoughts.map { it.confidence }.average()
        val consensusBonus = if (collaboration.consensusReached) 0.1 else 0.0
        val participationBonus = (collaboration.participants.size.toDouble() / 6.0).coerceAtMost(0.1)
        
        return (avgThoughtConfidence + consensusBonus + participationBonus).coerceAtMost(1.0)
    }
    
    /**
     * Generates alternative approaches from synthesized thoughts
     */
    private fun generateSynthesizedAlternatives(thoughts: List<Thought>): List<Alternative> {
        return thoughts.drop(1).take(3).mapIndexed { index, thought ->
            Alternative(
                id = "synthesis_alt_$index",
                description = "Alternative approach: ${thought.content.take(100)}...",
                pros = listOf("Different perspective", "Agent expertise: ${thought.agentId}"),
                cons = listOf("Lower confidence: ${thought.confidence}"),
                score = thought.confidence,
                reasoning = thought.reasoning
            )
        }
    }
    
    /**
     * Creates a fallback response when synthesis fails
     */
    private fun createFallbackResponse(
        thoughtTree: ThoughtTree,
        collaboration: Collaboration
    ): AgentResponse {
        return AgentResponse(
            agentId = "orchestrator",
            content = "I encountered some challenges processing your request, but I can provide this initial analysis: ${thoughtTree.rootThought.content}",
            reasoning = ChainOfThought(
                steps = listOf(
                    ThoughtStep(
                        id = "fallback_step",
                        description = "Fallback analysis",
                        reasoning = "System encountered issues but provided best available response",
                        evidence = listOf(thoughtTree.rootThought.content)
                    )
                ),
                conclusion = "Fallback response provided",
                confidence = 0.5
            ),
            confidence = 0.5,
            alternatives = emptyList(),
            timestamp = Clock.System.now()
        )
    }
    
    /**
     * Generates a comprehensive response based on a selected thought path
     */
    private suspend fun generatePathResponse(thoughts: List<Thought>): Result<AgentResponse> = withContext(Dispatchers.Default) { // Ensure this computation is offloaded
        if (thoughts.isEmpty()) {
            return@withContext Result.success(createEmptyPathResponse())
        }
        
        return@withContext try {
            val pathContent = synthesizePathContent(thoughts)
            val pathReasoning = buildPathReasoning(thoughts)
            val pathConfidence = calculatePathConfidence(thoughts)
            val pathAlternatives = generatePathAlternatives(thoughts)
            
            Result.success(AgentResponse(
                agentId = "orchestrator",
                content = pathContent,
                reasoning = pathReasoning,
                confidence = pathConfidence,
                alternatives = pathAlternatives,
                metadata = mapOf(
                    "path_length" to thoughts.size.toString(),
                    "path_agents" to thoughts.map { it.agentId }.distinct().joinToString(","),
                    "avg_confidence" to thoughts.map { it.confidence }.average().toString()
                ),
                timestamp = Clock.System.now()
            ))
        } catch (e: Exception) {
            Log.e(TAG, "Error generating path response", e)
            Result.failure(e)
        }
    }
    
    private fun synthesizePathContent(thoughts: List<Thought>): String {
        val contentBuilder = StringBuilder()
        
        contentBuilder.appendLine("Based on the selected reasoning path:")
        contentBuilder.appendLine()
        
        thoughts.forEachIndexed { index, thought ->
            contentBuilder.appendLine("Step ${index + 1}: ${thought.content}")
            if (index < thoughts.size - 1) contentBuilder.appendLine()
        }
        
        if (thoughts.size > 1) {
            contentBuilder.appendLine()
            contentBuilder.appendLine("Conclusion: ${thoughts.last().content}")
        }
        
        return contentBuilder.toString().trim()
    }
    
    private fun buildPathReasoning(thoughts: List<Thought>): ChainOfThought {
        val steps = thoughts.mapIndexed { index, thought ->
            ThoughtStep(
                id = "path_step_$index",
                description = "Path step ${index + 1}",
                reasoning = thought.reasoning,
                evidence = listOf(thought.content),
                assumptions = listOf("Sequential reasoning path")
            )
        }
        
        return ChainOfThought(
            steps = steps,
            conclusion = "Selected path represents coherent reasoning chain with ${thoughts.size} steps",
            confidence = calculatePathConfidence(thoughts)
        )
    }
    
    private fun calculatePathConfidence(thoughts: List<Thought>): Double {
        if (thoughts.isEmpty()) return 0.0
        
        val avgConfidence = thoughts.map { it.confidence }.average()
        val pathCoherence = calculatePathCoherence(thoughts)
        
        return (avgConfidence * 0.7 + pathCoherence * 0.3).coerceAtMost(1.0)
    }
    
    private fun calculatePathCoherence(thoughts: List<Thought>): Double {
        if (thoughts.size <= 1) return 1.0
        
        // Simple coherence measure - in production, use semantic similarity
        var coherenceSum = 0.0
        for (i in 0 until thoughts.size - 1) {
            val current = thoughts[i].content.lowercase()
            val next = thoughts[i + 1].content.lowercase()
            
            val commonWords = current.split(" ").intersect(next.split(" ").toSet())
            coherenceSum += commonWords.size.toDouble() / (current.split(" ").size + next.split(" ").size)
        }
        
        return coherenceSum / (thoughts.size - 1)
    }
    
    private fun generatePathAlternatives(thoughts: List<Thought>): List<Alternative> {
        return thoughts.flatMap { it.alternatives }.take(3)
    }
    
    private fun createEmptyPathResponse(): AgentResponse {
        return AgentResponse(
            agentId = "orchestrator",
            content = "No valid reasoning path was selected. Please try rephrasing your request.",
            reasoning = ChainOfThought(
                steps = emptyList(),
                conclusion = "Empty path selected",
                confidence = 0.1
            ),
            confidence = 0.1,
            alternatives = emptyList(),
            timestamp = Clock.System.now()
        )
    }
    
    /**
     * Validates that a thought path is coherent and valid
     */
    private fun validateThoughtPath(thoughts: List<Thought>): PathValidation {
        if (thoughts.isEmpty()) {
            return PathValidation(false, "Path is empty")
        }
        
        if (thoughts.size == 1) {
            return PathValidation(true, "Single thought path")
        }
        
        // Check that thoughts form a valid chain
        for (i in 1 until thoughts.size) {
            val current = thoughts[i]
            val previous = thoughts[i - 1]
            
            // Verify parent-child relationship or at least same project
            if (current.parentId != previous.id && current.projectId != previous.projectId) {
                return PathValidation(
                    false, 
                    "Thoughts ${previous.id} and ${current.id} are not properly connected"
                )
            }
        }
        
        return PathValidation(true, "Valid thought path")
    }
    
    /**
     * Updates the status of a specific agent
     */
    suspend fun updateAgentStatus(agentId: String, status: AgentStatus): Result<Unit> {
        return try {
            val result = agentRepository.updateAgentStatus(agentId, status)
            Log.d(TAG, "Updated agent $agentId status to $status")
            result
        } catch (e: Exception) {
            Log.e(TAG, "Failed to update agent $agentId status to $status", e)
            Result.failure(e)
        }
    }
    
    /**
     * Gets all active collaborations for a project
     */
    suspend fun getActiveCollaborations(projectId: String): Flow<List<Collaboration>> {
        return collaborationRepository.getCollaborationsByProject(projectId)
    }
    
    /**
     * Provides detailed orchestration metrics and performance data
     */
    suspend fun getOrchestrationMetrics(): OrchestrationMetrics {
        val currentTime = Clock.System.now()
        val state = _orchestrationState.value
        
        return OrchestrationMetrics(
            activeAgentsCount = state.activeAgents.size,
            activeCollaborationsCount = state.activeCollaborations.size,
            isProcessing = state.isProcessing,
            processingTimeMs = state.processingStartTime?.let { 
                currentTime.toEpochMilliseconds() - it.toEpochMilliseconds()
            } ?: 0L,
            lastResponseConfidence = state.lastResponse?.confidence ?: 0.0,
            errorCount = if (state.error != null) 1 else 0,
            timestamp = currentTime
        )
    }
    
    /**
     * Gracefully shuts down all active operations
     */
    suspend fun shutdown(): Result<Unit> {
        return try {
            Log.d(TAG, "Shutting down orchestrator...")
            
            // End all active collaborations
            _orchestrationState.value.activeCollaborations.forEach { collaboration ->
                applicationScope.launch { // Launch in applicationScope for fire-and-forget
                    try {
                        collaborationManager.endCollaboration(collaboration.id)
                    } catch (e: Exception) {
                        Log.w(TAG, "Error ending collaboration ${collaboration.id}", e)
                    }
                }
            }
            
            // Reset agent statuses
            _orchestrationState.value.activeAgents.forEach { agent ->
                applicationScope.launch { // Launch in applicationScope for fire-and-forget
                    try {
                        updateAgentStatus(agent.id, AgentStatus.IDLE)
                    } catch (e: Exception) {
                        Log.w(TAG, "Error resetting agent ${agent.id} status", e)
                    }
                }
            }
            
            // Clear state
            _orchestrationState.value = OrchestrationState()
            
            Log.d(TAG, "Orchestrator shutdown complete")
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "Error during orchestrator shutdown", e)
            Result.failure(e)
        }
    }
    
    companion object {
        private const val TAG = "AgentOrchestrator"
        private const val MAX_CONCURRENT_AGENTS = 6
        private const val MAX_RESPONSE_TIME = 10000.0 // 10 seconds
    }
}

/**
 * Represents the current state of the orchestration system
 */
data class OrchestrationState(
    val isProcessing: Boolean = false,
    val currentTask: String = "",
    val activeAgents: List<Agent> = emptyList(),
    val activeCollaborations: List<Collaboration> = emptyList(),
    val lastResponse: AgentResponse? = null,
    val error: String? = null,
    val processingStartTime: kotlinx.datetime.Instant? = null,
    val thoughtTreesActive: Int = 0,
    val collaborationSessions: Int = 0
)

/**
 * Helper class for agent scoring during selection
 */
private data class AgentScore(
    val agent: Agent,
    val score: Double
)

/**
 * Validation result for thought paths
 */
private data class PathValidation(
    val isValid: Boolean,
    val reason: String
)

/**
 * Metrics for orchestration system performance
 */
data class OrchestrationMetrics(
    val activeAgentsCount: Int,
    val activeCollaborationsCount: Int,
    val isProcessing: Boolean,
    val processingTimeMs: Long,
    val lastResponseConfidence: Double,
    val errorCount: Int,
    val timestamp: kotlinx.datetime.Instant
)
