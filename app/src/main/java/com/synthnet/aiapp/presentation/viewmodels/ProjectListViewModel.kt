package com.synthnet.aiapp.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.synthnet.aiapp.domain.models.Project
import com.synthnet.aiapp.domain.usecase.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProjectListViewModel @Inject constructor(
    private val getAllProjectsUseCase: GetAllProjectsUseCase,
    private val searchProjectsUseCase: SearchProjectsUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ProjectListUiState())
    val uiState: StateFlow<ProjectListUiState> = _uiState.asStateFlow()
    
    private val _searchQuery = MutableStateFlow("")
    
    init {
        loadProjects()
    }
    
    private fun loadProjects() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true, error = null)
                
                combine(
                    getAllProjectsUseCase(),
                    _searchQuery
                ) { allProjects, query ->
                    if (query.isBlank()) {
                        allProjects
                    } else {
                        // Filter projects locally for now
                        allProjects.filter { project ->
                            project.name.contains(query, ignoreCase = true) ||
                            project.description.contains(query, ignoreCase = true) ||
                            project.tags.any { it.contains(query, ignoreCase = true) }
                        }
                    }
                }.collect { projects ->
                    _uiState.value = _uiState.value.copy(
                        projects = projects,
                        isLoading = false,
                        error = null
                    )
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Unknown error occurred"
                )
            }
        }
    }
    
    fun searchProjects(query: String) {
        _searchQuery.value = query
    }
    
    fun refreshProjects() {
        loadProjects()
    }
}

data class ProjectListUiState(
    val projects: List<Project> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)