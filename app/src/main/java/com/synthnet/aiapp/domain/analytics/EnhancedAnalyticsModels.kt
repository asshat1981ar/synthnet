package com.synthnet.aiapp.domain.analytics

import kotlinx.datetime.Instant

// Real-time Analytics Models
data class RealtimeInsights(
    val projectId: String,
    val timestamp: Instant,
    val activeAgents: Int,
    val recentThoughtVelocity: Double,
    val collaborationIntensity: Double,
    val innovationMomentum: Double,
    val systemHealth: Double,
    val emergingPatterns: List<EmergingPattern>,
    val alerts: List<RealtimeAlert>
)

data class EmergingPattern(
    val type: PatternType,
    val description: String,
    val strength: Double,
    val confidence: Double,
    val timeframe: String = "current",
    val affectedEntities: List<String> = emptyList()
)

enum class PatternType {
    THOUGHT_CLUSTERING,
    COLLABORATION_PREFERENCE,
    PERFORMANCE_TREND,
    INNOVATION_BURST,
    COMMUNICATION_FLOW,
    LEARNING_ACCELERATION
}

data class RealtimeAlert(
    val type: AlertType,
    val severity: AlertSeverity,
    val message: String,
    val affectedEntities: List<String>,
    val timestamp: Instant = kotlinx.datetime.Clock.System.now(),
    val actionRequired: Boolean = true,
    val suggestedActions: List<String> = emptyList()
)

enum class AlertType {
    PERFORMANCE,
    QUALITY,
    COLLABORATION,
    SYSTEM_HEALTH,
    SECURITY,
    RESOURCE_UTILIZATION
}

