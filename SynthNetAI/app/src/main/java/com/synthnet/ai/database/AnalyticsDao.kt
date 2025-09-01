package com.synthnet.ai.database

import androidx.room.*
import com.synthnet.ai.entity.AnalyticsEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface AnalyticsDao {
    
    @Query("SELECT * FROM analytics_table ORDER BY createdAt DESC")
    fun getAll(): Flow<List<AnalyticsEntity>>
    
    @Query("SELECT * FROM analytics_table WHERE id = :id")
    suspend fun getById(id: Long): AnalyticsEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: AnalyticsEntity): Long
    
    @Update
    suspend fun update(entity: AnalyticsEntity)
    
    @Delete
    suspend fun delete(entity: AnalyticsEntity)
    
    @Query("DELETE FROM analytics_table")
    suspend fun deleteAll()
}