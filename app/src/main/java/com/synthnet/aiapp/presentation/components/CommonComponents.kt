package com.synthnet.aiapp.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.synthnet.aiapp.data.entities.AutonomyLevel
import com.synthnet.aiapp.data.entities.ProjectStatus
import com.synthnet.aiapp.data.entities.AgentStatus
import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.orchestration.OrchestrationState
import com.synthnet.aiapp.domain.services.ConnectionState
import com.synthnet.aiapp.presentation.theme.*

@Composable
fun ProjectStatusBadge(status: ProjectStatus) {
    val color = when (status) {
        ProjectStatus.ACTIVE -> AIGreen
        ProjectStatus.PAUSED -> AIAmber
        ProjectStatus.COMPLETED -> AIBlue
        ProjectStatus.ARCHIVED -> AIGrey
        ProjectStatus.DRAFT -> AIGreyLight
    }
    
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = color.copy(alpha = 0.2f),
        modifier = Modifier.padding(4.dp)
    ) {
        Text(
            text = status.name,
            style = MaterialTheme.typography.labelSmall,
            color = color,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

@Composable
fun AutonomyLevelBadge(level: AutonomyLevel) {
    val (color, gradient) = when (level) {
        AutonomyLevel.MANUAL -> AIRed to listOf(AIRedLight, AIRedDark)
        AutonomyLevel.ASSISTED -> AIAmber to listOf(AIAmberLight, AIAmberDark)
        AutonomyLevel.SEMI_AUTONOMOUS -> AIBlue to listOf(AIBlueLight, AIBlueDark)
        AutonomyLevel.FULLY_AUTONOMOUS -> AIGreen to listOf(AIGreenLight, AIGreenDark)
    }
    
    Box(
        modifier = Modifier
            .background(
                brush = Brush.horizontalGradient(gradient),
                shape = RoundedCornerShape(16.dp)
            )
            .padding(horizontal = 12.dp, vertical = 6.dp)
    ) {
        Text(
            text = level.name.replace('_', ' '),
            style = MaterialTheme.typography.labelMedium,
            color = Color.White,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun EmptyStateView(
    title: String,
    description: String,
    actionText: String,
    onActionClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Person,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )
        
        Text(
            text = description,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
        )
        
        Button(onClick = onActionClick) {
            Text(actionText)
        }
    }
}

@Composable
fun ProjectInfoCard(project: Project) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Project Information",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = project.description,
                style = MaterialTheme.typography.bodyMedium
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row {
                Text(
                    text = "Status: ",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium
                )
                ProjectStatusBadge(project.status)
            }
        }
    }
}

@Composable
fun AgentStatusPanel(
    agents: List<Agent>,
    orchestrationState: OrchestrationState
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Agents",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            agents.forEach { agent ->
                AgentStatusItem(agent = agent)
                Spacer(modifier = Modifier.height(8.dp))
            }
            
            if (orchestrationState.isProcessing) {
                Divider(modifier = Modifier.padding(vertical = 8.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        strokeWidth = 2.dp
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = orchestrationState.currentTask,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}

@Composable
private fun AgentStatusItem(agent: Agent) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = agent.name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = agent.role.name,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        AgentStatusIndicator(status = agent.status)
    }
}

@Composable
private fun AgentStatusIndicator(status: AgentStatus) {
    val color = when (status) {
        AgentStatus.IDLE -> AIGrey
        AgentStatus.THINKING -> AIAmber
        AgentStatus.WORKING -> AIBlue
        AgentStatus.WAITING -> AIGreyLight
        AgentStatus.ERROR -> AIRed
        AgentStatus.OFFLINE -> AIGreyDark
    }
    
    Box(
        modifier = Modifier
            .size(12.dp)
            .background(color, CircleShape)
    )
}

@Composable
fun ThoughtTreeVisualization(
    thoughtTree: ThoughtTree,
    onThoughtSelected: (String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Thought Tree",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Simplified tree visualization
            ThoughtNode(
                thought = thoughtTree.rootThought,
                onThoughtSelected = onThoughtSelected,
                isRoot = true
            )
        }
    }
}

@Composable
private fun ThoughtNode(
    thought: Thought,
    onThoughtSelected: (String) -> Unit,
    isRoot: Boolean = false,
    depth: Int = 0
) {
    Column(
        modifier = Modifier.padding(start = (depth * 16).dp)
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onThoughtSelected(thought.id) },
            colors = CardDefaults.cardColors(
                containerColor = if (thought.isSelected) 
                    MaterialTheme.colorScheme.primaryContainer
                else 
                    MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier.padding(12.dp)
            ) {
                Text(
                    text = thought.content,
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 2
                )
                Text(
                    text = "Confidence: ${(thought.confidence * 100).toInt()}%",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        
        // Render children
        thought.children.forEach { child ->
            Spacer(modifier = Modifier.height(8.dp))
            ThoughtNode(
                thought = child,
                onThoughtSelected = onThoughtSelected,
                depth = depth + 1
            )
        }
    }
}

@Composable
fun CollaborationPanel(
    collaborations: List<Collaboration>,
    connectionState: ConnectionState
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
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
                    text = "Collaboration",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                ConnectionStatusIndicator(state = connectionState)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            if (collaborations.isEmpty()) {
                Text(
                    text = "No active collaborations",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                collaborations.forEach { collaboration ->
                    CollaborationItem(collaboration = collaboration)
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun ConnectionStatusIndicator(state: ConnectionState) {
    val (color, text) = when (state) {
        ConnectionState.CONNECTED -> AIGreen to "Connected"
        ConnectionState.CONNECTING -> AIAmber to "Connecting"
        ConnectionState.DISCONNECTED -> AIGrey to "Disconnected"
        ConnectionState.ERROR -> AIRed to "Error"
    }
    
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .background(color, CircleShape)
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}

@Composable
private fun CollaborationItem(collaboration: Collaboration) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = collaboration.sessionType.name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = "${collaboration.participants.size} participants",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        Text(
            text = collaboration.knowledgeExchanges.toString(),
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
    }
}

@Composable
fun InnovationMetricsDashboard(metrics: ProjectMetrics) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Innovation Metrics",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                MetricDisplay(
                    label = "Innovation",
                    value = "${(metrics.innovationVelocity * 100).toInt()}%",
                    color = NeuralPurple
                )
                
                MetricDisplay(
                    label = "Autonomy",
                    value = "${(metrics.autonomyIndex * 100).toInt()}%",
                    color = AIBlue
                )
                
                MetricDisplay(
                    label = "Collaboration",
                    value = "${(metrics.collaborationDensity * 100).toInt()}%",
                    color = AIGreen
                )
            }
        }
    }
}

@Composable
private fun MetricDisplay(
    label: String,
    value: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun UserInputSection(
    value: String,
    onValueChange: (String) -> Unit,
    onSubmit: () -> Unit,
    isProcessing: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            OutlinedTextField(
                value = value,
                onValueChange = onValueChange,
                label = { Text("Ask the AI agents...") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 2,
                maxLines = 4,
                enabled = !isProcessing
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Button(
                onClick = onSubmit,
                modifier = Modifier.fillMaxWidth(),
                enabled = value.isNotBlank() && !isProcessing
            ) {
                if (isProcessing) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Processing...")
                } else {
                    Text("Submit")
                }
            }
        }
    }
}