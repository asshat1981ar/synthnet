package com.synthnet.aiapp.presentation.screens.project.tabs

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.synthnet.aiapp.data.entities.AgentStatus
import com.synthnet.aiapp.domain.models.Agent
import com.synthnet.aiapp.domain.orchestration.OrchestrationState

@Composable
fun ProjectAgentsTab(
    agents: List<Agent>,
    orchestrationState: OrchestrationState,
    onAgentAction: (String, String) -> Unit,
    onStartAgent: (String) -> Unit,
    onStopAgent: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
    ) {
        // Orchestration Status Header
        OrchestrationStatusCard(
            orchestrationState = orchestrationState,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        // Agents Overview
        AgentsOverviewCard(
            agents = agents,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        // Agent List
        if (agents.isNotEmpty()) {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(agents) { agent ->
                    AgentCard(
                        agent = agent,
                        onStartAgent = { onStartAgent(agent.id) },
                        onStopAgent = { onStopAgent(agent.id) },
                        onPerformAction = { action -> onAgentAction(agent.id, action) }
                    )
                }
                
                // Bottom spacing
                item {
                    Spacer(modifier = Modifier.height(32.dp))
                }
            }
        } else {
            EmptyAgentsState()
        }
    }
}

@Composable
private fun OrchestrationStatusCard(
    orchestrationState: OrchestrationState,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
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
                    text = "Orchestration Status",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                OrchestrationStatusIndicator(
                    isProcessing = orchestrationState.isProcessing
                )
            }
            
            if (orchestrationState.isProcessing) {
                Spacer(modifier = Modifier.height(12.dp))
                
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = orchestrationState.currentTask,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Progress bar for current task
                Spacer(modifier = Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = { orchestrationState.currentTaskProgress },
                    modifier = Modifier.fillMaxWidth(),
                    color = MaterialTheme.colorScheme.primary,
                )
            } else {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "System idle - Ready for new tasks",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun OrchestrationStatusIndicator(
    isProcessing: Boolean,
    modifier: Modifier = Modifier
) {
    val color by animateColorAsState(
        targetValue = if (isProcessing) 
            MaterialTheme.colorScheme.primary 
        else 
            MaterialTheme.colorScheme.outline,
        label = "status_color"
    )
    
    val scale by animateFloatAsState(
        targetValue = if (isProcessing) 1.2f else 1f,
        label = "status_scale"
    )
    
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .scale(scale)
                .background(color, CircleShape)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = if (isProcessing) "Active" else "Idle",
            style = MaterialTheme.typography.labelMedium,
            color = color,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun AgentsOverviewCard(
    agents: List<Agent>,
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
                text = "Agent Overview",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Status counts
            val statusCounts = agents.groupBy { it.status }.mapValues { it.value.size }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatusCount(
                    label = "Active",
                    count = statusCounts[AgentStatus.WORKING] ?: 0,
                    color = MaterialTheme.colorScheme.primary,
                    icon = Icons.Default.PlayArrow
                )
                StatusCount(
                    label = "Thinking",
                    count = statusCounts[AgentStatus.THINKING] ?: 0,
                    color = MaterialTheme.colorScheme.secondary,
                    icon = Icons.Default.Psychology
                )
                StatusCount(
                    label = "Idle",
                    count = statusCounts[AgentStatus.IDLE] ?: 0,
                    color = MaterialTheme.colorScheme.outline,
                    icon = Icons.Default.Pause
                )
                StatusCount(
                    label = "Error",
                    count = statusCounts[AgentStatus.ERROR] ?: 0,
                    color = MaterialTheme.colorScheme.error,
                    icon = Icons.Default.Error
                )
            }
        }
    }
}

