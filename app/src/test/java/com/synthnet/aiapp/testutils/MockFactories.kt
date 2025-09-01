package com.synthnet.aiapp.testutils

import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.repository.*
import com.synthnet.aiapp.domain.ai.service.AIServiceIntegration
import com.synthnet.aiapp.domain.ai.service.OpenAIService
import com.synthnet.aiapp.domain.ai.service.AnthropicService
import com.synthnet.aiapp.domain.services.WebSocketManager
import com.synthnet.aiapp.data.entities.AgentStatus
import com.synthnet.aiapp.data.entities.CollaborationStatus
import io.mockk.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import kotlinx.datetime.Clock

/**
 * Factory for creating mock objects for testing SynthNet AI components
 */
object MockFactories {
    
    /**
     * Repository mocks
     */
    fun createMockProjectRepository(): ProjectRepository {
        return mockk<ProjectRepository> {
            every { getAllProjects() } returns flowOf(TestDataBuilders.createTestProjectList())
            coEvery { getProjectById(any()) } returns TestDataBuilders.createTestProject()
            coEvery { insertProject(any()) } returns Result.success(Unit)
            coEvery { updateProject(any()) } returns Result.success(Unit)
            coEvery { deleteProject(any()) } returns Result.success(Unit)
            coEvery { searchProjects(any()) } returns flowOf(TestDataBuilders.createTestProjectList(2))
        }
    }
    
    fun createMockAgentRepository(): AgentRepository {
        return mockk<AgentRepository> {
            coEvery { getAgentsByProject(any()) } returns flowOf(TestDataBuilders.createTestAgentList())
            coEvery { getAgentById(any()) } returns TestDataBuilders.createTestAgent()
            coEvery { insertAgent(any()) } returns Result.success(Unit)
            coEvery { updateAgent(any()) } returns Result.success(Unit)
            coEvery { updateAgentStatus(any(), any()) } returns Result.success(Unit)
            coEvery { deleteAgent(any()) } returns Result.success(Unit)
            every { getActiveAgents() } returns flowOf(TestDataBuilders.createTestAgentList(3))
        }
    }
    
    fun createMockThoughtRepository(): ThoughtRepository {
        return mockk<ThoughtRepository> {
            coEvery { getThoughtById(any()) } returns TestDataBuilders.createTestThought()
            coEvery { getThoughtsByProject(any()) } returns flowOf(TestDataBuilders.createTestThoughtList())
            coEvery { getThoughtsByAgent(any()) } returns flowOf(TestDataBuilders.createTestThoughtList(5))
            coEvery { insertThought(any()) } returns Result.success(Unit)
            coEvery { updateThought(any()) } returns Result.success(Unit)
            coEvery { selectThought(any()) } returns Result.success(Unit)
            coEvery { deleteThought(any()) } returns Result.success(Unit)
            coEvery { getChildThoughts(any()) } returns flowOf(TestDataBuilders.createTestThoughtList(3))
            coEvery { getThoughtTree(any()) } returns TestDataBuilders.createTestThoughtTree()
        }
    }
    
    fun createMockCollaborationRepository(): CollaborationRepository {
        return mockk<CollaborationRepository> {
            coEvery { getCollaborationById(any()) } returns TestDataBuilders.createTestCollaboration()
            coEvery { getCollaborationsByProject(any()) } returns flowOf(listOf(TestDataBuilders.createTestCollaboration()))
            coEvery { insertCollaboration(any()) } returns Result.success(Unit)
            coEvery { updateCollaboration(any()) } returns Result.success(Unit)
            coEvery { updateCollaborationStatus(any(), any()) } returns Result.success(Unit)
            coEvery { deleteCollaboration(any()) } returns Result.success(Unit)
            every { getActiveCollaborations() } returns flowOf(listOf(TestDataBuilders.createTestCollaboration()))
        }
    }
    
    /**
     * AI Service mocks
     */
    fun createMockAIServiceIntegration(): AIServiceIntegration {
        return mockk<AIServiceIntegration> {
            coEvery { generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse()
            )
            coEvery { generateThoughts(any(), any(), any()) } returns Result.success(
                TestDataBuilders.createTestThoughtList(3)
            )
            coEvery { evaluateThought(any(), any()) } returns Result.success(0.8)
            coEvery { optimizeResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(confidence = 0.9)
            )
            coEvery { checkServiceHealth(any()) } returns Result.success(true)
            every { isServiceAvailable(any()) } returns true
        }
    }
    
