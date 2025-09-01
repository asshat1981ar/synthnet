package com.synthnet.aiapp.presentation.screens.project.tabs

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.presentation.components.*

@Composable
fun ProjectOverviewTab(
    project: Project,
    thoughtTree: ThoughtTree?,
    userInput: String,
    onUserInputChange: (String) -> Unit,
    onSubmitInput: () -> Unit,
    onThoughtSelected: (String) -> Unit,
    isProcessing: Boolean,
    lastResponse: AgentResponse?,
    showDetailedMetrics: Boolean,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp)
    ) {
        // Project Information Section
        ProjectInfoCard(project = project)
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Innovation Metrics Dashboard
        InnovationMetricsDashboard(
            metrics = project.metrics,
            showDetailed = showDetailedMetrics
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Thought Tree Visualization (if available)
        thoughtTree?.let { tree ->
            ThoughtTreeVisualization(
                thoughtTree = tree,
                onThoughtSelected = onThoughtSelected
            )
            
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // Last Agent Response (if available)
        lastResponse?.let { response ->
            AgentResponseCard(response = response)
            
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // User Input Section
        UserInputSection(
            value = userInput,
            onValueChange = onUserInputChange,
            onSubmit = onSubmitInput,
            isProcessing = isProcessing
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Project Tags and Metadata
        ProjectMetadataCard(project = project)
        
        // Bottom spacing for better scrolling experience
        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
private fun InnovationMetricsDashboard(
    metrics: ProjectMetrics,
    showDetailed: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
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
                    text = "Innovation Metrics",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                
                if (showDetailed) {
                    Icon(
                        imageVector = Icons.Default.Analytics,
                        contentDescription = "Detailed view",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Primary metrics
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                MetricCard(
                    label = "Innovation Velocity",
                    value = "${(metrics.innovationVelocity * 100).toInt()}%",
                    icon = Icons.Default.TrendingUp,
                    color = MaterialTheme.colorScheme.primary,
                    description = "Rate of innovative solutions"
                )
                
                MetricCard(
                    label = "Autonomy Index",
                    value = "${(metrics.autonomyIndex * 100).toInt()}%",
                    icon = Icons.Default.Psychology,
                    color = MaterialTheme.colorScheme.secondary,
                    description = "Level of autonomous operation"
                )
                
                MetricCard(
                    label = "Collaboration",
                    value = "${(metrics.collaborationDensity * 100).toInt()}%",
                    icon = Icons.Default.Group,
                    color = MaterialTheme.colorScheme.tertiary,
                    description = "Collaboration effectiveness"
                )
            }
            
            AnimatedVisibility(visible = showDetailed) {
                Column {
                    Spacer(modifier = Modifier.height(16.dp))
                    HorizontalDivider()
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Additional detailed metrics
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        MetricCard(
                            label = "Context Leverage",
                            value = "${(metrics.contextLeverage * 100).toInt()}%",
                            icon = Icons.Default.Memory,
                            color = MaterialTheme.colorScheme.primary,
                            description = "Context utilization efficiency"
                        )
                        
                        MetricCard(
                            label = "Error Evolution",
                            value = "${(metrics.errorEvolution * 100).toInt()}%",
                            icon = Icons.Default.Timeline,
                            color = MaterialTheme.colorScheme.secondary,
                            description = "Learning from errors rate"
                        )
                        
                        MetricCard(
                            label = "Knowledge Depth",
                            value = "${(metrics.knowledgeDepth * 100).toInt()}%",
                            icon = Icons.Default.School,
                            color = MaterialTheme.colorScheme.tertiary,
                            description = "Domain knowledge depth"
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun MetricCard(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: androidx.compose.ui.graphics.Color,
    description: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.width(110.dp),
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(24.dp)
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
            
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2
            )
        }
    }
}

@Composable
private fun AgentResponseCard(
    response: AgentResponse,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
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
                    text = "Latest AI Response",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                Text(
                    text = "Agent: ${response.agentId}",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = response.content,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            if (response.confidence > 0) {
                Spacer(modifier = Modifier.height(8.dp))
                
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Confidence: ",
                        style = MaterialTheme.typography.labelSmall
                    )
                    LinearProgressIndicator(
                        progress = { response.confidence.toFloat() },
                        modifier = Modifier
                            .weight(1f)
                            .height(6.dp),
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "${(response.confidence * 100).toInt()}%",
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
private fun ProjectMetadataCard(
    project: Project,
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
                text = "Project Details",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Project Tags
            if (project.tags.isNotEmpty()) {
                Text(
                    text = "Tags",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    project.tags.forEach { tag ->
                        TagChip(tag = tag)
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            // Collaborators
            if (project.collaborators.isNotEmpty()) {
                Text(
                    text = "Collaborators (${project.collaborators.size})",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                project.collaborators.take(5).forEach { collaborator ->
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 2.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = collaborator,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
                
                if (project.collaborators.size > 5) {
                    Text(
                        text = "and ${project.collaborators.size - 5} more...",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Creation and update timestamps
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "Created",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = project.createdAt.toString().split('T')[0], // Simple date formatting
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    Text(
                        text = "Last Updated",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = project.updatedAt.toString().split('T')[0], // Simple date formatting
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
private fun TagChip(
    tag: String,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.small,
        color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.7f)
    ) {
        Text(
            text = tag,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
        )
    }
}