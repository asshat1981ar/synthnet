package com.synthnet.aiapp.presentation.screens.project.tabs

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.synthnet.aiapp.domain.models.Collaboration
import com.synthnet.aiapp.domain.services.ConnectionState
import com.synthnet.aiapp.presentation.viewmodels.CollaborationSession

@Composable
fun ProjectCollaborationTab(
    collaborations: List<Collaboration>,
    connectionState: ConnectionState,
    sessionHistory: List<CollaborationSession>,
    onStartCollaboration: () -> Unit,
    onJoinCollaboration: (String) -> Unit,
    onLeaveCollaboration: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
    ) {
        // Connection Status Header
        CollaborationConnectionCard(
            connectionState = connectionState,
            onStartCollaboration = onStartCollaboration,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        // Active Collaborations
        if (collaborations.isNotEmpty()) {
            ActiveCollaborationsSection(
                collaborations = collaborations,
                onJoinCollaboration = onJoinCollaboration,
                onLeaveCollaboration = onLeaveCollaboration,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }
        
        // Collaboration History and Statistics
        CollaborationHistorySection(
            sessionHistory = sessionHistory,
            collaborations = collaborations
        )
    }
}

@Composable
private fun CollaborationConnectionCard(
    connectionState: ConnectionState,
    onStartCollaboration: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (connectionState) {
                ConnectionState.CONNECTED -> MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                ConnectionState.CONNECTING -> MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.3f)
                ConnectionState.ERROR -> MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f)
                ConnectionState.DISCONNECTED -> MaterialTheme.colorScheme.surfaceVariant
            }
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Collaboration Network",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                ConnectionStatusIndicator(connectionState = connectionState)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            val statusMessage = when (connectionState) {
                ConnectionState.CONNECTED -> "Connected to SynthNet collaboration network. Ready to start new sessions."
                ConnectionState.CONNECTING -> "Establishing connection to collaboration network..."
                ConnectionState.ERROR -> "Connection error. Please check your network connection."
                ConnectionState.DISCONNECTED -> "Not connected to collaboration network. Connect to start collaborating."
            }
            
            Text(
                text = statusMessage,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = onStartCollaboration,
                    enabled = connectionState == ConnectionState.CONNECTED,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Default.GroupAdd,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Start Session")
                }
                
                OutlinedButton(
                    onClick = { /* Handle discovery */ },
                    enabled = connectionState == ConnectionState.CONNECTED,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Default.Search,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Find Sessions")
                }
            }
        }
    }
}

