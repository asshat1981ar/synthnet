package com.synthnet.aiapp.testutils

import com.synthnet.aiapp.data.entities.*
import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.domain.analytics.EnhancedAnalyticsModels.*
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlin.random.Random

/**
 * Comprehensive test data factory for generating realistic test data across all SynthNet components.
 * Provides builders and generators for entities, domain models, and complex data structures.
 */
object TestDataFactory {

    // Agent Test Data
    fun createAgent(
        id: String = "agent_${Random.nextInt(10000)}",
        name: String = "Test Agent",
        role: AgentRole = AgentRole.STRATEGY,
        capabilities: List<String> = listOf("analysis", "reasoning", "planning"),
        status: AgentStatus = AgentStatus.IDLE,
        projectId: String = "test_project_123",
        isActive: Boolean = true,
        metrics: ContributionMetrics = createContributionMetrics(),
        createdAt: Instant = Clock.System.now(),
        updatedAt: Instant = Clock.System.now()
    ): Agent = Agent(
        id = id,
        name = name,
        role = role,
        capabilities = capabilities,
        status = status,
        projectId = projectId,
        isActive = isActive,
        metrics = metrics,
        createdAt = createdAt,
        updatedAt = updatedAt
    )

    fun createAgentEntity(
        id: String = "agent_${Random.nextInt(10000)}",
        name: String = "Test Agent Entity",
        role: AgentRole = AgentRole.IMPLEMENTATION,
        capabilities: String = "development,testing,deployment",
        status: AgentStatus = AgentStatus.IDLE,
        projectId: String = "test_project_123",
        isActive: Boolean = true,
        successRate: Double = 0.85,
        averageResponseTime: Long = 2500L,
        createdAt: Instant = Clock.System.now(),
        updatedAt: Instant = Clock.System.now()
    ): AgentEntity = AgentEntity(
        id = id,
        name = name,
        role = role,
        capabilities = capabilities,
        status = status,
        projectId = projectId,
        isActive = isActive,
        successRate = successRate,
        averageResponseTime = averageResponseTime,
        createdAt = createdAt,
        updatedAt = updatedAt
    )

    // Project Test Data
    fun createProject(
        id: String = "project_${Random.nextInt(10000)}",
        name: String = "Test Project",
        description: String = "A comprehensive test project for AI collaboration",
        isActive: Boolean = true,
        createdAt: Instant = Clock.System.now(),
        updatedAt: Instant = Clock.System.now()
    ): Project = Project(
        id = id,
        name = name,
        description = description,
        isActive = isActive,
        createdAt = createdAt,
        updatedAt = updatedAt
    )

    fun createProjectEntity(
        id: String = "project_${Random.nextInt(10000)}",
        name: String = "Test Project Entity",
        description: String = "A comprehensive test project entity for database operations",
        isActive: Boolean = true,
        createdAt: Instant = Clock.System.now(),
        updatedAt: Instant = Clock.System.now()
    ): ProjectEntity = ProjectEntity(
        id = id,
        name = name,
        description = description,
        isActive = isActive,
        createdAt = createdAt,
        updatedAt = updatedAt
    )

    // Thought and Reasoning Test Data
    fun createThought(
        id: String = "thought_${Random.nextInt(10000)}",
        content: String = "This is a comprehensive analysis of the problem domain with detailed reasoning...",
        reasoning: String = "Based on multiple factors including user requirements, technical constraints, and business objectives",
        confidence: Double = 0.85,
        agentId: String = "test_agent_123",
        projectId: String = "test_project_123",
        parentId: String? = null,
        alternatives: List<Alternative> = listOf(createAlternative()),
        metadata: Map<String, String> = mapOf("complexity" to "high", "domain" to "software_development"),
        timestamp: Instant = Clock.System.now()
    ): Thought = Thought(
        id = id,
        content = content,
        reasoning = reasoning,
        confidence = confidence,
        agentId = agentId,
        projectId = projectId,
        parentId = parentId,
        alternatives = alternatives,
        metadata = metadata,
        timestamp = timestamp
    )

