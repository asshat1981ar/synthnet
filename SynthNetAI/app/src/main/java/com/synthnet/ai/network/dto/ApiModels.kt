package com.synthnet.ai.network.dto

import kotlinx.serialization.Serializable

@Serializable
data class AgentResponse(
    val id: String,
    val name: String,
    val type: String,
    val status: String,
    val capabilities: List<String>,
    val createdAt: String,
    val lastActive: String
)

@Serializable
data class CreateAgentRequest(
    val name: String,
    val type: String,
    val capabilities: List<String>,
    val configuration: Map<String, String>
)

@Serializable
data class UpdateAgentRequest(
    val name: String?,
    val status: String?,
    val configuration: Map<String, String>?
)

@Serializable
data class ExecuteAgentRequest(
    val input: String,
    val parameters: Map<String, String>
)

@Serializable
data class AgentExecutionResponse(
    val executionId: String,
    val result: String,
    val status: String,
    val duration: Long,
    val timestamp: String
)

@Serializable
data class CollaborationSessionResponse(
    val id: String,
    val name: String,
    val participants: List<String>,
    val status: String,
    val createdAt: String
)

@Serializable
data class CreateSessionRequest(
    val name: String,
    val invitees: List<String>,
    val agentIds: List<String>
)

@Serializable
data class AnalyticsDashboardResponse(
    val totalAgents: Int,
    val activeSessions: Int,
    val totalExecutions: Long,
    val performanceMetrics: PerformanceMetrics
)

@Serializable
data class PerformanceMetrics(
    val averageResponseTime: Double,
    val successRate: Double,
    val throughput: Double
)

@Serializable
data class MetricsResponse(
    val timeRange: String,
    val dataPoints: List<MetricDataPoint>
)

@Serializable
data class MetricDataPoint(
    val timestamp: String,
    val value: Double,
    val metric: String
)