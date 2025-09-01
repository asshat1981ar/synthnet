package com.synthnet.aiapp.presentation.screens.project

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.synthnet.aiapp.data.entities.AutonomyLevel
import com.synthnet.aiapp.presentation.viewmodels.CreateProjectViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateProjectScreen(
    onNavigateBack: () -> Unit,
    onProjectCreated: (String) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: CreateProjectViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val keyboardController = LocalSoftwareKeyboardController.current
    
    var currentStep by remember { mutableStateOf(0) }
    val totalSteps = 4
    
    // Form state
    var projectName by remember { mutableStateOf("") }
    var projectDescription by remember { mutableStateOf("") }
    var selectedAutonomyLevel by remember { mutableStateOf(AutonomyLevel.ASSISTED) }
    var selectedTags by remember { mutableStateOf(setOf<String>()) }
    var customTag by remember { mutableStateOf("") }
    var enableRealTimeCollaboration by remember { mutableStateOf(true) }
    var enableAdvancedAnalytics by remember { mutableStateOf(false) }
    
    // Focus requesters
    val nameFocusRequester = remember { FocusRequester() }
    val descriptionFocusRequester = remember { FocusRequester() }
    
    // Form validation
    val isNameValid = projectName.isNotBlank() && projectName.length >= 3
    val isDescriptionValid = projectDescription.isNotBlank() && projectDescription.length >= 10
    
    LaunchedEffect(uiState.createdProjectId) {
        uiState.createdProjectId?.let { projectId ->
            onProjectCreated(projectId)
        }
    }
    
    // Auto-focus on name field when screen loads
    LaunchedEffect(Unit) {
        nameFocusRequester.requestFocus()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Create New Project",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Step ${currentStep + 1} of $totalSteps",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Progress indicator
            LinearProgressIndicator(
                progress = { (currentStep + 1).toFloat() / totalSteps },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Step content
            AnimatedContent(
                targetState = currentStep,
                transitionSpec = {
                    (slideInVertically { it } + fadeIn()).with(
                        slideOutVertically { -it } + fadeOut()
                    ).using(tween(300))
                },
                modifier = Modifier.weight(1f)
            ) { step ->
                when (step) {
                    0 -> ProjectBasicsStep(
                        projectName = projectName,
                        onNameChange = { projectName = it },
                        projectDescription = projectDescription,
                        onDescriptionChange = { projectDescription = it },
                        nameFocusRequester = nameFocusRequester,
                        descriptionFocusRequester = descriptionFocusRequester,
                        isNameValid = isNameValid,
                        isDescriptionValid = isDescriptionValid,
                        suggestions = uiState.nameSuggestions
                    )
                    1 -> AutonomySelectionStep(
                        selectedLevel = selectedAutonomyLevel,
                        onLevelSelected = { selectedAutonomyLevel = it }
                    )
                    2 -> TagsAndFeaturesStep(
                        selectedTags = selectedTags,
                        onTagsChange = { selectedTags = it },
                        customTag = customTag,
                        onCustomTagChange = { customTag = it },
                        enableRealTimeCollaboration = enableRealTimeCollaboration,
                        onRealTimeCollaborationChange = { enableRealTimeCollaboration = it },
                        enableAdvancedAnalytics = enableAdvancedAnalytics,
                        onAdvancedAnalyticsChange = { enableAdvancedAnalytics = it }
                    )
                    3 -> ReviewAndCreateStep(
                        projectName = projectName,
                        projectDescription = projectDescription,
                        autonomyLevel = selectedAutonomyLevel,
                        tags = selectedTags,
                        enableRealTimeCollaboration = enableRealTimeCollaboration,
                        enableAdvancedAnalytics = enableAdvancedAnalytics
                    )
                }
            }
            
            // Navigation buttons
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Back button
                    if (currentStep > 0) {
                        OutlinedButton(
                            onClick = { currentStep-- },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Back")
                        }
                        
                        Spacer(modifier = Modifier.width(12.dp))
                    }
                    
                    // Next/Create button
                    Button(
                        onClick = {
                            if (currentStep < totalSteps - 1) {
                                currentStep++
                                keyboardController?.hide()
                            } else {
                                viewModel.createProject(
                                    name = projectName,
                                    description = projectDescription,
                                    autonomyLevel = selectedAutonomyLevel,
                                    tags = selectedTags.toList(),
                                    enableRealTimeCollaboration = enableRealTimeCollaboration,
                                    enableAdvancedAnalytics = enableAdvancedAnalytics
                                )
                            }
                        },
                        enabled = when (currentStep) {
                            0 -> isNameValid && isDescriptionValid
                            1 -> true
                            2 -> true
                            3 -> !uiState.isLoading
                            else -> false
                        },
                        modifier = Modifier.weight(if (currentStep > 0) 1f else 2f)
                    ) {
                        if (currentStep == totalSteps - 1 && uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(18.dp),
                                strokeWidth = 2.dp,
                                color = MaterialTheme.colorScheme.onPrimary
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Creating...")
                        } else {
                            Text(
                                if (currentStep == totalSteps - 1) "Create Project" else "Next"
                            )
                            if (currentStep < totalSteps - 1) {
                                Spacer(modifier = Modifier.width(8.dp))
                                Icon(
                                    imageVector = Icons.Default.ArrowForward,
                                    contentDescription = null,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                    }
                }
            }
            
            // Error display
            AnimatedVisibility(
                visible = uiState.error != null,
                enter = slideInVertically { it } + fadeIn(),
                exit = slideOutVertically { it } + fadeOut()
            ) {
                uiState.error?.let { error ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        )
                    ) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.Error,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onErrorContainer
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Text(
                                text = error,
                                color = MaterialTheme.colorScheme.onErrorContainer,
                                modifier = Modifier.weight(1f)
                            )
                            TextButton(
                                onClick = { viewModel.clearError() }
                            ) {
                                Text("Dismiss")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ProjectBasicsStep(
    projectName: String,
    onNameChange: (String) -> Unit,
    projectDescription: String,
    onDescriptionChange: (String) -> Unit,
    nameFocusRequester: FocusRequester,
    descriptionFocusRequester: FocusRequester,
    isNameValid: Boolean,
    isDescriptionValid: Boolean,
    suggestions: List<String>,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        StepHeader(
            title = "Project Basics",
            description = "Let's start with the fundamental details of your AI project"
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Project Name
        OutlinedTextField(
            value = projectName,
            onValueChange = onNameChange,
            label = { Text("Project Name *") },
            placeholder = { Text("My AI Assistant") },
            modifier = Modifier
                .fillMaxWidth()
                .focusRequester(nameFocusRequester),
            shape = RoundedCornerShape(12.dp),
            singleLine = true,
            keyboardOptions = KeyboardOptions(
                capitalization = KeyboardCapitalization.Words,
                imeAction = ImeAction.Next
            ),
            keyboardActions = KeyboardActions(
                onNext = { descriptionFocusRequester.requestFocus() }
            ),
            isError = projectName.isNotEmpty() && !isNameValid,
            supportingText = if (projectName.isNotEmpty() && !isNameValid) {
                { Text("Name must be at least 3 characters") }
            } else null,
            trailingIcon = if (isNameValid) {
                {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "Valid",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            } else null
        )
        
        // Name suggestions
        if (suggestions.isNotEmpty() && projectName.isEmpty()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Suggestions:",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(4.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                suggestions.forEach { suggestion ->
                    SuggestionChip(
                        onClick = { onNameChange(suggestion) },
                        label = { Text(suggestion) }
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Project Description
        OutlinedTextField(
            value = projectDescription,
            onValueChange = onDescriptionChange,
            label = { Text("Project Description *") },
            placeholder = { Text("Describe what your AI project will accomplish...") },
            modifier = Modifier
                .fillMaxWidth()
                .focusRequester(descriptionFocusRequester),
            shape = RoundedCornerShape(12.dp),
            minLines = 4,
            maxLines = 6,
            keyboardOptions = KeyboardOptions(
                capitalization = KeyboardCapitalization.Sentences,
                imeAction = ImeAction.Done
            ),
            isError = projectDescription.isNotEmpty() && !isDescriptionValid,
            supportingText = {
                val length = projectDescription.length
                val remaining = 10 - length
                Text(
                    text = if (length < 10) {
                        "Minimum 10 characters ($remaining remaining)"
                    } else {
                        "$length characters"
                    },
                    color = if (isDescriptionValid) 
                        MaterialTheme.colorScheme.primary 
                    else 
                        MaterialTheme.colorScheme.error
                )
            }
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Tips Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.Top
            ) {
                Icon(
                    imageVector = Icons.Default.Tips,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = "Tips for great project names",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "• Be specific about your AI's purpose\n• Use clear, memorable language\n• Avoid technical jargon",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun AutonomySelectionStep(
    selectedLevel: AutonomyLevel,
    onLevelSelected: (AutonomyLevel) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        StepHeader(
            title = "Autonomy Level",
            description = "Choose how much independence your AI agents will have"
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        AutonomyLevel.values().forEach { level ->
            val isSelected = selectedLevel == level
            val animatedAlpha by animateFloatAsState(
                targetValue = if (isSelected) 1f else 0.7f,
                label = "autonomy_alpha"
            )
            
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .alpha(animatedAlpha)
                    .clickable { onLevelSelected(level) },
                colors = CardDefaults.cardColors(
                    containerColor = if (isSelected) 
                        MaterialTheme.colorScheme.primaryContainer 
                    else 
                        MaterialTheme.colorScheme.surface
                ),
                border = if (isSelected) {
                    androidx.compose.foundation.BorderStroke(
                        2.dp, 
                        MaterialTheme.colorScheme.primary
                    )
                } else null
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = isSelected,
                        onClick = { onLevelSelected(level) }
                    )
                    
                    Spacer(modifier = Modifier.width(12.dp))
                    
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = level.name.replace('_', ' ').toLowerCase().split(' ').joinToString(" ") { 
                                it.replaceFirstChar { char -> char.uppercaseChar() } 
                            },
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected) 
                                MaterialTheme.colorScheme.onPrimaryContainer 
                            else 
                                MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(4.dp))
                        
                        Text(
                            text = getAutonomyLevelDescription(level),
                            style = MaterialTheme.typography.bodyMedium,
                            color = if (isSelected) 
                                MaterialTheme.colorScheme.onPrimaryContainer 
                            else 
                                MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            getAutonomyLevelFeatures(level).forEach { feature ->
                                Surface(
                                    shape = RoundedCornerShape(12.dp),
                                    color = if (isSelected) 
                                        MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                                    else 
                                        MaterialTheme.colorScheme.surfaceVariant
                                ) {
                                    Text(
                                        text = feature,
                                        style = MaterialTheme.typography.labelSmall,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                }
                            }
                        }
                    }
                    
                    Icon(
                        imageVector = getAutonomyLevelIcon(level),
                        contentDescription = null,
                        modifier = Modifier.size(32.dp),
                        tint = if (isSelected) 
                            MaterialTheme.colorScheme.primary 
                        else 
                            MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
        }
    }
}

@Composable
private fun TagsAndFeaturesStep(
    selectedTags: Set<String>,
    onTagsChange: (Set<String>) -> Unit,
    customTag: String,
    onCustomTagChange: (String) -> Unit,
    enableRealTimeCollaboration: Boolean,
    onRealTimeCollaborationChange: (Boolean) -> Unit,
    enableAdvancedAnalytics: Boolean,
    onAdvancedAnalyticsChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    val predefinedTags = listOf(
        "AI", "Machine Learning", "NLP", "Computer Vision", "Robotics",
        "Mobile", "Web", "Backend", "Frontend", "API",
        "Research", "Prototype", "Production", "Enterprise", "Startup"
    )
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        StepHeader(
            title = "Tags & Features",
            description = "Categorize your project and enable advanced features"
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Tags Section
        Text(
            text = "Project Tags",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        
        Text(
            text = "Select tags that describe your project (optional)",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            predefinedTags.forEach { tag ->
                FilterChip(
                    selected = selectedTags.contains(tag),
                    onClick = {
                        onTagsChange(
                            if (selectedTags.contains(tag)) {
                                selectedTags - tag
                            } else {
                                selectedTags + tag
                            }
                        )
                    },
                    label = { Text(tag) }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Custom tag input
        OutlinedTextField(
            value = customTag,
            onValueChange = onCustomTagChange,
            label = { Text("Custom Tag") },
            placeholder = { Text("Add your own tag") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            singleLine = true,
            trailingIcon = {
                IconButton(
                    onClick = {
                        if (customTag.isNotBlank()) {
                            onTagsChange(selectedTags + customTag)
                            onCustomTagChange("")
                        }
                    },
                    enabled = customTag.isNotBlank()
                ) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "Add tag"
                    )
                }
            }
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Features Section
        Text(
            text = "Advanced Features",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        
        Text(
            text = "Enable additional capabilities for your project",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Real-time collaboration
        FeatureToggle(
            title = "Real-time Collaboration",
            description = "Enable multiple agents to work together simultaneously",
            icon = Icons.Default.Group,
            enabled = enableRealTimeCollaboration,
            onEnabledChange = onRealTimeCollaborationChange
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Advanced analytics
        FeatureToggle(
            title = "Advanced Analytics",
            description = "Get detailed insights and performance metrics",
            icon = Icons.Default.Analytics,
            enabled = enableAdvancedAnalytics,
            onEnabledChange = onAdvancedAnalyticsChange
        )
    }
}

@Composable
private fun ReviewAndCreateStep(
    projectName: String,
    projectDescription: String,
    autonomyLevel: AutonomyLevel,
    tags: Set<String>,
    enableRealTimeCollaboration: Boolean,
    enableAdvancedAnalytics: Boolean,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        StepHeader(
            title = "Review & Create",
            description = "Review your project configuration before creating"
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Project summary cards
        ReviewCard(
            title = "Project Details",
            icon = Icons.Default.Info
        ) {
            ReviewItem("Name", projectName)
            ReviewItem("Description", projectDescription)
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        ReviewCard(
            title = "Autonomy Configuration",
            icon = Icons.Default.Psychology
        ) {
            ReviewItem(
                "Level", 
                autonomyLevel.name.replace('_', ' ').toLowerCase().split(' ').joinToString(" ") { 
                    it.replaceFirstChar { char -> char.uppercaseChar() } 
                }
            )
            ReviewItem("Description", getAutonomyLevelDescription(autonomyLevel))
        }
        
        if (tags.isNotEmpty()) {
            Spacer(modifier = Modifier.height(12.dp))
            
            ReviewCard(
                title = "Tags",
                icon = Icons.Default.Label
            ) {
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    tags.forEach { tag ->
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = MaterialTheme.colorScheme.primaryContainer
                        ) {
                            Text(
                                text = tag,
                                style = MaterialTheme.typography.labelSmall,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }
                }
            }
        }
        
        val enabledFeatures = listOfNotNull(
            if (enableRealTimeCollaboration) "Real-time Collaboration" else null,
            if (enableAdvancedAnalytics) "Advanced Analytics" else null
        )
        
        if (enabledFeatures.isNotEmpty()) {
            Spacer(modifier = Modifier.height(12.dp))
            
            ReviewCard(
                title = "Enabled Features",
                icon = Icons.Default.Star
            ) {
                enabledFeatures.forEach { feature ->
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 2.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = feature,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Creation info
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.3f)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Rocket,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.secondary,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Ready to Launch",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.secondary
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Your AI project will be created with the configuration above. You can always modify settings later in the project dashboard.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun StepHeader(
    title: String,
    description: String,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(
            text = title,
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = description,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun FeatureToggle(
    title: String,
    description: String,
    icon: ImageVector,
    enabled: Boolean,
    onEnabledChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable { onEnabledChange(!enabled) }
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(24.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Switch(
                checked = enabled,
                onCheckedChange = onEnabledChange
            )
        }
    }
}

@Composable
private fun ReviewCard(
    title: String,
    icon: ImageVector,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            content()
        }
    }
}

@Composable
private fun ReviewItem(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.padding(vertical = 4.dp)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 2.dp)
        )
    }
}

private fun getAutonomyLevelDescription(level: AutonomyLevel): String {
    return when (level) {
        AutonomyLevel.MANUAL -> "You control every decision and action"
        AutonomyLevel.ASSISTED -> "AI provides suggestions, you make decisions"
        AutonomyLevel.SEMI_AUTONOMOUS -> "AI makes routine decisions, asks for complex ones"
        AutonomyLevel.FULLY_AUTONOMOUS -> "AI operates independently with minimal oversight"
    }
}

private fun getAutonomyLevelIcon(level: AutonomyLevel): ImageVector {
    return when (level) {
        AutonomyLevel.MANUAL -> Icons.Default.TouchApp
        AutonomyLevel.ASSISTED -> Icons.Default.SupportAgent
        AutonomyLevel.SEMI_AUTONOMOUS -> Icons.Default.Psychology
        AutonomyLevel.FULLY_AUTONOMOUS -> Icons.Default.AutoMode
    }
}

private fun getAutonomyLevelFeatures(level: AutonomyLevel): List<String> {
    return when (level) {
        AutonomyLevel.MANUAL -> listOf("Full Control", "Step-by-step")
        AutonomyLevel.ASSISTED -> listOf("AI Suggestions", "Human Decisions")
        AutonomyLevel.SEMI_AUTONOMOUS -> listOf("Smart Automation", "Human Oversight")
        AutonomyLevel.FULLY_AUTONOMOUS -> listOf("Full Automation", "Minimal Oversight")
    }
}