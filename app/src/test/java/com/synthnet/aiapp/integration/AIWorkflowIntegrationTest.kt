package com.synthnet.aiapp.integration

import com.synthnet.aiapp.domain.orchestration.AgentOrchestrator
import com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine
import com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting
import com.synthnet.aiapp.domain.services.CollaborationManager
import com.synthnet.aiapp.domain.services.AntifragileSystem
import com.synthnet.aiapp.domain.repository.*
import com.synthnet.aiapp.domain.ai.service.AIServiceIntegration
import com.synthnet.aiapp.data.entities.*
import com.synthnet.aiapp.testutils.TestDataBuilders
import com.synthnet.aiapp.testutils.MockFactories
import com.synthnet.aiapp.testutils.TestDatabaseRule
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import io.mockk.*
import org.junit.jupiter.api.*
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import kotlin.test.*

/**
 * Comprehensive integration test suite for complete AI workflows
 * 
 * Tests cover:
 * - Complete AI reasoning workflows
 * - Multi-agent collaboration scenarios  
 * - Real-time collaboration features
 * - Data persistence and retrieval
 * - Error recovery and fallback mechanisms
 * - End-to-end system integration
 */
@ExtendWith(MockKExtension::class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class AIWorkflowIntegrationTest {
    
    private lateinit var orchestrator: AgentOrchestrator
    private lateinit var totEngine: TreeOfThoughtEngine
    private lateinit var rmpEngine: RecursiveMetaPrompting
    private lateinit var collaborationManager: CollaborationManager
    private lateinit var antifragileSystem: AntifragileSystem
    private lateinit var aiServiceIntegration: AIServiceIntegration
    
    // Repositories
    private lateinit var agentRepository: AgentRepository
    private lateinit var thoughtRepository: ThoughtRepository
    private lateinit var collaborationRepository: CollaborationRepository
    private lateinit var projectRepository: ProjectRepository
    
    private val testProjectId = "integration-test-project"
    private val testUserId = "test-user-123"
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        
        // Create mock repositories
        agentRepository = MockFactories.createMockAgentRepository()
        thoughtRepository = MockFactories.createMockThoughtRepository()
        collaborationRepository = MockFactories.createMockCollaborationRepository()
        projectRepository = MockFactories.createMockProjectRepository()
        
        // Create mock services
        aiServiceIntegration = MockFactories.createMockAIServiceIntegration()
        antifragileSystem = MockFactories.createMockAntifragileSystem()
        collaborationManager = MockFactories.createMockCollaborationManager()
        
        // Create engines
        totEngine = TreeOfThoughtEngine(thoughtRepository, aiServiceIntegration)
        rmpEngine = RecursiveMetaPrompting(aiServiceIntegration)
        
        // Create orchestrator with all dependencies
        orchestrator = AgentOrchestrator(
            agentRepository,
            thoughtRepository,
            collaborationRepository,
            totEngine,
            rmpEngine,
            collaborationManager,
            antifragileSystem,
            aiServiceIntegration
        )
    }
    
    @Nested
    @DisplayName("Complete AI Reasoning Workflows")
    inner class AIReasoningWorkflowTests {
        
        @Test
        fun `complete workflow processes user input through all AI systems`() = runTest {
            // Given - Complete setup
            val agents = TestDataBuilders.createTestAgentList(5, testProjectId)
            val thoughtTree = TestDataBuilders.createTestThoughtTree(projectId = testProjectId)
            val collaboration = TestDataBuilders.createTestCollaboration(projectId = testProjectId)
            val optimizedResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.92)
            val context = TestDataBuilders.createTestProjectContext()
            
            // Setup mocks for complete workflow
            coEvery { agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                TestDataBuilders.createTestThoughtList(3, testProjectId)
            )
            coEvery { thoughtRepository.insertThought(any()) } returns Result.success(Unit)
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns collaboration
            coEvery { rmpEngine.optimizeResponse(any(), any()) } returns optimizedResponse
            
            val userInput = "Design a scalable microservices architecture for a high-traffic e-commerce platform"
            
            // When - Execute complete workflow
            val startTime = System.currentTimeMillis()
            val result = orchestrator.processUserInput(testProjectId, userInput, context)
            val duration = System.currentTimeMillis() - startTime
            
            // Then - Verify complete workflow execution
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Verify response quality
            assertTrue(response.confidence > 0.8)
            assertTrue(response.content.isNotEmpty())
            assertNotNull(response.reasoning)
            assertTrue(response.alternatives.isNotEmpty() || response.content.length > 100)
            
            // Verify all systems were engaged
            coVerify { agentRepository.getAgentsByProject(testProjectId) }
            coVerify(atLeast = agents.size) { aiServiceIntegration.generateThoughts(any(), any(), any()) }
            coVerify { collaborationManager.startCollaboration(any(), any(), any(), any()) }
            coVerify { rmpEngine.optimizeResponse(any(), any()) }
            
            // Verify performance
            assertTrue(duration < 15000, "Complete workflow should execute within 15 seconds")
            
            // Verify agent status management
            agents.forEach { agent ->
                coVerify { agentRepository.updateAgentStatus(agent.id, AgentStatus.THINKING) }
                coVerify { agentRepository.updateAgentStatus(agent.id, AgentStatus.IDLE) }
            }
        }
        
        @Test
        fun `workflow handles complex multi-domain queries`() = runTest {
            // Given - Diverse agent team
            val agents = listOf(
                TestDataBuilders.createTestAgent(
                    id = "architect-agent",
                    role = AgentRole.STRATEGY,
                    capabilities = listOf("system architecture", "scalability", "design patterns")
                ),
                TestDataBuilders.createTestAgent(
                    id = "security-agent",
                    role = AgentRole.REVIEW,
                    capabilities = listOf("security", "authentication", "encryption")
                ),
                TestDataBuilders.createTestAgent(
                    id = "implementation-agent",
                    role = AgentRole.IMPLEMENTATION,
                    capabilities = listOf("coding", "databases", "APIs")
                ),
                TestDataBuilders.createTestAgent(
                    id = "devops-agent",
                    role = AgentRole.IMPLEMENTATION,
                    capabilities = listOf("deployment", "monitoring", "infrastructure")
                )
            )
            
            setupWorkflowMocks(agents)
            
            val complexQuery = """
                Design a secure, scalable e-commerce platform that handles:
                1. User authentication and authorization
                2. Real-time inventory management
                3. Payment processing with multiple providers
                4. Order fulfillment and tracking
                5. Analytics and reporting
                6. Mobile and web interfaces
                7. Third-party integrations
                Requirements: 1M+ daily users, 99.9% uptime, PCI compliance, global deployment
            """.trimIndent()
            
            // When
            val result = orchestrator.processUserInput(testProjectId, complexQuery, TestDataBuilders.createTestProjectContext())
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Should produce comprehensive analysis
            assertTrue(response.content.length > 500)
            assertTrue(response.confidence > 0.7)
            
            // Should engage multiple agent specialties
            coVerify { agentRepository.getAgentsByProject(testProjectId) }
            coVerify(atLeast = agents.size) { aiServiceIntegration.generateThoughts(any(), any(), any()) }
        }
        
        @Test
        fun `workflow processes iterative refinement requests`() = runTest {
            // Given - Initial response and refinement request
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            setupWorkflowMocks(agents)
            
            val initialQuery = "Design a REST API for user management"
            val refinementQuery = "Add OAuth2 authentication and rate limiting to the previous API design"
            
            val contextWithHistory = TestDataBuilders.createTestProjectContext(
                sessionMemory = listOf(
                    TestDataBuilders.createTestContextItem(
                        content = "Previous API design discussion",
                        relevance = 0.9
                    )
                )
            )
            
            // When - Process initial query
            val initialResult = orchestrator.processUserInput(testProjectId, initialQuery, TestDataBuilders.createTestProjectContext())
            
            // Process refinement query with context
            val refinedResult = orchestrator.processUserInput(testProjectId, refinementQuery, contextWithHistory)
            
            // Then
            assertTrue(initialResult.isSuccess)
            assertTrue(refinedResult.isSuccess)
            
            val initialResponse = initialResult.getOrNull()!!
            val refinedResponse = refinedResult.getOrNull()!!
            
            // Refined response should build on initial response
            assertTrue(refinedResponse.content.length >= initialResponse.content.length)
            assertTrue(refinedResponse.confidence >= initialResponse.confidence - 0.1)
        }
        
        @ParameterizedTest
        @ValueSource(strings = [
            "Create a simple TODO app",
            "Design enterprise software architecture", 
            "Explain quantum computing concepts",
            "Plan a machine learning pipeline",
            "Develop a blockchain application"
        ])
        fun `workflow handles diverse domain queries`(query: String) = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(4, testProjectId)
            setupWorkflowMocks(agents)
            
            // When
            val result = orchestrator.processUserInput(testProjectId, query, TestDataBuilders.createTestProjectContext())
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.content.isNotEmpty())
            assertTrue(response.confidence > 0.0)
        }
    }
    
    @Nested
    @DisplayName("Multi-Agent Collaboration Scenarios")
    inner class MultiAgentCollaborationTests {
        
        @Test
        fun `agents collaborate effectively on complex problems`() = runTest {
            // Given - Specialized agents
            val strategyAgent = TestDataBuilders.createTestAgent(
                id = "strategy-lead",
                role = AgentRole.STRATEGY,
                metrics = TestDataBuilders.createTestAgentMetrics(successRate = 0.9)
            )
            val techAgent = TestDataBuilders.createTestAgent(
                id = "tech-lead", 
                role = AgentRole.IMPLEMENTATION,
                metrics = TestDataBuilders.createTestAgentMetrics(successRate = 0.85)
            )
            val reviewAgent = TestDataBuilders.createTestAgent(
                id = "reviewer",
                role = AgentRole.REVIEW,
                metrics = TestDataBuilders.createTestAgentMetrics(successRate = 0.88)
            )
            
            val collaborativeAgents = listOf(strategyAgent, techAgent, reviewAgent)
            setupWorkflowMocks(collaborativeAgents)
            
            // Mock collaboration with consensus
            val consensusCollaboration = TestDataBuilders.createTestCollaboration(
                projectId = testProjectId,
                participants = collaborativeAgents.map { it.id },
                consensusReached = true,
                sharedContext = TestDataBuilders.createTestSharedContext(
                    agreedDecisions = listOf(
                        TestDataBuilders.createTestDecision(
                            description = "Use microservices architecture",
                            participants = collaborativeAgents.map { it.id }
                        ),
                        TestDataBuilders.createTestDecision(
                            description = "Implement API-first design",
                            participants = collaborativeAgents.map { it.id }
                        )
                    )
                )
            )
            
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns consensusCollaboration
            
            val collaborativeQuery = "Design a system architecture for a real-time chat application with 100K+ concurrent users"
            
            // When
            val result = orchestrator.processUserInput(testProjectId, collaborativeQuery, TestDataBuilders.createTestProjectContext())
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Should reflect collaborative decision-making
            assertTrue(response.confidence > 0.8) // High confidence from consensus
            assertTrue(response.content.contains("microservices") || response.content.contains("API"))
            assertTrue(response.metadata.contains("collaboration_participants"))
            
            // Verify collaboration process
            coVerify { collaborationManager.startCollaboration(
                projectId = testProjectId,
                participants = collaborativeAgents.map { it.id },
                thoughtTree = any(),
                sessionType = SessionType.PROBLEM_SOLVING
            )}
        }
        
        @Test
        fun `agents handle disagreements and reach consensus`() = runTest {
            // Given - Agents with conflicting views
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            setupWorkflowMocks(agents)
            
            // Mock collaboration with initial conflict, then consensus
            val conflictedCollaboration = TestDataBuilders.createTestCollaboration(
                projectId = testProjectId,
                consensusReached = false,
                sharedContext = TestDataBuilders.createTestSharedContext(
                    conflictingViews = listOf(
                        TestDataBuilders.createTestConflictingView(
                            description = "Database choice disagreement",
                            positions = mapOf(
                                agents[0].id to "Use PostgreSQL for ACID compliance",
                                agents[1].id to "Use MongoDB for flexible schema",
                                agents[2].id to "Use Redis for performance"
                            ),
                            resolution = "Hybrid approach: PostgreSQL for core data, Redis for caching"
                        )
                    )
                )
            )
            
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns conflictedCollaboration
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId, 
                "Choose the best database technology for our application",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Should handle conflicts gracefully
            assertNotNull(response.alternatives) // Should present alternatives
            assertTrue(response.alternatives.isNotEmpty())
        }
        
        @Test
        fun `collaboration scales with increasing agent count`() = runTest {
            // Given - Large team of agents
            val largeTeam = TestDataBuilders.createTestAgentList(10, testProjectId)
            setupWorkflowMocks(largeTeam)
            
            val collaborationWithLargeTeam = TestDataBuilders.createTestCollaboration(
                projectId = testProjectId,
                participants = largeTeam.map { it.id },
                consensusReached = true
            )
            
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns collaborationWithLargeTeam
            
            // When
            val startTime = System.currentTimeMillis()
            val result = orchestrator.processUserInput(
                testProjectId,
                "Design a comprehensive enterprise software solution",
                TestDataBuilders.createTestProjectContext()
            )
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Should scale reasonably well
            assertTrue(duration < 30000, "Large team collaboration should complete within 30 seconds")
            assertTrue(response.confidence > 0.7) // Large team should produce high confidence
            
            // Verify all agents were engaged
            coVerify { collaborationManager.startCollaboration(
                projectId = testProjectId,
                participants = largeTeam.map { it.id },
                thoughtTree = any(),
                sessionType = any()
            )}
        }
    }
    
    @Nested
    @DisplayName("Real-time Collaboration Features")
    inner class RealTimeCollaborationTests {
        
        @Test
        fun `real-time updates propagate across collaboration session`() = runTest {
            // Given - Active collaboration
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            setupWorkflowMocks(agents)
            
            val collaboration = TestDataBuilders.createTestCollaboration(
                projectId = testProjectId,
                participants = agents.map { it.id },
                status = CollaborationStatus.ACTIVE
            )
            
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns collaboration
            coEvery { collaborationRepository.getCollaborationsByProject(testProjectId) } returns flowOf(listOf(collaboration))
            
            // When - Start workflow and check active collaborations
            val workflowResult = orchestrator.processUserInput(
                testProjectId,
                "Real-time collaboration test",
                TestDataBuilders.createTestProjectContext()
            )
            
            val activeCollaborations = orchestrator.getActiveCollaborations(testProjectId).first()
            
            // Then
            assertTrue(workflowResult.isSuccess)
            assertTrue(activeCollaborations.isNotEmpty())
            assertEquals(collaboration.id, activeCollaborations.first().id)
            assertEquals(CollaborationStatus.ACTIVE, activeCollaborations.first().status)
        }
        
        @Test
        fun `thought synchronization works across agents`() = runTest {
            // Given - Multiple agents generating thoughts
            val agents = TestDataBuilders.createTestAgentList(4, testProjectId)
            val synchronizedThoughts = agents.flatMapIndexed { index, agent ->
                TestDataBuilders.createTestThoughtList(2, testProjectId, agent.id).mapIndexed { thoughtIndex, thought ->
                    thought.copy(
                        id = "${agent.id}-thought-$thoughtIndex",
                        content = "Synchronized thought from ${agent.name}: $thoughtIndex"
                    )
                }
            }
            
            setupWorkflowMocks(agents)
            
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), any()) } answers {
                val agent = thirdArg<com.synthnet.aiapp.domain.models.Agent>()
                Result.success(synchronizedThoughts.filter { it.agentId == agent.id })
            }
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Generate thoughts for synchronization test",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then
            assertTrue(result.isSuccess)
            
            // Verify thoughts from all agents were processed
            coVerify(exactly = agents.size) { aiServiceIntegration.generateThoughts(any(), any(), any()) }
            
            // Verify thought persistence for synchronization
            coVerify(atLeast = synchronizedThoughts.size) { thoughtRepository.insertThought(any()) }
        }
        
        @Test
        fun `consensus building works in real-time`() = runTest {
            // Given - Collaboration with consensus process
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            setupWorkflowMocks(agents)
            
            val consensusBuilding = TestDataBuilders.createTestCollaboration(
                projectId = testProjectId,
                participants = agents.map { it.id },
                consensusReached = false, // Start without consensus
                sharedContext = TestDataBuilders.createTestSharedContext(
                    syncPoints = listOf(
                        TestDataBuilders.createTestSyncPoint(
                            description = "Initial proposal review",
                            participants = agents.map { it.id }
                        )
                    )
                )
            )
            
            val finalConsensus = consensusBuilding.copy(consensusReached = true)
            
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns consensusBuilding
            coEvery { collaborationManager.reachConsensus(consensusBuilding.id) } returns Result.success(true)
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Build consensus on system architecture approach",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Should reflect consensus building
            assertTrue(response.metadata.contains("consensus_reached") || 
                      response.content.contains("consensus") ||
                      response.confidence > 0.8)
        }
    }
    
    @Nested
    @DisplayName("Data Persistence and Retrieval")
    inner class DataPersistenceTests {
        
        @Test
        fun `workflow persists all generated data correctly`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            setupWorkflowMocks(agents)
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Test data persistence workflow",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then
            assertTrue(result.isSuccess)
            
            // Verify all data persistence operations
            coVerify(atLeast = 1) { thoughtRepository.insertThought(any()) }
            coVerify(atLeast = 1) { collaborationRepository.insertCollaboration(any()) }
            
            // Verify agent status updates were persisted
            agents.forEach { agent ->
                coVerify { agentRepository.updateAgentStatus(agent.id, AgentStatus.THINKING) }
                coVerify { agentRepository.updateAgentStatus(agent.id, AgentStatus.IDLE) }
            }
        }
        
        @Test
        fun `workflow retrieves and uses historical context`() = runTest {
            // Given - Project with historical context
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val historicalContext = TestDataBuilders.createTestProjectContext(
                projectMemory = listOf(
                    TestDataBuilders.createTestContextItem(
                        content = "Previous architectural decisions: microservices, REST APIs",
                        relevance = 0.9
                    ),
                    TestDataBuilders.createTestContextItem(
                        content = "Technology stack: Kotlin, Spring Boot, PostgreSQL",
                        relevance = 0.8
                    )
                )
            )
            
            setupWorkflowMocks(agents)
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Extend the existing system with new features",
                historicalContext
            )
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            
            // Should incorporate historical context
            assertTrue(response.content.contains("microservices") || 
                      response.content.contains("existing") ||
                      response.confidence > 0.7)
        }
        
        @Test
        fun `workflow handles data consistency across repositories`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            setupWorkflowMocks(agents)
            
            // Track all data operations
            val thoughtInsertions = mutableListOf<String>()
            val collaborationUpdates = mutableListOf<String>()
            val agentStatusUpdates = mutableListOf<String>()
            
            coEvery { thoughtRepository.insertThought(any()) } answers {
                thoughtInsertions.add(firstArg<com.synthnet.aiapp.domain.models.Thought>().id)
                Result.success(Unit)
            }
            
            coEvery { collaborationRepository.updateCollaboration(any()) } answers {
                collaborationUpdates.add(firstArg<com.synthnet.aiapp.domain.models.Collaboration>().id)
                Result.success(Unit)
            }
            
            coEvery { agentRepository.updateAgentStatus(any(), any()) } answers {
                agentStatusUpdates.add("${firstArg<String>()}-${secondArg<AgentStatus>()}")
                Result.success(Unit)
            }
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Test data consistency",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then
            assertTrue(result.isSuccess)
            
            // Verify data consistency
            assertTrue(thoughtInsertions.isNotEmpty())
            assertTrue(agentStatusUpdates.isNotEmpty())
            
            // Verify proper agent status transitions
            val statusTransitions = agentStatusUpdates.filter { it.contains(agents[0].id) }
            assertTrue(statusTransitions.any { it.contains("THINKING") })
            assertTrue(statusTransitions.any { it.contains("IDLE") })
        }
    }
    
    @Nested
    @DisplayName("Error Recovery and Fallback Mechanisms")
    inner class ErrorRecoveryTests {
        
        @Test
        fun `workflow recovers from partial service failures`() = runTest {
            // Given - Partial service failures
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            
            coEvery { agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            
            // AI service fails for some agents, succeeds for others
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), agents[0]) } returns Result.success(
                TestDataBuilders.createTestThoughtList(2, testProjectId, agents[0].id)
            )
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), agents[1]) } returns Result.failure(
                RuntimeException("AI service temporarily unavailable")
            )
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), agents[2]) } returns Result.success(
                TestDataBuilders.createTestThoughtList(2, testProjectId, agents[2].id)
            )
            
            coEvery { thoughtRepository.insertThought(any()) } returns Result.success(Unit)
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns 
                TestDataBuilders.createTestCollaboration(projectId = testProjectId)
            coEvery { rmpEngine.optimizeResponse(any(), any()) } returns 
                TestDataBuilders.createTestAgentResponse(confidence = 0.8)
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Test partial failure recovery",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then - Should succeed with available agents
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.confidence > 0.0)
            
            // Should have used antifragile system
            coVerify { antifragileSystem.executeWithFallback<com.synthnet.aiapp.domain.models.AgentResponse>(any(), any()) }
        }
        
        @Test
        fun `workflow provides fallback response when major systems fail`() = runTest {
            // Given - Major system failures
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            
            coEvery { agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.failure(
                RuntimeException("All AI services down")
            )
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } throws
                RuntimeException("Collaboration service unavailable")
            
            // Antifragile system should provide fallback
            coEvery { antifragileSystem.executeWithFallback<com.synthnet.aiapp.domain.models.AgentResponse>(any(), any()) } answers {
                val fallbackBlock = secondArg<suspend () -> Result<com.synthnet.aiapp.domain.models.AgentResponse>>()
                try {
                    fallbackBlock()
                } catch (e: Exception) {
                    Result.success(TestDataBuilders.createTestAgentResponse(
                        content = "I encountered some technical difficulties, but here's a basic analysis based on available information.",
                        confidence = 0.5
                    ))
                }
            }
            
            // When
            val result = orchestrator.processUserInput(
                testProjectId,
                "Test major failure fallback",
                TestDataBuilders.createTestProjectContext()
            )
            
            // Then - Should provide fallback response
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.content.contains("difficulties") || response.confidence <= 0.6)
        }
        
        @Test
        fun `workflow maintains system health during cascading failures`() = runTest {
            // Given - Cascading failure scenario
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            
            // Simulate cascading failures
            var failureCount = 0
            coEvery { agentRepository.getAgentsByProject(testProjectId) } answers {
                if (++failureCount <= 2) {
                    throw RuntimeException("Database connection failed")
                } else {
                    flowOf(agents) // Recover after 2 failures
                }
            }
            
            coEvery { aiServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                TestDataBuilders.createTestThoughtList(1, testProjectId)
            )
            coEvery { thoughtRepository.insertThought(any()) } returns Result.success(Unit)
            coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns
                TestDataBuilders.createTestCollaboration(projectId = testProjectId)
            coEvery { rmpEngine.optimizeResponse(any(), any()) } returns
                TestDataBuilders.createTestAgentResponse()
            
            // When - Multiple attempts
            val results = mutableListOf<Result<com.synthnet.aiapp.domain.models.AgentResponse>>()
            repeat(3) {
                val result = orchestrator.processUserInput(
                    testProjectId,
                    "Test cascading failure recovery",
                    TestDataBuilders.createTestProjectContext()
                )
                results.add(result)
            }
            
            // Then - Should eventually recover
            assertTrue(results.last().isSuccess, "System should recover from cascading failures")
            
            // Should have attempted multiple times
            coVerify(atLeast = 3) { agentRepository.getAgentsByProject(testProjectId) }
        }
    }
    
    // Helper method to setup common mocks for workflows
    private fun setupWorkflowMocks(agents: List<com.synthnet.aiapp.domain.models.Agent>) {
        coEvery { agentRepository.getAgentsByProject(testProjectId) } returns flowOf(agents)
        
        coEvery { aiServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
            TestDataBuilders.createTestThoughtList(3, testProjectId)
        )
        
        coEvery { thoughtRepository.insertThought(any()) } returns Result.success(Unit)
        
        coEvery { collaborationManager.startCollaboration(any(), any(), any(), any()) } returns
            TestDataBuilders.createTestCollaboration(
                projectId = testProjectId,
                participants = agents.map { it.id }
            )
        
        coEvery { rmpEngine.optimizeResponse(any(), any()) } returns
            TestDataBuilders.createTestAgentResponse(confidence = 0.88)
        
        // Setup agent status updates
        agents.forEach { agent ->
            coEvery { agentRepository.updateAgentStatus(agent.id, any()) } returns Result.success(Unit)
        }
    }
}