@Composable
private fun StatusCount(
    label: String,
    count: Int,
    color: Color,
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
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = count.toString(),
            style = MaterialTheme.typography.titleMedium,
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
private fun AgentCard(
    agent: Agent,
    onStartAgent: () -> Unit,
    onStopAgent: () -> Unit,
    onPerformAction: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Agent Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = agent.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = agent.role.name.replace('_', ' '),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                AgentStatusBadge(status = agent.status)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Agent Capabilities
            if (agent.capabilities.isNotEmpty()) {
                Text(
                    text = "Capabilities",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    agent.capabilities.forEach { capability ->
                        CapabilityChip(capability = capability)
                    }
                }
                
                Spacer(modifier = Modifier.height(12.dp))
            }
            
            // Performance Metrics
            AgentMetrics(agent = agent)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Action Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                when (agent.status) {
                    AgentStatus.IDLE, AgentStatus.OFFLINE, AgentStatus.ERROR -> {
                        Button(
                            onClick = onStartAgent,
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Default.PlayArrow,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Start")
                        }
                    }
                    AgentStatus.WORKING, AgentStatus.THINKING, AgentStatus.WAITING -> {
                        OutlinedButton(
                            onClick = onStopAgent,
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Stop,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Stop")
                        }
                    }
                }
                
                // More actions dropdown
                var showMenu by remember { mutableStateOf(false) }
                Box {
                    OutlinedButton(
                        onClick = { showMenu = true }
                    ) {
                        Icon(
                            imageVector = Icons.Default.MoreVert,
                            contentDescription = "More actions"
                        )
                    }
                    
                    DropdownMenu(
                        expanded = showMenu,
                        onDismissRequest = { showMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Restart") },
                            onClick = {
                                onPerformAction("RESTART")
                                showMenu = false
                            },
                            leadingIcon = {
                                Icon(Icons.Default.Refresh, contentDescription = null)
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("View Logs") },
                            onClick = {
                                onPerformAction("VIEW_LOGS")
                                showMenu = false
                            },
                            leadingIcon = {
                                Icon(Icons.Default.Description, contentDescription = null)
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Configure") },
                            onClick = {
                                onPerformAction("CONFIGURE")
                                showMenu = false
                            },
                            leadingIcon = {
                                Icon(Icons.Default.Settings, contentDescription = null)
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AgentStatusBadge(
    status: AgentStatus,
    modifier: Modifier = Modifier
) {
    val (color, text) = when (status) {
        AgentStatus.IDLE -> MaterialTheme.colorScheme.outline to "Idle"
        AgentStatus.THINKING -> MaterialTheme.colorScheme.secondary to "Thinking"
        AgentStatus.WORKING -> MaterialTheme.colorScheme.primary to "Working"
        AgentStatus.WAITING -> MaterialTheme.colorScheme.tertiary to "Waiting"
        AgentStatus.ERROR -> MaterialTheme.colorScheme.error to "Error"
        AgentStatus.OFFLINE -> MaterialTheme.colorScheme.outlineVariant to "Offline"
    }
    
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.small,
        color = color.copy(alpha = 0.2f)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(color, CircleShape)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = text,
                style = MaterialTheme.typography.labelMedium,
                color = color,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
private fun CapabilityChip(
    capability: String,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.extraSmall,
        color = MaterialTheme.colorScheme.surfaceVariant
    ) {
        Text(
            text = capability,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

@Composable
private fun AgentMetrics(
    agent: Agent,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        MetricItem(
            label = "Performance",
            value = "${(agent.performanceScore * 100).toInt()}%",
            progress = agent.performanceScore
        )
        
        MetricItem(
            label = "Reliability",
            value = "${(agent.reliabilityScore * 100).toInt()}%",
            progress = agent.reliabilityScore
        )
        
        MetricItem(
            label = "Efficiency",
            value = "${(agent.efficiency * 100).toInt()}%",
            progress = agent.efficiency
        )
    }
}

@Composable
private fun MetricItem(
    label: String,
    value: String,
    progress: Double,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
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
        Spacer(modifier = Modifier.height(4.dp))
        LinearProgressIndicator(
            progress = { progress.toFloat() },
            modifier = Modifier
                .width(60.dp)
                .height(4.dp),
            color = MaterialTheme.colorScheme.primary,
        )
    }
}

@Composable
private fun EmptyAgentsState(
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.SmartToy,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "No Agents Assigned",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "This project doesn't have any AI agents assigned yet. Agents will appear here once they're added to the project.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}