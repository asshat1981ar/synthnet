package com.synthnet.aiapp.domain.repository

import com.synthnet.aiapp.domain.models.Thought
import com.synthnet.aiapp.domain.models.ThoughtTree
import com.synthnet.aiapp.data.entities.ThoughtType
import kotlinx.coroutines.flow.Flow

interface ThoughtRepository {
    fun getAllThoughts(): Flow<List<Thought>>
    
    suspend fun getThoughtById(thoughtId: String): Thought?
    
    fun getThoughtsByProject(projectId: String): Flow<List<Thought>>
    
    fun getThoughtsByAgent(agentId: String): Flow<List<Thought>>
    
    fun getChildThoughts(parentId: String): Flow<List<Thought>>
    
    fun getRootThoughts(projectId: String): Flow<List<Thought>>
    
    fun getThoughtsByType(type: ThoughtType): Flow<List<Thought>>
    
    fun getSelectedThoughts(projectId: String): Flow<List<Thought>>
    
    fun getHighConfidenceThoughts(minConfidence: Double): Flow<List<Thought>>
    
    suspend fun createThought(thought: Thought): Result<String>
    
    suspend fun updateThought(thought: Thought): Result<Unit>
    
    suspend fun deleteThought(thoughtId: String): Result<Unit>
    
    suspend fun selectThought(thoughtId: String): Result<Unit>
    
    suspend fun deselectSiblingThoughts(projectId: String, parentId: String?): Result<Unit>
    
    suspend fun buildThoughtTree(projectId: String): ThoughtTree?
    
    suspend fun evaluateThoughtPath(thoughtIds: List<String>): Result<Double>
    
    suspend fun generateAlternatives(thoughtId: String): Result<List<String>>
    
    suspend fun getThoughtCountByProject(projectId: String): Int
    
    suspend fun getAverageConfidenceByProject(projectId: String): Double?
}