    fun createThoughtEntity(
        id: String = "thought_${Random.nextInt(10000)}",
        content: String = "Test thought content with comprehensive analysis",
        reasoning: String = "Detailed reasoning chain with evidence and assumptions",
        confidence: Double = 0.78,
        agentId: String = "test_agent_123",
        projectId: String = "test_project_123",
        parentId: String? = null,
        alternatives: String = """[{"id":"alt1","description":"Alternative approach","score":0.7}]""",
        metadata: String = """{"complexity":"medium","domain":"ai_reasoning"}""",
        timestamp: Instant = Clock.System.now(),
        isSelected: Boolean = false
    ): ThoughtEntity = ThoughtEntity(
        id = id,
        content = content,
        reasoning = reasoning,
        confidence = confidence,
        agentId = agentId,
        projectId = projectId,
        parentId = parentId,
        alternatives = alternatives,
        metadata = metadata,
        timestamp = timestamp,
        isSelected = isSelected
    )

    fun createThoughtNode(
        id: String = "node_${Random.nextInt(10000)}",
        thought: Thought = createThought(),
        children: MutableList<ThoughtNode> = mutableListOf(),
        depth: Int = 0,
        isExpanded: Boolean = false,
        explorationScore: Double = 0.75
    ): ThoughtNode = ThoughtNode(
        id = id,
        thought = thought,
        children = children,
        depth = depth,
        isExpanded = isExpanded,
        explorationScore = explorationScore
    )

    fun createThoughtTree(
        rootThought: Thought = createThought(id = "root_thought"),
        branches: List<ThoughtBranch> = listOf(createThoughtBranch()),
        maxDepth: Int = 3,
        totalNodes: Int = 12,
        explorationComplete: Boolean = false
    ): ThoughtTree = ThoughtTree(
        rootThought = rootThought,
        branches = branches,
        maxDepth = maxDepth,
        totalNodes = totalNodes,
        explorationComplete = explorationComplete
    )

    fun createThoughtBranch(
        id: String = "branch_${Random.nextInt(10000)}",
        thoughts: List<Thought> = listOf(createThought(), createThought()),
        score: Double = 0.82,
        isComplete: Boolean = true
    ): ThoughtBranch = ThoughtBranch(
        id = id,
        thoughts = thoughts,
        score = score,
        isComplete = isComplete
    )

    // Collaboration Test Data
    fun createCollaboration(
        id: String = "collab_${Random.nextInt(10000)}",
        projectId: String = "test_project_123",
        participants: List<String> = listOf("agent_1", "agent_2", "agent_3"),
        sessionType: SessionType = SessionType.PROBLEM_SOLVING,
        status: CollaborationStatus = CollaborationStatus.ACTIVE,
        sharedContext: SharedContext = createSharedContext(),
        consensusReached: Boolean = false,
        startTime: Instant = Clock.System.now(),
        endTime: Instant? = null
    ): Collaboration = Collaboration(
        id = id,
        projectId = projectId,
        participants = participants,
        sessionType = sessionType,
        status = status,
        sharedContext = sharedContext,
        consensusReached = consensusReached,
        startTime = startTime,
        endTime = endTime
    )

    fun createCollaborationEntity(
        id: String = "collab_entity_${Random.nextInt(10000)}",
        projectId: String = "test_project_123",
        participants: String = "agent_1,agent_2,agent_3",
        sessionType: SessionType = SessionType.BRAINSTORMING,
        status: CollaborationStatus = CollaborationStatus.ACTIVE,
        sharedContext: String = """{"commonUnderstanding":["Key insight 1","Key insight 2"],"agreedDecisions":[]}""",
        consensusReached: Boolean = false,
        startTime: Instant = Clock.System.now(),
        endTime: Instant? = null
    ): CollaborationEntity = CollaborationEntity(
        id = id,
        projectId = projectId,
        participants = participants,
        sessionType = sessionType,
        status = status,
        sharedContext = sharedContext,
        consensusReached = consensusReached,
        startTime = startTime,
        endTime = endTime
    )

