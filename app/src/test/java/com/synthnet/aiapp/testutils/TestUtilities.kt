package com.synthnet.aiapp.testutils

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.rules.TestRule
import org.mockito.ArgumentCaptor
import org.mockito.Mockito
import org.mockito.kotlin.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.toList
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlin.time.Duration.Companion.seconds
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.test.assertNotNull
import kotlin.test.assertNull

/**
 * Comprehensive testing utilities for SynthNet AI testing framework.
 * Provides helper methods, extension functions, and testing rules.
 */
object TestUtilities {

    /**
     * Creates a test coroutine dispatcher for consistent testing
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    fun createTestDispatcher(): TestDispatcher = StandardTestDispatcher()

    /**
     * Creates a test scope with the given dispatcher
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    fun createTestScope(
        dispatcher: TestDispatcher = createTestDispatcher()
    ): TestScope = TestScope(dispatcher)

    /**
     * Rule for testing coroutines with main dispatcher replacement
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    class MainDispatcherRule(
        private val testDispatcher: TestDispatcher = StandardTestDispatcher()
    ) : TestRule {
        override fun apply(base: org.junit.runners.model.Statement, description: org.junit.runner.Description) = 
            object : org.junit.runners.model.Statement() {
                override fun evaluate() {
                    Dispatchers.setMain(testDispatcher)
                    try {
                        base.evaluate()
                    } finally {
                        Dispatchers.resetMain()
                    }
                }
            }
    }

    /**
     * Combined rule for Android Architecture Components and Coroutines
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    class AndroidTestRule : TestRule {
        private val instantTaskExecutorRule = InstantTaskExecutorRule()
        private val mainDispatcherRule = MainDispatcherRule()

        override fun apply(base: org.junit.runners.model.Statement, description: org.junit.runner.Description) =
            instantTaskExecutorRule.apply(
                mainDispatcherRule.apply(base, description),
                description
            )
    }

    /**
     * Assertion helpers for AI-specific testing
     */
    object Assertions {
        
        fun assertConfidenceInRange(actual: Double, expectedMin: Double = 0.0, expectedMax: Double = 1.0) {
            assertTrue(
                actual in expectedMin..expectedMax,
                "Confidence $actual should be between $expectedMin and $expectedMax"
            )
        }

        fun assertResponseTime(actual: Long, maxExpected: Long = 5000L) {
            assertTrue(
                actual <= maxExpected,
                "Response time $actual ms should be <= $maxExpected ms"
            )
        }

        fun assertAgentResponseValid(response: com.synthnet.aiapp.domain.models.AgentResponse?) {
            assertNotNull(response, "AgentResponse should not be null")
            response?.let {
                assertTrue(it.content.isNotBlank(), "Response content should not be blank")
                assertConfidenceInRange(it.confidence)
                assertNotNull(it.reasoning, "Reasoning should not be null")
                assertTrue(it.agentId.isNotBlank(), "Agent ID should not be blank")
            }
        }

        fun assertThoughtTreeValid(tree: com.synthnet.aiapp.domain.models.ThoughtTree?) {
            assertNotNull(tree, "ThoughtTree should not be null")
            tree?.let {
                assertNotNull(it.rootThought, "Root thought should not be null")
                assertTrue(it.branches.isNotEmpty(), "Tree should have at least one branch")
                assertTrue(it.maxDepth > 0, "Max depth should be positive")
                assertTrue(it.totalNodes > 0, "Total nodes should be positive")
            }
        }

        fun assertCollaborationValid(collaboration: com.synthnet.aiapp.domain.models.Collaboration?) {
            assertNotNull(collaboration, "Collaboration should not be null")
            collaboration?.let {
                assertTrue(it.participants.isNotEmpty(), "Collaboration should have participants")
                assertTrue(it.projectId.isNotBlank(), "Project ID should not be blank")
                assertNotNull(it.sharedContext, "Shared context should not be null")
            }
        }

        fun <T> assertListNotEmpty(list: List<T>?, message: String = "List should not be empty") {
            assertNotNull(list, "List should not be null")
            assertTrue(list!!.isNotEmpty(), message)
        }

        fun assertTimestampRecent(timestamp: Instant, toleranceSeconds: Long = 60) {
            val now = Clock.System.now()
            val diff = now.epochSeconds - timestamp.epochSeconds
            assertTrue(
                diff <= toleranceSeconds,
                "Timestamp should be within $toleranceSeconds seconds of now. Difference: $diff seconds"
            )
        }
    }

    /**
     * Mock creation helpers
     */
    object Mocks {
        
        inline fun <reified T : Any> createMock(): T = mock()
        
        inline fun <reified T : Any> createMockWithDefaults(): T = mock {
            on { toString() } doReturn "Mock<${T::class.simpleName}>"
        }

        fun <T> createSuccessfulFlow(value: T): Flow<T> = flowOf(value)
        
        fun <T> createEmptyFlow(): Flow<List<T>> = flowOf(emptyList())

