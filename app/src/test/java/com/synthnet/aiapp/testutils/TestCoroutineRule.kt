package com.synthnet.aiapp.testutils

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.rules.TestWatcher
import org.junit.runner.Description
import kotlin.coroutines.CoroutineContext

/**
 * JUnit rule that swaps the background executor used by the Architecture Components
 * with a different one that executes each task synchronously in tests.
 * 
 * This rule also provides a test dispatcher for controlled coroutine execution.
 */
@ExperimentalCoroutinesApi
class TestCoroutineRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    
    val testCoroutineScope = TestScope(testDispatcher)
    
    override fun starting(description: Description) {
        super.starting(description)
        // Set the main dispatcher to our test dispatcher
        Dispatchers.setMain(testDispatcher)
    }
    
    override fun finished(description: Description) {
        super.finished(description)
        // Clean up the test coroutines
        testCoroutineScope.cleanupTestCoroutines()
        // Reset the main dispatcher
        Dispatchers.resetMain()
    }
    
    /**
     * Runs a block of code using the test coroutine scope
     */
    fun runTest(block: suspend TestScope.() -> Unit) {
        testCoroutineScope.runTest(block)
    }
    
    /**
     * Advances time by the specified duration
     */
    fun advanceTimeBy(delayTimeMillis: Long) {
        testCoroutineScope.advanceTimeBy(delayTimeMillis)
    }
    
    /**
     * Advances until all scheduled coroutines complete
     */
    fun advanceUntilIdle() {
        testCoroutineScope.advanceUntilIdle()
    }
    
    /**
     * Gets the current virtual time
     */
    fun currentTime(): Long = testCoroutineScope.currentTime
}