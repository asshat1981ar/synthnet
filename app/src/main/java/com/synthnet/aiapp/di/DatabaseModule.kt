package com.synthnet.aiapp.di

import android.content.Context
import androidx.room.Room
import com.synthnet.aiapp.data.database.SynthNetDatabase
import com.synthnet.aiapp.data.dao.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideSynthNetDatabase(@ApplicationContext context: Context): SynthNetDatabase {
        return Room.databaseBuilder(
            context.applicationContext,
            SynthNetDatabase::class.java,
            SynthNetDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration()
            .build()
    }
    
    @Provides
    fun provideProjectDao(database: SynthNetDatabase): ProjectDao {
        return database.projectDao()
    }
    
    @Provides
    fun provideAgentDao(database: SynthNetDatabase): AgentDao {
        return database.agentDao()
    }
    
    @Provides
    fun provideThoughtDao(database: SynthNetDatabase): ThoughtDao {
        return database.thoughtDao()
    }
    
    @Provides
    fun provideCollaborationDao(database: SynthNetDatabase): CollaborationDao {
        return database.collaborationDao()
    }
}