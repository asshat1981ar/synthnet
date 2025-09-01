package com.synthnet.aiapp.testutils

import com.synthnet.aiapp.domain.models.*
import com.synthnet.aiapp.data.entities.*
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlin.random.Random

/**
 * Comprehensive test data builders for SynthNet AI testing framework
 */
object TestDataBuilders {
    
    /**
     * Agent test data builders
     */
    fun createTestAgent(
        id: String = "test-agent-${Random.nextInt()}",
        name: String = "Test Agent",
        role: AgentRole = AgentRole.IMPLEMENTATION,
        status: AgentStatus = AgentStatus.IDLE,
        capabilities: List<String> = listOf("testing", "development"),
        projectId: String = "test-project",
        metrics: AgentMetrics = createTestAgentMetrics(),
        isActive: Boolean = true
    ): Agent = Agent(
        id = id,
        name = name,
        role = role,
        status = status,
        capabilities = capabilities,
        projectId = projectId,
        metrics = metrics,
        isActive = isActive,
        createdAt = Clock.System.now(),
        updatedAt = Clock.System.now()
    )
    
    fun createTestAgentMetrics(
        successRate: Double = 0.85,
        averageResponseTime: Double = 2500.0,
        totalTasks: Int = 100,
        completedTasks: Int = 85,
        errorCount: Int = 5,
        lastActivity: Instant = Clock.System.now()
    ): AgentMetrics = AgentMetrics(
        successRate = successRate,
        averageResponseTime = averageResponseTime,
        totalTasks = totalTasks,
        completedTasks = completedTasks,
        errorCount = errorCount,
        lastActivity = lastActivity
    )
    
    /**
     * Project test data builders
     */
    fun createTestProject(
        id: String = "test-project-${Random.nextInt()}",
        name: String = "Test Project",
        description: String = "A test project for unit testing",
        status: ProjectStatus = ProjectStatus.ACTIVE,
        createdAt: Instant = Clock.System.now()
    ): Project = Project(
        id = id,
        name = name,
        description = description,
        status = status,
        createdAt = createdAt,
        updatedAt = Clock.System.now(),
        metadata = mapOf("test" to "true")
    )
    
    fun createTestProjectContext(
        workingMemory: List<ContextItem> = emptyList(),
        sessionMemory: List<ContextItem> = listOf(createTestContextItem()),
        projectMemory: List<ContextItem> = listOf(createTestContextItem("project"))
    ): ProjectContext = ProjectContext(
        workingMemory = workingMemory,
        sessionMemory = sessionMemory,
        projectMemory = projectMemory
    )
    
    fun createTestContextItem(
        type: String = "session",
        content: String = "Test context item",
        relevance: Double = 0.8,
        timestamp: Instant = Clock.System.now()
    ): ContextItem = ContextItem(
        id = "context-${Random.nextInt()}",
        type = type,
        content = content,
        relevance = relevance,
        timestamp = timestamp,
        metadata = mapOf("test" to "true")
    )
    
    /**
     * Thought and reasoning test data builders
     */
    fun createTestThought(
        id: String = "thought-${Random.nextInt()}",
        agentId: String = "test-agent",
        projectId: String = "test-project",
        content: String = "Test thought content",
        reasoning: String = "Test reasoning",
        confidence: Double = 0.8,
        parentId: String? = null,
        alternatives: List<Alternative> = emptyList(),
        type: ThoughtType = ThoughtType.ANALYSIS
    ): Thought = Thought(
        id = id,
        agentId = agentId,
        projectId = projectId,
        content = content,
        reasoning = reasoning,
        confidence = confidence,
        parentId = parentId,
        alternatives = alternatives,
        type = type,
        timestamp = Clock.System.now(),
        metadata = mapOf("test" to "true")
    )
    
    fun createTestThoughtTree(
        id: String = "tree-${Random.nextInt()}",
        projectId: String = "test-project",
        rootThought: Thought = createTestThought(),
        branches: List<ThoughtBranch> = listOf(createTestThoughtBranch()),
        depth: Int = 3,
        metrics: ThoughtTreeMetrics? = null
    ): ThoughtTree = ThoughtTree(
        id = id,
        projectId = projectId,
        rootThought = rootThought,
        branches = branches,
        depth = depth,
        createdAt = Clock.System.now(),
        metrics = metrics ?: createTestThoughtTreeMetrics()
    )
    
    fun createTestThoughtBranch(
        id: String = "branch-${Random.nextInt()}",
        parentThoughtId: String = "parent-thought",
        thoughts: List<Thought> = listOf(createTestThought()),
        score: Double = 0.8,
        isSelected: Boolean = false
    ): ThoughtBranch = ThoughtBranch(
        id = id,
        parentThoughtId = parentThoughtId,
        thoughts = thoughts,
        score = score,
        isSelected = isSelected,
        createdAt = Clock.System.now()
    )
    