    fun createSharedContext(
        commonUnderstanding: List<String> = listOf(
            "The project requires a scalable architecture",
            "Performance optimization is critical",
            "User experience should be prioritized"
        ),
        agreedDecisions: List<Decision> = listOf(createDecision()),
        conflictingViews: List<ConflictingView> = emptyList(),
        syncPoints: List<SyncPoint> = listOf(createSyncPoint())
    ): SharedContext = SharedContext(
        commonUnderstanding = commonUnderstanding,
        agreedDecisions = agreedDecisions,
        conflictingViews = conflictingViews,
        syncPoints = syncPoints
    )

    // Supporting Models
    fun createAlternative(
        id: String = "alt_${Random.nextInt(10000)}",
        description: String = "Alternative approach using microservices architecture",
        pros: List<String> = listOf("Better scalability", "Independent deployment", "Technology diversity"),
        cons: List<String> = listOf("Increased complexity", "Network overhead", "Monitoring challenges"),
        score: Double = 0.72,
        reasoning: String = "Microservices offer better long-term scalability but require more sophisticated infrastructure"
    ): Alternative = Alternative(
        id = id,
        description = description,
        pros = pros,
        cons = cons,
        score = score,
        reasoning = reasoning
    )

    fun createDecision(
        id: String = "decision_${Random.nextInt(10000)}",
        description: String = "Use containerized deployment strategy",
        rationale: String = "Containers provide consistent deployment environment across dev/staging/prod",
        confidence: Double = 0.88,
        supportingEvidence: List<String> = listOf("Industry best practice", "Team expertise available", "Infrastructure ready"),
        timestamp: Instant = Clock.System.now()
    ): Decision = Decision(
        id = id,
        description = description,
        rationale = rationale,
        confidence = confidence,
        supportingEvidence = supportingEvidence,
        timestamp = timestamp
    )

    fun createConflictingView(
        agentId: String = "agent_${Random.nextInt(1000)}",
        position: String = "Prefer monolithic architecture for initial deployment",
        reasoning: String = "Simpler deployment and debugging for MVP phase",
        confidence: Double = 0.65,
        supportingEvidence: List<String> = listOf("Faster initial development", "Simpler monitoring", "Lower operational overhead")
    ): ConflictingView = ConflictingView(
        agentId = agentId,
        position = position,
        reasoning = reasoning,
        confidence = confidence,
        supportingEvidence = supportingEvidence
    )

    fun createSyncPoint(
        id: String = "sync_${Random.nextInt(10000)}",
        description: String = "Architecture decision checkpoint",
        timestamp: Instant = Clock.System.now(),
        participants: List<String> = listOf("agent_1", "agent_2"),
        outcomes: List<String> = listOf("Agreed on container strategy", "Defined deployment pipeline")
    ): SyncPoint = SyncPoint(
        id = id,
        description = description,
        timestamp = timestamp,
        participants = participants,
        outcomes = outcomes
    )

    fun createContributionMetrics(
        successRate: Double = 0.85,
        averageResponseTime: Long = 2500L,
        totalContributions: Int = 42,
        qualityScore: Double = 0.78,
        collaborationRating: Double = 0.91
    ): ContributionMetrics = ContributionMetrics(
        successRate = successRate,
        averageResponseTime = averageResponseTime,
        totalContributions = totalContributions,
        qualityScore = qualityScore,
        collaborationRating = collaborationRating
    )

