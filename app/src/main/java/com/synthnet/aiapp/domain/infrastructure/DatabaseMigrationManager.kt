package com.synthnet.aiapp.domain.infrastructure

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DatabaseMigrationManager @Inject constructor() {
    
    val MIGRATION_1_2 = object : Migration(1, 2) {
        override fun migrate(database: SupportSQLiteDatabase) {
            database.execSQL("ALTER TABLE projects ADD COLUMN vector_embeddings TEXT DEFAULT ''")
            database.execSQL("ALTER TABLE thoughts ADD COLUMN semantic_similarity REAL DEFAULT 0.0")
            database.execSQL("CREATE INDEX idx_thoughts_semantic_similarity ON thoughts(semantic_similarity)")
        }
    }
    
    val MIGRATION_2_3 = object : Migration(2, 3) {
        override fun migrate(database: SupportSQLiteDatabase) {
            database.execSQL("""
                CREATE TABLE IF NOT EXISTS knowledge_entities (
                    id TEXT PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    relationships TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
            """)
            
            database.execSQL("""
                CREATE TABLE IF NOT EXISTS vector_embeddings (
                    id TEXT PRIMARY KEY NOT NULL,
                    entity_id TEXT NOT NULL,
                    embedding_vector TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    model_version TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY(entity_id) REFERENCES knowledge_entities(id) ON DELETE CASCADE
                )
            """)
            
            database.execSQL("CREATE INDEX idx_vector_embeddings_entity_id ON vector_embeddings(entity_id)")
        }
    }
    
    val MIGRATION_3_4 = object : Migration(3, 4) {
        override fun migrate(database: SupportSQLiteDatabase) {
            database.execSQL("ALTER TABLE agents ADD COLUMN performance_metrics TEXT DEFAULT '{}'")
            database.execSQL("ALTER TABLE agents ADD COLUMN learning_history TEXT DEFAULT '[]'")
            database.execSQL("ALTER TABLE collaborations ADD COLUMN quality_score REAL DEFAULT 0.0")
            database.execSQL("ALTER TABLE collaborations ADD COLUMN efficiency_metrics TEXT DEFAULT '{}'")
            
            database.execSQL("""
                CREATE TABLE IF NOT EXISTS thought_evaluations (
                    id TEXT PRIMARY KEY NOT NULL,
                    thought_id TEXT NOT NULL,
                    evaluator_agent_id TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    dimensions TEXT NOT NULL,
                    feedback TEXT NOT NULL,
                    evaluated_at INTEGER NOT NULL,
                    FOREIGN KEY(thought_id) REFERENCES thoughts(id) ON DELETE CASCADE,
                    FOREIGN KEY(evaluator_agent_id) REFERENCES agents(id) ON DELETE CASCADE
                )
            """)
        }
    }
    
    val MIGRATION_4_5 = object : Migration(4, 5) {
        override fun migrate(database: SupportSQLiteDatabase) {
            database.execSQL("""
                CREATE TABLE IF NOT EXISTS reasoning_traces (
                    id TEXT PRIMARY KEY NOT NULL,
                    thought_id TEXT NOT NULL,
                    reasoning_type TEXT NOT NULL,
                    trace_data TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY(thought_id) REFERENCES thoughts(id) ON DELETE CASCADE
                )
            """)
            
            database.execSQL("""
                CREATE TABLE IF NOT EXISTS semantic_clusters (
                    id TEXT PRIMARY KEY NOT NULL,
                    project_id TEXT NOT NULL,
                    cluster_center TEXT NOT NULL,
                    thought_ids TEXT NOT NULL,
                    coherence_score REAL NOT NULL,
                    diversity_score REAL NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            database.execSQL("CREATE INDEX idx_reasoning_traces_thought_id ON reasoning_traces(thought_id)")
            database.execSQL("CREATE INDEX idx_semantic_clusters_project_id ON semantic_clusters(project_id)")
        }
    }
    
    val ALL_MIGRATIONS = arrayOf(
        MIGRATION_1_2,
        MIGRATION_2_3,
        MIGRATION_3_4,
        MIGRATION_4_5
    )
    
    fun getLatestVersion(): Int = 5
    
    fun createInitialSchema(database: SupportSQLiteDatabase) {
        // Core tables creation
        createProjectsTable(database)
        createAgentsTable(database)
        createThoughtsTable(database)
        createCollaborationsTable(database)
        
        // Enhanced tables from migrations
        createKnowledgeEntitiesTable(database)
        createVectorEmbeddingsTable(database)
        createThoughtEvaluationsTable(database)
        createReasoningTracesTable(database)
        createSemanticClustersTable(database)
        
        // Indices
        createIndices(database)
    }
    
    private fun createProjectsTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                autonomy_level TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                collaborators TEXT NOT NULL,
                tags TEXT NOT NULL,
                vector_embeddings TEXT DEFAULT ''
            )
        """)
    }
    
    private fun createAgentsTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                project_id TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                status TEXT NOT NULL,
                last_active INTEGER NOT NULL,
                metrics TEXT NOT NULL,
                configuration TEXT NOT NULL,
                performance_metrics TEXT DEFAULT '{}',
                learning_history TEXT DEFAULT '[]',
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createThoughtsTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY NOT NULL,
                project_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                parent_id TEXT,
                content TEXT NOT NULL,
                thought_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT NOT NULL,
                alternatives TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                is_selected INTEGER NOT NULL DEFAULT 0,
                semantic_similarity REAL DEFAULT 0.0,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY(agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                FOREIGN KEY(parent_id) REFERENCES thoughts(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createCollaborationsTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS collaborations (
                id TEXT PRIMARY KEY NOT NULL,
                project_id TEXT NOT NULL,
                session_type TEXT NOT NULL,
                participants TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at INTEGER NOT NULL,
                ended_at INTEGER,
                sync_points TEXT NOT NULL,
                knowledge_exchanges INTEGER NOT NULL,
                consensus_reached INTEGER NOT NULL DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                efficiency_metrics TEXT DEFAULT '{}',
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createKnowledgeEntitiesTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS knowledge_entities (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                properties TEXT NOT NULL,
                relationships TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)
    }
    
    private fun createVectorEmbeddingsTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS vector_embeddings (
                id TEXT PRIMARY KEY NOT NULL,
                entity_id TEXT NOT NULL,
                embedding_vector TEXT NOT NULL,
                dimension INTEGER NOT NULL,
                model_version TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY(entity_id) REFERENCES knowledge_entities(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createThoughtEvaluationsTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS thought_evaluations (
                id TEXT PRIMARY KEY NOT NULL,
                thought_id TEXT NOT NULL,
                evaluator_agent_id TEXT NOT NULL,
                quality_score REAL NOT NULL,
                dimensions TEXT NOT NULL,
                feedback TEXT NOT NULL,
                evaluated_at INTEGER NOT NULL,
                FOREIGN KEY(thought_id) REFERENCES thoughts(id) ON DELETE CASCADE,
                FOREIGN KEY(evaluator_agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createReasoningTracesTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS reasoning_traces (
                id TEXT PRIMARY KEY NOT NULL,
                thought_id TEXT NOT NULL,
                reasoning_type TEXT NOT NULL,
                trace_data TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY(thought_id) REFERENCES thoughts(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createSemanticClustersTable(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS semantic_clusters (
                id TEXT PRIMARY KEY NOT NULL,
                project_id TEXT NOT NULL,
                cluster_center TEXT NOT NULL,
                thought_ids TEXT NOT NULL,
                coherence_score REAL NOT NULL,
                diversity_score REAL NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
    }
    
    private fun createIndices(database: SupportSQLiteDatabase) {
        // Primary indices for performance
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_agents_project_id ON agents(project_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thoughts_project_id ON thoughts(project_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thoughts_agent_id ON thoughts(agent_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thoughts_parent_id ON thoughts(parent_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thoughts_semantic_similarity ON thoughts(semantic_similarity)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_collaborations_project_id ON collaborations(project_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_collaborations_status ON collaborations(status)")
        
        // Enhanced indices from migrations
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_vector_embeddings_entity_id ON vector_embeddings(entity_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thought_evaluations_thought_id ON thought_evaluations(thought_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_reasoning_traces_thought_id ON reasoning_traces(thought_id)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_semantic_clusters_project_id ON semantic_clusters(project_id)")
        
        // Performance indices
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thoughts_confidence ON thoughts(confidence)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_thoughts_created_at ON thoughts(created_at)")
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_agents_last_active ON agents(last_active)")
    }
    
    fun performDatabaseOptimization(database: SupportSQLiteDatabase) {
        // Vacuum database to reclaim space
        database.execSQL("VACUUM")
        
        // Analyze tables to update statistics
        database.execSQL("ANALYZE")
        
        // Set performance pragmas
        database.execSQL("PRAGMA synchronous = NORMAL")
        database.execSQL("PRAGMA cache_size = 10000")
        database.execSQL("PRAGMA temp_store = MEMORY")
        database.execSQL("PRAGMA journal_mode = WAL")
        database.execSQL("PRAGMA wal_autocheckpoint = 1000")
    }
    
    fun validateDatabaseIntegrity(database: SupportSQLiteDatabase): Boolean {
        return try {
            val cursor = database.query("PRAGMA integrity_check")
            cursor.use {
                it.moveToFirst()
                val result = it.getString(0)
                result == "ok"
            }
        } catch (e: Exception) {
            false
        }
    }
}