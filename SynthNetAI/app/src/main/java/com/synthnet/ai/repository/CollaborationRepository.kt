package com.synthnet.ai.repository

import com.synthnet.ai.database.CollaborationDao
import com.synthnet.ai.entity.CollaborationEntity
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CollaborationRepository @Inject constructor(
    private val collaborationDao: CollaborationDao
) {
    
    fun getAll(): Flow<List<CollaborationEntity>> = collaborationDao.getAll()
    
    suspend fun getById(id: Long): CollaborationEntity? = collaborationDao.getById(id)
    
    suspend fun insert(entity: CollaborationEntity): Long = collaborationDao.insert(entity)
    
    suspend fun update(entity: CollaborationEntity) = collaborationDao.update(entity)
    
    suspend fun delete(entity: CollaborationEntity) = collaborationDao.delete(entity)
    
    suspend fun deleteAll() = collaborationDao.deleteAll()
}