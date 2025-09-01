package com.synthnet.ai.repository

import com.synthnet.ai.database.AgentDao
import com.synthnet.ai.entity.AgentEntity
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AgentRepository @Inject constructor(
    private val agentDao: AgentDao
) {
    
    fun getAll(): Flow<List<AgentEntity>> = agentDao.getAll()
    
    suspend fun getById(id: Long): AgentEntity? = agentDao.getById(id)
    
    suspend fun insert(entity: AgentEntity): Long = agentDao.insert(entity)
    
    suspend fun update(entity: AgentEntity) = agentDao.update(entity)
    
    suspend fun delete(entity: AgentEntity) = agentDao.delete(entity)
    
    suspend fun deleteAll() = agentDao.deleteAll()
}