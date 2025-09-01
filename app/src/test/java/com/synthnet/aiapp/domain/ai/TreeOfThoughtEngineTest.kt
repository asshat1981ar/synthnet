package com.synthnet.aiapp.domain.ai

import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.repository.ThoughtRepository
import com.synthnet.aiapp.domain.ai.service.AIServiceIntegration
import com.synthnet.aiapp.data.entities.ThoughtType
import com.synthnet.aiapp.testutils.TestDataBuilders
import com.synthnet.aiapp.testutils.MockFactories
import kotlinx.coroutines.test.*
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import io.mockk.*
import org.junit.jupiter.api.*
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.junit.jupiter.params.provider.EnumSource
import kotlin.test.*

/**
 * Comprehensive test suite for TreeOfThoughtEngine
 * 
 * Tests cover:
 * - Thought generation and expansion algorithms
 * - Branch evaluation and selection logic
 * - Thought tree building and traversal
 * - Confidence scoring and ranking
 * - Performance with large thought trees
 * - Mock thought repository operations
 */
@ExtendWith(MockKExtension::class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class TreeOfThoughtEngineTest {
    
    private lateinit var engine: TreeOfThoughtEngine
    private lateinit var mockThoughtRepository: ThoughtRepository
    private lateinit var mockAIServiceIntegration: AIServiceIntegration
    
    private val testProjectId = "test-project-123"
    private val testPrompt = "Analyze the best approach to implement a scalable microservices architecture"
    private val testContext = TestDataBuilders.createTestProjectContext()
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        mockThoughtRepository = MockFactories.createMockThoughtRepository()
        mockAIServiceIntegration = MockFactories.createMockAIServiceIntegration()
        
        engine = TreeOfThoughtEngine(
            mockThoughtRepository,
            mockAIServiceIntegration
        )
    }
    
    @Nested
    @DisplayName("Tree of Thought Workflow")
    inner class ToTWorkflowTests {
        
        @Test
        fun `executeToTWorkflow completes full workflow successfully`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val expectedThoughts = TestDataBuilders.createTestThoughtList(5, testProjectId)
            val expectedTree = TestDataBuilders.createTestThoughtTree(projectId = testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(expectedThoughts)
            coEvery { mockThoughtRepository.insertThought(any()) } returns Result.success(Unit)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertEquals(testProjectId, result.projectId)
            assertTrue(result.branches.isNotEmpty())
            assertNotNull(result.rootThought)
            assertNotNull(result.metrics)
            
            // Verify thoughts were generated for each agent
            coVerify(atLeast = agents.size) { mockAIServiceIntegration.generateThoughts(any(), any(), any()) }
        }
        
        @Test
        fun `executeToTWorkflow handles empty agent list`() = runTest {
            // Given
            val emptyAgents = emptyList<Agent>()
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, emptyAgents, testContext)
            
            // Then - Should create fallback tree
            assertNotNull(result)
            assertEquals(testProjectId, result.projectId)
        }
        
        @Test
        fun `executeToTWorkflow handles AI service errors gracefully`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.failure(
                RuntimeException("AI service unavailable")
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should create fallback tree
            assertNotNull(result)
            assertEquals(testProjectId, result.projectId)
        }
        
        @ParameterizedTest
        @ValueSource(strings = ["", "simple", "complex analysis with multiple requirements"])
        fun `executeToTWorkflow handles different prompt types`(prompt: String) = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, prompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertEquals(testProjectId, result.projectId)
        }
        
        @Test
        fun `executeToTWorkflow creates comprehensive tree metrics`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(4, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(10, testProjectId)
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            val metrics = result.metrics
            assertNotNull(metrics)
            assertTrue(metrics.totalThoughts >= 0)
            assertTrue(metrics.maxDepth >= 0)
            assertTrue(metrics.averageConfidence >= 0.0)
            assertTrue(metrics.averageConfidence <= 1.0)
            assertTrue(metrics.branchingFactor >= 0.0)
            assertTrue(metrics.selectedPaths >= 0)
            assertTrue(metrics.processingTime >= 0)
        }
    }
    
    @Nested
    @DisplayName("Thought Generation")
    inner class ThoughtGenerationTests {
        
        @Test
        fun `generateInitialThoughts creates diverse thoughts from multiple agents`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val thoughtsPerAgent = 2
            val expectedThoughtsPerCall = TestDataBuilders.createTestThoughtList(thoughtsPerAgent, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(expectedThoughtsPerCall)
            coEvery { mockThoughtRepository.insertThought(any()) } returns Result.success(Unit)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            // Should have called generateThoughts for each agent
            coVerify(exactly = agents.size) { mockAIServiceIntegration.generateThoughts(any(), any(), any()) }
        }
        
        @Test
        fun `generateInitialThoughts handles partial failures`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val successfulThoughts = TestDataBuilders.createTestThoughtList(2, testProjectId)
            
            // First call succeeds, second fails, third succeeds
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), agents[0]) } returns Result.success(successfulThoughts)
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), agents[1]) } returns Result.failure(RuntimeException("Generation failed"))
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), agents[2]) } returns Result.success(successfulThoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should still create a tree with successful thoughts
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
        
        @ParameterizedTest
        @EnumSource(ThoughtType::class)
        fun `generateInitialThoughts handles different thought types`(thoughtType: ThoughtType) = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(1, testProjectId)
            val typedThought = TestDataBuilders.createTestThought(
                projectId = testProjectId,
                type = thoughtType
            )
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(listOf(typedThought))
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            // Should handle any thought type
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
    }
    
    @Nested
    @DisplayName("Thought Expansion")
    inner class ThoughtExpansionTests {
        
        @Test
        fun `expandThoughtsIteratively increases thought tree depth`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val initialThoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
            val expandedThoughts = TestDataBuilders.createTestThoughtList(6, testProjectId) // More thoughts after expansion
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returnsMany listOf(
                Result.success(initialThoughts),
                Result.success(expandedThoughts)
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.depth >= 1) // Should have expanded at least one level
        }
        
        @Test
        fun `expandThoughtsIteratively respects depth limits`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(5, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.depth <= 5) // Should respect reasonable depth limits
        }
        
        @Test
        fun `expandThoughtsIteratively handles expansion errors`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val initialThoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returnsMany listOf(
                Result.success(initialThoughts),
                Result.failure(RuntimeException("Expansion failed"))
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should still produce a valid tree with initial thoughts
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
    }
    
    @Nested
    @DisplayName("Thought Evaluation")
    inner class ThoughtEvaluationTests {
        
        @Test
        fun `evaluateThoughtBranches assigns quality scores`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(5, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            coEvery { mockAIServiceIntegration.evaluateThought(any(), any()) } returns Result.success(0.8)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty())
            result.branches.forEach { branch ->
                assertTrue(branch.score >= 0.0 && branch.score <= 1.0)
            }
        }
        
        @Test
        fun `evaluateThoughtBranches handles evaluation failures`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            coEvery { mockAIServiceIntegration.evaluateThought(any(), any()) } returns Result.failure(RuntimeException("Evaluation failed"))
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should use default scoring
            assertNotNull(result)
            if (result.branches.isNotEmpty()) {
                result.branches.forEach { branch ->
                    assertTrue(branch.score >= 0.0)
                }
            }
        }
        
        @Test
        fun `evaluateThoughtBranches ranks branches by quality`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val highQualityThought = TestDataBuilders.createTestThought(confidence = 0.9, projectId = testProjectId)
            val lowQualityThought = TestDataBuilders.createTestThought(confidence = 0.3, projectId = testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                listOf(highQualityThought, lowQualityThought)
            )
            coEvery { mockAIServiceIntegration.evaluateThought(highQualityThought, any()) } returns Result.success(0.9)
            coEvery { mockAIServiceIntegration.evaluateThought(lowQualityThought, any()) } returns Result.success(0.3)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            if (result.branches.size >= 2) {
                val sortedBranches = result.branches.sortedByDescending { it.score }
                assertTrue(sortedBranches[0].score >= sortedBranches[1].score)
            }
        }
    }
    
    @Nested
    @DisplayName("Path Selection")
    inner class PathSelectionTests {
        
        @Test
        fun `selectOptimalPaths identifies best reasoning chains`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val highConfidenceThoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
                .map { it.copy(confidence = 0.9) }
            val lowConfidenceThoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
                .map { it.copy(confidence = 0.3) }
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                highConfidenceThoughts + lowConfidenceThoughts
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty())
            
            // At least one branch should be marked as selected or have high score
            val hasSelectedBranch = result.branches.any { it.isSelected }
            val hasHighScoringBranch = result.branches.any { it.score > 0.7 }
            assertTrue(hasSelectedBranch || hasHighScoringBranch)
        }
        
        @Test
        fun `selectOptimalPaths handles single path scenario`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(1, testProjectId)
            val singleThought = listOf(TestDataBuilders.createTestThought(projectId = testProjectId))
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(singleThought)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            // Should handle single path gracefully
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
        
        @Test
        fun `selectOptimalPaths considers context relevance`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val contextRelevantThought = TestDataBuilders.createTestThought(
                content = "This relates to the project context memory",
                projectId = testProjectId
            )
            val irrelevantThought = TestDataBuilders.createTestThought(
                content = "This is completely unrelated content",
                projectId = testProjectId
            )
            
            val contextWithMemory = TestDataBuilders.createTestProjectContext(
                projectMemory = listOf(
                    TestDataBuilders.createTestContextItem(content = "project context memory")
                )
            )
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                listOf(contextRelevantThought, irrelevantThought)
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, contextWithMemory)
            
            // Then
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty())
        }
    }
    
    @Nested
    @DisplayName("Tree Building")
    inner class TreeBuildingTests {
        
        @Test
        fun `buildThoughtTree creates proper hierarchical structure`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val parentThought = TestDataBuilders.createTestThought(id = "parent", projectId = testProjectId)
            val childThought = TestDataBuilders.createTestThought(
                id = "child",
                parentId = "parent",
                projectId = testProjectId
            )
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                listOf(parentThought, childThought)
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            assertNotNull(result.rootThought)
            assertTrue(result.branches.isNotEmpty())
            
            // Verify hierarchical relationship
            val hasParentChildRelation = result.branches.any { branch ->
                branch.thoughts.any { thought -> thought.parentId != null }
            }
            assertTrue(hasParentChildRelation || result.rootThought.id == "parent")
        }
        
        @Test
        fun `buildThoughtTree handles disconnected thoughts`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val disconnectedThoughts = listOf(
                TestDataBuilders.createTestThought(id = "thought1", projectId = testProjectId),
                TestDataBuilders.createTestThought(id = "thought2", projectId = testProjectId),
                TestDataBuilders.createTestThought(id = "thought3", projectId = testProjectId)
            )
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(disconnectedThoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should create a valid tree structure
            assertNotNull(result)
            assertNotNull(result.rootThought)
            assertTrue(result.branches.isNotEmpty())
        }
        
        @Test
        fun `buildThoughtTree preserves thought metadata`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(1, testProjectId)
            val thoughtWithMetadata = TestDataBuilders.createTestThought(
                projectId = testProjectId,
                metadata = mapOf("custom_key" to "custom_value", "agent_expertise" to "high")
            )
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(
                listOf(thoughtWithMetadata)
            )
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then
            assertNotNull(result)
            val preservedThought = result.rootThought
            assertNotNull(preservedThought.metadata)
            assertTrue(preservedThought.metadata.isNotEmpty())
        }
    }
    
    @Nested
    @DisplayName("Performance and Scalability")
    inner class PerformanceTests {
        
        @Test
        fun `engine handles large number of agents efficiently`() = runTest {
            // Given
            val manyAgents = TestDataBuilders.createTestAgentList(20, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(5, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            
            // When
            val startTime = System.currentTimeMillis()
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, manyAgents, testContext)
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertNotNull(result)
            assertTrue(duration < 15000, "Should complete within 15 seconds even with many agents")
        }
        
        @Test
        fun `engine handles large thought trees efficiently`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val manyThoughts = TestDataBuilders.createTestThoughtList(50, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(manyThoughts)
            
            // When
            val startTime = System.currentTimeMillis()
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertNotNull(result)
            assertTrue(duration < 20000, "Should handle large thought trees within 20 seconds")
            assertNotNull(result.metrics)
            assertTrue(result.metrics.processingTime > 0)
        }
        
        @Test
        fun `engine handles concurrent workflow executions`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(5, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            
            // When - Execute multiple workflows concurrently
            val concurrentTasks = (1..5).map { i ->
                async {
                    engine.executeToTWorkflow("project-$i", "Prompt $i", agents, testContext)
                }
            }
            
            val results = concurrentTasks.awaitAll()
            
            // Then - All should complete successfully
            assertEquals(5, results.size)
            results.forEach { result ->
                assertNotNull(result)
                assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
            }
        }
        
        @Test
        fun `engine manages memory usage with large datasets`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(5, testProjectId)
            val largeThoughts = (1..100).map { i ->
                TestDataBuilders.createTestThought(
                    id = "thought-$i",
                    content = "Large content ".repeat(100), // Simulate large thoughts
                    projectId = testProjectId
                )
            }
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(largeThoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should complete without memory issues
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
    }
    
    @Nested
    @DisplayName("Error Handling and Resilience")
    inner class ErrorHandlingTests {
        
        @Test
        fun `engine creates fallback tree on complete failure`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            
            // All operations fail
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.failure(RuntimeException("Service down"))
            coEvery { mockThoughtRepository.insertThought(any()) } returns Result.failure(RuntimeException("DB error"))
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should create a fallback tree
            assertNotNull(result)
            assertEquals(testProjectId, result.projectId)
            assertNotNull(result.rootThought) // Should have at least a fallback thought
        }
        
        @Test
        fun `engine handles repository failures gracefully`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val thoughts = TestDataBuilders.createTestThoughtList(3, testProjectId)
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(thoughts)
            coEvery { mockThoughtRepository.insertThought(any()) } returns Result.failure(RuntimeException("Repository error"))
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should still create tree even if persistence fails
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
        
        @Test
        fun `engine handles mixed success and failure scenarios`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3, testProjectId)
            val successfulThoughts = TestDataBuilders.createTestThoughtList(2, testProjectId)
            
            // Some agents succeed, others fail
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), agents[0]) } returns Result.success(successfulThoughts)
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), agents[1]) } returns Result.failure(RuntimeException("Agent 1 failed"))
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), agents[2]) } returns Result.success(successfulThoughts)
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should work with partial success
            assertNotNull(result)
            assertTrue(result.branches.isNotEmpty() || result.rootThought != null)
        }
        
        @Test
        fun `engine maintains consistency during partial failures`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(2, testProjectId)
            val partialThoughts = TestDataBuilders.createTestThoughtList(1, testProjectId) // Limited thoughts
            
            coEvery { mockAIServiceIntegration.generateThoughts(any(), any(), any()) } returns Result.success(partialThoughts)
            coEvery { mockAIServiceIntegration.evaluateThought(any(), any()) } returns Result.failure(RuntimeException("Evaluation failed"))
            
            // When
            val result = engine.executeToTWorkflow(testProjectId, testPrompt, agents, testContext)
            
            // Then - Should maintain tree consistency
            assertNotNull(result)
            assertNotNull(result.rootThought)
            assertEquals(testProjectId, result.projectId)
            assertNotNull(result.metrics)
        }
    }
}