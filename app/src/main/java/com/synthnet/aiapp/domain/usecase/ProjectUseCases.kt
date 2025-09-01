package com.synthnet.aiapp.domain.usecase

import com.synthnet.aiapp.domain.models.Project
import com.synthnet.aiapp.domain.repository.ProjectRepository
import com.synthnet.aiapp.data.entities.ProjectStatus
import com.synthnet.aiapp.data.entities.AutonomyLevel
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetAllProjectsUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    operator fun invoke(): Flow<List<Project>> = repository.getAllProjects()
}

class GetProjectByIdUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    suspend operator fun invoke(projectId: String): Project? {
        return repository.getProjectById(projectId)
    }
}

class CreateProjectUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    suspend operator fun invoke(project: Project): Result<String> {
        return repository.createProject(project)
    }
}

class UpdateProjectUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    suspend operator fun invoke(project: Project): Result<Unit> {
        return repository.updateProject(project)
    }
}

class DeleteProjectUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    suspend operator fun invoke(projectId: String): Result<Unit> {
        return repository.deleteProject(projectId)
    }
}

class SearchProjectsUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    operator fun invoke(query: String): Flow<List<Project>> {
        return repository.searchProjects(query)
    }
}

class GetProjectsByStatusUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    operator fun invoke(status: ProjectStatus): Flow<List<Project>> {
        return repository.getProjectsByStatus(status)
    }
}

class PromoteProjectAutonomyUseCase @Inject constructor(
    private val repository: ProjectRepository
) {
    suspend operator fun invoke(projectId: String): Result<AutonomyLevel> {
        return repository.promoteProjectAutonomy(projectId)
    }
}