enum class AlertSeverity {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

// Export Configuration Models
data class AnalyticsExportConfig(
    val scope: ExportScope,
    val format: ExportFormat,
    val timeRange: TimeRange,
    val outputPath: String,
    val projectId: String? = null,
    val agentId: String? = null,
    val includeMetadata: Boolean = true,
    val compression: Boolean = false,
    val filters: Map<String, Any> = emptyMap()
)

enum class ExportScope {
    PROJECT,
    SYSTEM_WIDE,
    AGENT_SPECIFIC,
    TIME_RANGE
}

enum class ExportFormat {
    JSON,
    CSV,
    XML,
    EXCEL
}

data class ExportData(
    val type: String,
    val data: Map<String, Any>,
    val metadata: Map<String, Any> = emptyMap()
)

data class ExportResult(
    val format: ExportFormat,
    val filePath: String,
    val size: Long,
    val recordCount: Int,
    val generatedAt: Instant,
    val checksum: String? = null,
    val exportDuration: Long = 0L
)

// Advanced Report Models
data class AdvancedReportConfig(
    val title: String,
    val scope: ReportScope,
    val timeRange: TimeRange,
    val projectId: String? = null,
    val includeSummary: Boolean = true,
    val includePerformance: Boolean = true,
    val includeCollaboration: Boolean = true,
    val includeInnovation: Boolean = true,
    val includePredictions: Boolean = true,
    val includeRecommendations: Boolean = true,
    val filters: Map<String, Any> = emptyMap(),
    val customSections: List<CustomSection> = emptyList()
)

enum class ReportScope {
    PROJECT,
    AGENT,
    SYSTEM,
    COMPARISON
}

data class CustomSection(
    val title: String,
    val query: String,
    val visualization: String = "table"
)

data class AdvancedReport(
    val id: String,
    val title: String,
    val generatedAt: Instant,
    val timeRange: TimeRange,
    val sections: List<ReportSection>,
    val metadata: Map<String, Any>,
    val summary: ReportSummary? = null,
    val appendices: List<ReportAppendix> = emptyList()
)

data class ReportSection(
    val title: String,
    val content: String,
    val charts: List<ChartData> = emptyList(),
    val insights: List<String> = emptyList(),
    val recommendations: List<String> = emptyList(),
    val dataQuality: Double = 1.0
)

data class ChartData(
    val id: String,
    val type: String, // bar, line, pie, scatter, network, etc.
    val data: Map<String, Any>,
    val config: Map<String, Any> = emptyMap()
)

data class ReportSummary(
    val overallScore: Double,
    val keyFindings: List<String>,
    val criticalIssues: List<String>,
    val topRecommendations: List<String>
)

data class ReportAppendix(
    val title: String,
    val content: String,
    val type: AppendixType = AppendixType.TEXT
)

enum class AppendixType {
    TEXT,
    TABLE,
    CHART,
    RAW_DATA
}

// Additional Analytics Models
data class AnalyticsEventStream(
    val streamId: String,
    val events: List<AnalyticsEvent>,
    val startTime: Instant,
    val endTime: Instant?,
    val eventCount: Int,
    val avgEventsPerSecond: Double
)

data class PerformanceBenchmark(
    val category: String,
    val metric: String,
    val currentValue: Double,
    val benchmarkValue: Double,
    val percentile: Double,
    val trend: TrendDirection,
    val recommendation: String? = null
)

enum class TrendDirection {
    IMPROVING,
    DECLINING,
    STABLE,
    VOLATILE
}

data class AnalyticsDashboard(
    val id: String,
    val title: String,
    val widgets: List<DashboardWidget>,
    val refreshRate: Long = 30000L, // milliseconds
    val lastUpdated: Instant,
    val layout: DashboardLayout
)

data class DashboardWidget(
    val id: String,
    val type: WidgetType,
    val title: String,
    val config: Map<String, Any>,
    val position: WidgetPosition,
    val dataSource: String,
    val refreshInterval: Long = 0L // 0 = use dashboard refresh rate
)

enum class WidgetType {
    METRIC_CARD,
    LINE_CHART,
    BAR_CHART,
    PIE_CHART,
    TABLE,
    GAUGE,
    ALERT_LIST,
    RECENT_ACTIVITY
}

data class WidgetPosition(
    val x: Int,
    val y: Int,
    val width: Int,
    val height: Int
)

data class DashboardLayout(
    val columns: Int = 12,
    val rows: Int = 8,
    val theme: String = "default"
)

// ML/AI Analytics Models
data class PredictiveModel(
    val id: String,
    val name: String,
    val type: ModelType,
    val features: List<String>,
    val accuracy: Double,
    val trainedAt: Instant,
    val lastPrediction: Instant?,
    val predictionCount: Int = 0
)

enum class ModelType {
    LINEAR_REGRESSION,
    RANDOM_FOREST,
    NEURAL_NETWORK,
    TIME_SERIES,
    CLUSTERING,
    CLASSIFICATION
}

data class AnomalyDetectionResult(
    val entityId: String,
    val entityType: String,
    val anomalyScore: Double,
    val anomalyType: AnomalyType,
    val description: String,
    val detectedAt: Instant,
    val confidence: Double,
    val expectedValue: Double?,
    val actualValue: Double?,
    val context: Map<String, Any> = emptyMap()
)

enum class AnomalyType {
    PERFORMANCE_DROP,
    UNUSUAL_PATTERN,
    DATA_QUALITY_ISSUE,
    BEHAVIORAL_CHANGE,
    SYSTEM_DRIFT
}

data class DataQualityReport(
    val entityType: String,
    val entityId: String?,
    val completeness: Double,
    val accuracy: Double,
    val consistency: Double,
    val timeliness: Double,
    val validity: Double,
    val overallScore: Double,
    val issues: List<DataQualityIssue>,
    val generatedAt: Instant
)

data class DataQualityIssue(
    val type: DataQualityIssueType,
    val severity: Severity,
    val description: String,
    val affectedFields: List<String>,
    val suggestedFix: String? = null
)

enum class DataQualityIssueType {
    MISSING_DATA,
    INVALID_FORMAT,
    OUTLIER,
    INCONSISTENCY,
    DUPLICATION,
    STALENESS
}

enum class Severity {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

// Collaboration Analytics Models
data class CollaborationNetwork(
    val nodes: List<NetworkNode>,
    val edges: List<NetworkEdge>,
    val metrics: NetworkMetrics,
    val communities: List<NetworkCommunity> = emptyList()
)

data class NetworkNode(
    val id: String,
    val label: String,
    val type: NodeType,
    val metrics: NodeMetrics,
    val properties: Map<String, Any> = emptyMap()
)

enum class NodeType {
    AGENT,
    PROJECT,
    THOUGHT,
    COLLABORATION,
    DECISION
}

data class NodeMetrics(
    val degree: Int,
    val betweennessCentrality: Double,
    val closenessCentrality: Double,
    val eigenvectorCentrality: Double,
    val clusteringCoefficient: Double
)

data class NetworkEdge(
    val source: String,
    val target: String,
    val weight: Double,
    val type: EdgeType,
    val properties: Map<String, Any> = emptyMap()
)

enum class EdgeType {
    COLLABORATION,
    COMMUNICATION,
    KNOWLEDGE_TRANSFER,
    INFLUENCE,
    DEPENDENCY
}

data class NetworkCommunity(
    val id: String,
    val members: List<String>,
    val cohesion: Double,
    val modularity: Double,
    val description: String
)