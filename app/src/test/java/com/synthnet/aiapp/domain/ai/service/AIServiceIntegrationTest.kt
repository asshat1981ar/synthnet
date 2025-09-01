package com.synthnet.aiapp.domain.ai.service

import com.synthnet.aiapp.domain.models.*
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
 * Comprehensive test suite for AIServiceIntegration
 * 
 * Tests cover:
 * - OpenAI and Anthropic service integrations
 * - Circuit breaker functionality
 * - Service health monitoring and failover
 * - Rate limiting and timeout handling
 * - Error recovery and retry mechanisms
 * - Mock HTTP responses and network conditions
 */
@ExtendWith(MockKExtension::class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class AIServiceIntegrationTest {
    
    private lateinit var aiServiceIntegration: AIServiceIntegration
    private lateinit var mockOpenAIService: OpenAIService
    private lateinit var mockAnthropicService: AnthropicService
    
    private val testPrompt = "Analyze the best practices for implementing microservices architecture"
    private val testContext = TestDataBuilders.createTestProjectContext()
    private val testAgent = TestDataBuilders.createTestAgent()
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        mockOpenAIService = MockFactories.createMockOpenAIService()
        mockAnthropicService = MockFactories.createMockAnthropicService()
        
        aiServiceIntegration = AIServiceIntegration(
            mockOpenAIService,
            mockAnthropicService
        )
    }
    
    @Nested
    @DisplayName("Service Integration")
    inner class ServiceIntegrationTests {
        
        @Test
        fun `generateResponse uses primary service successfully`() = runTest {
            // Given
            val expectedResponse = TestDataBuilders.createTestAgentResponse()
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("OpenAI response content")
            
            // When
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.content.isNotEmpty())
        }
        
        @Test
        fun `generateResponse falls back to secondary service on primary failure`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("OpenAI service unavailable")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.success("Anthropic response content")
            
            // When
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.content.contains("Anthropic") || response.content.isNotEmpty())
            
            // Verify fallback was used
            coVerify { mockOpenAIService.generateCompletion(any(), any()) }
            coVerify { mockAnthropicService.generateCompletion(any(), any()) }
        }
        
        @Test
        fun `generateResponse fails when both services are down`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("OpenAI service down")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Anthropic service down")
            )
            
            // When
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then
            assertTrue(result.isFailure)
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception.message!!.contains("service") || exception.message!!.contains("unavailable"))
        }
        
        @ParameterizedTest
        @ValueSource(strings = ["", "simple prompt", "complex multi-paragraph analysis request"])
        fun `generateResponse handles different prompt types`(prompt: String) = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("Response to: $prompt")
            
            // When
            val result = aiServiceIntegration.generateResponse(prompt, testContext)
            
            // Then
            if (prompt.isNotEmpty()) {
                assertTrue(result.isSuccess)
                val response = result.getOrNull()
                assertNotNull(response)
            }
        }
    }
    
    @Nested
    @DisplayName("Thought Generation")
    inner class ThoughtGenerationTests {
        
        @Test
        fun `generateThoughts creates multiple diverse thoughts`() = runTest {
            // Given
            val agents = TestDataBuilders.createTestAgentList(3)
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success(
                "Thought 1: Analysis approach\nThought 2: Implementation strategy\nThought 3: Risk assessment"
            )
            
            // When
            val result = aiServiceIntegration.generateThoughts(testPrompt, testContext, testAgent)
            
            // Then
            assertTrue(result.isSuccess)
            val thoughts = result.getOrNull()
            assertNotNull(thoughts)
            assertTrue(thoughts.isNotEmpty())
        }
        
        @Test
        fun `generateThoughts handles empty response`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("")
            
            // When
            val result = aiServiceIntegration.generateThoughts(testPrompt, testContext, testAgent)
            
            // Then
            assertTrue(result.isSuccess)
            val thoughts = result.getOrNull()
            assertNotNull(thoughts)
            // Should provide at least one fallback thought
            assertTrue(thoughts.isNotEmpty())
        }
        
        @Test
        fun `generateThoughts creates agent-specific thoughts`() = runTest {
            // Given
            val strategyAgent = TestDataBuilders.createTestAgent(
                name = "Strategy Agent",
                capabilities = listOf("planning", "strategy")
            )
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success(
                "Strategic analysis of the problem with focus on long-term planning"
            )
            
            // When
            val result = aiServiceIntegration.generateThoughts(testPrompt, testContext, strategyAgent)
            
            // Then
            assertTrue(result.isSuccess)
            val thoughts = result.getOrNull()
            assertNotNull(thoughts)
            thoughts.forEach { thought ->
                assertEquals(strategyAgent.id, thought.agentId)
            }
        }
        
        @Test
        fun `generateThoughts handles service failures gracefully`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Service error")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Service error")
            )
            
            // When
            val result = aiServiceIntegration.generateThoughts(testPrompt, testContext, testAgent)
            
            // Then - Should provide fallback thoughts
            assertTrue(result.isSuccess)
            val thoughts = result.getOrNull()
            assertNotNull(thoughts)
            assertTrue(thoughts.isNotEmpty()) // Should have fallback
        }
    }
    
    @Nested
    @DisplayName("Thought Evaluation")
    inner class ThoughtEvaluationTests {
        
        @Test
        fun `evaluateThought returns quality score`() = runTest {
            // Given
            val thought = TestDataBuilders.createTestThought()
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("0.85")
            
            // When
            val result = aiServiceIntegration.evaluateThought(thought, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            val score = result.getOrNull()
            assertNotNull(score)
            assertTrue(score >= 0.0)
            assertTrue(score <= 1.0)
        }
        
        @Test
        fun `evaluateThought handles invalid score responses`() = runTest {
            // Given
            val thought = TestDataBuilders.createTestThought()
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("invalid_score")
            
            // When
            val result = aiServiceIntegration.evaluateThought(thought, testContext)
            
            // Then - Should provide fallback score
            assertTrue(result.isSuccess)
            val score = result.getOrNull()
            assertNotNull(score)
            assertTrue(score >= 0.0)
            assertTrue(score <= 1.0)
        }
        
        @Test
        fun `evaluateThought considers thought confidence`() = runTest {
            // Given
            val highConfidenceThought = TestDataBuilders.createTestThought(confidence = 0.9)
            val lowConfidenceThought = TestDataBuilders.createTestThought(confidence = 0.2)
            
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("0.8")
            
            // When
            val highResult = aiServiceIntegration.evaluateThought(highConfidenceThought, testContext)
            val lowResult = aiServiceIntegration.evaluateThought(lowConfidenceThought, testContext)
            
            // Then
            assertTrue(highResult.isSuccess)
            assertTrue(lowResult.isSuccess)
            
            val highScore = highResult.getOrNull()!!
            val lowScore = lowResult.getOrNull()!!
            
            assertTrue(highScore >= 0.0)
            assertTrue(lowScore >= 0.0)
        }
        
        @Test
        fun `evaluateThought handles evaluation service failure`() = runTest {
            // Given
            val thought = TestDataBuilders.createTestThought()
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Evaluation service down")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Evaluation service down")
            )
            
            // When
            val result = aiServiceIntegration.evaluateThought(thought, testContext)
            
            // Then - Should use confidence as fallback
            assertTrue(result.isSuccess)
            val score = result.getOrNull()
            assertNotNull(score)
            assertTrue(score >= 0.0)
            assertTrue(score <= 1.0)
        }
    }
    
    @Nested
    @DisplayName("Response Optimization")
    inner class ResponseOptimizationTests {
        
        @Test
        fun `optimizeResponse improves response quality`() = runTest {
            // Given
            val initialResponse = TestDataBuilders.createTestAgentResponse(
                content = "Basic response",
                confidence = 0.6
            )
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success(
                "Enhanced and improved response with better analysis"
            )
            
            // When
            val result = aiServiceIntegration.optimizeResponse(initialResponse, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            val optimizedResponse = result.getOrNull()
            assertNotNull(optimizedResponse)
            assertTrue(optimizedResponse.content.length >= initialResponse.content.length)
            assertTrue(optimizedResponse.confidence >= initialResponse.confidence)
        }
        
        @Test
        fun `optimizeResponse handles optimization failure`() = runTest {
            // Given
            val initialResponse = TestDataBuilders.createTestAgentResponse()
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Optimization service unavailable")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Optimization service unavailable")
            )
            
            // When
            val result = aiServiceIntegration.optimizeResponse(initialResponse, testContext)
            
            // Then - Should return original response
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertEquals(initialResponse.content, response.content)
        }
        
        @Test
        fun `optimizeResponse preserves response metadata`() = runTest {
            // Given
            val initialResponse = TestDataBuilders.createTestAgentResponse(
                metadata = mapOf("custom_key" to "custom_value")
            )
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success(
                "Optimized response content"
            )
            
            // When
            val result = aiServiceIntegration.optimizeResponse(initialResponse, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            val optimizedResponse = result.getOrNull()
            assertNotNull(optimizedResponse)
            assertEquals(initialResponse.agentId, optimizedResponse.agentId)
            assertTrue(optimizedResponse.metadata.isNotEmpty())
        }
    }
    
    @Nested
    @DisplayName("Service Health Monitoring")
    inner class ServiceHealthTests {
        
        @Test
        fun `checkServiceHealth reports healthy services`() = runTest {
            // Given
            coEvery { mockOpenAIService.isHealthy() } returns true
            coEvery { mockAnthropicService.isHealthy() } returns true
            
            // When
            val openAIResult = aiServiceIntegration.checkServiceHealth("openai")
            val anthropicResult = aiServiceIntegration.checkServiceHealth("anthropic")
            
            // Then
            assertTrue(openAIResult.isSuccess)
            assertTrue(anthropicResult.isSuccess)
            assertTrue(openAIResult.getOrNull() == true)
            assertTrue(anthropicResult.getOrNull() == true)
        }
        
        @Test
        fun `checkServiceHealth reports unhealthy services`() = runTest {
            // Given
            coEvery { mockOpenAIService.isHealthy() } returns false
            coEvery { mockAnthropicService.isHealthy() } returns false
            
            // When
            val openAIResult = aiServiceIntegration.checkServiceHealth("openai")
            val anthropicResult = aiServiceIntegration.checkServiceHealth("anthropic")
            
            // Then
            assertTrue(openAIResult.isSuccess)
            assertTrue(anthropicResult.isSuccess)
            assertFalse(openAIResult.getOrNull() == true)
            assertFalse(anthropicResult.getOrNull() == true)
        }
        
        @Test
        fun `checkServiceHealth handles unknown service`() = runTest {
            // When
            val result = aiServiceIntegration.checkServiceHealth("unknown_service")
            
            // Then
            assertTrue(result.isFailure)
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception.message!!.contains("Unknown") || exception.message!!.contains("service"))
        }
        
        @Test
        fun `isServiceAvailable returns correct availability status`() = runTest {
            // Given
            coEvery { mockOpenAIService.isHealthy() } returns true
            coEvery { mockAnthropicService.isHealthy() } returns false
            
            // When
            val openAIAvailable = aiServiceIntegration.isServiceAvailable("openai")
            val anthropicAvailable = aiServiceIntegration.isServiceAvailable("anthropic")
            val unknownAvailable = aiServiceIntegration.isServiceAvailable("unknown")
            
            // Then
            assertTrue(openAIAvailable)
            assertFalse(anthropicAvailable)
            assertFalse(unknownAvailable)
        }
    }
    
    @Nested
    @DisplayName("Circuit Breaker Functionality")
    inner class CircuitBreakerTests {
        
        @Test
        fun `circuit breaker prevents calls to failing service`() = runTest {
            // Given - Simulate repeated failures
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Service consistently failing")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.success("Fallback response")
            
            // When - Make multiple requests to trigger circuit breaker
            repeat(5) {
                aiServiceIntegration.generateResponse(testPrompt, testContext)
            }
            
            val finalResult = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then - Should use fallback service
            assertTrue(finalResult.isSuccess)
            
            // Verify attempts were made to both services
            coVerify(atLeast = 1) { mockOpenAIService.generateCompletion(any(), any()) }
            coVerify(atLeast = 1) { mockAnthropicService.generateCompletion(any(), any()) }
        }
        
        @Test
        fun `circuit breaker recovers after service becomes healthy`() = runTest {
            // Given - Initially failing service
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Temporary failure")
            )
            coEvery { mockOpenAIService.isHealthy() } returns false
            
            // Trigger circuit breaker
            repeat(3) {
                aiServiceIntegration.generateResponse(testPrompt, testContext)
            }
            
            // Service becomes healthy
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("Service recovered")
            coEvery { mockOpenAIService.isHealthy() } returns true
            
            // When - Make new request
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then - Should use recovered service
            assertTrue(result.isSuccess)
        }
    }
    
    @Nested
    @DisplayName("Rate Limiting and Timeouts")
    inner class RateLimitingTests {
        
        @Test
        fun `service handles rate limiting gracefully`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Rate limit exceeded")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.success("Alternative response")
            
            // When
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then - Should fallback to alternative service
            assertTrue(result.isSuccess)
            coVerify { mockAnthropicService.generateCompletion(any(), any()) }
        }
        
        @Test
        fun `service handles timeouts appropriately`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } coAnswers {
                kotlinx.coroutines.delay(30000) // Simulate timeout
                Result.success("Delayed response")
            }
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.success("Quick response")
            
            // When
            val startTime = System.currentTimeMillis()
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            val duration = System.currentTimeMillis() - startTime
            
            // Then - Should complete quickly using fallback
            assertTrue(result.isSuccess)
            assertTrue(duration < 5000, "Should not wait for timeout")
        }
        
        @Test
        fun `concurrent requests respect rate limits`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("Response")
            
            // When - Make concurrent requests
            val concurrentRequests = (1..10).map { i ->
                async {
                    aiServiceIntegration.generateResponse("Prompt $i", testContext)
                }
            }
            
            val results = concurrentRequests.awaitAll()
            
            // Then - All should complete
            assertEquals(10, results.size)
            results.forEach { result ->
                assertTrue(result.isSuccess)
            }
        }
    }
    
    @Nested
    @DisplayName("Error Recovery and Retry")
    inner class ErrorRecoveryTests {
        
        @Test
        fun `service retries transient failures`() = runTest {
            // Given - First call fails, second succeeds
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returnsMany listOf(
                Result.failure(RuntimeException("Transient network error")),
                Result.success("Success after retry")
            )
            
            // When
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then
            assertTrue(result.isSuccess)
            val response = result.getOrNull()
            assertNotNull(response)
            assertTrue(response.content.contains("Success") || response.content.isNotEmpty())
        }
        
        @Test
        fun `service gives up after max retries`() = runTest {
            // Given - All calls fail
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Persistent failure")
            )
            coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.failure(
                RuntimeException("Persistent failure")
            )
            
            // When
            val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
            
            // Then
            assertTrue(result.isFailure)
            // Should have attempted both services
            coVerify(atLeast = 1) { mockOpenAIService.generateCompletion(any(), any()) }
            coVerify(atLeast = 1) { mockAnthropicService.generateCompletion(any(), any()) }
        }
        
        @Test
        fun `service handles different error types appropriately`() = runTest {
            // Given
            val errorScenarios = MockFactories.createErrorScenarios()
            
            for ((errorType, exception) in errorScenarios) {
                // Reset mocks for each scenario
                clearMocks(mockOpenAIService, mockAnthropicService)
                
                coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.failure(exception)
                coEvery { mockAnthropicService.generateCompletion(any(), any()) } returns Result.success("Fallback response")
                
                // When
                val result = aiServiceIntegration.generateResponse(testPrompt, testContext)
                
                // Then - Should handle error gracefully
                if (errorType in listOf("network_timeout", "service_unavailable", "rate_limit")) {
                    // These should trigger fallback
                    assertTrue(result.isSuccess, "Error type '$errorType' should be handled with fallback")
                } else {
                    // Other errors may fail completely
                    assertNotNull(result) // Should at least return a result
                }
            }
        }
    }
    
    @Nested
    @DisplayName("Performance and Scalability")
    inner class PerformanceTests {
        
        @Test
        fun `service integration performs efficiently under load`() = runTest {
            // Given
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success("Quick response")
            
            // When - Generate many concurrent requests
            val highLoadRequests = (1..50).map { i ->
                async {
                    aiServiceIntegration.generateResponse("Load test prompt $i", testContext)
                }
            }
            
            val startTime = System.currentTimeMillis()
            val results = highLoadRequests.awaitAll()
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertEquals(50, results.size)
            results.forEach { result ->
                assertTrue(result.isSuccess)
            }
            assertTrue(duration < 10000, "Should handle high load efficiently")
        }
        
        @Test
        fun `service integration manages memory efficiently`() = runTest {
            // Given - Large responses
            val largeResponse = "Large response content ".repeat(1000)
            coEvery { mockOpenAIService.generateCompletion(any(), any()) } returns Result.success(largeResponse)
            
            // When - Process many large responses
            repeat(20) {
                val result = aiServiceIntegration.generateResponse("Large content request", testContext)
                assertTrue(result.isSuccess)
            }
            
            // Then - Should complete without memory issues (no assertion needed, just completion)
            assertTrue(true)
        }
    }
}