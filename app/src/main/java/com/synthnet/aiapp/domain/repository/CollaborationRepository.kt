package com.synthnet.aiapp.domain.repository

import com.synthnet.aiapp.domain.models.Collaboration
import com.synthnet.aiapp.domain.models.AgentPresence
import com.synthnet.aiapp.data.entities.SessionType
import com.synthnet.aiapp.data.entities.CollaborationStatus
import kotlinx.coroutines.flow.Flow

interface CollaborationRepository {
    fun getAllCollaborations(): Flow<List<Collaboration>>
    
    suspend fun getCollaborationById(collaborationId: String): Collaboration?
    
    fun getCollaborationsByProject(projectId: String): Flow<List<Collaboration>>
    
    fun getCollaborationsByStatus(status: CollaborationStatus): Flow<List<Collaboration>>
    
    fun getCollaborationsByType(type: SessionType): Flow<List<Collaboration>>
    
    suspend fun getActiveCollaborationByProject(projectId: String): Collaboration?
    
    suspend fun createCollaboration(collaboration: Collaboration): Result<String>
    
    suspend fun updateCollaboration(collaboration: Collaboration): Result<Unit>
    
    suspend fun deleteCollaboration(collaborationId: String): Result<Unit>
    
    suspend fun updateCollaborationStatus(collaborationId: String, status: CollaborationStatus): Result<Unit>
    
    suspend fun joinCollaboration(collaborationId: String, agentId: String): Result<Unit>
    
    suspend fun leaveCollaboration(collaborationId: String, agentId: String): Result<Unit>
    
    suspend fun updateAgentPresence(collaborationId: String, presence: AgentPresence): Result<Unit>
    
    suspend fun broadcastKnowledge(collaborationId: String, knowledge: String, senderId: String): Result<Unit>
    
    suspend fun reachConsensus(collaborationId: String, decision: String): Result<Unit>
    
    suspend fun getCollaborationCountByProject(projectId: String): Int
    
    suspend fun getAverageKnowledgeExchangesByProject(projectId: String): Double?
}