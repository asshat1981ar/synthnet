package com.synthnet.ai.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "agent_table")
data class AgentEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    val description: String,
    val status: String,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)