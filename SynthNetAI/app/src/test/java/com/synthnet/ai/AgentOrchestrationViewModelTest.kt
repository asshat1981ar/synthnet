package com.synthnet.ai

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.synthnet.ai.AgentOrchestrationActivityViewModel
import com.synthnet.ai.AgentOrchestrationAction
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.Assert.*

@OptIn(ExperimentalCoroutinesApi::class)
class AgentOrchestrationViewModelTest {
    
    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()
    
    private val testDispatcher = StandardTestDispatcher()
    private lateinit var viewModel: AgentOrchestrationActivityViewModel
    
    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = AgentOrchestrationActivityViewModel()
    }
    
    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }
    
    @Test
    fun `test initial state`() {
        val initialState = viewModel.uiState.value
        assertFalse(initialState.isLoading)
        assertEquals("", initialState.data)
        assertNull(initialState.error)
    }
    
    @Test
    fun `test load data action`() = runTest {
        // When
        viewModel.onAction(AgentOrchestrationAction.LoadData)
        
        // Then
        assertTrue(viewModel.uiState.value.isLoading)
        
        // Advance time to complete loading
        advanceTimeBy(1100)
        
        assertFalse(viewModel.uiState.value.isLoading)
        assertTrue(viewModel.uiState.value.data.isNotEmpty())
    }
}