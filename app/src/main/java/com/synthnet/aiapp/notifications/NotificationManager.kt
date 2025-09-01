package com.synthnet.aiapp.notifications

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.synthnet.aiapp.R
import com.synthnet.aiapp.presentation.MainActivity
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SynthNetNotificationManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    private val notificationManager = NotificationManagerCompat.from(context)
    
    companion object {
        const val CHANNEL_AGENT_UPDATES = "agent_updates"
        const val CHANNEL_PROJECT_ALERTS = "project_alerts"
        const val CHANNEL_COLLABORATION = "collaboration"
        const val CHANNEL_INSIGHTS = "insights"
        const val CHANNEL_SYSTEM = "system"
        
        const val NOTIFICATION_AGENT_STATUS = 1001
        const val NOTIFICATION_PROJECT_MILESTONE = 1002
        const val NOTIFICATION_COLLABORATION_INVITE = 1003
        const val NOTIFICATION_NEW_INSIGHT = 1004
        const val NOTIFICATION_SYSTEM_UPDATE = 1005
        const val NOTIFICATION_AUTONOMY_PROMOTION = 1006
        const val NOTIFICATION_ERROR_ALERT = 1007
        const val NOTIFICATION_THOUGHT_COMPLETION = 1008
    }
    
    init {
        createNotificationChannels()
    }
    
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channels = listOf(
                NotificationChannel(
                    CHANNEL_AGENT_UPDATES,
                    "Agent Updates",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notifications about agent status changes and activities"
                    enableLights(true)
                    enableVibration(true)
                },
                
                NotificationChannel(
                    CHANNEL_PROJECT_ALERTS,
                    "Project Alerts",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Important project milestones and alerts"
                    enableLights(true)
                    enableVibration(true)
                },
                
                NotificationChannel(
                    CHANNEL_COLLABORATION,
                    "Collaboration",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Collaboration invites and real-time updates"
                    enableLights(true)
                    enableVibration(false)
                },
                
                NotificationChannel(
                    CHANNEL_INSIGHTS,
                    "AI Insights",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "New insights and recommendations from AI agents"
                    enableLights(false)
                    enableVibration(false)
                },
                
                NotificationChannel(
                    CHANNEL_SYSTEM,
                    "System",
                    NotificationManager.IMPORTANCE_MIN
                ).apply {
                    description = "System updates and maintenance notifications"
                    enableLights(false)
                    enableVibration(false)
                }
            )
            
            val systemNotificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            channels.forEach { channel ->
                systemNotificationManager.createNotificationChannel(channel)
            }
        }
    }
    
    fun showAgentStatusNotification(
        agentName: String,
        status: String,
        projectId: String,
        details: String? = null
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("project_id", projectId)
            putExtra("focus", "agents")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(context, CHANNEL_AGENT_UPDATES)
            .setSmallIcon(R.drawable.ic_notification) // Add this icon to resources
            .setContentTitle("Agent Update: $agentName")
            .setContentText("Status: $status")
            .setStyle(NotificationCompat.BigTextStyle().apply {
                details?.let { bigText(it) }
            })
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_blue_bright))
            .addAction(
                R.drawable.ic_notification,
                "View Details",
                pendingIntent
            )
            .build()
        
        notificationManager.notify(NOTIFICATION_AGENT_STATUS, notification)
    }
    
    fun showProjectMilestoneNotification(
        projectName: String,
        milestone: String,
        projectId: String,
        progress: Int? = null
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("project_id", projectId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val builder = NotificationCompat.Builder(context, CHANNEL_PROJECT_ALERTS)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Project Milestone Reached")
            .setContentText("$projectName: $milestone")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_green_light))
        
        progress?.let { progressValue ->
            builder.setProgress(100, progressValue, false)
                .setSubText("$progressValue% complete")
        }
        
        notificationManager.notify(NOTIFICATION_PROJECT_MILESTONE, builder.build())
    }
    
    fun showCollaborationInviteNotification(
        inviterAgentName: String,
        sessionType: String,
        projectName: String,
        collaborationId: String
    ) {
        val joinIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("collaboration_id", collaborationId)
            putExtra("action", "join")
        }
        
        val joinPendingIntent = PendingIntent.getActivity(
            context, 1, joinIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val viewIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("collaboration_id", collaborationId)
            putExtra("action", "view")
        }
        
        val viewPendingIntent = PendingIntent.getActivity(
            context, 2, viewIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(context, CHANNEL_COLLABORATION)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Collaboration Invite")
            .setContentText("$inviterAgentName invites you to a $sessionType session")
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("$inviterAgentName has started a $sessionType session for $projectName and would like your input."))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(viewPendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_purple))
            .addAction(R.drawable.ic_notification, "Join", joinPendingIntent)
            .addAction(R.drawable.ic_notification, "View", viewPendingIntent)
            .build()
        
        notificationManager.notify(NOTIFICATION_COLLABORATION_INVITE, notification)
    }
    
    fun showNewInsightNotification(
        insightTitle: String,
        insightSummary: String,
        projectId: String,
        confidenceScore: Double
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("project_id", projectId)
            putExtra("focus", "insights")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val confidencePercent = (confidenceScore * 100).toInt()
        
        val notification = NotificationCompat.Builder(context, CHANNEL_INSIGHTS)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("New AI Insight")
            .setContentText(insightTitle)
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("$insightSummary\\n\\nConfidence: $confidencePercent%"))
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_orange_light))
            .setSubText("Confidence: $confidencePercent%")
            .build()
        
        notificationManager.notify(NOTIFICATION_NEW_INSIGHT, notification)
    }
    
    fun showAutonomyPromotionNotification(
        projectName: String,
        newLevel: String,
        projectId: String,
        achievements: List<String>
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("project_id", projectId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val achievementText = achievements.joinToString("\\n• ", "• ")
        
        val notification = NotificationCompat.Builder(context, CHANNEL_PROJECT_ALERTS)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Autonomy Level Increased!")
            .setContentText("$projectName promoted to $newLevel")
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("$projectName has been promoted to $newLevel autonomy level!\\n\\nAchievements:\\n$achievementText"))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_green_dark))
            .setCategory(NotificationCompat.CATEGORY_STATUS)
            .build()
        
        notificationManager.notify(NOTIFICATION_AUTONOMY_PROMOTION, notification)
    }
    
    fun showErrorAlertNotification(
        errorType: String,
        errorMessage: String,
        projectId: String? = null,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            projectId?.let { putExtra("project_id", it) }
            putExtra("focus", "errors")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val priority = when (severity) {
            ErrorSeverity.LOW -> NotificationCompat.PRIORITY_LOW
            ErrorSeverity.MEDIUM -> NotificationCompat.PRIORITY_DEFAULT
            ErrorSeverity.HIGH -> NotificationCompat.PRIORITY_HIGH
            ErrorSeverity.CRITICAL -> NotificationCompat.PRIORITY_MAX
        }
        
        val notification = NotificationCompat.Builder(context, CHANNEL_SYSTEM)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("System Alert: $errorType")
            .setContentText(errorMessage)
            .setStyle(NotificationCompat.BigTextStyle().bigText(errorMessage))
            .setPriority(priority)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_red_light))
            .setCategory(NotificationCompat.CATEGORY_ERROR)
            .apply {
                if (severity == ErrorSeverity.CRITICAL) {
                    setOngoing(true) // Make it persistent for critical errors
                    setSound(null) // Custom sound for critical errors
                }
            }
            .build()
        
        notificationManager.notify(NOTIFICATION_ERROR_ALERT, notification)
    }
    
    fun showThoughtCompletionNotification(
        thoughtTitle: String,
        confidence: Double,
        alternativesCount: Int,
        projectId: String
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("project_id", projectId)
            putExtra("focus", "thoughts")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val confidencePercent = (confidence * 100).toInt()
        
        val notification = NotificationCompat.Builder(context, CHANNEL_AGENT_UPDATES)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Thought Process Complete")
            .setContentText(thoughtTitle)
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("$thoughtTitle\\n\\nConfidence: $confidencePercent%\\nAlternatives explored: $alternativesCount"))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_blue_dark))
            .setProgress(100, confidencePercent, false)
            .build()
        
        notificationManager.notify(NOTIFICATION_THOUGHT_COMPLETION, notification)
    }
    
    fun showProgressNotification(
        id: Int,
        title: String,
        currentStep: String,
        progress: Int,
        maxProgress: Int = 100,
        ongoing: Boolean = true
    ) {
        val notification = NotificationCompat.Builder(context, CHANNEL_SYSTEM)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(currentStep)
            .setProgress(maxProgress, progress, false)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(ongoing)
            .setCategory(NotificationCompat.CATEGORY_PROGRESS)
            .build()
        
        notificationManager.notify(id, notification)
    }
    
    fun dismissNotification(notificationId: Int) {
        notificationManager.cancel(notificationId)
    }
    
    fun dismissAllNotifications() {
        notificationManager.cancelAll()
    }
    
    fun areNotificationsEnabled(): Boolean {
        return notificationManager.areNotificationsEnabled()
    }
}

enum class ErrorSeverity {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}