        fun createMockAgentRepository(): com.synthnet.aiapp.domain.repository.AgentRepository = mock {
            on { getAgentsByProject(any()) } doReturn createSuccessfulFlow(TestDataFactory.createAgentList())
            on { updateAgentStatus(any(), any()) } doReturn Result.success(Unit)
        }

        fun createMockThoughtRepository(): com.synthnet.aiapp.domain.repository.ThoughtRepository = mock {
            on { getThoughtById(any()) } doReturn TestDataFactory.createThought()
            on { selectThought(any()) } doReturn Result.success(Unit)
        }

        fun createMockCollaborationRepository(): com.synthnet.aiapp.domain.repository.CollaborationRepository = mock {
            on { getCollaborationsByProject(any()) } doReturn createSuccessfulFlow(TestDataFactory.createCollaborationList())
        }

        fun createMockTreeOfThoughtEngine(): com.synthnet.aiapp.domain.ai.TreeOfThoughtEngine = mock {
            onBlocking { executeToTWorkflow(any(), any(), any(), any()) } doReturn TestDataFactory.createThoughtTree()
        }

        fun createMockRecursiveMetaPrompting(): com.synthnet.aiapp.domain.ai.RecursiveMetaPrompting = mock {
            onBlocking { optimizeResponse(any(), any()) } doAnswer { invocation ->
                invocation.getArgument<com.synthnet.aiapp.domain.models.AgentResponse>(0)
            }
        }

        fun createMockCollaborationManager(): com.synthnet.aiapp.domain.services.CollaborationManager = mock {
            onBlocking { startCollaboration(any(), any(), any(), any()) } doReturn TestDataFactory.createCollaboration()
        }

        fun createMockAntifragileSystem(): com.synthnet.aiapp.domain.services.AntifragileSystem = mock {
            onBlocking { executeWithFallback(any(), any()) } doAnswer { invocation ->
                val block = invocation.getArgument<suspend () -> Result<Any>>(1)
                block()
            }
        }
    }

    /**
     * Flow testing utilities
     */
    object FlowTesting {
        
        suspend fun <T> Flow<T>.collectFirst(): T = toList().first()
        
        suspend fun <T> Flow<T>.collectAll(): List<T> = toList()

        suspend fun <T> assertFlowEmits(flow: Flow<T>, expected: T) {
            val actual = flow.collectFirst()
            assertEquals(expected, actual)
        }

        suspend fun <T> assertFlowEmitsCount(flow: Flow<List<T>>, expectedCount: Int) {
            val actual = flow.collectFirst()
            assertEquals(expectedCount, actual.size)
        }
    }

    /**
     * Argument capture utilities
     */
    object ArgumentCapture {
        
        inline fun <reified T : Any> captureArgument(): ArgumentCaptor<T> = 
            ArgumentCaptor.forClass(T::class.java)

        inline fun <reified T : Any> verifyArgumentCaptured(
            mock: Any,
            methodCall: (Any) -> Unit,
            crossinline assertion: (T) -> Unit
        ) {
            val captor = captureArgument<T>()
            verify(mock).let(methodCall)
            assertion(captor.value)
        }
    }

    /**
     * Performance testing utilities
     */
    object Performance {
        
        suspend fun <T> measureExecutionTime(block: suspend () -> T): Pair<T, Long> {
            val startTime = System.currentTimeMillis()
            val result = block()
            val endTime = System.currentTimeMillis()
            return Pair(result, endTime - startTime)
        }

        suspend fun assertExecutionTimeUnder(
            maxTimeMs: Long,
            block: suspend () -> Unit
        ) {
            val (_, executionTime) = measureExecutionTime(block)
            assertTrue(
                executionTime <= maxTimeMs,
                "Execution took $executionTime ms, expected <= $maxTimeMs ms"
            )
        }

        fun createPerformanceThreshold(
            maxResponseTime: Long = 5000L,
            minSuccessRate: Double = 0.95,
            maxErrorRate: Double = 0.05
        ): PerformanceThreshold = PerformanceThreshold(
            maxResponseTime = maxResponseTime,
            minSuccessRate = minSuccessRate,
            maxErrorRate = maxErrorRate
        )
    }

    /**
     * Database testing utilities
     */
    object Database {
        
        fun createInMemoryDatabaseName(): String = "test_db_${System.currentTimeMillis()}"

        suspend fun <T> withDatabaseTransaction(
            database: androidx.room.RoomDatabase,
            block: suspend () -> T
        ): T {
            database.runInTransaction {
                // Transaction block
            }
            return block()
        }
    }

    /**
     * WebSocket testing utilities
     */
    object WebSocket {
        
        fun createMockWebSocketServer(port: Int = 8080): okhttp3.mockwebserver.MockWebServer {
            val server = okhttp3.mockwebserver.MockWebServer()
            server.start(port)
            return server
        }

