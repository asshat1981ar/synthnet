package com.synthnet.aiapp.domain.ai.embeddings

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.*

@Singleton
class VectorEmbeddingService @Inject constructor() {
    
    data class Embedding(
        val vector: FloatArray,
        val dimension: Int = vector.size,
        val metadata: Map<String, Any> = emptyMap()
    ) {
        fun cosineSimilarity(other: Embedding): Double {
            require(this.dimension == other.dimension) { "Embeddings must have same dimension" }
            
            val dotProduct = vector.zip(other.vector).sumOf { (a, b) -> (a * b).toDouble() }
            val normA = sqrt(vector.sumOf { (it * it).toDouble() })
            val normB = sqrt(other.vector.sumOf { (it * it).toDouble() })
            
            return dotProduct / (normA * normB)
        }
        
        override fun equals(other: Any?): Boolean {
            if (this === other) return true
            if (other !is Embedding) return false
            return vector.contentEquals(other.vector)
        }
        
        override fun hashCode(): Int {
            return vector.contentHashCode()
        }
    }
    
    suspend fun generateEmbedding(
        text: String,
        type: EmbeddingType = EmbeddingType.SEMANTIC
    ): Result<Embedding> = withContext(Dispatchers.IO) {
        try {
            // In a real implementation, this would call an embedding service like OpenAI, Cohere, etc.
            val embedding = when (type) {
                EmbeddingType.SEMANTIC -> generateSemanticEmbedding(text)
                EmbeddingType.CONTEXTUAL -> generateContextualEmbedding(text)
                EmbeddingType.CODE -> generateCodeEmbedding(text)
                EmbeddingType.KNOWLEDGE -> generateKnowledgeEmbedding(text)
            }
            
            Result.success(embedding)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun findSimilar(
        query: Embedding,
        candidates: List<Embedding>,
        threshold: Double = 0.7,
        maxResults: Int = 10
    ): List<SimilarityResult> = withContext(Dispatchers.Default) {
        candidates
            .map { candidate ->
                SimilarityResult(
                    embedding = candidate,
                    similarity = query.cosineSimilarity(candidate)
                )
            }
            .filter { it.similarity >= threshold }
            .sortedByDescending { it.similarity }
            .take(maxResults)
    }
    
    suspend fun clusterEmbeddings(
        embeddings: List<Embedding>,
        numClusters: Int = 5
    ): Result<List<EmbeddingCluster>> = withContext(Dispatchers.Default) {
        try {
            // Simple K-means clustering implementation
            val clusters = kMeansCluster(embeddings, numClusters)
            Result.success(clusters)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun generateSemanticEmbedding(text: String): Embedding {
        // Mock implementation - would use actual embedding model
        val words = text.lowercase().split("\\s+".toRegex())
        val vector = FloatArray(384) { 0f } // Common embedding dimension
        
        // Simple word frequency-based mock embedding
        words.forEachIndexed { index, word ->
            val hash = word.hashCode()
            for (i in 0 until 384) {
                vector[i] += ((hash + i) % 100) / 100f
            }
        }
        
        // Normalize vector
        val norm = sqrt(vector.sumOf { (it * it).toDouble() }).toFloat()
        for (i in vector.indices) {
            vector[i] = vector[i] / norm
        }
        
        return Embedding(
            vector = vector,
            metadata = mapOf(
                "text" to text,
                "type" to EmbeddingType.SEMANTIC,
                "word_count" to words.size
            )
        )
    }
    
    private fun generateContextualEmbedding(text: String): Embedding {
        // Mock contextual embedding with positional encoding
        val base = generateSemanticEmbedding(text)
        val contextVector = base.vector.copyOf()
        
        // Add positional encoding
        for (i in contextVector.indices step 2) {
            contextVector[i] *= sin(i / 10000.0).toFloat()
            if (i + 1 < contextVector.size) {
                contextVector[i + 1] *= cos(i / 10000.0).toFloat()
            }
        }
        
        return Embedding(
            vector = contextVector,
            metadata = base.metadata + ("type" to EmbeddingType.CONTEXTUAL)
        )
    }
    
    private fun generateCodeEmbedding(text: String): Embedding {
        // Mock code embedding with syntax awareness
        val base = generateSemanticEmbedding(text)
        val codeVector = base.vector.copyOf()
        
        // Boost weights for code-related patterns
        val codeKeywords = listOf("class", "function", "import", "return", "if", "for", "while")
        val words = text.lowercase().split("\\s+".toRegex())
        val codeBoost = words.count { it in codeKeywords } / words.size.toFloat()
        
        for (i in codeVector.indices) {
            codeVector[i] *= (1 + codeBoost)
        }
        
        return Embedding(
            vector = codeVector,
            metadata = base.metadata + mapOf(
                "type" to EmbeddingType.CODE,
                "code_boost" to codeBoost
            )
        )
    }
    
    private fun generateKnowledgeEmbedding(text: String): Embedding {
        // Mock knowledge embedding with entity recognition
        val base = generateSemanticEmbedding(text)
        val knowledgeVector = base.vector.copyOf()
        
        // Simple entity detection (mock)
        val entities = extractEntities(text)
        val entityBoost = entities.size / 10f
        
        for (i in knowledgeVector.indices) {
            knowledgeVector[i] *= (1 + entityBoost)
        }
        
        return Embedding(
            vector = knowledgeVector,
            metadata = base.metadata + mapOf(
                "type" to EmbeddingType.KNOWLEDGE,
                "entities" to entities,
                "entity_count" to entities.size
            )
        )
    }
    
    private fun extractEntities(text: String): List<String> {
        // Mock entity extraction
        val words = text.split("\\s+".toRegex())
        return words.filter { it.length > 3 && it[0].isUpperCase() }
    }
    
    private fun kMeansCluster(embeddings: List<Embedding>, k: Int): List<EmbeddingCluster> {
        if (embeddings.isEmpty()) return emptyList()
        
        val dimension = embeddings.first().dimension
        var centroids = initializeCentroids(embeddings, k, dimension)
        var assignments = IntArray(embeddings.size) { 0 }
        
        repeat(10) { // Max 10 iterations
            // Assign points to clusters
            embeddings.forEachIndexed { i, embedding ->
                assignments[i] = centroids.withIndex().minByOrNull { (_, centroid) ->
                    embedding.cosineSimilarity(centroid)
                }?.index ?: 0
            }
            
            // Update centroids
            centroids = updateCentroids(embeddings, assignments, k, dimension)
        }
        
        return (0 until k).map { clusterId ->
            val clusterEmbeddings = embeddings.filterIndexed { i, _ -> assignments[i] == clusterId }
            EmbeddingCluster(
                id = clusterId,
                centroid = centroids[clusterId],
                members = clusterEmbeddings,
                size = clusterEmbeddings.size
            )
        }
    }
    
    private fun initializeCentroids(embeddings: List<Embedding>, k: Int, dimension: Int): List<Embedding> {
        return embeddings.shuffled().take(k)
    }
    
    private fun updateCentroids(
        embeddings: List<Embedding>,
        assignments: IntArray,
        k: Int,
        dimension: Int
    ): List<Embedding> {
        return (0 until k).map { clusterId ->
            val clusterPoints = embeddings.filterIndexed { i, _ -> assignments[i] == clusterId }
            
            if (clusterPoints.isEmpty()) {
                Embedding(FloatArray(dimension) { 0f })
            } else {
                val centroidVector = FloatArray(dimension) { 0f }
                clusterPoints.forEach { embedding ->
                    embedding.vector.forEachIndexed { i, value ->
                        centroidVector[i] += value
                    }
                }
                
                val count = clusterPoints.size.toFloat()
                for (i in centroidVector.indices) {
                    centroidVector[i] /= count
                }
                
                Embedding(centroidVector)
            }
        }
    }
}

enum class EmbeddingType {
    SEMANTIC,
    CONTEXTUAL,
    CODE,
    KNOWLEDGE
}

data class SimilarityResult(
    val embedding: VectorEmbeddingService.Embedding,
    val similarity: Double
)

data class EmbeddingCluster(
    val id: Int,
    val centroid: VectorEmbeddingService.Embedding,
    val members: List<VectorEmbeddingService.Embedding>,
    val size: Int
)