package com.synthnet.ai.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.tooling.preview.Preview

@Composable
fun ThemeToggle(
    isDarkMode: Boolean,
    onToggle: (Boolean) -> Unit
) {
    IconButton(onClick = { onToggle(!isDarkMode) }) {
        Icon(
            imageVector = if (isDarkMode) Icons.Default.LightMode else Icons.Default.DarkMode,
            contentDescription = if (isDarkMode) "Switch to Light Mode" else "Switch to Dark Mode"
        )
    }
}

@Preview
@Composable
fun ThemeTogglePreview() {
    ThemeToggle(isDarkMode = false, onToggle = {})
}