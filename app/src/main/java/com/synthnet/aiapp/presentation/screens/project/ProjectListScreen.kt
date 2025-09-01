package com.synthnet.aiapp.presentation.screens.project

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.synthnet.aiapp.presentation.components.ProjectCard
import com.synthnet.aiapp.presentation.components.EmptyStateView
import com.synthnet.aiapp.presentation.viewmodels.ProjectListViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProjectListScreen(
    onNavigateToProject: (String) -> Unit,
    onNavigateToCreateProject: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: ProjectListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var searchQuery by remember { mutableStateOf("") }
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "SynthNet AI Projects",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
            
            FloatingActionButton(
                onClick = onNavigateToCreateProject,
                modifier = Modifier.size(56.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "Create Project"
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Search Bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { 
                searchQuery = it
                viewModel.searchProjects(it)
            },
            label = { Text("Search projects") },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Default.Search,
                    contentDescription = "Search"
                )
            },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp)
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Project List
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            
            uiState.projects.isEmpty() -> {
                EmptyStateView(
                    title = "No Projects Yet",
                    description = "Create your first AI-powered project to get started",
                    actionText = "Create Project",
                    onActionClick = onNavigateToCreateProject
                )
            }
            
            else -> {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(uiState.projects) { project ->
                        ProjectCard(
                            project = project,
                            onClick = { onNavigateToProject(project.id) },
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            }
        }
        
        // Error handling
        uiState.error?.let { error ->
            LaunchedEffect(error) {
                // Show snackbar or error dialog
            }
        }
    }
}