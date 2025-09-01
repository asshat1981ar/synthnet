package com.synthnet.aiapp.presentation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.ui.Modifier
import com.synthnet.aiapp.presentation.navigation.SynthNetNavigation
import com.synthnet.aiapp.presentation.theme.SynthNetTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        setContent {
            SynthNetTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    SynthNetNavigation(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}