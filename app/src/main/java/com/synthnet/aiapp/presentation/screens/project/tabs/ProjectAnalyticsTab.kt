package com.synthnet.aiapp.presentation.screens.project.tabs

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.synthnet.aiapp.domain.models.ProjectMetrics
import com.synthnet.aiapp.domain.models.ThoughtTree
import com.synthnet.aiapp.presentation.viewmodels.HistoricalMetrics
import com.synthnet.aiapp.presentation.viewmodels.PerformanceMetrics
import com.synthnet.aiapp.presentation.viewmodels.TrendPoint
import kotlin.math.max
import kotlin.math.min

@Composable
fun ProjectAnalyticsTab(
    metrics: ProjectMetrics,
    thoughtTree: ThoughtTree?,
    historicalData: HistoricalMetrics?,
    performanceData: PerformanceMetrics?,
    onExportData: (String) -> Unit,
    onRefreshMetrics: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp)
    ) {
        // Analytics Header with Export Options
        AnalyticsHeader(
            onExportData = onExportData,
            onRefreshMetrics = onRefreshMetrics,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        // Key Performance Indicators
        KPISection(
            metrics = metrics,
            performanceData = performanceData,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        // Historical Trends
        historicalData?.let { data ->
            TrendAnalysisSection(
                historicalMetrics = data,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }
        
        // Performance Metrics
        performanceData?.let { data ->
            PerformanceSection(
                performanceMetrics = data,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }
        
        // Thought Tree Analytics
        thoughtTree?.let { tree ->
            ThoughtTreeAnalyticsSection(
                thoughtTree = tree,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }
        
        // Innovation Insights
        InnovationInsightsSection(
            metrics = metrics,
            modifier = Modifier.padding(bottom = 32.dp)
        )
    }
}

@Composable
private fun AnalyticsHeader(
    onExportData: (String) -> Unit,
    onRefreshMetrics: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Analytics Dashboard",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Real-time project intelligence and insights",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                IconButton(onClick = onRefreshMetrics) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = "Refresh Data"
                    )
                }
                
                var showExportMenu by remember { mutableStateOf(false) }
                Box {
                    IconButton(onClick = { showExportMenu = true }) {
                        Icon(
                            imageVector = Icons.Default.Download,
                            contentDescription = "Export Data"
                        )
                    }
                    
                    DropdownMenu(
                        expanded = showExportMenu,
                        onDismissRequest = { showExportMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Export as PDF") },
                            onClick = {
                                onExportData("PDF")
                                showExportMenu = false
                            },
                            leadingIcon = {
                                Icon(Icons.Default.PictureAsPdf, contentDescription = null)
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Export as CSV") },
                            onClick = {
                                onExportData("CSV")
                                showExportMenu = false
                            },
                            leadingIcon = {
                                Icon(Icons.Default.TableView, contentDescription = null)
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Export as JSON") },
                            onClick = {
                                onExportData("JSON")
                                showExportMenu = false
                            },
                            leadingIcon = {
                                Icon(Icons.Default.Code, contentDescription = null)
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun KPISection(
    metrics: ProjectMetrics,
    performanceData: PerformanceMetrics?,
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
                text = "Key Performance Indicators",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                KPICard(
                    title = "Innovation Velocity",
                    value = "${(metrics.innovationVelocity * 100).toInt()}%",
                    change = "+12%",
                    isPositive = true,
                    icon = Icons.Default.TrendingUp,
                    color = MaterialTheme.colorScheme.primary
                )
                
                KPICard(
                    title = "Autonomy Index",
                    value = "${(metrics.autonomyIndex * 100).toInt()}%",
                    change = "+8%",
                    isPositive = true,
                    icon = Icons.Default.Psychology,
                    color = MaterialTheme.colorScheme.secondary
                )
                
                KPICard(
                    title = "Collaboration Density",
                    value = "${(metrics.collaborationDensity * 100).toInt()}%",
                    change = "-2%",
                    isPositive = false,
                    icon = Icons.Default.Group,
                    color = MaterialTheme.colorScheme.tertiary
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            performanceData?.let { performance ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    KPICard(
                        title = "Response Time",
                        value = "${performance.averageResponseTime.toInt()}ms",
                        change = "-15ms",
                        isPositive = true,
                        icon = Icons.Default.Speed,
                        color = MaterialTheme.colorScheme.primary
                    )
                    
                    KPICard(
                        title = "Success Rate",
                        value = "${(performance.successRate * 100).toInt()}%",
                        change = "+3%",
                        isPositive = true,
                        icon = Icons.Default.CheckCircle,
                        color = MaterialTheme.colorScheme.tertiary
                    )
                    
                    KPICard(
                        title = "Resource Usage",
                        value = "${(performance.resourceUtilization * 100).toInt()}%",
                        change = "+5%",
                        isPositive = false,
                        icon = Icons.Default.Memory,
                        color = MaterialTheme.colorScheme.secondary
                    )
                }
            }
        }
    }
}

@Composable
private fun KPICard(
    title: String,
    value: String,
    change: String,
    isPositive: Boolean,
    icon: ImageVector,
    color: Color,
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
                text = title,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (isPositive) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                    contentDescription = null,
                    modifier = Modifier.size(12.dp),
                    tint = if (isPositive) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.error
                )
                Spacer(modifier = Modifier.width(2.dp))
                Text(
                    text = change,
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isPositive) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.error,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
private fun TrendAnalysisSection(
    historicalMetrics: HistoricalMetrics,
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
                text = "Trend Analysis (30 Days)",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Innovation Trend Chart
            TrendChart(
                title = "Innovation Velocity",
                data = historicalMetrics.innovationTrend,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 16.dp)
            )
            
            // Autonomy Trend Chart
            TrendChart(
                title = "Autonomy Index",
                data = historicalMetrics.autonomyTrend,
                color = MaterialTheme.colorScheme.secondary,
                modifier = Modifier.padding(bottom = 16.dp)
            )
            
            // Collaboration Trend Chart
            TrendChart(
                title = "Collaboration Density",
                data = historicalMetrics.collaborationTrend,
                color = MaterialTheme.colorScheme.tertiary
            )
        }
    }
}

@Composable
private fun TrendChart(
    title: String,
    data: List<TrendPoint>,
    color: Color,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Medium
            )
            
            if (data.isNotEmpty()) {
                val currentValue = data.last().value
                val previousValue = if (data.size > 1) data[data.size - 2].value else currentValue
                val change = ((currentValue - previousValue) / previousValue * 100).toInt()
                
                Text(
                    text = "${(currentValue * 100).toInt()}% (${if (change >= 0) "+" else ""}$change%)",
                    style = MaterialTheme.typography.labelMedium,
                    color = color,
                    fontWeight = FontWeight.Medium
                )
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        if (data.isNotEmpty()) {
            MiniLineChart(
                data = data,
                color = color,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp)
            )
        } else {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp)
                    .background(
                        MaterialTheme.colorScheme.surfaceVariant,
                        RoundedCornerShape(8.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "No data available",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun MiniLineChart(
    data: List<TrendPoint>,
    color: Color,
    modifier: Modifier = Modifier
) {
    Canvas(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f))
            .padding(8.dp)
    ) {
        if (data.size < 2) return@Canvas
        
        val maxValue = data.maxOf { it.value }
        val minValue = data.minOf { it.value }
        val valueRange = maxValue - minValue
        
        if (valueRange == 0.0) return@Canvas
        
        val path = Path()
        val points = data.mapIndexed { index, point ->
            val x = (index.toFloat() / (data.size - 1)) * size.width
            val y = size.height - ((point.value - minValue) / valueRange).toFloat() * size.height
            Offset(x, y)
        }
        
        // Draw line
        path.moveTo(points.first().x, points.first().y)
        for (i in 1 until points.size) {
            path.lineTo(points[i].x, points[i].y)
        }
        
        drawPath(
            path = path,
            color = color,
            style = androidx.compose.ui.graphics.drawscope.Stroke(
                width = 2.dp.toPx(),
                cap = StrokeCap.Round
            )
        )
        
        // Draw points
        points.forEach { point ->
            drawCircle(
                color = color,
                radius = 3.dp.toPx(),
                center = point
            )
        }
    }
}

@Composable
private fun PerformanceSection(
    performanceMetrics: PerformanceMetrics,
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
                text = "System Performance",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            PerformanceMetricBar(
                title = "Response Time",
                value = performanceMetrics.averageResponseTime,
                maxValue = 1000.0,
                unit = "ms",
                color = MaterialTheme.colorScheme.primary,
                isLowerBetter = true
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            PerformanceMetricBar(
                title = "Success Rate",
                value = performanceMetrics.successRate,
                maxValue = 1.0,
                unit = "%",
                color = MaterialTheme.colorScheme.tertiary,
                isLowerBetter = false
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            PerformanceMetricBar(
                title = "Resource Utilization",
                value = performanceMetrics.resourceUtilization,
                maxValue = 1.0,
                unit = "%",
                color = MaterialTheme.colorScheme.secondary,
                isLowerBetter = false
            )
        }
    }
}

@Composable
private fun PerformanceMetricBar(
    title: String,
    value: Double,
    maxValue: Double,
    unit: String,
    color: Color,
    isLowerBetter: Boolean,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            
            val displayValue = if (unit == "%") "${(value * 100).toInt()}$unit" else "${value.toInt()}$unit"
            Text(
                text = displayValue,
                style = MaterialTheme.typography.bodyMedium,
                color = color,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        val progress = (value / maxValue).coerceIn(0.0, 1.0)
        LinearProgressIndicator(
            progress = { progress.toFloat() },
            modifier = Modifier.fillMaxWidth(),
            color = color,
            trackColor = MaterialTheme.colorScheme.surfaceVariant,
        )
        
        // Performance indicator
        val performanceLevel = when {
            (isLowerBetter && progress < 0.3) || (!isLowerBetter && progress > 0.8) -> "Excellent"
            (isLowerBetter && progress < 0.6) || (!isLowerBetter && progress > 0.6) -> "Good"
            (isLowerBetter && progress < 0.8) || (!isLowerBetter && progress > 0.4) -> "Fair"
            else -> "Needs Improvement"
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = performanceLevel,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun ThoughtTreeAnalyticsSection(
    thoughtTree: ThoughtTree,
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
                text = "Thought Tree Analysis",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                ThoughtMetricCard(
                    title = "Total Nodes",
                    value = thoughtTree.getAllNodes().size.toString(),
                    icon = Icons.Default.AccountTree,
                    color = MaterialTheme.colorScheme.primary
                )
                
                ThoughtMetricCard(
                    title = "Max Depth",
                    value = thoughtTree.getMaxDepth().toString(),
                    icon = Icons.Default.Height,
                    color = MaterialTheme.colorScheme.secondary
                )
                
                ThoughtMetricCard(
                    title = "Avg Confidence",
                    value = "${(thoughtTree.getAverageConfidence() * 100).toInt()}%",
                    icon = Icons.Default.TrendingUp,
                    color = MaterialTheme.colorScheme.tertiary
                )
                
                ThoughtMetricCard(
                    title = "Alternatives",
                    value = thoughtTree.getAlternativeCount().toString(),
                    icon = Icons.Default.AltRoute,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun ThoughtMetricCard(
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
            text = title,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun InnovationInsightsSection(
    metrics: ProjectMetrics,
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
                text = "AI-Generated Insights",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            val insights = generateInsights(metrics)
            
            insights.forEach { insight ->
                InsightCard(insight = insight)
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun InsightCard(
    insight: Insight,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = insight.color.copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = insight.icon,
                contentDescription = null,
                tint = insight.color,
                modifier = Modifier.size(20.dp)
            )
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = insight.title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium,
                    color = insight.color
                )
                Text(
                    text = insight.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

private data class Insight(
    val title: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

@Composable
private fun generateInsights(metrics: ProjectMetrics): List<Insight> {
    return listOf(
        Insight(
            title = "Strong Innovation Trajectory",
            description = "Your innovation velocity of ${(metrics.innovationVelocity * 100).toInt()}% indicates excellent creative output and solution generation.",
            icon = Icons.Default.TrendingUp,
            color = MaterialTheme.colorScheme.primary
        ),
        Insight(
            title = "Autonomy Optimization",
            description = "With ${(metrics.autonomyIndex * 100).toInt()}% autonomy, your agents are operating efficiently with minimal human intervention.",
            icon = Icons.Default.Psychology,
            color = MaterialTheme.colorScheme.secondary
        ),
        if (metrics.collaborationDensity > 0.7) {
            Insight(
                title = "High Collaboration Efficiency",
                description = "Excellent team coordination is driving superior collective intelligence outcomes.",
                icon = Icons.Default.Group,
                color = MaterialTheme.colorScheme.tertiary
            )
        } else {
            Insight(
                title = "Collaboration Opportunity",
                description = "Consider increasing agent collaboration to unlock additional innovation potential.",
                icon = Icons.Default.GroupWork,
                color = MaterialTheme.colorScheme.primary
            )
        }
    )
}