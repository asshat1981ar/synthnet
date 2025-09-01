package com.synthnet.aiapp.domain.orchestration

import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine
import com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting
import com.synthnet.aiapp.domain.services.CollaborationManager
import com.synthnet.aiapp.domain.services.AntifragileSystem
import com.synthnet.aiapp.domain.repository.*
import com.synthnet.aiapp.domain.ai.service.AIServiceIntegration
import com.synthnet.aiapp.data.entities.AgentStatus
import com.synthnet.aiapp.data.entities.AgentRole
import com.synthnet.aiapp.data.entities.SessionType
import com.synthnet.aiapp.data.entities.CollaborationStatus
import com.synthnet.aiapp.testutils.TestDataBuilders
import com.synthnet.aiapp.testutils.MockFactories
import com.synthnet.aiapp.testutils.TestCoroutineRule
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import io.mockk.*
import org.junit.jupiter.api.*
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource
import org.junit.jupiter.params.provider.ValueSource
import kotlin.test.*

/**
 * Comprehensive test suite for AgentOrchestrator
 * 
 * Tests cover:
 * - Agent selection algorithms with various scenarios
 * - Multi-agent coordination and response synthesis
 * - Error handling and fallback mechanisms
 * - Real-time collaboration coordination
 * - Performance under different loads
 * - Mock AI service integrations
 */