    fun createMockOpenAIService(): OpenAIService {
        return mockk<OpenAIService> {
            coEvery { generateCompletion(any(), any()) } returns Result.success("OpenAI response")
            coEvery { generateEmbedding(any()) } returns Result.success(List(1536) { 0.1 })
            coEvery { isHealthy() } returns true
            coEvery { getUsageStats() } returns mapOf("requests" to "100", "tokens" to "10000")
        }
    }
    
    fun createMockAnthropicService(): AnthropicService {
        return mockk<AnthropicService> {
            coEvery { generateCompletion(any(), any()) } returns Result.success("Anthropic response")
            coEvery { isHealthy() } returns true
            coEvery { getUsageStats() } returns mapOf("requests" to "50", "tokens" to "5000")
        }
    }
    
    /**
     * WebSocket and communication mocks
     */
    fun createMockWebSocketManager(): WebSocketManager {
        return mockk<WebSocketManager> {
            coEvery { connect(any()) } returns Result.success(Unit)
            coEvery { disconnect() } returns Result.success(Unit)
            coEvery { sendMessage(any()) } returns Result.success(Unit)
            coEvery { subscribe(any(), any()) } returns Result.success(Unit)
            coEvery { unsubscribe(any()) } returns Result.success(Unit)
            every { isConnected() } returns true
            every { getConnectionStatus() } returns flowOf("CONNECTED")
        }
    }
    
    fun createMockWebSocket(): WebSocket {
        return mockk<WebSocket> {
            every { send(any<String>()) } returns true
            every { close(any(), any()) } returns true
            every { cancel() } just runs
            every { queueSize() } returns 0L
        }
    }
    
    /**
     * Domain service mocks
     */
    fun createMockCollaborationManager(): com.synthnet.aiapp.domain.services.CollaborationManager {
        return mockk<com.synthnet.aiapp.domain.services.CollaborationManager> {
            coEvery { startCollaboration(any(), any(), any(), any()) } returns TestDataBuilders.createTestCollaboration()
            coEvery { endCollaboration(any()) } returns Result.success(Unit)
            coEvery { addParticipant(any(), any()) } returns Result.success(Unit)
            coEvery { removeParticipant(any(), any()) } returns Result.success(Unit)
            coEvery { updateSharedContext(any(), any()) } returns Result.success(Unit)
            coEvery { reachConsensus(any()) } returns Result.success(true)
            every { getActiveCollaborations() } returns flowOf(listOf(TestDataBuilders.createTestCollaboration()))
        }
    }
    
    fun createMockAntifragileSystem(): com.synthnet.aiapp.domain.services.AntifragileSystem {
        return mockk<com.synthnet.aiapp.domain.services.AntifragileSystem> {
            coEvery { executeWithFallback<Any>(any(), any()) } answers {
                val block = secondArg<suspend () -> Result<Any>>()
                block()
            }
            every { recordFailure(any()) } just runs
            every { recordSuccess(any()) } just runs
            every { shouldCircuitBreak(any()) } returns false
            every { getSystemHealth() } returns mapOf("status" to "healthy", "uptime" to "99.9%")
        }
    }
    
    /**
     * AI Engine mocks
     */
    fun createMockTreeOfThoughtEngine(): com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine {
        return mockk<com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine> {
            coEvery { executeToTWorkflow(any(), any(), any(), any()) } returns TestDataBuilders.createTestThoughtTree()
            coEvery { expandThought(any(), any()) } returns TestDataBuilders.createTestThoughtList(3)
            coEvery { evaluateThoughts(any()) } returns TestDataBuilders.createTestThoughtList().map { 0.8 }
            coEvery { selectBestPath(any()) } returns TestDataBuilders.createTestThoughtList(5)
            coEvery { pruneThoughts(any(), any()) } returns TestDataBuilders.createTestThoughtList(8)
        }
    }
    
    fun createMockRecursiveMetaPrompting(): com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting {
        return mockk<com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting> {
            coEvery { optimizeResponse(any(), any()) } returns TestDataBuilders.createTestAgentResponse(
                confidence = 0.9,
                content = "Optimized response"
            )
            coEvery { assessQuality(any()) } returns 0.85
            coEvery { generateImprovement(any(), any()) } returns TestDataBuilders.createTestAgentResponse()
            coEvery { shouldContinueOptimization(any(), any()) } returns false
            coEvery { calibrateConfidence(any()) } returns 0.8
        }
    }
    
