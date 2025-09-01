package com.synthnet.ai.database

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context
import com.synthnet.ai.entity.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Database(
    entities = [
        AgentEntity::class,
        CollaborationEntity::class,
        AnalyticsEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class SynthNetDatabase : RoomDatabase() {
    abstract fun agentDao(): AgentDao
    abstract fun collaborationDao(): CollaborationDao
    abstract fun analyticsDao(): AnalyticsDao
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): SynthNetDatabase {
        return Room.databaseBuilder(
            context,
            SynthNetDatabase::class.java,
            "synthnet_database"
        ).build()
    }
    
    @Provides
    fun provideAgentDao(database: SynthNetDatabase): AgentDao = database.agentDao()
    
    @Provides
    fun provideCollaborationDao(database: SynthNetDatabase): CollaborationDao = database.collaborationDao()
    
    @Provides
    fun provideAnalyticsDao(database: SynthNetDatabase): AnalyticsDao = database.analyticsDao()
}