package com.synthnet.aiapp.domain.ai

import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.ai.service.AIServiceIntegration
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
import kotlin.test.*

/**
 * Comprehensive test suite for RecursiveMetaPrompting
 * 
 * Tests cover:
 * - Quality assessment algorithms
 * - Iterative improvement logic
 * - Confidence calibration mechanisms
 * - Convergence and optimization
 * - Performance and timeout handling
 * - Mock AI service calls
 */
@ExtendWith(MockKExtension::class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RecursiveMetaPromptingTest {
    
    private lateinit var engine: RecursiveMetaPrompting
    private lateinit var mockAIServiceIntegration: AIServiceIntegration
    
    private val testContext = TestDataBuilders.createTestProjectContext()
    private val initialResponse = TestDataBuilders.createTestAgentResponse(
        content = "Initial response with basic quality",
        confidence = 0.6
    )
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        mockAIServiceIntegration = MockFactories.createMockAIServiceIntegration()
        
        engine = RecursiveMetaPrompting(mockAIServiceIntegration)
    }
    
    @Nested
    @DisplayName("Response Optimization")
    inner class ResponseOptimizationTests {
        
        @Test
        fun `optimizeResponse improves response quality through iterations`() = runTest {
            // Given
            val improvementIterations = listOf(
                TestDataBuilders.createTestAgentResponse(
                    content = "Improved response with better analysis",
                    confidence = 0.7
                ),
                TestDataBuilders.createTestAgentResponse(
                    content = "Further improved response with comprehensive analysis",
                    confidence = 0.85
                ),
                TestDataBuilders.createTestAgentResponse(
                    content = "Optimized response with expert-level analysis and insights",
                    confidence = 0.92
                )
            )
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returnsMany 
                improvementIterations.map { Result.success(it) }
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returnsMany 
                improvementIterations.map { Result.success(it) }
            
            // When
            val result = engine.optimizeResponse(initialResponse, testContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.confidence > initialResponse.confidence)
            assertTrue(result.content.length > initialResponse.content.length)
            assertTrue(result.content.contains("analysis") || result.content.contains("improved"))
        }
        
        @Test
        fun `optimizeResponse handles single iteration improvement`() = runTest {
            // Given
            val improvedResponse = TestDataBuilders.createTestAgentResponse(
                content = "Significantly improved response",
                confidence = 0.9
            )
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.success(improvedResponse)
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(improvedResponse)
            
            // When
            val result = engine.optimizeResponse(initialResponse, testContext)
            
            // Then
            assertEquals(improvedResponse, result)
            assertTrue(result.confidence > initialResponse.confidence)
        }
        
        @Test
        fun `optimizeResponse returns original on optimization failure`() = runTest {
            // Given
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.failure(
                RuntimeException("Optimization service unavailable")
            )
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.failure(
                RuntimeException("Generation service unavailable")
            )
            
            // When
            val result = engine.optimizeResponse(initialResponse, testContext)
            
            // Then
            assertEquals(initialResponse.content, result.content)
            assertTrue(result.confidence <= initialResponse.confidence)
        }
        
        @Test
        fun `optimizeResponse stops at convergence`() = runTest {
            // Given - Same response indicates convergence
            val convergedResponse = TestDataBuilders.createTestAgentResponse(
                content = "Converged optimal response",
                confidence = 0.95
            )
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.success(convergedResponse)
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(convergedResponse)
            
            // When
            val result = engine.optimizeResponse(initialResponse, testContext)
            
            // Then
            assertEquals(convergedResponse, result)
            // Should have stopped at convergence, not continue iterating indefinitely
            coVerify(atMost = 5) { mockAIServiceIntegration.optimizeResponse(any(), any()) }
        }
        
        @ParameterizedTest
        @ValueSource(doubles = [0.1, 0.3, 0.5, 0.7, 0.9])
        fun `optimizeResponse handles different initial confidence levels`(initialConfidence: Double) = runTest {
            // Given
            val responseWithConfidence = initialResponse.copy(confidence = initialConfidence)
            val improvedResponse = TestDataBuilders.createTestAgentResponse(
                confidence = (initialConfidence + 0.2).coerceAtMost(1.0)
            )
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.success(improvedResponse)
            
            // When
            val result = engine.optimizeResponse(responseWithConfidence, testContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.confidence >= initialConfidence)
        }
    }
    
    @Nested
    @DisplayName("Quality Assessment")
    inner class QualityAssessmentTests {
        
        @Test
        fun `assessQuality returns accurate quality scores`() = runTest {
            // Given
            val highQualityResponse = TestDataBuilders.createTestAgentResponse(
                content = "Comprehensive analysis with detailed reasoning, multiple perspectives, and clear conclusions",
                confidence = 0.9,
                reasoning = TestDataBuilders.createTestChainOfThought(
                    steps = TestDataBuilders.createTestThoughtStep().let { listOf(it, it, it) },
                    confidence = 0.9
                )
            )
            
            val expectedQuality = 0.85
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(content = expectedQuality.toString())
            )
            
            // When
            val result = engine.assessQuality(highQualityResponse)
            
            // Then
            assertTrue(result >= 0.0)
            assertTrue(result <= 1.0)
            // High quality response should get high score
            assertTrue(result > 0.5)
        }
        
        @Test
        fun `assessQuality handles low quality responses`() = runTest {
            // Given
            val lowQualityResponse = TestDataBuilders.createTestAgentResponse(
                content = "Brief response",
                confidence = 0.2,
                reasoning = TestDataBuilders.createTestChainOfThought(confidence = 0.2)
            )
            
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(content = "0.3")
            )
            
            // When
            val result = engine.assessQuality(lowQualityResponse)
            
            // Then
            assertTrue(result >= 0.0)
            assertTrue(result <= 1.0)
            // Low quality response should get lower score
            assertTrue(result < 0.7)
        }
        
        @Test
        fun `assessQuality handles assessment service failures`() = runTest {
            // Given
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.failure(
                RuntimeException("Assessment service down")
            )
            
            // When
            val result = engine.assessQuality(initialResponse)
            
            // Then - Should provide fallback assessment
            assertTrue(result >= 0.0)
            assertTrue(result <= 1.0)
            // Fallback should be based on confidence
            assertTrue(result > 0.0) // Should not be zero
        }
        
        @Test
        fun `assessQuality considers multiple quality factors`() = runTest {
            // Given
            val comprehensiveResponse = TestDataBuilders.createTestAgentResponse(
                content = "Detailed analysis with examples and multiple viewpoints",
                confidence = 0.8,
                reasoning = TestDataBuilders.createTestChainOfThought(
                    steps = (1..5).map { TestDataBuilders.createTestThoughtStep() },
                    confidence = 0.8
                ),
                alternatives = listOf(
                    TestDataBuilders.createTestAlternative(),
                    TestDataBuilders.createTestAlternative()
                )
            )
            
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(content = "0.88")
            )
            
            // When
            val result = engine.assessQuality(comprehensiveResponse)
            
            // Then
            assertTrue(result > 0.7) // Should recognize comprehensive quality
        }
    }
    
    @Nested
    @DisplayName("Iterative Improvement")
    inner class IterativeImprovementTests {
        
        @Test
        fun `generateImprovement creates enhanced responses`() = runTest {
            // Given
            val improvementFeedback = "Add more specific examples and strengthen the conclusion"
            val enhancedResponse = TestDataBuilders.createTestAgentResponse(
                content = "Enhanced response with specific examples and stronger conclusion",
                confidence = 0.85
            )
            
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(enhancedResponse)
            
            // When
            val result = engine.generateImprovement(initialResponse, improvementFeedback)
            
            // Then
            assertEquals(enhancedResponse, result)
            assertTrue(result.confidence > initialResponse.confidence)
            assertNotEquals(initialResponse.content, result.content)
        }
        
        @Test
        fun `generateImprovement handles empty feedback`() = runTest {
            // Given
            val emptyFeedback = ""
            val fallbackResponse = initialResponse.copy(
                content = "Refined " + initialResponse.content,
                confidence = initialResponse.confidence + 0.1
            )
            
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(fallbackResponse)
            
            // When
            val result = engine.generateImprovement(initialResponse, emptyFeedback)
            
            // Then
            assertNotNull(result)
            assertTrue(result.confidence >= initialResponse.confidence)
        }
        
        @Test
        fun `generateImprovement handles generation failures`() = runTest {
            // Given
            val feedback = "Improve the analysis"
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.failure(
                RuntimeException("Generation failed")
            )
            
            // When
            val result = engine.generateImprovement(initialResponse, feedback)
            
            // Then - Should return original or slightly modified version
            assertNotNull(result)
            assertEquals(initialResponse.agentId, result.agentId)
        }
        
        @Test
        fun `generateImprovement preserves response structure`() = runTest {
            // Given
            val feedback = "Add more detail"
            val improvedResponse = TestDataBuilders.createTestAgentResponse(
                agentId = initialResponse.agentId,
                content = "More detailed " + initialResponse.content,
                reasoning = initialResponse.reasoning,
                alternatives = initialResponse.alternatives,
                metadata = initialResponse.metadata
            )
            
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(improvedResponse)
            
            // When
            val result = engine.generateImprovement(initialResponse, feedback)
            
            // Then
            assertEquals(initialResponse.agentId, result.agentId)
            assertNotNull(result.reasoning)
            assertTrue(result.alternatives.isNotEmpty() || initialResponse.alternatives.isEmpty())
        }
    }
    
    @Nested
    @DisplayName("Convergence Detection")
    inner class ConvergenceTests {
        
        @Test
        fun `shouldContinueOptimization stops at high confidence`() = runTest {
            // Given
            val highConfidenceResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.95)
            val currentIteration = 2
            
            // When
            val result = engine.shouldContinueOptimization(highConfidenceResponse, currentIteration)
            
            // Then
            assertFalse(result) // Should stop at high confidence
        }
        
        @Test
        fun `shouldContinueOptimization stops at max iterations`() = runTest {
            // Given
            val mediumConfidenceResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.6)
            val maxIterations = 10
            
            // When
            val result = engine.shouldContinueOptimization(mediumConfidenceResponse, maxIterations)
            
            // Then
            assertFalse(result) // Should stop at max iterations
        }
        
        @Test
        fun `shouldContinueOptimization continues for low confidence`() = runTest {
            // Given
            val lowConfidenceResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.4)
            val earlyIteration = 1
            
            // When
            val result = engine.shouldContinueOptimization(lowConfidenceResponse, earlyIteration)
            
            // Then
            assertTrue(result) // Should continue for low confidence
        }
        
        @ParameterizedTest
        @ValueSource(ints = [1, 3, 5, 7, 9])
        fun `shouldContinueOptimization handles different iteration counts`(iteration: Int) = runTest {
            // Given
            val mediumConfidenceResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.7)
            
            // When
            val result = engine.shouldContinueOptimization(mediumConfidenceResponse, iteration)
            
            // Then
            assertNotNull(result) // Should make a decision for any iteration count
            if (iteration >= 8) {
                assertFalse(result) // Should stop at high iterations
            }
        }
    }
    
    @Nested
    @DisplayName("Confidence Calibration")
    inner class ConfidenceCalibrationTests {
        
        @Test
        fun `calibrateConfidence adjusts confidence based on quality`() = runTest {
            // Given
            val responseWithUncalibratedConfidence = TestDataBuilders.createTestAgentResponse(
                confidence = 0.9, // High confidence
                content = "Brief response" // But low quality content
            )
            
            // Mock quality assessment to return lower quality
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(content = "0.5") // Lower quality assessment
            )
            
            // When
            val result = engine.calibrateConfidence(responseWithUncalibratedConfidence)
            
            // Then
            assertTrue(result <= responseWithUncalibratedConfidence.confidence)
            assertTrue(result >= 0.0)
            assertTrue(result <= 1.0)
        }
        
        @Test
        fun `calibrateConfidence increases confidence for high quality`() = runTest {
            // Given
            val responseWithLowConfidence = TestDataBuilders.createTestAgentResponse(
                confidence = 0.5, // Low confidence
                content = "Comprehensive analysis with detailed reasoning and multiple perspectives" // High quality
            )
            
            // Mock quality assessment to return higher quality
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(content = "0.9") // High quality assessment
            )
            
            // When
            val result = engine.calibrateConfidence(responseWithLowConfidence)
            
            // Then
            assertTrue(result >= responseWithLowConfidence.confidence)
            assertTrue(result <= 1.0)
        }
        
        @Test
        fun `calibrateConfidence handles calibration service failures`() = runTest {
            // Given
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.failure(
                RuntimeException("Calibration service failed")
            )
            
            // When
            val result = engine.calibrateConfidence(initialResponse)
            
            // Then - Should return reasonable fallback
            assertTrue(result >= 0.0)
            assertTrue(result <= 1.0)
            // Fallback should be close to original
            assertTrue(kotlin.math.abs(result - initialResponse.confidence) <= 0.3)
        }
        
        @Test
        fun `calibrateConfidence maintains confidence bounds`() = runTest {
            // Given
            val extremeResponse = TestDataBuilders.createTestAgentResponse(confidence = 1.0)
            coEvery { mockAIServiceIntegration.generateResponse(any(), any()) } returns Result.success(
                TestDataBuilders.createTestAgentResponse(content = "1.5") // Out of bounds
            )
            
            // When
            val result = engine.calibrateConfidence(extremeResponse)
            
            // Then
            assertTrue(result >= 0.0)
            assertTrue(result <= 1.0)
        }
    }
    
    @Nested
    @DisplayName("Performance and Timeout Handling")
    inner class PerformanceTests {
        
        @Test
        fun `optimization completes within reasonable time`() = runTest {
            // Given
            val improvedResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.8)
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.success(improvedResponse)
            
            // When
            val startTime = System.currentTimeMillis()
            val result = engine.optimizeResponse(initialResponse, testContext)
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertNotNull(result)
            assertTrue(duration < 5000, "Optimization should complete within 5 seconds")
        }
        
        @Test
        fun `optimization handles slow service responses`() = runTest {
            // Given
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } coAnswers {
                kotlinx.coroutines.delay(100) // Simulate slow response
                Result.success(TestDataBuilders.createTestAgentResponse(confidence = 0.8))
            }
            
            // When
            val result = engine.optimizeResponse(initialResponse, testContext)
            
            // Then - Should still complete successfully
            assertNotNull(result)
            assertTrue(result.confidence > 0.0)
        }
        
        @Test
        fun `optimization handles concurrent requests`() = runTest {
            // Given
            val responses = List(5) { i ->
                TestDataBuilders.createTestAgentResponse(
                    content = "Response $i",
                    confidence = 0.5 + (i * 0.1)
                )
            }
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } answers {
                Result.success(TestDataBuilders.createTestAgentResponse(confidence = 0.8))
            }
            
            // When
            val concurrentOptimizations = responses.map { response ->
                async { engine.optimizeResponse(response, testContext) }
            }
            
            val results = concurrentOptimizations.awaitAll()
            
            // Then
            assertEquals(5, results.size)
            results.forEach { result ->
                assertNotNull(result)
                assertTrue(result.confidence > 0.0)
            }
        }
        
        @Test
        fun `optimization prevents infinite loops`() = runTest {
            // Given - Service keeps returning same low quality
            val stagnantResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.3)
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.success(stagnantResponse)
            
            // When
            val startTime = System.currentTimeMillis()
            val result = engine.optimizeResponse(initialResponse, testContext)
            val duration = System.currentTimeMillis() - startTime
            
            // Then - Should terminate instead of looping infinitely
            assertNotNull(result)
            assertTrue(duration < 10000, "Should not run infinitely")
            coVerify(atMost = 10) { mockAIServiceIntegration.optimizeResponse(any(), any()) }
        }
    }
    
    @Nested
    @DisplayName("Context Integration")
    inner class ContextIntegrationTests {
        
        @Test
        fun `optimization considers project context`() = runTest {
            // Given
            val contextWithMemory = TestDataBuilders.createTestProjectContext(
                projectMemory = listOf(
                    TestDataBuilders.createTestContextItem(
                        content = "Previous project decisions and constraints"
                    )
                )
            )
            
            val contextAwareResponse = TestDataBuilders.createTestAgentResponse(
                content = "Response considering project constraints and decisions",
                confidence = 0.8
            )
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), contextWithMemory) } returns Result.success(contextAwareResponse)
            
            // When
            val result = engine.optimizeResponse(initialResponse, contextWithMemory)
            
            // Then
            assertEquals(contextAwareResponse, result)
            coVerify { mockAIServiceIntegration.optimizeResponse(any(), contextWithMemory) }
        }
        
        @Test
        fun `optimization handles empty context`() = runTest {
            // Given
            val emptyContext = TestDataBuilders.createTestProjectContext(
                workingMemory = emptyList(),
                sessionMemory = emptyList(),
                projectMemory = emptyList()
            )
            
            val optimizedResponse = TestDataBuilders.createTestAgentResponse(confidence = 0.8)
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), any()) } returns Result.success(optimizedResponse)
            
            // When
            val result = engine.optimizeResponse(initialResponse, emptyContext)
            
            // Then
            assertNotNull(result)
            assertTrue(result.confidence >= initialResponse.confidence)
        }
        
        @Test
        fun `optimization leverages session memory`() = runTest {
            // Given
            val contextWithSession = TestDataBuilders.createTestProjectContext(
                sessionMemory = listOf(
                    TestDataBuilders.createTestContextItem(
                        content = "Recent conversation context and user preferences"
                    )
                )
            )
            
            val sessionAwareResponse = TestDataBuilders.createTestAgentResponse(
                content = "Response that builds on recent conversation",
                confidence = 0.85
            )
            
            coEvery { mockAIServiceIntegration.optimizeResponse(any(), contextWithSession) } returns Result.success(sessionAwareResponse)
            
            // When
            val result = engine.optimizeResponse(initialResponse, contextWithSession)
            
            // Then
            assertEquals(sessionAwareResponse, result)
            coVerify { mockAIServiceIntegration.optimizeResponse(any(), contextWithSession) }
        }
    }
}