    /**
     * Test rule helpers for creating consistently configured mocks
     */
    fun createFullMockOrchestrator(): Triple<
        com.synthnet.aiapp.domain.orchestration.AgentOrchestrator,
        MockData,
        MockVerificationHelper
    > {
        val mockData = MockData(
            agentRepository = createMockAgentRepository(),
            thoughtRepository = createMockThoughtRepository(),
            collaborationRepository = createMockCollaborationRepository(),
            totEngine = createMockTreeOfThoughtEngine(),
            rmpEngine = createMockRecursiveMetaPrompting(),
            collaborationManager = createMockCollaborationManager(),
            antifragileSystem = createMockAntifragileSystem(),
            aiServiceIntegration = createMockAIServiceIntegration()
        )
        
        val orchestrator = com.synthnet.aiapp.domain.orchestration.AgentOrchestrator(
            mockData.agentRepository,
            mockData.thoughtRepository,
            mockData.collaborationRepository,
            mockData.totEngine,
            mockData.rmpEngine,
            mockData.collaborationManager,
            mockData.antifragileSystem,
            mockData.aiServiceIntegration
        )
        
        val verificationHelper = MockVerificationHelper(mockData)
        
        return Triple(orchestrator, mockData, verificationHelper)
    }
    
    /**
     * Data class to hold all mock dependencies
     */
    data class MockData(
        val agentRepository: AgentRepository,
        val thoughtRepository: ThoughtRepository,
        val collaborationRepository: CollaborationRepository,
        val totEngine: com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine,
        val rmpEngine: com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting,
        val collaborationManager: com.synthnet.aiapp.domain.services.CollaborationManager,
        val antifragileSystem: com.synthnet.aiapp.domain.services.AntifragileSystem,
        val aiServiceIntegration: AIServiceIntegration
    )
    
    /**
     * Helper class for common mock verifications
     */
    class MockVerificationHelper(private val mockData: MockData) {
        
        fun verifyAgentStatusUpdated(agentId: String, status: AgentStatus) {
            coVerify { mockData.agentRepository.updateAgentStatus(agentId, status) }
        }
        
        fun verifyThoughtTreeExecuted() {
            coVerify { mockData.totEngine.executeToTWorkflow(any(), any(), any(), any()) }
        }
        
        fun verifyCollaborationStarted() {
            coVerify { mockData.collaborationManager.startCollaboration(any(), any(), any(), any()) }
        }
        
        fun verifyResponseOptimized() {
            coVerify { mockData.rmpEngine.optimizeResponse(any(), any()) }
        }
        
        fun verifyAntifragileExecution() {
            coVerify { mockData.antifragileSystem.executeWithFallback<Any>(any(), any()) }
        }
        
        fun verifyNoErrorsRecorded() {
            verify(exactly = 0) { mockData.antifragileSystem.recordFailure(any()) }
        }
        
        fun verifySuccessRecorded() {
            verify(atLeast = 1) { mockData.antifragileSystem.recordSuccess(any()) }
        }
        
        fun verifyThoughtInserted() {
            coVerify { mockData.thoughtRepository.insertThought(any()) }
        }
        
        fun verifyCollaborationUpdated() {
            coVerify { mockData.collaborationRepository.updateCollaboration(any()) }
        }
    }
    
    /**
     * Creates mock responses with different confidence levels for testing
     */
    fun createConfidenceLevelResponses(): List<AgentResponse> = listOf(
        TestDataBuilders.createTestAgentResponse(confidence = 0.95), // High confidence
        TestDataBuilders.createTestAgentResponse(confidence = 0.75), // Medium confidence
        TestDataBuilders.createTestAgentResponse(confidence = 0.45), // Low confidence
        TestDataBuilders.createTestAgentResponse(confidence = 0.15)  // Very low confidence
    )
    
    /**
     * Creates mock error scenarios for testing error handling
     */
    fun createErrorScenarios(): Map<String, Exception> = mapOf(
        "network_timeout" to java.net.SocketTimeoutException("Connection timeout"),
        "service_unavailable" to IllegalStateException("AI service unavailable"),
        "invalid_input" to IllegalArgumentException("Invalid input provided"),
        "database_error" to RuntimeException("Database connection failed"),
        "authentication_error" to SecurityException("Authentication failed"),
        "rate_limit" to RuntimeException("Rate limit exceeded")
    )
}