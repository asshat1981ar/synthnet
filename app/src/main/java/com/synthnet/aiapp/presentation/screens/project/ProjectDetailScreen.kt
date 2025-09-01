package com.synthnet.aiapp.presentation.screens.project

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.synthnet.aiapp.presentation.components.*
import com.synthnet.aiapp.presentation.screens.project.tabs.*
import com.synthnet.aiapp.presentation.viewmodels.ProjectDetailViewModel
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProjectDetailScreen(
    projectId: String,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: ProjectDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var userInput by remember { mutableStateOf("") }
    var selectedTab by remember { mutableStateOf(0) }
    var showMetricsDetail by remember { mutableStateOf(false) }
    val snackbarHostState = remember { SnackbarHostState() }
    
    LaunchedEffect(projectId) {
        viewModel.loadProject(projectId)
    }
    
    // Auto-refresh every 30 seconds for real-time updates
    LaunchedEffect(projectId) {
        while (true) {
            delay(30_000)
            viewModel.refreshData()
        }
    }
    
    // Handle error display
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(
                message = error,
                duration = SnackbarDuration.Long
            )
            viewModel.clearError()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = uiState.project?.name ?: "Loading...",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        AnimatedVisibility(visible = uiState.isLoading) {
                            Text(
                                text = "Syncing...",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                actions = {
                    // Real-time status indicator
                    RealTimeStatusIndicator(
                        isConnected = uiState.isRealTimeConnected,
                        isLoading = uiState.isLoading
                    )
                    
                    // Refresh button
                    IconButton(
                        onClick = { viewModel.refreshData() },
                        enabled = !uiState.isLoading
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Refresh",
                            tint = if (uiState.isLoading) 
                                MaterialTheme.colorScheme.onSurfaceVariant 
                            else 
                                MaterialTheme.colorScheme.onSurface
                        )
                    }
                    
                    // More options menu
                    var showMenu by remember { mutableStateOf(false) }
                    Box {
                        IconButton(onClick = { showMenu = true }) {
                            Icon(
                                imageVector = Icons.Default.MoreVert,
                                contentDescription = "More options"
                            )
                        }
                        DropdownMenu(
                            expanded = showMenu,
                            onDismissRequest = { showMenu = false }
                        ) {
                            DropdownMenuItem(
                                text = { Text("Export Data") },
                                onClick = {
                                    viewModel.exportProjectData()
                                    showMenu = false
                                },
                                leadingIcon = {
                                    Icon(Icons.Default.Download, contentDescription = null)
                                }
                            )
                            DropdownMenuItem(
                                text = { Text("Share Project") },
                                onClick = {
                                    viewModel.shareProject()
                                    showMenu = false
                                },
                                leadingIcon = {
                                    Icon(Icons.Default.Share, contentDescription = null)
                                }
                            )
                            DropdownMenuItem(
                                text = { 
                                    Text(if (showMetricsDetail) "Hide Details" else "Show Details") 
                                },
                                onClick = {
                                    showMetricsDetail = !showMetricsDetail
                                    showMenu = false
                                },
                                leadingIcon = {
                                    Icon(
                                        if (showMetricsDetail) Icons.Default.VisibilityOff 
                                        else Icons.Default.Visibility,
                                        contentDescription = null
                                    )
                                }
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        },
        snackbarHost = {
            SnackbarHost(hostState = snackbarHostState)
        },
        modifier = modifier
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Enhanced project header with quick metrics
            uiState.project?.let { project ->
                EnhancedProjectHeader(
                    project = project,
                    isRealTime = uiState.isRealTimeConnected,
                    lastUpdated = uiState.lastUpdated,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                )
            }
            
            // Tab Layout for organizing content
            ProjectDetailTabs(
                selectedTabIndex = selectedTab,
                onTabSelected = { selectedTab = it },
                agentCount = uiState.agents.size,
                collaborationCount = uiState.activeCollaborations.size,
                hasAnalytics = uiState.project != null,
                modifier = Modifier.padding(horizontal = 16.dp)
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            when {
                uiState.isLoading && uiState.project == null -> {
                    LoadingState()
                }
                
                uiState.project != null -> {
                    AnimatedContent(
                        targetState = selectedTab,
                        transitionSpec = {
                            fadeIn(animationSpec = tween(300)) with
                                    fadeOut(animationSpec = tween(300))
                        },
                        modifier = Modifier.weight(1f)
                    ) { tabIndex ->
                        when (tabIndex) {
                            0 -> ProjectOverviewTab(
                                project = uiState.project!!,
                                thoughtTree = uiState.thoughtTree,
                                userInput = userInput,
                                onUserInputChange = { userInput = it },
                                onSubmitInput = {
                                    if (userInput.isNotBlank()) {
                                        viewModel.processUserInput(userInput)
                                        userInput = ""
                                    }
                                },
                                onThoughtSelected = { thoughtId ->
                                    viewModel.selectThought(thoughtId)
                                },
                                isProcessing = uiState.isProcessing,
                                lastResponse = uiState.lastAgentResponse,
                                showDetailedMetrics = showMetricsDetail
                            )
                            1 -> ProjectAgentsTab(
                                agents = uiState.agents,
                                orchestrationState = uiState.orchestrationState,
                                onAgentAction = { agentId, action ->
                                    viewModel.performAgentAction(agentId, action)
                                },
                                onStartAgent = { agentId ->
                                    viewModel.startAgent(agentId)
                                },
                                onStopAgent = { agentId ->
                                    viewModel.stopAgent(agentId)
                                }
                            )
                            2 -> ProjectCollaborationTab(
                                collaborations = uiState.activeCollaborations,
                                connectionState = uiState.collaborationConnectionState,
                                sessionHistory = uiState.collaborationHistory,
                                onStartCollaboration = { 
                                    viewModel.startCollaboration() 
                                },
                                onJoinCollaboration = { id -> 
                                    viewModel.joinCollaboration(id) 
                                },
                                onLeaveCollaboration = { id ->
                                    viewModel.leaveCollaboration(id)
                                }
                            )
                            3 -> ProjectAnalyticsTab(
                                metrics = uiState.innovationMetrics,
                                thoughtTree = uiState.thoughtTree,
                                historicalData = uiState.historicalMetrics,
                                performanceData = uiState.performanceMetrics,
                                onExportData = { format ->
                                    viewModel.exportAnalytics(format)
                                },
                                onRefreshMetrics = {
                                    viewModel.refreshMetrics()
                                }
                            )
                        }
                    }
                }
                
                else -> {
                    ProjectNotFoundState(onNavigateBack = onNavigateBack)
                }
            }
        }
    }
}

@Composable
private fun LoadingState(
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(48.dp),
                strokeWidth = 4.dp
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Loading project details...",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Please wait while we fetch the latest data",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ProjectNotFoundState(
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    EmptyStateView(
        title = "Project Not Found",
        description = "The requested project could not be loaded. It may have been deleted or you might not have access to it.",
        actionText = "Go Back",
        onActionClick = onNavigateBack,
        modifier = modifier
    )
}

@Composable
private fun RealTimeStatusIndicator(
    isConnected: Boolean,
    isLoading: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.padding(horizontal = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        when {
            isLoading -> {
                CircularProgressIndicator(
                    modifier = Modifier.size(12.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            else -> {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(
                            color = if (isConnected) 
                                MaterialTheme.colorScheme.primary 
                            else 
                                MaterialTheme.colorScheme.error,
                            shape = CircleShape
                        )
                )
            }
        }
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = when {
                isLoading -> "Syncing"
                isConnected -> "Live"
                else -> "Offline"
            },
            style = MaterialTheme.typography.labelSmall,
            color = when {
                isLoading -> MaterialTheme.colorScheme.primary
                isConnected -> MaterialTheme.colorScheme.primary
                else -> MaterialTheme.colorScheme.error
            }
        )
    }
}

@Composable
private fun EnhancedProjectHeader(
    project: com.synthnet.aiapp.domain.models.Project,
    isRealTime: Boolean,
    lastUpdated: String?,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = project.description,
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        ProjectStatusBadge(status = project.status)
                        if (lastUpdated != null) {
                            Text(
                                text = "Updated $lastUpdated",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
                
                AutonomyLevelBadge(level = project.autonomyLevel)
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Quick metrics overview with better layout
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                QuickMetric(
                    label = "Agents",
                    value = project.agents.size.toString(),
                    icon = Icons.Default.SmartToy,
                    color = MaterialTheme.colorScheme.primary
                )
                QuickMetric(
                    label = "Trees",
                    value = project.thoughtTrees.size.toString(),
                    icon = Icons.Default.AccountTree,
                    color = MaterialTheme.colorScheme.secondary
                )
                QuickMetric(
                    label = "Innovation",
                    value = "${(project.metrics.innovationVelocity * 100).toInt()}%",
                    icon = Icons.Default.TrendingUp,
                    color = MaterialTheme.colorScheme.tertiary
                )
                QuickMetric(
                    label = "Autonomy",
                    value = "${(project.metrics.autonomyIndex * 100).toInt()}%",
                    icon = Icons.Default.Psychology,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun QuickMetric(
    label: String,
    value: String,
    icon: ImageVector,
    color: androidx.compose.ui.graphics.Color,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun ProjectDetailTabs(
    selectedTabIndex: Int,
    onTabSelected: (Int) -> Unit,
    agentCount: Int,
    collaborationCount: Int,
    hasAnalytics: Boolean,
    modifier: Modifier = Modifier
) {
    val tabData = listOf(
        TabItem("Overview", Icons.Default.Dashboard, null),
        TabItem("Agents", Icons.Default.SmartToy, if (agentCount > 0) agentCount.toString() else null),
        TabItem("Collaborate", Icons.Default.Group, if (collaborationCount > 0) collaborationCount.toString() else null),
        TabItem("Analytics", Icons.Default.Analytics, null)
    )
    
    ScrollableTabRow(
        selectedTabIndex = selectedTabIndex,
        modifier = modifier,
        contentColor = MaterialTheme.colorScheme.primary,
        edgePadding = 16.dp
    ) {
        tabData.forEachIndexed { index, tabItem ->
            Tab(
                selected = selectedTabIndex == index,
                onClick = { onTabSelected(index) },
                text = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = tabItem.title,
                            style = MaterialTheme.typography.labelMedium
                        )
                        tabItem.badge?.let { badge ->
                            Badge {
                                Text(
                                    text = badge,
                                    style = MaterialTheme.typography.labelSmall
                                )
                            }
                        }
                    }
                },
                icon = {
                    Icon(
                        imageVector = tabItem.icon,
                        contentDescription = tabItem.title,
                        modifier = Modifier.size(20.dp)
                    )
                }
            )
        }
    }
}

private data class TabItem(
    val title: String,
    val icon: ImageVector,
    val badge: String?
)