    fun createTestThoughtTreeMetrics(
        totalThoughts: Int = 10,
        maxDepth: Int = 3,
        averageConfidence: Double = 0.75,
        branchingFactor: Double = 2.5,
        prunedBranches: Int = 2,
        selectedPaths: Int = 1,
        processingTime: Long = 5000L
    ): ThoughtTreeMetrics = ThoughtTreeMetrics(
        totalThoughts = totalThoughts,
        maxDepth = maxDepth,
        averageConfidence = averageConfidence,
        branchingFactor = branchingFactor,
        prunedBranches = prunedBranches,
        selectedPaths = selectedPaths,
        processingTime = processingTime
    )
    
    fun createTestChainOfThought(
        steps: List<ThoughtStep> = listOf(createTestThoughtStep()),
        conclusion: String = "Test conclusion",
        confidence: Double = 0.8
    ): ChainOfThought = ChainOfThought(
        steps = steps,
        conclusion = conclusion,
        confidence = confidence
    )
    
    fun createTestThoughtStep(
        id: String = "step-${Random.nextInt()}",
        description: String = "Test step",
        reasoning: String = "Test reasoning",
        evidence: List<String> = listOf("Test evidence"),
        assumptions: List<String> = listOf("Test assumption")
    ): ThoughtStep = ThoughtStep(
        id = id,
        description = description,
        reasoning = reasoning,
        evidence = evidence,
        assumptions = assumptions
    )
    
