package com.synthnet.aiapp.domain.analytics

import kotlinx.datetime.Instant

// Core Analytics Models
data class ProjectAnalytics(
    val projectId: String,
    val timeRange: TimeRange,
    val generatedAt: Instant,
    val timeSeriesData: TimeSeriesData,
    val performanceMetrics: PerformanceMetrics,
    val cognitiveInsights: CognitiveInsights,
    val collaborationAnalysis: CollaborationAnalysis,
    val predictions: PredictionResults,
    val summary: String
)

data class SystemAnalytics(
    val timeRange: TimeRange,
    val generatedAt: Instant,
    val systemMetrics: SystemMetrics,
    val trends: List<SystemTrend>,
    val benchmarks: SystemBenchmarks,
    val recommendations: List<String>
)

data class AgentPerformanceReport(
    val agentId: String,
    val timeRange: TimeRange,
    val generatedAt: Instant,
    val performanceMetrics: AgentPerformanceMetrics,
    val learningProgress: LearningProgress,
    val strengths: List<String>,
    val improvementAreas: List<String>,
    val competencyMap: Map<String, Double>
)

data class InnovationReport(
    val scope: InnovationScope,
    val projectId: String? = null,
    val timeRange: TimeRange,
    val generatedAt: Instant,
    val innovationMetrics: InnovationMetrics,
    val breakthroughs: List<Breakthrough>,
    val creativityPatterns: CreativityPatterns,
    val innovationFactors: List<InnovationFactor>
)

// Time Series Models
data class TimeSeriesData(
    val timeRange: TimeRange,
    val dataPoints: List<TimeSeriesPoint>
)

data class TimeSeriesPoint(
    val timestamp: Instant,
    val innovationVelocity: Double,
    val autonomyIndex: Double,
    val collaborationDensity: Double,
    val errorRate: Double,
    val agentActivity: Double
)

enum class TimeRange(val days: Int) {
    LAST_7_DAYS(7),
    LAST_30_DAYS(30),
    LAST_90_DAYS(90),
    LAST_YEAR(365)
}

// Performance Models
data class PerformanceMetrics(
    val totalTasksCompleted: Int,
    val averageSuccessRate: Double,
    val averageResponseTime: Double,
    val totalCollaborations: Int,
    val activeCollaborations: Int,
    val productivityScore: Double,
    val qualityScore: Double,
    val efficiencyScore: Double
)

data class AgentPerformanceMetrics(
    val taskCompletionRate: Double,
    val averageResponseTime: Double,
    val qualityScore: Double,
    val collaborationScore: Double,
    val innovationContribution: Double,
    val learningRate: Double
)

data class LearningProgress(
    val improvementRate: Double,
    val skillDevelopment: Map<String, Double>,
    val knowledgeAcquisition: Double
)

// Cognitive Analysis Models
data class CognitiveInsights(
    val averageConfidence: Double,
    val thoughtTypeDistribution: Map<com.synthnet.aiapp.data.entities.ThoughtType, Int>,
    val complexityDistribution: Map<String, Int>,
    val reasoningPatterns: List<String>,
    val creativityMetrics: CreativityMetrics,
    val cognitiveLoad: Double
)

data class CreativityMetrics(
    val noveltyScore: Double,
    val diversityScore: Double,
    val originalityIndex: Double
)

// Collaboration Analysis Models
data class CollaborationAnalysis(
    val averageParticipants: Double,
    val averageKnowledgeExchanges: Double,
    val consensusRate: Double,
    val networkMetrics: NetworkMetrics,
    val communicationPatterns: List<String>,
    val collaborationEffectiveness: Double
)

data class NetworkMetrics(
    val density: Double,
    val averageConnections: Double,
    val centralityMeasures: Map<String, Double>
)

// Prediction Models
data class PredictionResults(
    val innovationVelocityTrend: Double,
    val autonomyIndexTrend: Double,
    val predictedMilestones: List<PredictedMilestone>,
    val riskFactors: List<String>,
    val opportunities: List<String>
)

data class PredictedMilestone(
    val name: String,
    val estimatedDate: Instant,
    val confidence: Double,
    val description: String
)

// System-wide Models
data class SystemMetrics(
    val totalProjects: Int,
    val activeProjects: Int,
    val totalAgents: Int,
    val averageProjectHealth: Double,
    val systemUtilization: Double,
    val globalInnovationRate: Double
)

data class SystemTrend(
    val name: String,
    val description: String,
    val strength: Double,
    val timeframe: TimeRange
)

data class SystemBenchmarks(
    val topPerformingProjectId: String?,
    val averageTimeToAutonomy: Double,
    val bestPracticePatterns: List<String>,
    val performancePercentiles: Map<String, Double>
)

// Innovation Models
enum class InnovationScope {
    PROJECT,
    AGENT,
    SYSTEM_WIDE
}

data class InnovationMetrics(
    val overallInnovationRate: Double,
    val breakthroughPotential: Double,
    val creativityIndex: Double,
    val noveltyScore: Double
)

data class Breakthrough(
    val id: String,
    val title: String,
    val description: String,
    val impact: Double,
    val projectId: String?,
    val discoveredAt: Instant
)

data class CreativityPatterns(
    val dominantPatterns: List<String>,
    val emergentBehaviors: List<String>,
    val creativityDistribution: Map<String, Int>
)

data class InnovationFactor(
    val name: String,
    val impact: Double,
    val description: String
)

// Event Tracking Models
data class AnalyticsEvent(
    val id: String,
    val type: AnalyticsEventType,
    val properties: Map<String, Any>,
    val projectId: String? = null,
    val agentId: String? = null,
    val timestamp: Instant
)

enum class AnalyticsEventType {
    PROJECT_CREATED,
    PROJECT_COMPLETED,
    AGENT_ACTIVATED,
    AGENT_TRAINED,
    THOUGHT_GENERATED,
    COLLABORATION_STARTED,
    COLLABORATION_ENDED,
    MILESTONE_REACHED,
    ERROR_OCCURRED,
    INSIGHT_DISCOVERED,
    USER_INTERACTION,
    AUTONOMY_PROMOTED,
    KNOWLEDGE_SHARED,
    DECISION_MADE,
    BREAKTHROUGH_ACHIEVED
}