        fun createWebSocketResponse(message: String): okhttp3.mockwebserver.MockResponse {
            return okhttp3.mockwebserver.MockResponse()
                .withWebSocketUpgrade(object : okhttp3.mockwebserver.WebSocketListener() {
                    override fun onOpen(webSocket: okhttp3.WebSocket, response: okhttp3.Response) {
                        webSocket.send(message)
                    }
                })
        }
    }

    /**
     * Retry utilities for flaky tests
     */
    object Retry {
        
        suspend fun <T> withRetry(
            maxAttempts: Int = 3,
            delayMs: Long = 100,
            block: suspend (attempt: Int) -> T
        ): T {
            var lastException: Exception? = null
            
            repeat(maxAttempts) { attempt ->
                try {
                    return block(attempt)
                } catch (e: Exception) {
                    lastException = e
                    if (attempt < maxAttempts - 1) {
                        kotlinx.coroutines.delay(delayMs)
                    }
                }
            }
            
            throw lastException ?: Exception("All retry attempts failed")
        }
    }

    /**
     * Conditional test execution
     */
    object Conditionals {
        
        fun skipIfCondition(condition: Boolean, reason: String = "Condition not met") {
            org.junit.Assume.assumeFalse(reason, condition)
        }

        fun runOnlyIfCondition(condition: Boolean, reason: String = "Condition not met") {
            org.junit.Assume.assumeTrue(reason, condition)
        }
    }

    /**
     * Test data validation
     */
    object Validation {
        
        fun validateTestData(data: Any): ValidationResult {
            return when (data) {
                is com.synthnet.aiapp.domain.models.Agent -> validateAgent(data)
                is com.synthnet.aiapp.domain.models.Thought -> validateThought(data)
                is com.synthnet.aiapp.domain.models.Collaboration -> validateCollaboration(data)
                is com.synthnet.aiapp.domain.models.AgentResponse -> validateAgentResponse(data)
                else -> ValidationResult(true, "Unknown data type")
            }
        }

        private fun validateAgent(agent: com.synthnet.aiapp.domain.models.Agent): ValidationResult {
            if (agent.id.isBlank()) return ValidationResult(false, "Agent ID is blank")
            if (agent.name.isBlank()) return ValidationResult(false, "Agent name is blank")
            if (agent.capabilities.isEmpty()) return ValidationResult(false, "Agent has no capabilities")
            return ValidationResult(true, "Valid agent")
        }

        private fun validateThought(thought: com.synthnet.aiapp.domain.models.Thought): ValidationResult {
            if (thought.id.isBlank()) return ValidationResult(false, "Thought ID is blank")
            if (thought.content.isBlank()) return ValidationResult(false, "Thought content is blank")
            if (thought.confidence !in 0.0..1.0) return ValidationResult(false, "Invalid confidence value")
            return ValidationResult(true, "Valid thought")
        }

        private fun validateCollaboration(collaboration: com.synthnet.aiapp.domain.models.Collaboration): ValidationResult {
            if (collaboration.id.isBlank()) return ValidationResult(false, "Collaboration ID is blank")
            if (collaboration.participants.isEmpty()) return ValidationResult(false, "No participants")
            if (collaboration.projectId.isBlank()) return ValidationResult(false, "Project ID is blank")
            return ValidationResult(true, "Valid collaboration")
        }

        private fun validateAgentResponse(response: com.synthnet.aiapp.domain.models.AgentResponse): ValidationResult {
            if (response.agentId.isBlank()) return ValidationResult(false, "Agent ID is blank")
            if (response.content.isBlank()) return ValidationResult(false, "Response content is blank")
            if (response.confidence !in 0.0..1.0) return ValidationResult(false, "Invalid confidence value")
            return ValidationResult(true, "Valid agent response")
        }
    }
}

/**
 * Data classes for testing utilities
 */
data class PerformanceThreshold(
    val maxResponseTime: Long,
    val minSuccessRate: Double,
    val maxErrorRate: Double
)

data class ValidationResult(
    val isValid: Boolean,
    val message: String
)

/**
 * Extension functions for testing
 */
suspend fun <T> kotlinx.coroutines.flow.Flow<T>.test(
    timeout: kotlin.time.Duration = 5.seconds,
    block: suspend kotlinx.coroutines.flow.FlowCollector<T>.() -> Unit
) {
    kotlinx.coroutines.withTimeout(timeout) {
        collect(block)
    }
}

fun <T> T.shouldBe(expected: T) {
    assertEquals(expected, this)
}

fun <T> T?.shouldNotBeNull(): T {
    assertNotNull(this)
    return this!!
}

fun <T> T?.shouldBeNull() {
    assertNull(this)
}

inline fun <reified T : Exception> shouldThrow(crossinline block: () -> Any): T {
    try {
        block()
        throw AssertionError("Expected exception of type ${T::class.simpleName} but no exception was thrown")
    } catch (e: Exception) {
        if (e is T) {
            return e
        } else {
            throw AssertionError("Expected exception of type ${T::class.simpleName} but got ${e::class.simpleName}: ${e.message}")
        }
    }
}