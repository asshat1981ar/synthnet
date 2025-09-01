package com.synthnet.ai

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.synthnet.ai.theme.SynthNetTheme
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MainActivityUITest {
    
    @get:Rule
    val composeTestRule = createComposeRule()
    
    @Test
    fun testMainScreenDisplayed() {
        composeTestRule.setContent {
            SynthNetTheme {
                MainScreen()
            }
        }
        
        composeTestRule.onNodeWithText("SynthNet AI").assertIsDisplayed()
        composeTestRule.onNodeWithText("Agent Orchestration").assertIsDisplayed()
        composeTestRule.onNodeWithText("Collaboration").assertIsDisplayed()
        composeTestRule.onNodeWithText("Analytics").assertIsDisplayed()
    }
    
    @Test
    fun testButtonClicks() {
        composeTestRule.setContent {
            SynthNetTheme {
                MainScreen()
            }
        }
        
        composeTestRule.onNodeWithText("Agent Orchestration").performClick()
        // Would verify navigation in real test
    }
}