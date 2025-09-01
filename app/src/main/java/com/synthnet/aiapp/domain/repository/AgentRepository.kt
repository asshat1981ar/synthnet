package com.synthnet.aiapp.domain.repository

import com.synthnet.aiapp.domain.models.Agent
import com.synthnet.aiapp.domain.models.AgentResponse
import com.synthnet.aiapp.data.entities.AgentRole
import com.synthnet.aiapp.data.entities.AgentStatus
import kotlinx.coroutines.flow.Flow

interface AgentRepository {
    fun getAllAgents(): Flow<List<Agent>>
    
    suspend fun getAgentById(agentId: String): Agent?
    
    fun getAgentsByProject(projectId: String): Flow<List<Agent>>
    
    fun getAgentsByRole(role: AgentRole): Flow<List<Agent>>
    
    fun getAgentsByStatus(status: AgentStatus): Flow<List<Agent>>
    
    suspend fun getAgentByProjectAndRole(projectId: String, role: AgentRole): Agent?
    
    suspend fun createAgent(agent: Agent): Result<String>
    
    suspend fun updateAgent(agent: Agent): Result<Unit>
    
    suspend fun deleteAgent(agentId: String): Result<Unit>
    
    suspend fun updateAgentStatus(agentId: String, status: AgentStatus): Result<Unit>
    
    suspend fun processAgentRequest(agentId: String, request: String): Result<AgentResponse>
    
    suspend fun trainAgent(agentId: String, data: List<String>): Result<Unit>
    
    suspend fun getAgentCountByProject(projectId: String): Int
    
    suspend fun getAgentCountByStatus(status: AgentStatus): Int
    
    suspend fun activateAgent(agentId: String): Result<Unit>
    
    suspend fun deactivateAgent(agentId: String): Result<Unit>
}