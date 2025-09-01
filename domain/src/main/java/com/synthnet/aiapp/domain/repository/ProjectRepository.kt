package com.synthnet.aiapp.domain.repository

import com.synthnet.aiapp.domain.models.Project
import com.synthnet.aiapp.domain.models.ProjectMetrics
import com.synthnet.aiapp.data.entities.ProjectStatus
import com.synthnet.aiapp.data.entities.AutonomyLevel
import kotlinx.coroutines.flow.Flow

interface ProjectRepository {
    fun getAllProjects(): Flow<List<Project>>
    
    suspend fun getProjectById(projectId: String): Project?
    
    fun getProjectsByStatus(status: ProjectStatus): Flow<List<Project>>
    
    fun getProjectsByAutonomyLevel(level: AutonomyLevel): Flow<List<Project>>
    
    fun searchProjects(query: String): Flow<List<Project>>
    
    suspend fun createProject(project: Project): Result<String>
    
    suspend fun updateProject(project: Project): Result<Unit>
    
    suspend fun deleteProject(projectId: String): Result<Unit>
    
    suspend fun updateProjectMetrics(projectId: String, metrics: ProjectMetrics): Result<Unit>
    
    suspend fun promoteProjectAutonomy(projectId: String): Result<AutonomyLevel>
    
    suspend fun getProjectCount(): Int
    
    suspend fun getProjectCountByStatus(status: ProjectStatus): Int
    
    suspend fun archiveProject(projectId: String): Result<Unit>
    
    suspend fun restoreProject(projectId: String): Result<Unit>
}