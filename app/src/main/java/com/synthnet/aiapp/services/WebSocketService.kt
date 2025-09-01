package com.synthnet.aiapp.services

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import com.synthnet.aiapp.domain.networking.WebSocketManager
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * WebSocket Service for maintaining persistent connections for real-time collaboration
 * and AI agent communication.
 */
@AndroidEntryPoint
class WebSocketService : Service() {
    
    @Inject
    lateinit var webSocketManager: WebSocketManager
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    companion object {
        private const val TAG = "WebSocketService"
        const val ACTION_START_CONNECTION = "START_CONNECTION"
        const val ACTION_STOP_CONNECTION = "STOP_CONNECTION"
        const val EXTRA_PROJECT_ID = "PROJECT_ID"
        const val EXTRA_ENDPOINT_URL = "ENDPOINT_URL"
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "WebSocket Service created")
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_CONNECTION -> {
                val projectId = intent.getStringExtra(EXTRA_PROJECT_ID)
                val endpointUrl = intent.getStringExtra(EXTRA_ENDPOINT_URL)
                
                if (projectId != null && endpointUrl != null) {
                    startWebSocketConnection(projectId, endpointUrl)
                }
            }
            ACTION_STOP_CONNECTION -> {
                stopWebSocketConnection()
            }
        }
        
        return START_STICKY
    }
    
    private fun startWebSocketConnection(projectId: String, endpointUrl: String) {
        serviceScope.launch {
            try {
                Log.d(TAG, "Starting WebSocket connection for project: $projectId")
                webSocketManager.connect(endpointUrl, projectId)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to start WebSocket connection", e)
            }
        }
    }
    
    private fun stopWebSocketConnection() {
        serviceScope.launch {
            try {
                Log.d(TAG, "Stopping WebSocket connection")
                webSocketManager.disconnect()
            } catch (e: Exception) {
                Log.e(TAG, "Failed to stop WebSocket connection", e)
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "WebSocket Service destroyed")
        serviceScope.cancel()
        
        // Ensure WebSocket is disconnected
        serviceScope.launch {
            webSocketManager.disconnect()
        }
    }
}