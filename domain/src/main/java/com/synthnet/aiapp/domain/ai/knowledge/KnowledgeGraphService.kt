package com.synthnet.aiapp.domain.ai.knowledge

import com.synthnet.aiapp.domain.ai.embeddings.VectorEmbeddingService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.withContext
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class KnowledgeGraphService @Inject constructor(
    private val embeddingService: VectorEmbeddingService
) {
    
    private val _knowledgeGraph = MutableStateFlow(KnowledgeGraph())
    val knowledgeGraph: StateFlow<KnowledgeGraph> = _knowledgeGraph.asStateFlow()
    
    suspend fun addEntity(
        id: String,
        label: String,
        type: EntityType,
        properties: Map<String, Any> = emptyMap(),
        description: String = ""
    ): Result<KnowledgeEntity> = withContext(Dispatchers.IO) {
        try {
            val embedding = embeddingService.generateEmbedding(
                "$label $description",
                com.synthnet.aiapp.domain.ai.embeddings.EmbeddingType.KNOWLEDGE
            ).getOrThrow()
            
            val entity = KnowledgeEntity(
                id = id,
                label = label,
                type = type,
                properties = properties,
                description = description,
                embedding = embedding,
                createdAt = Clock.System.now(),
                updatedAt = Clock.System.now()
            )
            
            val currentGraph = _knowledgeGraph.value
            _knowledgeGraph.value = currentGraph.copy(
                entities = currentGraph.entities + (id to entity)
            )
            
            Result.success(entity)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun addRelation(
        fromEntityId: String,
        toEntityId: String,
        relationType: RelationType,
        properties: Map<String, Any> = emptyMap(),
        weight: Double = 1.0
    ): Result<KnowledgeRelation> = withContext(Dispatchers.IO) {
        try {
            val currentGraph = _knowledgeGraph.value
            
            // Validate entities exist
            if (fromEntityId !in currentGraph.entities || toEntityId !in currentGraph.entities) {
                return@withContext Result.failure(Exception("One or both entities not found"))
            }
            
            val relation = KnowledgeRelation(
                id = generateRelationId(fromEntityId, toEntityId, relationType),
                fromEntityId = fromEntityId,
                toEntityId = toEntityId,
                type = relationType,
                properties = properties,
                weight = weight,
                createdAt = Clock.System.now()
            )
            
            _knowledgeGraph.value = currentGraph.copy(
                relations = currentGraph.relations + (relation.id to relation)
            )
            
            Result.success(relation)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun findRelatedEntities(
        entityId: String,
        relationTypes: Set<RelationType> = RelationType.values().toSet(),
        maxDepth: Int = 2,
        minWeight: Double = 0.1
    ): Result<List<RelatedEntity>> = withContext(Dispatchers.Default) {
        try {
            val currentGraph = _knowledgeGraph.value
            val startEntity = currentGraph.entities[entityId]
                ?: return@withContext Result.failure(Exception("Entity not found"))
            
            val visited = mutableSetOf<String>()
            val results = mutableListOf<RelatedEntity>()
            
            fun traverseGraph(currentEntityId: String, depth: Int, pathWeight: Double) {
                if (depth > maxDepth || currentEntityId in visited) return
                
                visited.add(currentEntityId)
                
                // Find all outgoing relations
                currentGraph.relations.values
                    .filter { relation ->
                        relation.fromEntityId == currentEntityId &&
                        relation.type in relationTypes &&
                        relation.weight >= minWeight
                    }
                    .forEach { relation ->
                        val targetEntity = currentGraph.entities[relation.toEntityId]
                        if (targetEntity != null && relation.toEntityId != entityId) {
                            val combinedWeight = pathWeight * relation.weight
                            results.add(RelatedEntity(
                                entity = targetEntity,
                                relation = relation,
                                path = emptyList(), // Could track full path if needed
                                distance = depth,
                                weight = combinedWeight
                            ))
                            
                            traverseGraph(relation.toEntityId, depth + 1, combinedWeight)
                        }
                    }
                
                // Find all incoming relations
                currentGraph.relations.values
                    .filter { relation ->
                        relation.toEntityId == currentEntityId &&
                        relation.type in relationTypes &&
                        relation.weight >= minWeight
                    }
                    .forEach { relation ->
                        val sourceEntity = currentGraph.entities[relation.fromEntityId]
                        if (sourceEntity != null && relation.fromEntityId != entityId) {
                            val combinedWeight = pathWeight * relation.weight
                            results.add(RelatedEntity(
                                entity = sourceEntity,
                                relation = relation,
                                path = emptyList(),
                                distance = depth,
                                weight = combinedWeight
                            ))
                            
                            traverseGraph(relation.fromEntityId, depth + 1, combinedWeight)
                        }
                    }
            }
            
            traverseGraph(entityId, 0, 1.0)
            
            val uniqueResults = results
                .distinctBy { it.entity.id }
                .sortedByDescending { it.weight }
            
            Result.success(uniqueResults)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun semanticSearch(
        query: String,
        entityTypes: Set<EntityType> = EntityType.values().toSet(),
        maxResults: Int = 20,
        threshold: Double = 0.7
    ): Result<List<SemanticSearchResult>> = withContext(Dispatchers.IO) {
        try {
            val queryEmbedding = embeddingService.generateEmbedding(
                query,
                com.synthnet.aiapp.domain.ai.embeddings.EmbeddingType.KNOWLEDGE
            ).getOrThrow()
            
            val currentGraph = _knowledgeGraph.value
            val candidates = currentGraph.entities.values
                .filter { it.type in entityTypes }
                .map { entity ->
                    val similarity = queryEmbedding.cosineSimilarity(entity.embedding)
                    SemanticSearchResult(
                        entity = entity,
                        similarity = similarity,
                        matchedProperties = findMatchedProperties(entity, query)
                    )
                }
                .filter { it.similarity >= threshold }
                .sortedByDescending { it.similarity }
                .take(maxResults)
            
            Result.success(candidates)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun inferNewRelations(
        confidenceThreshold: Double = 0.8
    ): Result<List<InferredRelation>> = withContext(Dispatchers.Default) {
        try {
            val currentGraph = _knowledgeGraph.value
            val inferredRelations = mutableListOf<InferredRelation>()
            
            // Simple inference based on entity similarity and existing patterns
            currentGraph.entities.values.forEach { entity1 ->
                currentGraph.entities.values.forEach { entity2 ->
                    if (entity1.id != entity2.id) {
                        val similarity = entity1.embedding.cosineSimilarity(entity2.embedding)
                        
                        if (similarity >= confidenceThreshold) {
                            // Check if relation already exists
                            val existingRelation = currentGraph.relations.values.any { relation ->
                                (relation.fromEntityId == entity1.id && relation.toEntityId == entity2.id) ||
                                (relation.fromEntityId == entity2.id && relation.toEntityId == entity1.id)
                            }
                            
                            if (!existingRelation) {
                                val inferredType = inferRelationType(entity1, entity2)
                                inferredRelations.add(InferredRelation(
                                    fromEntity = entity1,
                                    toEntity = entity2,
                                    suggestedType = inferredType,
                                    confidence = similarity,
                                    reasoning = "High semantic similarity: ${(similarity * 100).toInt()}%"
                                ))
                            }
                        }
                    }
                }
            }
            
            Result.success(inferredRelations.sortedByDescending { it.confidence })
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getEntityClusters(numClusters: Int = 5): Result<List<EntityCluster>> {
        return try {
            val currentGraph = _knowledgeGraph.value
            val embeddings = currentGraph.entities.values.map { it.embedding }
            
            val clusters = embeddingService.clusterEmbeddings(embeddings, numClusters).getOrThrow()
            
            val entityClusters = clusters.map { cluster ->
                val entities = currentGraph.entities.values.filter { entity ->
                    cluster.members.contains(entity.embedding)
                }
                
                EntityCluster(
                    id = cluster.id,
                    entities = entities,
                    centroidLabel = generateClusterLabel(entities),
                    commonProperties = findCommonProperties(entities)
                )
            }
            
            Result.success(entityClusters)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun findMatchedProperties(entity: KnowledgeEntity, query: String): List<String> {
        val queryWords = query.lowercase().split("\\s+".toRegex())
        val matchedProps = mutableListOf<String>()
        
        // Check label
        if (queryWords.any { entity.label.lowercase().contains(it) }) {
            matchedProps.add("label")
        }
        
        // Check description
        if (queryWords.any { entity.description.lowercase().contains(it) }) {
            matchedProps.add("description")
        }
        
        // Check properties
        entity.properties.forEach { (key, value) ->
            if (queryWords.any { value.toString().lowercase().contains(it) }) {
                matchedProps.add(key)
            }
        }
        
        return matchedProps
    }
    
    private fun inferRelationType(entity1: KnowledgeEntity, entity2: KnowledgeEntity): RelationType {
        // Simple heuristic-based relation type inference
        return when {
            entity1.type == EntityType.PERSON && entity2.type == EntityType.ORGANIZATION -> RelationType.WORKS_FOR
            entity1.type == EntityType.CONCEPT && entity2.type == EntityType.CONCEPT -> RelationType.RELATES_TO
            entity1.type == EntityType.PROJECT && entity2.type == EntityType.TECHNOLOGY -> RelationType.USES
            else -> RelationType.RELATES_TO
        }
    }
    
    private fun generateClusterLabel(entities: List<KnowledgeEntity>): String {
        val commonWords = entities
            .flatMap { it.label.split("\\s+".toRegex()) }
            .groupingBy { it }
            .eachCount()
            .maxByOrNull { it.value }
            ?.key
        
        return commonWords ?: "Cluster ${entities.firstOrNull()?.type?.name ?: "Unknown"}"
    }
    
    private fun findCommonProperties(entities: List<KnowledgeEntity>): Map<String, Any> {
        if (entities.isEmpty()) return emptyMap()
        
        val commonProps = mutableMapOf<String, Any>()
        val allKeys = entities.flatMap { it.properties.keys }.toSet()
        
        allKeys.forEach { key ->
            val values = entities.mapNotNull { it.properties[key] }
            if (values.size == entities.size) {
                // All entities have this property
                val uniqueValues = values.toSet()
                if (uniqueValues.size == 1) {
                    // All entities have the same value
                    commonProps[key] = uniqueValues.first()
                }
            }
        }
        
        return commonProps
    }
    
    private fun generateRelationId(fromId: String, toId: String, type: RelationType): String {
        return "${fromId}_${type.name}_${toId}_${System.currentTimeMillis()}"
    }
    
    fun getGraphMetrics(): GraphMetrics {
        val currentGraph = _knowledgeGraph.value
        return GraphMetrics(
            entityCount = currentGraph.entities.size,
            relationCount = currentGraph.relations.size,
            averageConnections = if (currentGraph.entities.isNotEmpty()) {
                currentGraph.relations.size.toDouble() / currentGraph.entities.size
            } else 0.0,
            entityTypeDistribution = currentGraph.entities.values
                .groupingBy { it.type }
                .eachCount(),
            relationTypeDistribution = currentGraph.relations.values
                .groupingBy { it.type }
                .eachCount()
        )
    }
}

data class KnowledgeGraph(
    val entities: Map<String, KnowledgeEntity> = emptyMap(),
    val relations: Map<String, KnowledgeRelation> = emptyMap()
)

data class KnowledgeEntity(
    val id: String,
    val label: String,
    val type: EntityType,
    val properties: Map<String, Any> = emptyMap(),
    val description: String = "",
    val embedding: VectorEmbeddingService.Embedding,
    val createdAt: Instant,
    val updatedAt: Instant
)

data class KnowledgeRelation(
    val id: String,
    val fromEntityId: String,
    val toEntityId: String,
    val type: RelationType,
    val properties: Map<String, Any> = emptyMap(),
    val weight: Double = 1.0,
    val createdAt: Instant
)

enum class EntityType {
    PERSON,
    ORGANIZATION,
    PROJECT,
    CONCEPT,
    TECHNOLOGY,
    DOCUMENT,
    TASK,
    DECISION,
    INSIGHT
}

enum class RelationType {
    RELATES_TO,
    PART_OF,
    INSTANCE_OF,
    SIMILAR_TO,
    DEPENDS_ON,
    INFLUENCES,
    WORKS_FOR,
    CREATED_BY,
    USES,
    IMPLEMENTS,
    EXTENDS
}

data class RelatedEntity(
    val entity: KnowledgeEntity,
    val relation: KnowledgeRelation,
    val path: List<String>,
    val distance: Int,
    val weight: Double
)

data class SemanticSearchResult(
    val entity: KnowledgeEntity,
    val similarity: Double,
    val matchedProperties: List<String>
)

data class InferredRelation(
    val fromEntity: KnowledgeEntity,
    val toEntity: KnowledgeEntity,
    val suggestedType: RelationType,
    val confidence: Double,
    val reasoning: String
)

data class EntityCluster(
    val id: Int,
    val entities: List<KnowledgeEntity>,
    val centroidLabel: String,
    val commonProperties: Map<String, Any>
)

data class GraphMetrics(
    val entityCount: Int,
    val relationCount: Int,
    val averageConnections: Double,
    val entityTypeDistribution: Map<EntityType, Int>,
    val relationTypeDistribution: Map<RelationType, Int>
)