package com.synthnet.aiapp.domain.services

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.decodeFromString
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WebSocketManager @Inject constructor() {
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val json = Json { ignoreUnknownKeys = true }
    
    // Connection state management
    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()
    
    private val _messages = MutableStateFlow<List<CollaborationMessage>>(emptyList())
    val messages: StateFlow<List<CollaborationMessage>> = _messages.asStateFlow()
    
    private val _connectionHealth = MutableStateFlow(ConnectionHealth())
    val connectionHealth: StateFlow<ConnectionHealth> = _connectionHealth.asStateFlow()
    
    // WebSocket client and session management
    private var webSocketClient: WebSocketClient? = null
    private val activeSessions = ConcurrentHashMap<String, CollaborationSession>()
    private val messageQueue = mutableListOf<QueuedMessage>()
    private val subscriptions = ConcurrentHashMap<String, MutableSet<MessageSubscription>>()
    
    // Connection management
    private val isReconnecting = AtomicBoolean(false)
    private val reconnectAttempts = AtomicInteger(0)
    private var heartbeatJob: Job? = null
    private var reconnectJob: Job? = null
    
    // Configuration
    private val maxReconnectAttempts = 5
    private val baseReconnectDelay = 1000L
    private val maxReconnectDelay = 30000L
    private val heartbeatInterval = 30000L
    private val messageTimeout = 10000L
    
    suspend fun createSession(collaborationId: String, participants: List<String>): Result<CollaborationSession> {
        return try {
            val session = CollaborationSession(
                id = collaborationId,
                participants = participants.toMutableSet(),
                isActive = true,
                createdAt = kotlinx.datetime.Clock.System.now(),
                lastActivity = kotlinx.datetime.Clock.System.now()
            )
            
            activeSessions[collaborationId] = session
            
            // Ensure connection is established
            if (_connectionState.value != ConnectionState.CONNECTED) {
                connectToWebSocket()
            }
            
            // Send session creation notification
            val createMessage = SessionManagementMessage(
                id = generateMessageId(),
                sessionId = collaborationId,
                action = SessionAction.CREATE,
                participants = participants,
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            sendMessage(createMessage)
            
            Result.success(session)
        } catch (e: Exception) {
            Result.failure(WebSocketException("Failed to create session: ${e.message}", e))
        }
    }
    
    suspend fun joinSession(collaborationId: String, agentId: String): Result<Unit> {
        return try {
            val session = activeSessions[collaborationId]
                ?: return Result.failure(SessionNotFoundException("Session $collaborationId not found"))
            
            session.participants.add(agentId)
            session.lastActivity = kotlinx.datetime.Clock.System.now()
            
            val joinMessage = ParticipantMessage(
                id = generateMessageId(),
                agentId = agentId,
                action = ParticipantAction.JOINED,
                sessionId = collaborationId,
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            broadcast(collaborationId, joinMessage)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(WebSocketException("Failed to join session: ${e.message}", e))
        }
    }
    
    suspend fun leaveSession(collaborationId: String, agentId: String): Result<Unit> {
        return try {
            val session = activeSessions[collaborationId]
                ?: return Result.failure(SessionNotFoundException("Session $collaborationId not found"))
            
            session.participants.remove(agentId)
            session.lastActivity = kotlinx.datetime.Clock.System.now()
            
            val leaveMessage = ParticipantMessage(
                id = generateMessageId(),
                agentId = agentId,
                action = ParticipantAction.LEFT,
                sessionId = collaborationId,
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            broadcast(collaborationId, leaveMessage)
            
            // Auto-close session if no participants left
            if (session.participants.isEmpty()) {
                closeSession(collaborationId)
            }
            
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(WebSocketException("Failed to leave session: ${e.message}", e))
        }
    }
    
    suspend fun broadcast(collaborationId: String, message: CollaborationMessage): Result<Unit> {
        return try {
            val session = activeSessions[collaborationId]
                ?: return Result.failure(SessionNotFoundException("Session $collaborationId not found"))
            
            session.lastActivity = kotlinx.datetime.Clock.System.now()
            
            val websocketMessage = WebSocketMessage(
                type = MessageType.BROADCAST,
                collaborationId = collaborationId,
                payload = json.encodeToString(message),
                messageId = generateMessageId(),
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            if (_connectionState.value == ConnectionState.CONNECTED) {
                sendMessage(websocketMessage)
            } else {
                queueMessage(websocketMessage)
            }
            
            // Add to local messages
            _messages.value = _messages.value + message
            
            // Notify subscribers
            notifySubscribers(message)
            
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(WebSocketException("Failed to broadcast message: ${e.message}", e))
        }
    }
    
    suspend fun closeSession(collaborationId: String): Result<Unit> {
        return try {
            val session = activeSessions.remove(collaborationId)
                ?: return Result.failure(SessionNotFoundException("Session $collaborationId not found"))
            
            // Send session close notification
            val closeMessage = SessionManagementMessage(
                id = generateMessageId(),
                sessionId = collaborationId,
                action = SessionAction.CLOSE,
                participants = session.participants.toList(),
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            sendMessage(closeMessage)
            
            // Clean up subscriptions
            subscriptions.remove(collaborationId)
            
            // Disconnect if no active sessions
            if (activeSessions.isEmpty()) {
                disconnectFromWebSocket()
            }
            
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(WebSocketException("Failed to close session: ${e.message}", e))
        }
    }
    
    private fun connectToWebSocket() {
        if (_connectionState.value == ConnectionState.CONNECTED || isReconnecting.get()) return
        
        serviceScope.launch {
            try {
                _connectionState.value = ConnectionState.CONNECTING
                
                val uri = URI("wss://synthnet-api.example.com/ws") // Replace with actual WebSocket URL
                
                webSocketClient = object : WebSocketClient(uri) {
                    override fun onOpen(handshake: ServerHandshake?) {
                        serviceScope.launch {
                            _connectionState.value = ConnectionState.CONNECTED
                            reconnectAttempts.set(0)
                            isReconnecting.set(false)
                            
                            updateConnectionHealth { 
                                it.copy(
                                    isConnected = true,
                                    lastConnectedAt = kotlinx.datetime.Clock.System.now(),
                                    connectionAttempts = 0,
                                    lastError = null
                                )
                            }
                            
                            // Send queued messages
                            flushMessageQueue()
                            
                            // Start heartbeat
                            startHeartbeat()
                        }
                    }
                    
                    override fun onMessage(message: String?) {
                        serviceScope.launch {
                            message?.let { handleIncomingMessage(it) }
                        }
                    }
                    
                    override fun onClose(code: Int, reason: String?, remote: Boolean) {
                        serviceScope.launch {
                            _connectionState.value = ConnectionState.DISCONNECTED
                            
                            updateConnectionHealth {
                                it.copy(
                                    isConnected = false,
                                    lastDisconnectedAt = kotlinx.datetime.Clock.System.now(),
                                    lastError = reason
                                )
                            }
                            
                            stopHeartbeat()
                            
                            // Auto-reconnect if not intentional disconnect
                            if (activeSessions.isNotEmpty() && !isReconnecting.get()) {
                                attemptReconnect()
                            }
                        }
                    }
                    
                    override fun onError(ex: Exception?) {
                        serviceScope.launch {
                            _connectionState.value = ConnectionState.ERROR
                            
                            updateConnectionHealth {
                                it.copy(
                                    isConnected = false,
                                    lastError = ex?.message ?: "Unknown error",
                                    errorCount = it.errorCount + 1
                                )
                            }
                            
                            stopHeartbeat()
                            
                            // Auto-reconnect on error
                            if (activeSessions.isNotEmpty() && !isReconnecting.get()) {
                                attemptReconnect()
                            }
                        }
                    }
                }
                
                webSocketClient?.connect()
                
            } catch (e: Exception) {
                _connectionState.value = ConnectionState.ERROR
                
                updateConnectionHealth {
                    it.copy(
                        isConnected = false,
                        lastError = e.message ?: "Connection failed",
                        errorCount = it.errorCount + 1
                    )
                }
            }
        }
    }
    
    private fun disconnectFromWebSocket() {
        serviceScope.launch {
            stopHeartbeat()
            reconnectJob?.cancel()
            isReconnecting.set(false)
            
            webSocketClient?.close()
            webSocketClient = null
            _connectionState.value = ConnectionState.DISCONNECTED
            
            updateConnectionHealth {
                it.copy(
                    isConnected = false,
                    lastDisconnectedAt = kotlinx.datetime.Clock.System.now()
                )
            }
        }
    }
    
    private suspend fun sendMessage(message: Any) {
        try {
            val jsonMessage = json.encodeToString(message)
            
            if (_connectionState.value == ConnectionState.CONNECTED) {
                webSocketClient?.send(jsonMessage)
                
                updateConnectionHealth {
                    it.copy(
                        messagesSent = it.messagesSent + 1,
                        lastSentAt = kotlinx.datetime.Clock.System.now()
                    )
                }
            } else {
                // Queue message if not connected
                if (message is WebSocketMessage) {
                    queueMessage(message)
                }
            }
        } catch (e: Exception) {
            updateConnectionHealth {
                it.copy(
                    lastError = "Send error: ${e.message}",
                    sendErrors = it.sendErrors + 1
                )
            }
        }
    }
    
    private suspend fun queueMessage(message: WebSocketMessage) {
        messageQueue.add(
            QueuedMessage(
                message = message,
                queuedAt = kotlinx.datetime.Clock.System.now(),
                attempts = 0
            )
        )
        
        // Limit queue size
        while (messageQueue.size > 100) {
            messageQueue.removeAt(0)
        }
    }
    
    private suspend fun flushMessageQueue() {
        val iterator = messageQueue.iterator()
        while (iterator.hasNext()) {
            val queuedMessage = iterator.next()
            try {
                sendMessage(queuedMessage.message)
                iterator.remove()
            } catch (e: Exception) {
                queuedMessage.attempts++
                if (queuedMessage.attempts > 3) {
                    iterator.remove() // Give up after 3 attempts
                }
            }
        }
    }
    
    private suspend fun handleIncomingMessage(message: String) {
        try {
            val websocketMessage = json.decodeFromString<WebSocketMessage>(message)
            
            updateConnectionHealth {
                it.copy(
                    lastMessageAt = kotlinx.datetime.Clock.System.now(),
                    messagesReceived = it.messagesReceived + 1
                )
            }
            
            when (websocketMessage.type) {
                MessageType.BROADCAST -> {
                    handleBroadcastMessage(websocketMessage)
                }
                MessageType.DIRECT -> {
                    handleDirectMessage(websocketMessage)
                }
                MessageType.SYSTEM -> {
                    handleSystemMessage(websocketMessage)
                }
                MessageType.HEARTBEAT -> {
                    handleHeartbeatMessage(websocketMessage)
                }
                MessageType.ACK -> {
                    handleAcknowledgmentMessage(websocketMessage)
                }
            }
        } catch (e: Exception) {
            updateConnectionHealth {
                it.copy(
                    lastError = "Message parsing error: ${e.message}",
                    parseErrors = it.parseErrors + 1
                )
            }
        }
    }
    
    private suspend fun handleBroadcastMessage(websocketMessage: WebSocketMessage) {
        try {
            // Determine the message type from payload structure
            val collaborationMessage = parseCollaborationMessage(websocketMessage.payload)
            
            // Update local message store
            _messages.value = _messages.value + collaborationMessage
            
            // Notify subscribers
            notifySubscribers(collaborationMessage)
            
            // Update session activity
            activeSessions[websocketMessage.collaborationId]?.let { session ->
                session.lastActivity = kotlinx.datetime.Clock.System.now()
            }
            
        } catch (e: Exception) {
            updateConnectionHealth {
                it.copy(lastError = "Broadcast handling error: ${e.message}")
            }
        }
    }
    
    private suspend fun handleDirectMessage(websocketMessage: WebSocketMessage) {
        // Handle direct messages to specific agents
        try {
            val directMessage = json.decodeFromString<DirectMessage>(websocketMessage.payload)
            // Process direct message
        } catch (e: Exception) {
            updateConnectionHealth {
                it.copy(lastError = "Direct message handling error: ${e.message}")
            }
        }
    }
    
    private suspend fun handleSystemMessage(websocketMessage: WebSocketMessage) {
        // Handle system messages (session events, notifications, etc.)
        try {
            val systemMessage = json.decodeFromString<SystemMessage>(websocketMessage.payload)
            
            when (systemMessage.type) {
                SystemMessageType.SESSION_CREATED -> {
                    // Handle session creation confirmation
                }
                SystemMessageType.PARTICIPANT_JOINED -> {
                    // Handle participant join notification
                }
                SystemMessageType.CONNECTION_STATUS -> {
                    // Handle connection status updates
                }
            }
        } catch (e: Exception) {
            updateConnectionHealth {
                it.copy(lastError = "System message handling error: ${e.message}")
            }
        }
    }
    
    private suspend fun handleHeartbeatMessage(websocketMessage: WebSocketMessage) {
        // Respond to heartbeat
        val heartbeatResponse = WebSocketMessage(
            type = MessageType.HEARTBEAT_RESPONSE,
            collaborationId = "",
            payload = "{\"status\":\"alive\",\"timestamp\":\"${kotlinx.datetime.Clock.System.now()}\"}",
            messageId = generateMessageId(),
            timestamp = kotlinx.datetime.Clock.System.now()
        )
        
        sendMessage(heartbeatResponse)
        
        updateConnectionHealth {
            it.copy(
                lastHeartbeatAt = kotlinx.datetime.Clock.System.now(),
                heartbeatCount = it.heartbeatCount + 1
            )
        }
    }
    
    private suspend fun handleAcknowledgmentMessage(websocketMessage: WebSocketMessage) {
        // Handle message acknowledgments
        val ackData = json.decodeFromString<AcknowledgmentData>(websocketMessage.payload)
        // Remove from pending messages, update delivery status, etc.
    }
    
    // Additional utility methods and lifecycle management
    private suspend fun attemptReconnect() {
        if (isReconnecting.compareAndSet(false, true)) {
            reconnectJob?.cancel()
            reconnectJob = serviceScope.launch {
                val attempts = reconnectAttempts.incrementAndGet()
                
                if (attempts <= maxReconnectAttempts) {
                    val delay = (baseReconnectDelay * (1 shl attempts)).coerceAtMost(maxReconnectDelay)
                    
                    updateConnectionHealth {
                        it.copy(
                            connectionAttempts = attempts,
                            lastError = "Reconnecting... attempt $attempts"
                        )
                    }
                    
                    delay(delay)
                    connectToWebSocket()
                } else {
                    isReconnecting.set(false)
                    updateConnectionHealth {
                        it.copy(
                            lastError = "Max reconnection attempts exceeded"
                        )
                    }
                }
            }
        }
    }
    
    private fun startHeartbeat() {
        stopHeartbeat()
        heartbeatJob = serviceScope.launch {
            while (_connectionState.value == ConnectionState.CONNECTED) {
                try {
                    val heartbeat = WebSocketMessage(
                        type = MessageType.HEARTBEAT,
                        collaborationId = "",
                        payload = "{\"ping\":\"${System.currentTimeMillis()}\"}",
                        messageId = generateMessageId(),
                        timestamp = kotlinx.datetime.Clock.System.now()
                    )
                    
                    sendMessage(heartbeat)
                    delay(heartbeatInterval)
                } catch (e: Exception) {
                    break
                }
            }
        }
    }
    
    private fun stopHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = null
    }
    
    private suspend fun updateConnectionHealth(update: (ConnectionHealth) -> ConnectionHealth) {
        _connectionHealth.value = update(_connectionHealth.value)
    }
    
    private fun generateMessageId(): String {
        return "msg_${System.currentTimeMillis()}_${(Math.random() * 10000).toInt()}"
    }
    
    private suspend fun parseCollaborationMessage(payload: String): CollaborationMessage {
        // Try to determine message type and parse accordingly
        return try {
            // First try parsing as ParticipantMessage
            json.decodeFromString<ParticipantMessage>(payload)
        } catch (e: Exception) {
            try {
                // Then try SessionManagementMessage
                json.decodeFromString<SessionManagementMessage>(payload)
            } catch (e: Exception) {
                // Create a generic message if parsing fails
                object : CollaborationMessage() {
                    override val id = generateMessageId()
                    override val timestamp = kotlinx.datetime.Clock.System.now()
                }
            }
        }
    }
    
    private suspend fun notifySubscribers(message: CollaborationMessage) {
        subscriptions.values.flatten().forEach { subscription ->
            try {
                if (subscription.messageTypes.isEmpty() || 
                    subscription.messageTypes.contains(message::class.simpleName)) {
                    subscription.callback(message)
                }
            } catch (e: Exception) {
                // Log subscription callback error but don't fail
            }
        }
    }
    
    // Public API methods
    suspend fun subscribe(
        sessionId: String,
        messageTypes: Set<String> = emptySet(),
        callback: suspend (CollaborationMessage) -> Unit
    ): String {
        val subscriptionId = generateMessageId()
        val subscription = MessageSubscription(subscriptionId, messageTypes, callback)
        
        subscriptions.getOrPut(sessionId) { mutableSetOf() }.add(subscription)
        
        return subscriptionId
    }
    
    fun unsubscribe(sessionId: String, subscriptionId: String) {
        subscriptions[sessionId]?.removeAll { it.id == subscriptionId }
    }
    
    fun getActiveSessionIds(): List<String> = activeSessions.keys.toList()
    
    fun getSessionParticipants(collaborationId: String): Set<String> {
        return activeSessions[collaborationId]?.participants ?: emptySet()
    }
    
    fun getSession(collaborationId: String): CollaborationSession? {
        return activeSessions[collaborationId]
    }
    
    suspend fun sendDirectMessage(
        fromAgentId: String,
        toAgentId: String,
        content: String
    ): Result<Unit> {
        return try {
            val directMessage = DirectMessage(
                id = generateMessageId(),
                fromAgentId = fromAgentId,
                toAgentId = toAgentId,
                content = content,
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            val websocketMessage = WebSocketMessage(
                type = MessageType.DIRECT,
                collaborationId = "",
                payload = json.encodeToString(directMessage),
                messageId = generateMessageId(),
                timestamp = kotlinx.datetime.Clock.System.now()
            )
            
            sendMessage(websocketMessage)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(WebSocketException("Failed to send direct message: ${e.message}", e))
        }
    }
    
    fun cleanup() {
        serviceScope.cancel()
        stopHeartbeat()
        reconnectJob?.cancel()
        disconnectFromWebSocket()
        activeSessions.clear()
        subscriptions.clear()
        messageQueue.clear()
    }
}

enum class ConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    ERROR
}

data class CollaborationSession(
    val id: String,
    val participants: MutableSet<String>,
    var isActive: Boolean,
    val createdAt: kotlinx.datetime.Instant,
    var lastActivity: kotlinx.datetime.Instant
)

@Serializable
data class WebSocketMessage(
    val type: MessageType,
    val collaborationId: String,
    val payload: String,
    val messageId: String,
    val timestamp: kotlinx.datetime.Instant
)

enum class MessageType {
    BROADCAST,
    DIRECT,
    SYSTEM,
    HEARTBEAT,
    HEARTBEAT_RESPONSE,
    ACK
}

@Serializable
data class ParticipantMessage(
    override val id: String,
    val agentId: String,
    val action: ParticipantAction,
    val sessionId: String,
    override val timestamp: kotlinx.datetime.Instant
) : CollaborationMessage()

enum class ParticipantAction {
    JOINED,
    LEFT,
    TYPING,
    THINKING,
    IDLE,
    PROCESSING
}

// Additional data classes for WebSocket functionality
@Serializable
data class SessionManagementMessage(
    override val id: String,
    val sessionId: String,
    val action: SessionAction,
    val participants: List<String>,
    override val timestamp: kotlinx.datetime.Instant
) : CollaborationMessage()

enum class SessionAction {
    CREATE,
    CLOSE,
    UPDATE
}

@Serializable
data class DirectMessage(
    val id: String,
    val fromAgentId: String,
    val toAgentId: String,
    val content: String,
    val timestamp: kotlinx.datetime.Instant
)

@Serializable
data class SystemMessage(
    val id: String,
    val type: SystemMessageType,
    val content: String,
    val timestamp: kotlinx.datetime.Instant
)

enum class SystemMessageType {
    SESSION_CREATED,
    PARTICIPANT_JOINED,
    CONNECTION_STATUS,
    ERROR
}

@Serializable
data class AcknowledgmentData(
    val messageId: String,
    val status: AckStatus,
    val timestamp: kotlinx.datetime.Instant
)

enum class AckStatus {
    RECEIVED,
    PROCESSED,
    ERROR
}

// Connection health and monitoring
data class ConnectionHealth(
    val isConnected: Boolean = false,
    val connectionAttempts: Int = 0,
    val lastConnectedAt: kotlinx.datetime.Instant? = null,
    val lastDisconnectedAt: kotlinx.datetime.Instant? = null,
    val lastMessageAt: kotlinx.datetime.Instant? = null,
    val lastSentAt: kotlinx.datetime.Instant? = null,
    val lastHeartbeatAt: kotlinx.datetime.Instant? = null,
    val messagesSent: Int = 0,
    val messagesReceived: Int = 0,
    val heartbeatCount: Int = 0,
    val errorCount: Int = 0,
    val parseErrors: Int = 0,
    val sendErrors: Int = 0,
    val lastError: String? = null
)

data class QueuedMessage(
    val message: WebSocketMessage,
    val queuedAt: kotlinx.datetime.Instant,
    var attempts: Int = 0
)

data class MessageSubscription(
    val id: String,
    val messageTypes: Set<String>,
    val callback: suspend (CollaborationMessage) -> Unit
)

// Custom exceptions
class WebSocketException(message: String, cause: Throwable? = null) : Exception(message, cause)
class SessionNotFoundException(message: String) : Exception(message)
class MessageDeliveryException(message: String) : Exception(message)