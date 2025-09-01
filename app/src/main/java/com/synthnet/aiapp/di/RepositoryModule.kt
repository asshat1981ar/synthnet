package com.synthnet.aiapp.di

import com.synthnet.aiapp.data.repository.*
import com.synthnet.aiapp.domain.repository.*
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    
    @Binds
    @Singleton
    abstract fun bindProjectRepository(
        projectRepositoryImpl: ProjectRepositoryImpl
    ): ProjectRepository
    
    @Binds
    @Singleton
    abstract fun bindAgentRepository(
        agentRepositoryImpl: AgentRepositoryImpl
    ): AgentRepository
    
    @Binds
    @Singleton
    abstract fun bindThoughtRepository(
        thoughtRepositoryImpl: ThoughtRepositoryImpl
    ): ThoughtRepository
    
    @Binds
    @Singleton
    abstract fun bindCollaborationRepository(
        collaborationRepositoryImpl: CollaborationRepositoryImpl
    ): CollaborationRepository
}