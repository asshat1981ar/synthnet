package com.synthnet.ai.network

import com.synthnet.ai.network.dto.*
import retrofit2.Response
import retrofit2.http.*

interface SynthNetApiService {
    
    @GET("agents")
    suspend fun getAgents(): Response<List<AgentResponse>>
    
    @POST("agents")
    suspend fun createAgent(@Body agent: CreateAgentRequest): Response<AgentResponse>
    
    @GET("agents/{id}")
    suspend fun getAgent(@Path("id") id: String): Response<AgentResponse>
    
    @PUT("agents/{id}")
    suspend fun updateAgent(
        @Path("id") id: String,
        @Body agent: UpdateAgentRequest
    ): Response<AgentResponse>
    
    @DELETE("agents/{id}")
    suspend fun deleteAgent(@Path("id") id: String): Response<Unit>
    
    @POST("agents/{id}/execute")
    suspend fun executeAgent(
        @Path("id") id: String,
        @Body request: ExecuteAgentRequest
    ): Response<AgentExecutionResponse>
    
    @GET("collaboration/sessions")
    suspend fun getCollaborationSessions(): Response<List<CollaborationSessionResponse>>
    
    @POST("collaboration/sessions")
    suspend fun createSession(@Body session: CreateSessionRequest): Response<CollaborationSessionResponse>
    
    @GET("analytics/dashboard")
    suspend fun getDashboardAnalytics(): Response<AnalyticsDashboardResponse>
    
    @GET("analytics/metrics")
    suspend fun getMetrics(@Query("timeRange") timeRange: String): Response<MetricsResponse>
}