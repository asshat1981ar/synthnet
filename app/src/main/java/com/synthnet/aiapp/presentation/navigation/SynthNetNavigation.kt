package com.synthnet.aiapp.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.synthnet.aiapp.presentation.screens.project.ProjectListScreen
import com.synthnet.aiapp.presentation.screens.project.ProjectDetailScreen
import com.synthnet.aiapp.presentation.screens.project.CreateProjectScreen

@Composable
fun SynthNetNavigation(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = "project_list",
        modifier = modifier
    ) {
        composable("project_list") {
            ProjectListScreen(
                onNavigateToProject = { projectId ->
                    navController.navigate("project_detail/$projectId")
                },
                onNavigateToCreateProject = {
                    navController.navigate("create_project")
                }
            )
        }
        
        composable("project_detail/{projectId}") { backStackEntry ->
            val projectId = backStackEntry.arguments?.getString("projectId") ?: ""
            ProjectDetailScreen(
                projectId = projectId,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable("create_project") {
            CreateProjectScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onProjectCreated = { projectId ->
                    navController.navigate("project_detail/$projectId") {
                        popUpTo("project_list")
                    }
                }
            )
        }
    }
}