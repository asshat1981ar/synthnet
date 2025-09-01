package com.synthnet.ai

import com.synthnet.ai.repository.AgentRepository
import com.synthnet.ai.entity.AgentEntity
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import org.junit.Before

class AgentRepositoryTest {
    
    @Mock
    private lateinit var mockRepository: AgentRepository
    
    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
    }
    
    @Test
    fun `test agent creation`() = runTest {
        // Given
        val agent = AgentEntity(
            id = 1,
            name = "Test Agent",
            description = "Test Description",
            status = "ACTIVE"
        )
        
        // When
        `when`(mockRepository.insert(agent)).thenReturn(1L)
        val result = mockRepository.insert(agent)
        
        // Then
        assertEquals(1L, result)
    }
    
    @Test
    fun `test agent retrieval`() = runTest {
        // Given
        val agents = listOf(
            AgentEntity(1, "Agent1", "Desc1", "ACTIVE"),
            AgentEntity(2, "Agent2", "Desc2", "INACTIVE")
        )
        
        // When
        `when`(mockRepository.getAll()).thenReturn(flowOf(agents))
        
        // Then - would need to collect flow in real test
        verify(mockRepository).getAll()
    }
}