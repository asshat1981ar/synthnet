package com.synthnet.ai.database

import androidx.room.*
import com.synthnet.ai.entity.AgentEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface AgentDao {
    
    @Query("SELECT * FROM agent_table ORDER BY createdAt DESC")
    fun getAll(): Flow<List<AgentEntity>>
    
    @Query("SELECT * FROM agent_table WHERE id = :id")
    suspend fun getById(id: Long): AgentEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: AgentEntity): Long
    
    @Update
    suspend fun update(entity: AgentEntity)
    
    @Delete
    suspend fun delete(entity: AgentEntity)
    
    @Query("DELETE FROM agent_table")
    suspend fun deleteAll()
}