    /**
     * Response and Alternative test data builders
     */
    fun createTestAgentResponse(
        agentId: String = "test-agent",
        content: String = "Test response content",
        reasoning: ChainOfThought = createTestChainOfThought(),
        confidence: Double = 0.8,
        alternatives: List<Alternative> = listOf(createTestAlternative()),
        metadata: Map<String, String> = mapOf("test" to "true"),
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
    
    fun createTestAlternative(
        id: String = "alt-${Random.nextInt()}",
        description: String = "Test alternative",
        pros: List<String> = listOf("Test pro"),
        cons: List<String> = listOf("Test con"),
        score: Double = 0.7,
        reasoning: String = "Test alternative reasoning"
    ): Alternative = Alternative(
        id = id,
        description = description,
        pros = pros,
        cons = cons,
        score = score,
        reasoning = reasoning
    )
    
    /**
     * Collaboration test data builders
     */
    fun createTestCollaboration(
        id: String = "collab-${Random.nextInt()}",
        projectId: String = "test-project",
        participants: List<String> = listOf("agent1", "agent2"),
        sessionType: SessionType = SessionType.PROBLEM_SOLVING,
        status: CollaborationStatus = CollaborationStatus.ACTIVE,
        sharedContext: SharedContext = createTestSharedContext(),
        consensusReached: Boolean = false
    ): Collaboration = Collaboration(
        id = id,
        projectId = projectId,
        participants = participants,
        sessionType = sessionType,
        status = status,
        sharedContext = sharedContext,
        consensusReached = consensusReached,
        createdAt = Clock.System.now(),
        updatedAt = Clock.System.now()
    )
    
    fun createTestSharedContext(
        commonUnderstanding: List<String> = listOf("Common understanding"),
        agreedDecisions: List<Decision> = listOf(createTestDecision()),
        conflictingViews: List<ConflictingView> = emptyList(),
        syncPoints: List<SyncPoint> = listOf(createTestSyncPoint())
    ): SharedContext = SharedContext(
        commonUnderstanding = commonUnderstanding,
        agreedDecisions = agreedDecisions,
        conflictingViews = conflictingViews,
        syncPoints = syncPoints
    )
    
    fun createTestDecision(
        id: String = "decision-${Random.nextInt()}",
        description: String = "Test decision",
        rationale: String = "Test rationale",
        confidence: Double = 0.8,
        participants: List<String> = listOf("agent1", "agent2"),
        timestamp: Instant = Clock.System.now()
    ): Decision = Decision(
        id = id,
        description = description,
        rationale = rationale,
        confidence = confidence,
        participants = participants,
        timestamp = timestamp
    )
    
    fun createTestSyncPoint(
        id: String = "sync-${Random.nextInt()}",
        description: String = "Test sync point",
        timestamp: Instant = Clock.System.now(),
        participants: List<String> = listOf("agent1", "agent2"),
        status: String = "completed"
    ): SyncPoint = SyncPoint(
        id = id,
        description = description,
        timestamp = timestamp,
        participants = participants,
        status = status
    )
    
    fun createTestConflictingView(
        id: String = "conflict-${Random.nextInt()}",
        description: String = "Test conflict",
        positions: Map<String, String> = mapOf("agent1" to "Position A", "agent2" to "Position B"),
        resolution: String? = null,
        timestamp: Instant = Clock.System.now()
    ): ConflictingView = ConflictingView(
        id = id,
        description = description,
        positions = positions,
        resolution = resolution,
        timestamp = timestamp
    )
    
    /**
     * Entity test data builders (for repository testing)
     */
    fun createTestProjectEntity(
        id: String = "project-${Random.nextInt()}",
        name: String = "Test Project Entity",
        description: String = "Test project entity description",
        status: String = "ACTIVE",
        createdAt: Long = Clock.System.now().toEpochMilliseconds(),
        updatedAt: Long = Clock.System.now().toEpochMilliseconds(),
        metadata: String = """{"test": "true"}"""
    ): ProjectEntity = ProjectEntity(
        id = id,
        name = name,
        description = description,
        status = status,
        createdAt = createdAt,
        updatedAt = updatedAt,
        metadata = metadata
    )
    
    fun createTestAgentEntity(
        id: String = "agent-${Random.nextInt()}",
        name: String = "Test Agent Entity",
        role: String = "IMPLEMENTATION",
        status: String = "IDLE",
        capabilities: String = """["testing", "development"]""",
        projectId: String = "test-project",
        metrics: String = """{"successRate": 0.85, "averageResponseTime": 2500.0}""",
        isActive: Boolean = true,
        createdAt: Long = Clock.System.now().toEpochMilliseconds(),
        updatedAt: Long = Clock.System.now().toEpochMilliseconds()
    ): AgentEntity = AgentEntity(
        id = id,
        name = name,
        role = role,
        status = status,
        capabilities = capabilities,
        projectId = projectId,
        metrics = metrics,
        isActive = isActive,
        createdAt = createdAt,
        updatedAt = updatedAt
    )
    
    fun createTestThoughtEntity(
        id: String = "thought-${Random.nextInt()}",
        agentId: String = "test-agent",
        projectId: String = "test-project",
        content: String = "Test thought entity content",
        reasoning: String = "Test reasoning",
        confidence: Double = 0.8,
        parentId: String? = null,
        alternatives: String = "[]",
        type: String = "ANALYSIS",
        isSelected: Boolean = false,
        timestamp: Long = Clock.System.now().toEpochMilliseconds(),
        metadata: String = """{"test": "true"}"""
    ): ThoughtEntity = ThoughtEntity(
        id = id,
        agentId = agentId,
        projectId = projectId,
        content = content,
        reasoning = reasoning,
        confidence = confidence,
        parentId = parentId,
        alternatives = alternatives,
        type = type,
        isSelected = isSelected,
        timestamp = timestamp,
        metadata = metadata
    )
    
    fun createTestCollaborationEntity(
        id: String = "collab-${Random.nextInt()}",
        projectId: String = "test-project",
        participants: String = """["agent1", "agent2"]""",
        sessionType: String = "PROBLEM_SOLVING",
        status: String = "ACTIVE",
        sharedContext: String = """{"commonUnderstanding": ["Common understanding"]}""",
        consensusReached: Boolean = false,
        createdAt: Long = Clock.System.now().toEpochMilliseconds(),
        updatedAt: Long = Clock.System.now().toEpochMilliseconds()
    ): CollaborationEntity = CollaborationEntity(
        id = id,
        projectId = projectId,
        participants = participants,
        sessionType = sessionType,
        status = status,
        sharedContext = sharedContext,
        consensusReached = consensusReached,
        createdAt = createdAt,
        updatedAt = updatedAt
    )
    
    /**
     * Creates lists of test data for bulk testing
     */
    fun createTestAgentList(
        count: Int = 5,
        projectId: String = "test-project"
    ): List<Agent> = (1..count).map { i ->
        createTestAgent(
            id = "agent-$i",
            name = "Agent $i",
            role = AgentRole.values()[i % AgentRole.values().size],
            projectId = projectId
        )
    }
    
    fun createTestThoughtList(
        count: Int = 10,
        projectId: String = "test-project",
        agentId: String = "test-agent"
    ): List<Thought> = (1..count).map { i ->
        createTestThought(
            id = "thought-$i",
            projectId = projectId,
            agentId = agentId,
            content = "Test thought $i",
            confidence = 0.5 + (i * 0.05) // Varying confidence levels
        )
    }
    
    fun createTestProjectList(count: Int = 3): List<Project> = (1..count).map { i ->
        createTestProject(
            id = "project-$i",
            name = "Test Project $i",
            description = "Description for test project $i"
        )
    }
}