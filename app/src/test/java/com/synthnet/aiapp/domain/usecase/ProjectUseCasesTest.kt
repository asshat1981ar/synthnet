package com.synthnet.aiapp.domain.usecase

import com.synthnet.aiapp.domain.models.Project
import com.synthnet.aiapp.domain.repository.ProjectRepository
import com.synthnet.aiapp.data.entities.AutonomyLevel
import com.synthnet.aiapp.data.entities.ProjectStatus
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import kotlinx.datetime.Clock
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import kotlin.test.assertEquals
import kotlin.test.assertNotNull

class ProjectUseCasesTest {
    
    @Mock
    private lateinit var projectRepository: ProjectRepository
    
    private lateinit var getAllProjectsUseCase: GetAllProjectsUseCase
    private lateinit var getProjectByIdUseCase: GetProjectByIdUseCase
    private lateinit var createProjectUseCase: CreateProjectUseCase
    
    private val testProject = Project(
        id = "test_project_1",
        name = "Test Project",
        description = "A test project",
        autonomyLevel = AutonomyLevel.ASSISTED,
        status = ProjectStatus.ACTIVE,
        createdAt = Clock.System.now(),
        updatedAt = Clock.System.now()
    )
    
    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        getAllProjectsUseCase = GetAllProjectsUseCase(projectRepository)
        getProjectByIdUseCase = GetProjectByIdUseCase(projectRepository)
        createProjectUseCase = CreateProjectUseCase(projectRepository)
    }
    
    @Test
    fun `getAllProjects returns flow of projects`() = runTest {
        // Given
        val projectsList = listOf(testProject)
        `when`(projectRepository.getAllProjects()).thenReturn(flowOf(projectsList))
        
        // When
        val result = getAllProjectsUseCase()
        
        // Then
        result.collect { projects ->
            assertEquals(1, projects.size)
            assertEquals(testProject.id, projects[0].id)
        }
    }
    
    @Test
    fun `getProjectById returns correct project`() = runTest {
        // Given
        `when`(projectRepository.getProjectById("test_project_1")).thenReturn(testProject)
        
        // When
        val result = getProjectByIdUseCase("test_project_1")
        
        // Then
        assertNotNull(result)
        assertEquals(testProject.id, result.id)
        assertEquals(testProject.name, result.name)
    }
    
    @Test
    fun `createProject returns success result`() = runTest {
        // Given
        `when`(projectRepository.createProject(testProject)).thenReturn(Result.success("test_project_1"))
        
        // When
        val result = createProjectUseCase(testProject)
        
        // Then
        assert(result.isSuccess)
        assertEquals("test_project_1", result.getOrNull())
    }
}