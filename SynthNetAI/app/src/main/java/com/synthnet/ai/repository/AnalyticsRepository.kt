package com.synthnet.ai.repository

import com.synthnet.ai.database.AnalyticsDao
import com.synthnet.ai.entity.AnalyticsEntity
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AnalyticsRepository @Inject constructor(
    private val analyticsDao: AnalyticsDao
) {
    
    fun getAll(): Flow<List<AnalyticsEntity>> = analyticsDao.getAll()
    
    suspend fun getById(id: Long): AnalyticsEntity? = analyticsDao.getById(id)
    
    suspend fun insert(entity: AnalyticsEntity): Long = analyticsDao.insert(entity)
    
    suspend fun update(entity: AnalyticsEntity) = analyticsDao.update(entity)
    
    suspend fun delete(entity: AnalyticsEntity) = analyticsDao.delete(entity)
    
    suspend fun deleteAll() = analyticsDao.deleteAll()
}