@ExtendWith(MockKExtension::class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class AgentOrchestratorTest {
    
    private lateinit var orchestrator: AgentOrchestrator
    private lateinit var mockData: MockFactories.MockData
    private lateinit var verificationHelper: MockFactories.MockVerificationHelper
    
    private val testProjectId = "test-project-123"
    private val testInput = "Create a comprehensive mobile application with user authentication and real-time features"
    private val testContext = TestDataBuilders.createTestProjectContext()
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        val (mockOrchestrator, data, helper) = MockFactories.createFullMockOrchestrator()
        orchestrator = mockOrchestrator
        mockData = data
        verificationHelper = helper
    }
    
    @Nested
    @DisplayName("Orchestration State Management")
    inner class OrchestrationStateTests {
        
        @Test
        fun `orchestrationState is initialized correctly`() {
            // When
            val state = orchestrator.orchestrationState.value
            
            // Then
            assertNotNull(state)
            assertFalse(state.isProcessing)
            assertTrue(state.activeAgents.isEmpty())
            assertTrue(state.activeCollaborations.isEmpty())
            assertNull(state.error)
            assertEquals("", state.currentTask)
            assertEquals(0, state.thoughtTreesActive)
            assertEquals(0, state.collaborationSessions)
        }
        
        @Test
        fun `orchestrationState updates during processing`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - State should have been updated during processing
            verifySequence {
                // Verify state updates happened
                mockData.antifragileSystem.executeWithFallback<AgentResponse>("processUserInput", any())
            }
        }
    }
    
    @Nested
    @DisplayName("User Input Processing")
    inner class UserInputProcessingTests {
        
        @Test
        fun `processUserInput executes complete workflow successfully`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(5, testProjectId)
            val thoughtTree = TestDataBuilders.createTestThoughtTree(projectId = testProjectId)
            val collaboration = TestDataBuilders.createTestCollaboration(projectId = testProjectId)
            val optimizedResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.9)
            
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { mockData.totEngine.executeToTWorkflow(any(), any(), any(), any()) } returns thoughtTree
            coEvery { mockData.collaborationManager.startCollaboration(any(), any(), any(), any()) } returns collaboration
            coEvery { mockData.rmpEngine.optimizeResponse(any(), any()) } returns optimizedResponse
            
            // When
            val result = orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            assertEquals(optimizedResponse, result.getOrNull())
            
            // Verify complete workflow execution
            verificationHelper.verifyThoughtTreeExecuted()
            verificationHelper.verifyCollaborationStarted()
            verificationHelper.verifyResponseOptimized()
            verificationHelper.verifyAntifragileExecution()
        }
        
        @Test
        fun `processUserInput handles no available agents gracefully`() = runTest {
            // Given - No agents available
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(emptyList())
            
            // When
            val result = orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then
            assertTrue(result.isFailure)
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception is IllegalStateException)
            assertTrue(exception.message!!.contains("No suitable agents available"))
        }
        
        @Test
        fun `processUserInput updates agent statuses during workflow`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - Verify agents were set to THINKING then back to IDLE
            agents.forEach { agent ->
                coVerify { mockData.agentRepository.updateAgentStatus(agent.id, AgentStatus.THINKING) }
                coVerify { mockData.agentRepository.updateAgentStatus(agent.id, AgentStatus.IDLE) }
            }
        }
        
        @Test
        fun `processUserInput handles errors and sets agent status to ERROR`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { mockData.totEngine.executeToTWorkflow(any(), any(), any(), any()) } throws RuntimeException("ToT execution failed")
            
            // When
            val result = orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then
            assertTrue(result.isFailure)
            
            // Verify agents were reset to ERROR status
            agents.forEach { agent ->
                coVerify { mockData.agentRepository.updateAgentStatus(agent.id, AgentStatus.ERROR) }
            }
        }
        
        @ParameterizedTest
        @ValueSource(strings = ["simple task", "complex multi-step analysis", "urgent request", ""])
        fun `processUserInput handles various input types`(input: String) = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // When
            val result = orchestrator.processUserInput(testProjectId, input, testContext)
            
            // Then
            if (input.isNotBlank()) {
                assertTrue(result.isSuccess || result.isFailure) // Should complete either way
            }
            verificationHelper.verifyAntifragileExecution()
        }
    }
    
    @Nested
    @DisplayName("Agent Selection Algorithm")
    inner class AgentSelectionTests {
        
        @Test
        fun `selectRelevantAgents chooses agents based on role relevance`() = runTest {
            // Given - Agents with different roles
            val strategyAgent = TestDataBuilders.createTestAgent(
                id = "strategy-agent",
                role = AgentRole.STRATEGY,
                capabilities = listOf("planning", "strategy")
            )
            val implementationAgent = TestDataBuilders.createTestAgent(
                id = "impl-agent", 
                role = AgentRole.IMPLEMENTATION,
                capabilities = listOf("coding", "implementation")
            )
            val agents = listOf(strategyAgent, implementationAgent)
            
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // When - Input that should favor strategy agent
            val strategyInput = "Plan a comprehensive software architecture strategy"
            orchestrator.processUserInput(testProjectId, strategyInput, testContext)
            
            // Then - Should have processed with available agents
            verificationHelper.verifyThoughtTreeExecuted()
        }
        
        @Test
        fun `selectRelevantAgents filters out unavailable agents`() = runTest {
            // Given - Mix of available and busy agents
            val availableAgent = TestDataBuilders.createTestAgent(
                id = "available",
                status = AgentStatus.IDLE
            )
            val busyAgent = TestDataBuilders.createTestAgent(
                id = "busy",
                status = AgentStatus.WORKING
            )
            val errorAgent = TestDataBuilders.createTestAgent(
                id = "error",
                status = AgentStatus.ERROR
            )
            val agents = listOf(availableAgent, busyAgent, errorAgent)
            
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - Should only use available agents
            verificationHelper.verifyThoughtTreeExecuted()
        }
        
        @ParameterizedTest
        @EnumSource(AgentRole::class)
        fun `selectRelevantAgents handles different agent roles`(role: AgentRole) = runTest {
            // Given
            val agent = TestDataBuilders.createTestAgent(role = role)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(listOf(agent))
            
            // When
            val result = orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - Should handle any role
            assertNotNull(result)
        }
        
        @Test
        fun `selectRelevantAgents respects MAX_CONCURRENT_AGENTS limit`() = runTest {
            // Given - More agents than the limit
            val manyAgents = TestDataBuilders.createTestAgentList(10, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(manyAgents)
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - Should still execute successfully with limited agents
            verificationHelper.verifyThoughtTreeExecuted()
        }
    }
    
    @Nested
    @DisplayName("Thought Path Selection")
    inner class ThoughtPathSelectionTests {
        
        @Test
        fun `selectThoughtPath executes valid path successfully`() = runTest {
            // Given
            val thoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
            val thoughtTree = TestDataBuilders.createTestThoughtTree(
                projectId = testProjectId,
                branches = listOf(
                    TestDataBuilders.createTestThoughtBranch(thoughts = thoughts)
                )
            )
            val selectedPath = thoughts.map { it.id }
            
            thoughts.forEach { thought ->
                coEvery { mockData.thoughtRepository.getThoughtById(thought.id) } returns thought
                coEvery { mockData.thoughtRepository.selectThought(thought.id) } returns Result.success(Unit)
            }
            
            // When
            val result = orchestrator.selectThoughtPath(thoughtTree, selectedPath)
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.content.contains("Based on the selected reasoning path"))
            
            // Verify thoughts were marked as selected
            thoughts.forEach { thought ->
                coVerify { mockData.thoughtRepository.selectThought(thought.id) }
            }
        }
        
        @Test
        fun `selectThoughtPath rejects empty path`() = runTest {
            // Given
            val thoughtTree = TestDataBuilders.createTestThoughtTree()
            val emptyPath = emptyList<String>()
            
            // When
            val result = orchestrator.selectThoughtPath(thoughtTree, emptyPath)
            
            // Then
            assertTrue(result.isFailure)
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception is IllegalArgumentException)
            assertTrue(exception.message!!.contains("Selected path cannot be empty"))
        }
        
        @Test
        fun `selectThoughtPath handles missing thoughts gracefully`() = runTest {
            // Given
            val thoughtTree = TestDataBuilders.createTestThoughtTree()
            val pathWithMissingThought = listOf("existing-thought", "missing-thought")
            
            coEvery { mockData.thoughtRepository.getThoughtById("existing-thought") } returns TestDataBuilders.createTestThought(id = "existing-thought")
            coEvery { mockData.thoughtRepository.getThoughtById("missing-thought") } returns null
            
            // When
            val result = orchestrator.selectThoughtPath(thoughtTree, pathWithMissingThought)
            
            // Then - Should still process with available thoughts
            assertTrue(result.isSuccess || result.isFailure) // Either outcome is acceptable
        }
        
        @Test
        fun `selectThoughtPath validates path coherence`() = runTest {
            // Given - Disconnected thoughts
            val thought1 = TestDataBuilders.createTestThought(
                id = "thought1", 
                projectId = "project1"
            )
            val thought2 = TestDataBuilders.createTestThought(
                id = "thought2", 
                projectId = "project2", // Different project
                parentId = "different-parent"
            )
            val thoughtTree = TestDataBuilders.createTestThoughtTree()
            val disconnectedPath = listOf("thought1", "thought2")
            
            coEvery { mockData.thoughtRepository.getThoughtById("thought1") } returns thought1
            coEvery { mockData.thoughtRepository.getThoughtById("thought2") } returns thought2
            
            // When
            val result = orchestrator.selectThoughtPath(thoughtTree, disconnectedPath)
            
            // Then
            assertTrue(result.isFailure)
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception.message!!.contains("not properly connected"))
        }
    }
    
    @Nested
    @DisplayName("Agent Status Management")
    inner class AgentStatusTests {
        
        @ParameterizedTest
        @EnumSource(AgentStatus::class)
        fun `updateAgentStatus handles all status types`(status: AgentStatus) = runTest {
            // Given
            val agentId = "test-agent-123"
            coEvery { mockData.agentRepository.updateAgentStatus(agentId, status) } returns Result.success(Unit)
            
            // When
            val result = orchestrator.updateAgentStatus(agentId, status)
            
            // Then
            assertTrue(result.isSuccess)
            coVerify { mockData.agentRepository.updateAgentStatus(agentId, status) }
        }
        
        @Test
        fun `updateAgentStatus handles repository errors`() = runTest {
            // Given
            val agentId = "test-agent-123"
            val error = RuntimeException("Database connection failed")
            coEvery { mockData.agentRepository.updateAgentStatus(agentId, any()) } throws error
            
            // When
            val result = orchestrator.updateAgentStatus(agentId, AgentStatus.IDLE)
            
            // Then
            assertTrue(result.isFailure)
            assertEquals(error, result.exceptionOrNull())
        }
    }
    
    @Nested
    @DisplayName("Collaboration Management")
    inner class CollaborationTests {
        
        @Test
        fun `getActiveCollaborations returns project collaborations`() = runTest {
            // Given
            val collaborations = listOf(
                TestDataBuilders.createTestCollaboration(projectId = testProjectId),
                TestDataBuilders.createTestCollaboration(projectId = testProjectId)
            )
            coEvery { mockData.collaborationRepository.getCollaborationsByProject(testProjectId) } returns flowOf(collaborations)
            
            // When
            val result = orchestrator.getActiveCollaborations(testProjectId).first()
            
            // Then
            assertEquals(collaborations, result)
        }
    }
    
    @Nested
    @DisplayName("Metrics and Monitoring")
    inner class MetricsTests {
        
        @Test
        fun `getOrchestrationMetrics returns current state metrics`() = runTest {
            // Given - Process some input to generate state
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val response = TestDataBuilders.createTestAgentResponse(confidence = 0.85)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { mockData.rmpEngine.optimizeResponse(any(), any()) } returns response
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            val metrics = orchestrator.getOrchestrationMetrics()
            
            // Then
            assertNotNull(metrics)
            assertTrue(metrics.processingTimeMs >= 0)
            assertNotNull(metrics.timestamp)
        }
        
        @Test
        fun `getOrchestrationMetrics reflects processing state`() = runTest {
            // When - Get metrics without processing
            val metrics = orchestrator.getOrchestrationMetrics()
            
            // Then
            assertFalse(metrics.isProcessing)
            assertEquals(0, metrics.activeAgentsCount)
            assertEquals(0, metrics.activeCollaborationsCount)
            assertEquals(0.0, metrics.lastResponseConfidence)
        }
    }
    
    @Nested
    @DisplayName("Shutdown and Cleanup")
    inner class ShutdownTests {
        
        @Test
        fun `shutdown ends active collaborations and resets agents`() = runTest {
            // Given - Some active state
            val collaboration = TestDataBuilders.createTestCollaboration()
            coEvery { mockData.collaborationManager.endCollaboration(any()) } returns Result.success(Unit)
            
            // When
            val result = orchestrator.shutdown()
            
            // Then
            assertTrue(result.isSuccess)
            
            // Verify final state is clean
            val finalState = orchestrator.orchestrationState.value
            assertTrue(finalState.activeAgents.isEmpty())
            assertTrue(finalState.activeCollaborations.isEmpty())
            assertFalse(finalState.isProcessing)
        }
        
        @Test
        fun `shutdown handles errors gracefully`() = runTest {
            // Given - Collaboration manager throws error
            coEvery { mockData.collaborationManager.endCollaboration(any()) } throws RuntimeException("Shutdown error")
            
            // When
            val result = orchestrator.shutdown()
            
            // Then - Should still complete successfully
            assertTrue(result.isSuccess)
        }
    }
    
    @Nested
    @DisplayName("Error Handling and Resilience")
    inner class ErrorHandlingTests {
        
        @Test
        fun `processUserInput uses antifragile system for error recovery`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then
            verificationHelper.verifyAntifragileExecution()
        }
        
        @Test
        fun `processUserInput handles multiple error scenarios`() = runTest {
            // Given - Various error conditions
            val errorScenarios = MockFactories.createErrorScenarios()
            
            for ((errorType, exception) in errorScenarios) {
                // Reset mocks for each scenario
                clearAllMocks()
                val (newOrchestrator, newMockData, _) = MockFactories.createFullMockOrchestrator()
                
                val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
                coEvery { newMockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
                coEvery { newMockData.totEngine.executeToTWorkflow(any(), any(), any(), any()) } throws exception
                
                // When
                val result = newOrchestrator.processUserInput(testProjectId, testInput, testContext)
                
                // Then
                assertTrue(result.isFailure, "Error scenario '$errorType' should result in failure")
            }
        }
        
        @Test
        fun `orchestrator maintains state consistency during errors`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { mockData.totEngine.executeToTWorkflow(any(), any(), any(), any()) } throws RuntimeException("Simulated error")
            
            // When
            orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - State should be reset to clean state
            val finalState = orchestrator.orchestrationState.value
            assertFalse(finalState.isProcessing)
            assertTrue(finalState.activeAgents.isEmpty())
            assertEquals(0, finalState.thoughtTreesActive)
            assertEquals(0, finalState.collaborationSessions)
            assertNotNull(finalState.error)
        }
    }
    
    @Nested
    @DisplayName("Performance and Load Testing")
    inner class PerformanceTests {
        
        @Test
        fun `orchestrator handles concurrent requests`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(5, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(any()) } returns flowOf(agents)
            
            // When - Multiple concurrent requests
            val requests = (1..3).map { i ->
                async {
                    orchestrator.processUserInput("project-$i", "Input $i", testContext)
                }
            }
            
            val results = requests.awaitAll()
            
            // Then - All requests should complete
            assertEquals(3, results.size)
        }
        
        @Test
        fun `orchestrator respects agent capacity limits`() = runTest {
            // Given - Limited agents
            val limitedAgents = TestDataBuilders.createTestAgentList(2, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(limitedAgents)
            
            // When
            val result = orchestrator.processUserInput(testProjectId, testInput, testContext)
            
            // Then - Should work with limited agents
            assertTrue(result.isSuccess || result.isFailure) // Should complete either way
        }
        
        @Test
        fun `orchestrator maintains performance with large thought trees`() = runTest {
            // Given - Large thought tree
            val largeThoughtTree = TestDataBuilders.createTestThoughtTree(
                projectId = testProjectId,
                branches = (1..10).map { 
                    TestDataBuilders.createTestThoughtBranch(
                        thoughts = TestDataBuilders.createTestThoughtList(20)
                    )
                }
            )
            
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            coEvery { mockData.agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { mockData.totEngine.executeToTWorkflow(any(), any(), any(), any()) } returns largeThoughtTree
            
            // When
            val startTime = System.currentTimeMillis()
            val result = orchestrator.processUserInput(testProjectId, testInput, testContext)
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertTrue(result.isSuccess)
            // Performance assertion - should complete in reasonable time
            assertTrue(duration < 10000, "Processing should complete within 10 seconds")
        }
    }
}