@Composable
private fun ConnectionStatusIndicator(
    connectionState: ConnectionState,
    modifier: Modifier = Modifier
) {
    val color by animateColorAsState(
        targetValue = when (connectionState) {
            ConnectionState.CONNECTED -> MaterialTheme.colorScheme.primary
            ConnectionState.CONNECTING -> MaterialTheme.colorScheme.secondary
            ConnectionState.ERROR -> MaterialTheme.colorScheme.error
            ConnectionState.DISCONNECTED -> MaterialTheme.colorScheme.outline
        },
        label = "connection_color"
    )
    
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically
    ) {
        when (connectionState) {
            ConnectionState.CONNECTING -> {
                CircularProgressIndicator(
                    modifier = Modifier.size(12.dp),
                    strokeWidth = 2.dp,
                    color = color
                )
            }
            else -> {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(color, CircleShape)
                )
            }
        }
        
        Spacer(modifier = Modifier.width(8.dp))
        
        Text(
            text = when (connectionState) {
                ConnectionState.CONNECTED -> "Connected"
                ConnectionState.CONNECTING -> "Connecting"
                ConnectionState.ERROR -> "Error"
                ConnectionState.DISCONNECTED -> "Disconnected"
            },
            style = MaterialTheme.typography.labelMedium,
            color = color,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun ActiveCollaborationsSection(
    collaborations: List<Collaboration>,
    onJoinCollaboration: (String) -> Unit,
    onLeaveCollaboration: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Active Sessions",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                Badge {
                    Text(
                        text = collaborations.size.toString(),
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            collaborations.forEach { collaboration ->
                CollaborationSessionCard(
                    collaboration = collaboration,
                    onJoinCollaboration = { onJoinCollaboration(collaboration.id) },
                    onLeaveCollaboration = { onLeaveCollaboration(collaboration.id) }
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun CollaborationSessionCard(
    collaboration: Collaboration,
    onJoinCollaboration: () -> Unit,
    onLeaveCollaboration: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = collaboration.sessionType.name.replace('_', ' '),
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "${collaboration.participants.size} participants",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                SessionTypeIcon(sessionType = collaboration.sessionType.name)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Session Statistics
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                SessionStat(
                    label = "Knowledge Exchanges",
                    value = collaboration.knowledgeExchanges.toString(),
                    icon = Icons.Default.SwapHoriz
                )
                
                SessionStat(
                    label = "Insights",
                    value = collaboration.insights.size.toString(),
                    icon = Icons.Default.Lightbulb
                )
                
                SessionStat(
                    label = "Alternatives",
                    value = collaboration.alternatives.size.toString(),
                    icon = Icons.Default.AltRoute
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Action buttons
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (collaboration.consensusReached) {
                    Button(
                        onClick = onJoinCollaboration,
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(
                            imageVector = Icons.Default.JoinFull,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Join", style = MaterialTheme.typography.labelMedium)
                    }
                } else {
                    OutlinedButton(
                        onClick = onLeaveCollaboration,
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(
                            imageVector = Icons.Default.ExitToApp,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Leave", style = MaterialTheme.typography.labelMedium)
                    }
                }
                
                OutlinedButton(
                    onClick = { /* Handle view details */ }
                ) {
                    Icon(
                        imageVector = Icons.Default.Visibility,
                        contentDescription = "View Details"
                    )
                }
            }
        }
    }
}

@Composable
private fun SessionTypeIcon(
    sessionType: String,
    modifier: Modifier = Modifier
) {
    val icon = when (sessionType.uppercase()) {
        "BRAINSTORMING" -> Icons.Default.Lightbulb
        "DECISION_MAKING" -> Icons.Default.HowToVote
        "KNOWLEDGE_SHARING" -> Icons.Default.School
        "PROBLEM_SOLVING" -> Icons.Default.Build
        else -> Icons.Default.Group
    }
    
    Icon(
        imageVector = icon,
        contentDescription = sessionType,
        modifier = modifier.size(24.dp),
        tint = MaterialTheme.colorScheme.primary
    )
}

@Composable
private fun SessionStat(
    label: String,
    value: String,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(20.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun CollaborationHistorySection(
    sessionHistory: List<CollaborationSession>,
    collaborations: List<Collaboration>,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Collaboration Analytics",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Analytics Overview
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                AnalyticCard(
                    title = "Total Sessions",
                    value = (sessionHistory.size + collaborations.size).toString(),
                    icon = Icons.Default.Timeline,
                    color = MaterialTheme.colorScheme.primary
                )
                
                AnalyticCard(
                    title = "Success Rate",
                    value = "${((collaborations.count { it.consensusReached }.toFloat() / collaborations.size.coerceAtLeast(1)) * 100).toInt()}%",
                    icon = Icons.Default.CheckCircle,
                    color = MaterialTheme.colorScheme.tertiary
                )
                
                AnalyticCard(
                    title = "Avg Participants",
                    value = if (collaborations.isNotEmpty()) 
                        "${collaborations.map { it.participants.size }.average().toInt()}" 
                    else "0",
                    icon = Icons.Default.People,
                    color = MaterialTheme.colorScheme.secondary
                )
            }
            
            if (sessionHistory.isNotEmpty()) {
                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider()
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Recent Sessions",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                sessionHistory.take(3).forEach { session ->
                    SessionHistoryItem(session = session)
                    Spacer(modifier = Modifier.height(8.dp))
                }
                
                if (sessionHistory.size > 3) {
                    TextButton(
                        onClick = { /* Handle view all */ },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("View All ${sessionHistory.size} Sessions")
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.Default.ArrowForward,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AnalyticCard(
    title: String,
    value: String,
    icon: ImageVector,
    color: Color,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(28.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = title,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun SessionHistoryItem(
    session: CollaborationSession,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = when (session.type.uppercase()) {
                    "BRAINSTORMING" -> Icons.Default.Lightbulb
                    "DECISION_MAKING" -> Icons.Default.HowToVote
                    else -> Icons.Default.Group
                },
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    text = session.type.replace('_', ' '),
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = session.startTime,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        
        Surface(
            shape = MaterialTheme.shapes.extraSmall,
            color = when (session.status.uppercase()) {
                "COMPLETED" -> MaterialTheme.colorScheme.primaryContainer
                "ACTIVE" -> MaterialTheme.colorScheme.secondaryContainer
                else -> MaterialTheme.colorScheme.surfaceVariant
            }
        ) {
            Text(
                text = session.status,
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
            )
        }
    }
}