    // AI Response Models
    fun createAgentResponse(
        agentId: String = "test_agent_${Random.nextInt(1000)}",
        content: String = "Based on comprehensive analysis, I recommend implementing a microservices architecture with containerized deployment. This approach provides scalability benefits while maintaining development velocity.",
        reasoning: ChainOfThought = createChainOfThought(),
        confidence: Double = 0.87,
        alternatives: List<Alternative> = listOf(createAlternative()),
        metadata: Map<String, String> = mapOf(
            "processing_time_ms" to "1250",
            "thought_tree_depth" to "3",
            "collaboration_participants" to "4"
        ),
        timestamp: Instant = Clock.System.now()
    ): AgentResponse = AgentResponse(
        agentId = agentId,
        content = content,
        reasoning = reasoning,
        confidence = confidence,
        alternatives = alternatives,
        metadata = metadata,
        timestamp = timestamp
    )

    fun createChainOfThought(
        steps: List<ThoughtStep> = listOf(
            createThoughtStep("analyze_requirements"),
            createThoughtStep("evaluate_options"),
            createThoughtStep("assess_constraints")
        ),
        conclusion: String = "Microservices architecture is the optimal solution based on scalability requirements and team capabilities",
        confidence: Double = 0.84
    ): ChainOfThought = ChainOfThought(
        steps = steps,
        conclusion = conclusion,
        confidence = confidence
    )

    fun createThoughtStep(
        id: String = "step_${Random.nextInt(10000)}",
        description: String = "Analyze system requirements and constraints",
        reasoning: String = "Examined scalability needs, team expertise, infrastructure capabilities, and timeline constraints",
        evidence: List<String> = listOf(
            "Current system handles 10K users",
            "Expected growth to 100K users in 12 months",
            "Team has container deployment experience"
        ),
        assumptions: List<String> = listOf(
            "Growth projections are accurate",
            "Infrastructure budget is available",
            "Team training time is acceptable"
        )
    ): ThoughtStep = ThoughtStep(
        id = id,
        description = description,
        reasoning = reasoning,
        evidence = evidence,
        assumptions = assumptions
    )

    // Project Context
    fun createProjectContext(
        workingMemory: List<ContextItem> = listOf(
            createContextItem("current_task", "Design system architecture"),
            createContextItem("user_input", "Create a scalable mobile app backend")
        ),
        sessionMemory: List<ContextItem> = listOf(
            createContextItem("previous_decision", "Decided on React Native for mobile"),
            createContextItem("constraint", "Budget limit of $50K")
        ),
        projectMemory: List<ContextItem> = listOf(
            createContextItem("team_size", "5 developers"),
            createContextItem("timeline", "6 months to MVP"),
            createContextItem("target_users", "10K initial, 100K within year")
        )
    ): ProjectContext = ProjectContext(
        workingMemory = workingMemory,
        sessionMemory = sessionMemory,
        projectMemory = projectMemory
    )

    fun createContextItem(
        key: String = "context_key_${Random.nextInt(1000)}",
        content: String = "Context content with relevant information",
        relevanceScore: Double = 0.75,
        timestamp: Instant = Clock.System.now(),
        source: String = "test_agent"
    ): ContextItem = ContextItem(
        key = key,
        content = content,
        relevanceScore = relevanceScore,
        timestamp = timestamp,
        source = source
    )

    // Analytics Models
    fun createUserEngagementMetrics(
        userId: String = "user_${Random.nextInt(10000)}",
        sessionDuration: Long = 45000L,
        interactionCount: Int = 23,
        featureUsage: Map<String, Int> = mapOf(
            "ai_chat" to 15,
            "project_creation" to 2,
            "collaboration" to 6
        ),
        timestamp: Instant = Clock.System.now()
    ): UserEngagementMetrics = UserEngagementMetrics(
        userId = userId,
        sessionDuration = sessionDuration,
        interactionCount = interactionCount,
        featureUsage = featureUsage,
        timestamp = timestamp
    )

