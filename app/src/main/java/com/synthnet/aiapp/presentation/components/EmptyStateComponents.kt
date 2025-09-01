package com.synthnet.aiapp.presentation.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.synthnet.aiapp.presentation.theme.AIGrey

@Composable
fun EmptyStateView(
    title: String,
    description: String,
    actionText: String,
    onActionClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector = Icons.Outlined.Lightbulb,
    showAction: Boolean = true
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Icon
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier
                .size(120.dp)
                .alpha(0.6f),
            tint = AIGrey
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Title
        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurface
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Description
        Text(
            text = description,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.widthIn(max = 320.dp)
        )
        
        if (showAction) {
            Spacer(modifier = Modifier.height(32.dp))
            
            // Action Button
            Button(
                onClick = onActionClick,
                modifier = Modifier
                    .fillMaxWidth(0.6f)
                    .height(48.dp),
                shape = RoundedCornerShape(24.dp)
            ) {
                Text(
                    text = actionText,
                    style = MaterialTheme.typography.titleMedium
                )
            }
        }
    }
}

@Composable
fun LoadingStateView(
    title: String = "Loading...",
    description: String = "Please wait while we prepare your data",
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        CircularProgressIndicator(
            modifier = Modifier.size(64.dp),
            strokeWidth = 4.dp
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Medium,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = description,
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun ErrorStateView(
    title: String = "Something went wrong",
    description: String = "We encountered an error. Please try again.",
    actionText: String = "Retry",
    onActionClick: () -> Unit,
    modifier: Modifier = Modifier,
    onSecondaryActionClick: (() -> Unit)? = null,
    secondaryActionText: String = "Go Back"
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Outlined.ErrorOutline,
            contentDescription = null,
            modifier = Modifier
                .size(120.dp)
                .alpha(0.6f),
            tint = MaterialTheme.colorScheme.error
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.error
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Text(
            text = description,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.widthIn(max = 320.dp)
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Primary Action Button
        Button(
            onClick = onActionClick,
            modifier = Modifier
                .fillMaxWidth(0.6f)
                .height(48.dp),
            shape = RoundedCornerShape(24.dp)
        ) {
            Text(
                text = actionText,
                style = MaterialTheme.typography.titleMedium
            )
        }
        
        // Secondary Action Button
        onSecondaryActionClick?.let { secondaryAction ->
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedButton(
                onClick = secondaryAction,
                modifier = Modifier
                    .fillMaxWidth(0.6f)
                    .height(48.dp),
                shape = RoundedCornerShape(24.dp)
            ) {
                Text(
                    text = secondaryActionText,
                    style = MaterialTheme.typography.titleMedium
                )
            }
        }
    }
}

@Composable
fun NoResultsStateView(
    searchQuery: String,
    onClearSearch: () -> Unit,
    onBrowseAll: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    EmptyStateView(
        title = "No results found",
        description = "We couldn't find anything matching \"$searchQuery\". Try adjusting your search terms.",
        actionText = "Clear Search",
        onActionClick = onClearSearch,
        icon = Icons.Outlined.SearchOff,
        modifier = modifier
    )
    
    onBrowseAll?.let { browseAction ->
        Column(
            modifier = Modifier.padding(top = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            TextButton(onClick = browseAction) {
                Text("Browse All Items")
            }
        }
    }
}

@Composable
fun MaintenanceStateView(
    modifier: Modifier = Modifier
) {
    EmptyStateView(
        title = "Under Maintenance",
        description = "We're currently performing system maintenance. Please check back in a few minutes.",
        actionText = "Refresh",
        onActionClick = { /* Handle refresh */ },
        icon = Icons.Outlined.Build,
        modifier = modifier
    )
}

@Composable
fun NetworkErrorStateView(
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    ErrorStateView(
        title = "Connection Problem",
        description = "Please check your internet connection and try again.",
        actionText = "Try Again",
        onActionClick = onRetry,
        modifier = modifier
    )
}