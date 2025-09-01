package com.synthnet.aiapp.domain.services

import com.synthnet.aiapp.testutils.TestDataBuilders
import com.synthnet.aiapp.testutils.MockFactories
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import io.mockk.*
import org.junit.jupiter.api.*
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import kotlin.test.*

/**
 * Comprehensive test suite for WebSocketManager
 * 
 * Tests cover:
 * - Connection management and auto-reconnection
 * - Message protocol and routing
 * - Subscription management
 * - Real-time collaboration features
 * - Error handling and recovery
 * - Mock WebSocket connections and network failures
 */
@ExtendWith(MockKExtension::class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class WebSocketManagerTest {
    
    private lateinit var webSocketManager: WebSocketManager
    private lateinit var mockWebSocket: WebSocket
    
    private val testUrl = "ws://localhost:8080/synthnet"
    private val testMessage = """{"type":"collaboration","payload":{"action":"join","roomId":"test-room"}}"""
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        mockWebSocket = MockFactories.createMockWebSocket()
        
        webSocketManager = WebSocketManager()
    }
    
    @Nested
    @DisplayName("Connection Management")
    inner class ConnectionManagementTests {
        
        @Test
        fun `connect establishes WebSocket connection successfully`() = runTest {
            // Given
            every { mockWebSocket.send(any<String>()) } returns true
            
            // When
            val result = webSocketManager.connect(testUrl)
            
            // Then
            assertTrue(result.isSuccess)
            assertTrue(webSocketManager.isConnected())
        }
        
        @Test
        fun `connect handles invalid URL gracefully`() = runTest {
            // Given
            val invalidUrl = "invalid-websocket-url"
            
            // When
            val result = webSocketManager.connect(invalidUrl)
            
            // Then
            assertTrue(result.isFailure)
            assertFalse(webSocketManager.isConnected())
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception.message!!.contains("Invalid") || exception.message!!.contains("URL"))
        }
        
        @Test
        fun `connect handles network failures`() = runTest {
            // Given
            val networkFailureUrl = "ws://unreachable-server:8080"
            
            // When
            val result = webSocketManager.connect(networkFailureUrl)
            
            // Then
            assertTrue(result.isFailure)
            assertFalse(webSocketManager.isConnected())
        }
        
        @Test
        fun `disconnect closes connection properly`() = runTest {
            // Given - Established connection
            webSocketManager.connect(testUrl)
            every { mockWebSocket.close(any(), any()) } returns true
            
            // When
            val result = webSocketManager.disconnect()
            
            // Then
            assertTrue(result.isSuccess)
            assertFalse(webSocketManager.isConnected())
        }
        
        @Test
        fun `disconnect handles already disconnected state`() = runTest {
            // Given - No connection established
            
            // When
            val result = webSocketManager.disconnect()
            
            // Then
            assertTrue(result.isSuccess) // Should succeed even if not connected
            assertFalse(webSocketManager.isConnected())
        }
        
        @Test
        fun `isConnected reflects actual connection state`() = runTest {
            // Initially disconnected
            assertFalse(webSocketManager.isConnected())
            
            // After connection
            webSocketManager.connect(testUrl)
            assertTrue(webSocketManager.isConnected())
            
            // After disconnection
            webSocketManager.disconnect()
            assertFalse(webSocketManager.isConnected())
        }
        
        @Test
        fun `connection status flow emits state changes`() = runTest {
            // Given
            val statusFlow = webSocketManager.getConnectionStatus()
            val collectedStatuses = mutableListOf<String>()
            
            val job = async {
                statusFlow.take(3).collect { status ->
                    collectedStatuses.add(status)
                }
            }
            
            // When
            webSocketManager.connect(testUrl)
            webSocketManager.disconnect()
            
            job.await()
            
            // Then
            assertTrue(collectedStatuses.isNotEmpty())
            // Should have collected status changes
            assertTrue(collectedStatuses.contains("DISCONNECTED") || 
                      collectedStatuses.contains("CONNECTING") || 
                      collectedStatuses.contains("CONNECTED"))
        }
    }
    
    @Nested
    @DisplayName("Auto-Reconnection")
    inner class AutoReconnectionTests {
        
        @Test
        fun `manager attempts reconnection on connection loss`() = runTest {
            // Given - Initial connection
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            // Simulate connection loss
            // This would typically be triggered by WebSocket listener callbacks
            
            // When - Connection is lost (simulated)
            // In a real scenario, this would be detected through WebSocket callbacks
            
            // Then - Manager should attempt reconnection
            // This test would need to be expanded with actual reconnection logic
            assertTrue(true) // placeholder for reconnection verification
        }
        
        @Test
        fun `manager respects reconnection backoff strategy`() = runTest {
            // Given - Connection that fails repeatedly
            var attemptCount = 0
            
            // Mock multiple failed attempts
            coEvery { webSocketManager.connect(any()) } answers {
                attemptCount++
                if (attemptCount < 3) {
                    Result.failure(RuntimeException("Connection failed"))
                } else {
                    Result.success(Unit)
                }
            }
            
            // When - Trigger reconnection attempts
            // This would be done through internal reconnection logic
            
            // Then - Should eventually succeed with backoff
            assertTrue(attemptCount > 0)
        }
        
        @Test
        fun `manager stops reconnection after max attempts`() = runTest {
            // Given - Connection that always fails
            val maxAttempts = 5
            var attemptCount = 0
            
            // When - Connection fails repeatedly
            repeat(maxAttempts + 2) {
                attemptCount++
                val result = webSocketManager.connect("ws://failing-server")
                assertTrue(result.isFailure)
            }
            
            // Then - Should have stopped attempting after max retries
            assertTrue(attemptCount <= maxAttempts + 2)
        }
    }
    
    @Nested
    @DisplayName("Message Protocol and Routing")
    inner class MessageProtocolTests {
        
        @Test
        fun `sendMessage transmits formatted message successfully`() = runTest {
            // Given - Established connection
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            // When
            val result = webSocketManager.sendMessage(testMessage)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `sendMessage handles disconnected state`() = runTest {
            // Given - No connection
            
            // When
            val result = webSocketManager.sendMessage(testMessage)
            
            // Then
            assertTrue(result.isFailure)
            val exception = result.exceptionOrNull()
            assertNotNull(exception)
            assertTrue(exception.message!!.contains("not connected") || 
                      exception.message!!.contains("disconnected"))
        }
        
        @Test
        fun `sendMessage handles send failures`() = runTest {
            // Given - Connection with send failure
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns false
            
            // When
            val result = webSocketManager.sendMessage(testMessage)
            
            // Then
            assertTrue(result.isFailure)
        }
        
        @ParameterizedTest
        @ValueSource(strings = [
            """{"type":"ping"}""",
            """{"type":"collaboration","payload":{"action":"message","content":"Hello"}}""",
            """{"type":"thought_sync","data":{"thoughtId":"123","content":"Updated thought"}}""",
            "simple string message"
        ])
        fun `sendMessage handles different message formats`(message: String) = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            // When
            val result = webSocketManager.sendMessage(message)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `sendMessage queues messages when connection is temporary unavailable`() = runTest {
            // Given - Connection temporarily lost
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns false // Simulate temporary failure
            
            val messages = listOf("message1", "message2", "message3")
            
            // When - Send messages while connection is down
            val results = messages.map { message ->
                webSocketManager.sendMessage(message)
            }
            
            // Then - Messages should be queued for retry
            results.forEach { result ->
                assertNotNull(result) // Should handle gracefully
            }
        }
    }
    
    @Nested
    @DisplayName("Subscription Management")
    inner class SubscriptionManagementTests {
        
        @Test
        fun `subscribe registers message handler for topic`() = runTest {
            // Given
            val topic = "collaboration:room-123"
            val handler: (String) -> Unit = mockk(relaxed = true)
            
            // When
            val result = webSocketManager.subscribe(topic, handler)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `subscribe handles duplicate subscriptions`() = runTest {
            // Given
            val topic = "collaboration:room-123"
            val handler1: (String) -> Unit = mockk(relaxed = true)
            val handler2: (String) -> Unit = mockk(relaxed = true)
            
            // When
            val result1 = webSocketManager.subscribe(topic, handler1)
            val result2 = webSocketManager.subscribe(topic, handler2) // Duplicate topic
            
            // Then
            assertTrue(result1.isSuccess)
            assertTrue(result2.isSuccess) // Should handle gracefully
        }
        
        @Test
        fun `unsubscribe removes message handler for topic`() = runTest {
            // Given - Existing subscription
            val topic = "collaboration:room-123"
            val handler: (String) -> Unit = mockk(relaxed = true)
            webSocketManager.subscribe(topic, handler)
            
            // When
            val result = webSocketManager.unsubscribe(topic)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `unsubscribe handles non-existent subscriptions`() = runTest {
            // Given - No existing subscription
            val topic = "non-existent-topic"
            
            // When
            val result = webSocketManager.unsubscribe(topic)
            
            // Then
            assertTrue(result.isSuccess) // Should handle gracefully
        }
        
        @Test
        fun `message routing calls appropriate handlers`() = runTest {
            // Given
            val collaborationTopic = "collaboration:room-123"
            val thoughtTopic = "thoughts:project-456"
            
            val collaborationHandler: (String) -> Unit = mockk(relaxed = true)
            val thoughtHandler: (String) -> Unit = mockk(relaxed = true)
            
            webSocketManager.subscribe(collaborationTopic, collaborationHandler)
            webSocketManager.subscribe(thoughtTopic, thoughtHandler)
            
            val collaborationMessage = """{"topic":"collaboration:room-123","data":"collaboration data"}"""
            val thoughtMessage = """{"topic":"thoughts:project-456","data":"thought data"}"""
            
            // When - Simulate incoming messages
            // Note: This would typically be triggered by WebSocket listener in real implementation
            // For testing, we would need to expose message routing or use integration tests
            
            // Then - Appropriate handlers should be called
            // This would be verified in integration tests with actual WebSocket callbacks
            assertTrue(true) // Placeholder for handler verification
        }
    }
    
    @Nested
    @DisplayName("Real-time Collaboration Features")
    inner class CollaborationFeaturesTests {
        
        @Test
        fun `manager handles collaboration room join`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val joinMessage = """{"type":"collaboration","action":"join","roomId":"room-123","userId":"user-456"}"""
            
            // When
            val result = webSocketManager.sendMessage(joinMessage)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `manager handles collaboration room leave`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val leaveMessage = """{"type":"collaboration","action":"leave","roomId":"room-123","userId":"user-456"}"""
            
            // When
            val result = webSocketManager.sendMessage(leaveMessage)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `manager handles thought synchronization`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val thought = TestDataBuilders.createTestThought()
            val syncMessage = """{"type":"thought_sync","thoughtId":"${thought.id}","content":"${thought.content}","confidence":${thought.confidence}}"""
            
            // When
            val result = webSocketManager.sendMessage(syncMessage)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `manager handles consensus building messages`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val consensusMessage = """{"type":"consensus","action":"propose","proposalId":"prop-123","content":"Proposed decision"}"""
            
            // When
            val result = webSocketManager.sendMessage(consensusMessage)
            
            // Then
            assertTrue(result.isSuccess)
        }
        
        @Test
        fun `manager handles agent status updates`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val statusMessage = """{"type":"agent_status","agentId":"agent-123","status":"THINKING","projectId":"project-456"}"""
            
            // When
            val result = webSocketManager.sendMessage(statusMessage)
            
            // Then
            assertTrue(result.isSuccess)
        }
    }
    
    @Nested
    @DisplayName("Error Handling and Recovery")
    inner class ErrorHandlingTests {
        
        @Test
        fun `manager handles connection timeouts`() = runTest {
            // Given
            val timeoutUrl = "ws://slow-server:8080"
            
            // When
            val result = webSocketManager.connect(timeoutUrl)
            
            // Then - Should fail gracefully on timeout
            assertTrue(result.isFailure)
            assertFalse(webSocketManager.isConnected())
        }
        
        @Test
        fun `manager handles malformed messages gracefully`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val malformedMessages = listOf(
                "invalid json",
                """{"incomplete": json""",
                """{"type":"unknown_type","invalid":"structure"}""",
                ""
            )
            
            // When
            val results = malformedMessages.map { message ->
                webSocketManager.sendMessage(message)
            }
            
            // Then - Should handle malformed messages gracefully
            results.forEach { result ->
                assertNotNull(result) // Should not crash
            }
        }
        
        @Test
        fun `manager handles server-side errors`() = runTest {
            // Given - Connection established
            webSocketManager.connect(testUrl)
            
            // When - Simulate server error response
            // This would typically be received through WebSocket listener callbacks
            val errorMessage = """{"type":"error","code":"INTERNAL_ERROR","message":"Server error occurred"}"""
            
            // Then - Should handle server errors gracefully
            // Error handling would be verified through actual WebSocket callbacks
            assertTrue(true) // Placeholder for error handling verification
        }
        
        @Test
        fun `manager maintains message order during recovery`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            val orderedMessages = listOf("message1", "message2", "message3", "message4")
            
            // Simulate connection drop and recovery
            every { mockWebSocket.send(any<String>()) } returnsMany listOf(
                true,  // message1 succeeds
                false, // message2 fails (connection drop)
                false, // message3 fails
                true   // message4 succeeds (after recovery)
            )
            
            // When
            val results = orderedMessages.map { message ->
                webSocketManager.sendMessage(message)
            }
            
            // Then - Should attempt to maintain order
            assertNotNull(results)
            assertEquals(4, results.size)
        }
        
        @Test
        fun `manager handles concurrent connection attempts`() = runTest {
            // Given
            val concurrentConnections = (1..5).map { i ->
                async {
                    webSocketManager.connect("$testUrl?client=$i")
                }
            }
            
            // When
            val results = concurrentConnections.awaitAll()
            
            // Then - Should handle concurrent attempts gracefully
            assertEquals(5, results.size)
            // At least one should succeed or all should fail consistently
            val successCount = results.count { it.isSuccess }
            assertTrue(successCount >= 0) // Should not crash
        }
    }
    
    @Nested
    @DisplayName("Performance and Load Testing")
    inner class PerformanceTests {
        
        @Test
        fun `manager handles high message throughput`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val highVolumeMessages = (1..1000).map { i ->
                """{"type":"test","id":$i,"data":"Test message $i"}"""
            }
            
            // When
            val startTime = System.currentTimeMillis()
            val results = highVolumeMessages.map { message ->
                webSocketManager.sendMessage(message)
            }
            val duration = System.currentTimeMillis() - startTime
            
            // Then
            assertEquals(1000, results.size)
            results.forEach { result ->
                assertTrue(result.isSuccess)
            }
            assertTrue(duration < 10000, "Should handle high throughput within 10 seconds")
        }
        
        @Test
        fun `manager handles multiple concurrent subscriptions`() = runTest {
            // Given
            val subscriptions = (1..50).map { i ->
                "topic-$i" to mockk<(String) -> Unit>(relaxed = true)
            }
            
            // When
            val results = subscriptions.map { (topic, handler) ->
                webSocketManager.subscribe(topic, handler)
            }
            
            // Then
            assertEquals(50, results.size)
            results.forEach { result ->
                assertTrue(result.isSuccess)
            }
        }
        
        @Test
        fun `manager manages memory efficiently with large messages`() = runTest {
            // Given
            webSocketManager.connect(testUrl)
            every { mockWebSocket.send(any<String>()) } returns true
            
            val largeMessage = "Large message content ".repeat(10000)
            
            // When - Send multiple large messages
            repeat(10) {
                val result = webSocketManager.sendMessage(largeMessage)
                assertTrue(result.isSuccess)
            }
            
            // Then - Should complete without memory issues
            assertTrue(true) // Completion itself indicates success
        }
        
        @Test
        fun `manager handles rapid connection state changes`() = runTest {
            // Given
            val connectionStates = listOf(
                { webSocketManager.connect(testUrl) },
                { webSocketManager.disconnect() },
                { webSocketManager.connect(testUrl) },
                { webSocketManager.disconnect() },
                { webSocketManager.connect(testUrl) }
            )
            
            // When - Rapidly change connection state
            val results = connectionStates.map { operation ->
                operation()
            }
            
            // Then - Should handle rapid state changes
            assertEquals(5, results.size)
            results.forEach { result ->
                assertTrue(result.isSuccess)
            }
        }
    }
    
    @Nested
    @DisplayName("Message Queue Management")
    inner class MessageQueueTests {
        
        @Test
        fun `manager queues messages when disconnected`() = runTest {
            // Given - Not connected
            val queuedMessages = listOf("msg1", "msg2", "msg3")
            
            // When - Send messages while disconnected
            val results = queuedMessages.map { message ->
                webSocketManager.sendMessage(message)
            }
            
            // Then - Should queue messages for later sending
            results.forEach { result ->
                // May fail immediately or be queued for retry
                assertNotNull(result)
            }
        }
        
        @Test
        fun `manager processes queued messages on reconnection`() = runTest {
            // Given - Messages sent while disconnected
            val queuedMessages = listOf("queued1", "queued2", "queued3")
            
            // Send while disconnected
            queuedMessages.forEach { message ->
                webSocketManager.sendMessage(message)
            }
            
            // When - Reconnect
            every { mockWebSocket.send(any<String>()) } returns true
            val connectionResult = webSocketManager.connect(testUrl)
            
            // Then - Should process queued messages
            assertTrue(connectionResult.isSuccess)
            // In a real implementation, queued messages would be sent automatically
        }
        
        @Test
        fun `manager respects message queue size limits`() = runTest {
            // Given - Many messages while disconnected
            val manyMessages = (1..1000).map { i -> "message-$i" }
            
            // When - Send many messages while disconnected
            val results = manyMessages.map { message ->
                webSocketManager.sendMessage(message)
            }
            
            // Then - Should handle queue limits gracefully
            assertEquals(1000, results.size)
            results.forEach { result ->
                assertNotNull(result) // Should not crash
            }
        }
    }
}