    fun createAIPerformanceMetrics(
        modelId: String = "gpt-4",
        averageResponseTime: Long = 3200L,
        successRate: Double = 0.92,
        confidenceDistribution: Map<String, Int> = mapOf(
            "high" to 45,
            "medium" to 32,
            "low" to 13
        ),
        errorCategories: Map<String, Int> = mapOf(
            "timeout" to 2,
            "api_error" to 1,
            "parsing_error" to 0
        ),
        timestamp: Instant = Clock.System.now()
    ): AIPerformanceMetrics = AIPerformanceMetrics(
        modelId = modelId,
        averageResponseTime = averageResponseTime,
        successRate = successRate,
        confidenceDistribution = confidenceDistribution,
        errorCategories = errorCategories,
        timestamp = timestamp
    )

    // Collection Builders for Bulk Test Data
    fun createAgentList(count: Int = 5): List<Agent> = (1..count).map { index ->
        createAgent(
            id = "agent_$index",
            name = "Test Agent $index",
            role = AgentRole.values()[index % AgentRole.values().size],
            capabilities = listOf("skill_$index", "capability_$index")
        )
    }

    fun createProjectList(count: Int = 3): List<Project> = (1..count).map { index ->
        createProject(
            id = "project_$index",
            name = "Test Project $index",
            description = "Description for test project $index"
        )
    }

    fun createThoughtList(count: Int = 10): List<Thought> = (1..count).map { index ->
        createThought(
            id = "thought_$index",
            content = "Thought content $index with detailed analysis and recommendations",
            confidence = 0.5 + (index * 0.05) // Varying confidence from 0.5 to 1.0
        )
    }

    fun createCollaborationList(count: Int = 3): List<Collaboration> = (1..count).map { index ->
        createCollaboration(
            id = "collab_$index",
            sessionType = SessionType.values()[index % SessionType.values().size],
            participants = (1..(index + 2)).map { "agent_$it" }
        )
    }

    // Error Scenarios for Testing
    fun createInvalidAgent(): Agent = createAgent(
        id = "", // Invalid empty ID
        capabilities = emptyList(), // No capabilities
        status = AgentStatus.ERROR
    )

    fun createCorruptedThought(): Thought = createThought(
        content = "", // Empty content
        confidence = -0.5, // Invalid negative confidence
        reasoning = ""
    )

    fun createFailedCollaboration(): Collaboration = createCollaboration(
        participants = emptyList(), // No participants
        status = CollaborationStatus.ERROR,
        consensusReached = false
    )

    // Large Data Sets for Performance Testing
    fun createLargeThoughtTree(depth: Int = 5, branchingFactor: Int = 3): ThoughtTree {
        val rootThought = createThought(id = "root")
        val branches = mutableListOf<ThoughtBranch>()
        
        repeat(branchingFactor) { branchIndex ->
            val thoughts = mutableListOf<Thought>()
            var currentThought = createThought(
                id = "thought_0_$branchIndex",
                parentId = rootThought.id
            )
            thoughts.add(currentThought)
            
            for (level in 1 until depth) {
                val nextThought = createThought(
                    id = "thought_${level}_$branchIndex",
                    parentId = currentThought.id
                )
                thoughts.add(nextThought)
                currentThought = nextThought
            }
            
            branches.add(createThoughtBranch(
                id = "branch_$branchIndex",
                thoughts = thoughts,
                score = 0.5 + (branchIndex * 0.1)
            ))
        }
        
        return ThoughtTree(
            rootThought = rootThought,
            branches = branches,
            maxDepth = depth,
            totalNodes = 1 + (branches.size * depth),
            explorationComplete = true
        )
    }

    fun createHighLoadCollaboration(participantCount: Int = 10): Collaboration = createCollaboration(
        participants = (1..participantCount).map { "agent_$it" },
        sharedContext = SharedContext(
            commonUnderstanding = (1..20).map { "Understanding point $it" },
            agreedDecisions = (1..10).map { createDecision(id = "decision_$it") },
            conflictingViews = (1..5).map { createConflictingView(agentId = "agent_$it") },
            syncPoints = (1..8).map { createSyncPoint(id = "sync_$it") }
        )
    )
}