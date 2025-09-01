package com.synthnet.aiapp.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.synthnet.aiapp.data.entities.AutonomyLevel
import com.synthnet.aiapp.data.entities.ProjectStatus
import com.synthnet.aiapp.domain.models.Project
import com.synthnet.aiapp.domain.models.ProjectMetrics
import com.synthnet.aiapp.domain.usecase.CreateProjectUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.datetime.Clock
import javax.inject.Inject

@HiltViewModel
class CreateProjectViewModel @Inject constructor(
    private val createProjectUseCase: CreateProjectUseCase
    // Note: Additional dependencies would be injected in a complete implementation
    // private val aiSuggestionService: AISuggestionService,
    // private val validationService: ValidationService
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(CreateProjectUiState())
    val uiState: StateFlow<CreateProjectUiState> = _uiState.asStateFlow()
    
    init {
        loadNameSuggestions()
    }
    
    fun createProject(
        name: String,
        description: String,
        autonomyLevel: AutonomyLevel,
        tags: List<String>,
        enableRealTimeCollaboration: Boolean = true,
        enableAdvancedAnalytics: Boolean = false
    ) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true, error = null)
                
                // Validate inputs
                val validationResult = validateProjectInput(name, description)
                if (validationResult != null) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = validationResult
                    )
                    return@launch
                }
                
                val project = Project(
                    id = generateProjectId(),
                    name = name.trim(),
                    description = description.trim(),
                    autonomyLevel = autonomyLevel,
                    status = ProjectStatus.ACTIVE,
                    createdAt = Clock.System.now(),
                    updatedAt = Clock.System.now(),
                    tags = tags,
                    metrics = ProjectMetrics()
                )
                
                val result = createProjectUseCase(project)
                
                result.fold(
                    onSuccess = { projectId ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            createdProjectId = projectId,
                            error = null
                        )
                    },
                    onFailure = { error ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            error = error.message ?: "Failed to create project"
                        )
                    }
                )
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Unknown error occurred"
                )
            }
        }
    }
    
    fun validateProjectName(name: String): ValidationResult {
        return when {
            name.isBlank() -> ValidationResult.Error("Project name is required")
            name.length < 3 -> ValidationResult.Error("Project name must be at least 3 characters")
            name.length > 50 -> ValidationResult.Error("Project name must be less than 50 characters")
            !name.matches(Regex("^[a-zA-Z0-9\\s\\-_]+$")) -> ValidationResult.Error("Project name contains invalid characters")
            else -> ValidationResult.Valid
        }
    }
    
    fun validateProjectDescription(description: String): ValidationResult {
        return when {
            description.isBlank() -> ValidationResult.Error("Project description is required")
            description.length < 10 -> ValidationResult.Error("Description must be at least 10 characters")
            description.length > 500 -> ValidationResult.Error("Description must be less than 500 characters")
            else -> ValidationResult.Valid
        }
    }
    
    fun generateNameSuggestions(input: String) {
        viewModelScope.launch {
            try {
                // Mock implementation - would use real AI suggestion service
                val suggestions = generateMockSuggestions(input)
                _uiState.value = _uiState.value.copy(
                    nameSuggestions = suggestions
                )
            } catch (e: Exception) {
                // Silently fail for suggestions - not critical
            }
        }
    }
    
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
    
    fun reset() {
        _uiState.value = CreateProjectUiState()
        loadNameSuggestions()
    }
    
    private fun loadNameSuggestions() {
        viewModelScope.launch {
            try {
                // Mock implementation - load default suggestions
                val defaultSuggestions = listOf(
                    "Smart Assistant AI",
                    "Intelligent Analyzer",
                    "Neural Network Helper",
                    "AI Content Creator",
                    "Autonomous Researcher",
                    "Cognitive Assistant"
                )
                
                _uiState.value = _uiState.value.copy(
                    nameSuggestions = defaultSuggestions
                )
            } catch (e: Exception) {
                // Fail silently for suggestions
            }
        }
    }
    
    private fun validateProjectInput(name: String, description: String): String? {
        val nameValidation = validateProjectName(name)
        if (nameValidation is ValidationResult.Error) {
            return nameValidation.message
        }
        
        val descriptionValidation = validateProjectDescription(description)
        if (descriptionValidation is ValidationResult.Error) {
            return descriptionValidation.message
        }
        
        return null
    }
    
    private fun generateMockSuggestions(input: String): List<String> {
        val keywords = input.toLowerCase().split(" ").filter { it.isNotBlank() }
        val suggestions = mutableListOf<String>()
        
        keywords.forEach { keyword ->
            when (keyword) {
                "ai", "artificial" -> {
                    suggestions.addAll(listOf("AI Assistant", "Smart AI Helper", "AI Companion"))
                }
                "chat", "conversation" -> {
                    suggestions.addAll(listOf("Chat AI", "Conversation Bot", "Interactive Assistant"))
                }
                "analyze", "analysis" -> {
                    suggestions.addAll(listOf("Data Analyzer AI", "Intelligence Analyzer", "Smart Analytics"))
                }
                "create", "creative" -> {
                    suggestions.addAll(listOf("Creative AI Assistant", "Content Creator AI", "Innovation AI"))
                }
                else -> {
                    suggestions.add("${keyword.replaceFirstChar { it.uppercaseChar() }} AI Assistant")
                }
            }
        }
        
        return suggestions.distinct().take(6)
    }
    
    private fun generateProjectId(): String {
        return "project_${System.currentTimeMillis()}"
    }
}

data class CreateProjectUiState(
    val isLoading: Boolean = false,
    val createdProjectId: String? = null,
    val nameSuggestions: List<String> = emptyList(),
    val error: String? = null
)

sealed class ValidationResult {
    object Valid : ValidationResult()
    data class Error(val message: String) : ValidationResult()
}