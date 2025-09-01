package com.synthnet.ai.database

import androidx.room.*
import com.synthnet.ai.entity.CollaborationEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CollaborationDao {
    
    @Query("SELECT * FROM collaboration_table ORDER BY createdAt DESC")
    fun getAll(): Flow<List<CollaborationEntity>>
    
    @Query("SELECT * FROM collaboration_table WHERE id = :id")
    suspend fun getById(id: Long): CollaborationEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: CollaborationEntity): Long
    
    @Update
    suspend fun update(entity: CollaborationEntity)
    
    @Delete
    suspend fun delete(entity: CollaborationEntity)
    
    @Query("DELETE FROM collaboration_table")
    suspend fun deleteAll()
}