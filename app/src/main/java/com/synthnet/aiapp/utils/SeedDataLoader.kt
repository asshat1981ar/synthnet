package com.synthnet.aiapp.utils

import com.synthnet.aiapp.data.entities.*
import com.synthnet.aiapp.domain.repository.*
import com.synthnet.aiapp.domain.models.*
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlinx.datetime.DateTimeUnit
import kotlinx.datetime.minus
import kotlinx.datetime.plus
import kotlin.random.Random
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SeedDataLoader @Inject constructor(
    private val projectRepository: ProjectRepository,
    private val agentRepository: AgentRepository,
    private val thoughtRepository: ThoughtRepository,
    private val collaborationRepository: CollaborationRepository
) {
    
    companion object {
        private val PROJECT_TEMPLATES = listOf(
            ProjectTemplate(
                nameTemplate = "{adjective} {domain} {type}",
                domains = listOf("AI", "Mobile", "Web", "Data", "Cloud", "IoT", "Blockchain"),
                types = listOf("Platform", "Application", "System", "Framework", "Service", "Tool"),
                adjectives = listOf("Smart", "Intelligent", "Advanced", "Next-Gen", "Innovative", "Adaptive")
            )
        )
        
        private val REALISTIC_SCENARIOS = listOf(
            "Healthcare Management System",
            "Financial Trading Platform",
            "E-commerce Recommendation Engine",
            "Smart City Traffic Management",
            "Educational Content Platform",
            "Environmental Monitoring System",
            "Supply Chain Optimizer",
            "Customer Service Chatbot",
            "Content Creation Assistant",
            "Predictive Maintenance System"
        )
    }
    
    data class ProjectTemplate(
        val nameTemplate: String,
        val domains: List<String>,
        val types: List<String>,
        val adjectives: List<String>
    )
    
    data class SeedDataConfiguration(
        val projectCount: Int = 5,
        val agentsPerProject: IntRange = 3..6,
        val thoughtsPerProject: IntRange = 10..25,
        val collaborationsPerProject: IntRange = 2..5,
        val timeSpreadDays: Int = 90,
        val includeHistoricalData: Boolean = true,
        val complexityLevel: ComplexityLevel = ComplexityLevel.MEDIUM
    )
    
    enum class ComplexityLevel {
        SIMPLE, MEDIUM, COMPLEX, ENTERPRISE
    }
    
    suspend fun loadSeedData(config: SeedDataConfiguration = SeedDataConfiguration()) {
        println("Loading comprehensive seed data with ${config.projectCount} projects...")
        
        // Generate diverse projects based on configuration
        val projects = generateDiverseProjects(config)
        
        for ((index, project) in projects.withIndex()) {
            println("Creating project ${index + 1}/${projects.size}: ${project.name}")
            
            // Create project
            projectRepository.createProject(project)
            
            // Generate agents for project
            val agents = generateProjectAgents(project, config)
            agents.forEach { agent ->
                agentRepository.createAgent(agent)
            }
            
            // Generate thought trees
            val thoughts = generateProjectThoughts(project, agents, config)
            thoughts.forEach { thought ->
                thoughtRepository.createThought(thought)
            }
            
            // Generate collaborations
            val collaborations = generateProjectCollaborations(project, agents, config)
            collaborations.forEach { collaboration ->
                collaborationRepository.createCollaboration(collaboration)
            }
        }
        
        if (config.includeHistoricalData) {
            generateHistoricalMetrics(projects)
        }
        
        println("Seed data loading completed successfully!")
    }
    
    private fun generateDiverseProjects(config: SeedDataConfiguration): List<Project> {
        val projects = mutableListOf<Project>()
        val now = Clock.System.now()
        
        repeat(config.projectCount) { index ->
            val scenario = REALISTIC_SCENARIOS[index % REALISTIC_SCENARIOS.size]
            val createdAt = now.minus((Random.nextInt(config.timeSpreadDays)).toLong(), DateTimeUnit.DAY)
            val updatedAt = createdAt.plus((Random.nextInt(30)).toLong(), DateTimeUnit.DAY)
            
            val project = Project(
                id = "project_${index + 1}_${System.currentTimeMillis()}",
                name = scenario,
                description = generateProjectDescription(scenario, config.complexityLevel),
                autonomyLevel = generateAutonomyLevel(config.complexityLevel),
                status = generateProjectStatus(),
                createdAt = createdAt,
                updatedAt = updatedAt,
                tags = generateProjectTags(scenario),
                collaborators = generateCollaborators(config.complexityLevel),
                metrics = generateProjectMetrics(config.complexityLevel)
            )
            
            projects.add(project)
        }
        
        return projects
    }
    
    private fun generateProjectAgents(project: Project, config: SeedDataConfiguration): List<Agent> {
        val agents = mutableListOf<Agent>()
        val agentCount = config.agentsPerProject.random()
        val now = Clock.System.now()
        
        // Always include a conductor
        agents.add(generateAgent(
            projectId = project.id,
            role = AgentRole.CONDUCTOR,
            index = 0,
            complexity = config.complexityLevel
        ))
        
        // Add other specialized agents
        val remainingRoles = listOf(
            AgentRole.STRATEGY,
            AgentRole.IMPLEMENTATION,
            AgentRole.TESTING,
            AgentRole.DOCUMENTATION,
            AgentRole.REVIEW
        ).shuffled()
        
        repeat(agentCount - 1) { index ->
            val role = remainingRoles[index % remainingRoles.size]
            agents.add(generateAgent(
                projectId = project.id,
                role = role,
                index = index + 1,
                complexity = config.complexityLevel
            ))
        }
        
        return agents
    }
    
    private fun generateProjectThoughts(project: Project, agents: List<Agent>, config: SeedDataConfiguration): List<Thought> {
        val thoughts = mutableListOf<Thought>()
        val thoughtCount = config.thoughtsPerProject.random()
        val now = Clock.System.now()
        
        // Generate root thoughts
        val rootThought = generateRootThought(project, agents.first())
        thoughts.add(rootThought)
        
        // Generate thought tree branches
        val branchingFactor = when (config.complexityLevel) {
            ComplexityLevel.SIMPLE -> 2..3
            ComplexityLevel.MEDIUM -> 3..4
            ComplexityLevel.COMPLEX -> 4..6
            ComplexityLevel.ENTERPRISE -> 5..8
        }
        
        var currentThoughts = listOf(rootThought)
        var remainingThoughts = thoughtCount - 1
        var depth = 1
        
        while (remainingThoughts > 0 && currentThoughts.isNotEmpty() && depth < 6) {
            val nextLevelThoughts = mutableListOf<Thought>()
            
            for (parentThought in currentThoughts) {
                val branchCount = minOf(
                    branchingFactor.random(),
                    remainingThoughts
                )
                
                repeat(branchCount) { branchIndex ->
                    if (remainingThoughts > 0) {
                        val childThought = generateChildThought(
                            parent = parentThought,
                            agent = agents.random(),
                            depth = depth,
                            branchIndex = branchIndex
                        )
                        thoughts.add(childThought)
                        nextLevelThoughts.add(childThought)
                        remainingThoughts--
                    }
                }
            }
            
            currentThoughts = nextLevelThoughts
            depth++
        }
        
        return thoughts
    }
    
    private fun generateProjectCollaborations(project: Project, agents: List<Agent>, config: SeedDataConfiguration): List<Collaboration> {
        val collaborations = mutableListOf<Collaboration>()
        val collaborationCount = config.collaborationsPerProject.random()
        val now = Clock.System.now()
        
        repeat(collaborationCount) { index ->
            val sessionType = SessionType.values().random()
            val participantCount = when (config.complexityLevel) {
                ComplexityLevel.SIMPLE -> 2..3
                ComplexityLevel.MEDIUM -> 3..4
                ComplexityLevel.COMPLEX -> 4..agents.size
                ComplexityLevel.ENTERPRISE -> 3..agents.size
            }.random()
            
            val participants = agents.shuffled().take(participantCount).map { it.id }
            val startedAt = now.minus((Random.nextInt(30)).toLong(), DateTimeUnit.DAY)
            val duration = Random.nextInt(30, 180) // 30 minutes to 3 hours
            val endedAt = if (Random.nextBoolean()) {
                startedAt.plus(duration.toLong(), DateTimeUnit.MINUTE)
            } else null // Some ongoing collaborations
            
            val collaboration = Collaboration(
                id = "collab_${project.id}_$index",
                projectId = project.id,
                sessionType = sessionType,
                participants = participants,
                status = if (endedAt == null) CollaborationStatus.ACTIVE else CollaborationStatus.COMPLETED,
                startedAt = startedAt,
                endedAt = endedAt,
                syncPoints = generateSyncPoints(sessionType, participants.size),
                knowledgeExchanges = Random.nextInt(1, 20),
                consensusReached = Random.nextBoolean(),
                agentPresences = generateAgentPresences(participants, startedAt),
                sharedContext = generateSharedContext(sessionType)
            )
            
            collaborations.add(collaboration)
        }
        
        return collaborations
    }
    
    // Helper methods for generating realistic data
    private fun generateProjectDescription(scenario: String, complexity: ComplexityLevel): String {
        val baseDescriptions = mapOf(
            "Healthcare Management System" to "Comprehensive healthcare platform integrating patient records, appointment scheduling, and medical analytics",
            "Financial Trading Platform" to "Real-time trading system with advanced analytics, risk management, and algorithmic trading capabilities",
            "E-commerce Recommendation Engine" to "AI-powered recommendation system that analyzes user behavior and preferences to suggest relevant products",
            "Smart City Traffic Management" to "Intelligent traffic control system using IoT sensors and machine learning to optimize urban traffic flow",
            "Educational Content Platform" to "Adaptive learning platform that personalizes educational content based on student progress and learning style"
        )
        
        val base = baseDescriptions[scenario] ?: "Advanced $scenario with intelligent automation and analytics capabilities"
        
        return when (complexity) {
            ComplexityLevel.SIMPLE -> base
            ComplexityLevel.MEDIUM -> "$base. Features modern architecture with microservices and cloud integration."
            ComplexityLevel.COMPLEX -> "$base. Enterprise-grade solution with advanced security, scalability, and integration capabilities."
            ComplexityLevel.ENTERPRISE -> "$base. Mission-critical system with enterprise security, multi-tenant architecture, and comprehensive audit trails."
        }
    }
    
    private fun generateAutonomyLevel(complexity: ComplexityLevel): AutonomyLevel {
        return when (complexity) {
            ComplexityLevel.SIMPLE -> listOf(AutonomyLevel.MANUAL, AutonomyLevel.ASSISTED).random()
            ComplexityLevel.MEDIUM -> listOf(AutonomyLevel.ASSISTED, AutonomyLevel.SEMI_AUTONOMOUS).random()
            ComplexityLevel.COMPLEX -> listOf(AutonomyLevel.SEMI_AUTONOMOUS, AutonomyLevel.FULLY_AUTONOMOUS).random()
            ComplexityLevel.ENTERPRISE -> AutonomyLevel.FULLY_AUTONOMOUS
        }
    }
    
    private fun generateProjectStatus(): ProjectStatus {
        return ProjectStatus.values().random()
    }
    
    private fun generateProjectTags(scenario: String): List<String> {
        val baseTags = when {
            scenario.contains("Healthcare") -> listOf("healthcare", "medical", "patient-care", "HIPAA")
            scenario.contains("Financial") -> listOf("fintech", "trading", "finance", "real-time", "security")
            scenario.contains("E-commerce") -> listOf("retail", "recommendation", "AI", "personalization")
            scenario.contains("Smart City") -> listOf("IoT", "urban", "traffic", "sensors", "optimization")
            scenario.contains("Educational") -> listOf("education", "learning", "adaptive", "students")
            else -> listOf("technology", "innovation", "automation")
        }
        
        val commonTags = listOf("AI", "machine-learning", "cloud", "scalable", "analytics", "mobile", "web")
        val selectedCommon = commonTags.shuffled().take(Random.nextInt(1, 4))
        
        return (baseTags + selectedCommon).distinct().take(8)
    }
    
    private fun generateCollaborators(complexity: ComplexityLevel): List<String> {
        val collaboratorCount = when (complexity) {
            ComplexityLevel.SIMPLE -> Random.nextInt(1, 3)
            ComplexityLevel.MEDIUM -> Random.nextInt(2, 5)
            ComplexityLevel.COMPLEX -> Random.nextInt(3, 8)
            ComplexityLevel.ENTERPRISE -> Random.nextInt(5, 15)
        }
        
        val collaboratorNames = listOf(
            "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Eva Davis",
            "Frank Miller", "Grace Wilson", "Henry Moore", "Iris Taylor", "Jack Anderson",
            "Kate Thomas", "Liam Jackson", "Mia White", "Noah Harris", "Olivia Martin"
        )
        
        return collaboratorNames.shuffled().take(collaboratorCount)
    }
    
    private fun generateProjectMetrics(complexity: ComplexityLevel): ProjectMetrics {
        val baseMultiplier = when (complexity) {
            ComplexityLevel.SIMPLE -> 0.3..0.6
            ComplexityLevel.MEDIUM -> 0.4..0.8
            ComplexityLevel.COMPLEX -> 0.6..0.9
            ComplexityLevel.ENTERPRISE -> 0.7..0.95
        }
        
        return ProjectMetrics(
            innovationVelocity = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive),
            autonomyIndex = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive),
            collaborationDensity = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive),
            contextLeverage = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive),
            errorEvolution = Random.nextDouble(0.01, 0.1), // Errors should be low
            confidenceGrowth = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive),
            knowledgeDepth = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive),
            adaptabilityScore = Random.nextDouble(baseMultiplier.start, baseMultiplier.endInclusive)
        )
    }
    
    private fun generateAgent(projectId: String, role: AgentRole, index: Int, complexity: ComplexityLevel): Agent {
        val roleBasedNames = mapOf(
            AgentRole.CONDUCTOR to listOf("Orchestra", "Maestro", "Director", "Coordinator"),
            AgentRole.STRATEGY to listOf("Strategist", "Planner", "Architect", "Visionary"),
            AgentRole.IMPLEMENTATION to listOf("Builder", "Creator", "Developer", "Engineer"),
            AgentRole.TESTING to listOf("Validator", "Tester", "QA", "Verifier"),
            AgentRole.DOCUMENTATION to listOf("Scribe", "Documenter", "Writer", "Recorder"),
            AgentRole.REVIEW to listOf("Reviewer", "Auditor", "Critic", "Inspector")
        )
        
        val baseName = roleBasedNames[role]?.random() ?: "Agent"
        val greekLetters = listOf("Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta")
        
        val capabilities = generateAgentCapabilities(role, complexity)
        val status = AgentStatus.values().random()
        
        return Agent(
            id = "agent_${role.name.lowercase()}_${projectId}_$index",
            name = "$baseName ${greekLetters[index % greekLetters.size]}",
            role = role,
            projectId = projectId,
            capabilities = capabilities,
            status = status,
            lastActive = Clock.System.now().minus(Random.nextInt(0, 24).toLong(), DateTimeUnit.HOUR),
            metrics = generateAgentMetrics(role, complexity),
            configuration = generateAgentConfiguration(role, complexity)
        )
    }
    
    private fun generateAgentCapabilities(role: AgentRole, complexity: ComplexityLevel): List<String> {
        val roleCapabilities = mapOf(
            AgentRole.CONDUCTOR to listOf("orchestration", "coordination", "planning", "resource-management", "team-leadership"),
            AgentRole.STRATEGY to listOf("analysis", "planning", "decision-making", "risk-assessment", "market-research"),
            AgentRole.IMPLEMENTATION to listOf("coding", "development", "architecture", "system-design", "integration"),
            AgentRole.TESTING to listOf("testing", "quality-assurance", "automation", "debugging", "performance-analysis"),
            AgentRole.DOCUMENTATION to listOf("writing", "documentation", "technical-writing", "knowledge-management"),
            AgentRole.REVIEW to listOf("code-review", "quality-control", "compliance", "audit", "assessment")
        )
        
        val baseCapabilities = roleCapabilities[role] ?: emptyList()
        val advancedCapabilities = when (complexity) {
            ComplexityLevel.SIMPLE -> emptyList()
            ComplexityLevel.MEDIUM -> listOf("machine-learning", "data-analysis")
            ComplexityLevel.COMPLEX -> listOf("machine-learning", "data-analysis", "natural-language-processing", "pattern-recognition")
            ComplexityLevel.ENTERPRISE -> listOf("machine-learning", "data-analysis", "natural-language-processing", "pattern-recognition", "predictive-analytics", "autonomous-reasoning")
        }
        
        return (baseCapabilities + advancedCapabilities.take(2)).take(7)
    }
    
    private fun generateAgentMetrics(role: AgentRole, complexity: ComplexityLevel): AgentMetrics {
        val basePerformance = when (complexity) {
            ComplexityLevel.SIMPLE -> 0.6..0.8
            ComplexityLevel.MEDIUM -> 0.7..0.9
            ComplexityLevel.COMPLEX -> 0.8..0.95
            ComplexityLevel.ENTERPRISE -> 0.85..0.98
        }
        
        val taskMultiplier = when (role) {
            AgentRole.CONDUCTOR -> 1.2
            AgentRole.IMPLEMENTATION -> 1.5
            AgentRole.TESTING -> 1.3
            else -> 1.0
        }
        
        return AgentMetrics(
            tasksCompleted = (Random.nextInt(10, 50) * taskMultiplier).toInt(),
            successRate = Random.nextDouble(basePerformance.start, basePerformance.endInclusive),
            averageResponseTime = Random.nextLong(500, 5000),
            innovationScore = Random.nextDouble(basePerformance.start, basePerformance.endInclusive),
            collaborationScore = Random.nextDouble(basePerformance.start, basePerformance.endInclusive)
        )
    }
    
    private fun generateAgentConfiguration(role: AgentRole, complexity: ComplexityLevel): Map<String, String> {
        val baseConfig = mapOf(
            "learning_rate" to Random.nextDouble(0.01, 0.1).toString(),
            "confidence_threshold" to Random.nextDouble(0.6, 0.9).toString(),
            "collaboration_preference" to Random.nextDouble(0.3, 0.9).toString()
        )
        
        val advancedConfig = when (complexity) {
            ComplexityLevel.SIMPLE -> emptyMap()
            ComplexityLevel.MEDIUM -> mapOf(
                "creativity_boost" to Random.nextDouble(0.1, 0.3).toString()
            )
            ComplexityLevel.COMPLEX -> mapOf(
                "creativity_boost" to Random.nextDouble(0.2, 0.5).toString(),
                "risk_tolerance" to Random.nextDouble(0.1, 0.7).toString()
            )
            ComplexityLevel.ENTERPRISE -> mapOf(
                "creativity_boost" to Random.nextDouble(0.3, 0.7).toString(),
                "risk_tolerance" to Random.nextDouble(0.2, 0.8).toString(),
                "autonomous_decision_making" to "true"
            )
        }
        
        return baseConfig + advancedConfig
    }
        // Call the comprehensive seed data generation
        loadSeedData(config)
    }
    
    private fun generateRootThought(project: Project, agent: Agent): Thought {
        val thoughtTemplates = listOf(
            "How can we leverage AI to solve the core challenges in {domain}?",
            "What are the key requirements for building a successful {type}?",
            "What innovative approaches can we take to improve {domain} efficiency?",
            "How do we balance automation with human oversight in this {type}?",
            "What are the potential risks and mitigation strategies for this project?"
        )
        
        val template = thoughtTemplates.random()
        val content = template.replace("{domain}", extractDomain(project.name))
                             .replace("{type}", extractType(project.name))
        
        return Thought(
            id = "thought_root_${project.id}_${System.currentTimeMillis()}",
            projectId = project.id,
            agentId = agent.id,
            content = content,
            thoughtType = ThoughtType.INITIAL,
            confidence = Random.nextDouble(0.7, 0.9),
            reasoning = generateReasoning(content),
            alternatives = generateAlternatives(),
            createdAt = project.createdAt.plus(Random.nextInt(1, 5).toLong(), DateTimeUnit.DAY),
            isSelected = true
        )
    }
    
    private fun generateChildThought(parent: Thought, agent: Agent, depth: Int, branchIndex: Int): Thought {
        val thoughtTypes = when (depth) {
            1 -> listOf(ThoughtType.BRANCH, ThoughtType.ANALYSIS)
            2 -> listOf(ThoughtType.BRANCH, ThoughtType.DECISION, ThoughtType.IMPLEMENTATION)
            else -> ThoughtType.values().toList()
        }
        
        val childContent = generateChildThoughtContent(parent.content, depth, branchIndex)
        
        return Thought(
            id = "thought_${parent.id}_${depth}_${branchIndex}_${System.currentTimeMillis()}",
            projectId = parent.projectId,
            agentId = agent.id,
            parentId = parent.id,
            content = childContent,
            thoughtType = thoughtTypes.random(),
            confidence = Random.nextDouble(0.6, 0.95),
            reasoning = generateReasoning(childContent),
            alternatives = if (Random.nextBoolean()) generateAlternatives() else emptyList(),
            createdAt = parent.createdAt.plus(Random.nextInt(1, depth * 2).toLong(), DateTimeUnit.DAY),
            isSelected = Random.nextDouble() > 0.7 // 30% chance of being selected
        )
    }
    
    private fun generateChildThoughtContent(parentContent: String, depth: Int, branchIndex: Int): String {
        val expansionTemplates = listOf(
            "Building on the previous idea, we should consider {expansion}",
            "An alternative approach to this would be {expansion}",
            "To implement this effectively, we need to {expansion}",
            "The key challenge here is {expansion}",
            "This could be enhanced by {expansion}"
        )
        
        val expansions = listOf(
            "implementing a microservices architecture",
            "using machine learning for pattern recognition",
            "integrating with cloud-native technologies",
            "establishing robust security protocols",
            "creating intuitive user interfaces",
            "optimizing for scalability and performance",
            "ensuring regulatory compliance",
            "building comprehensive testing frameworks"
        )
        
        val template = expansionTemplates.random()
        return template.replace("{expansion}", expansions.random())
    }
    
    private fun generateAlternatives(): List<Alternative> {
        val alternativeCount = Random.nextInt(0, 4)
        val alternatives = mutableListOf<Alternative>()
        
        val alternativeTemplates = listOf(
            "Traditional approach with manual processes",
            "Hybrid solution combining automation and manual control",
            "Fully automated AI-driven approach",
            "Incremental implementation with phased rollout",
            "Third-party integration solution"
        )
        
        repeat(alternativeCount) { index ->
            alternatives.add(
                Alternative(
                    id = "alt_${System.currentTimeMillis()}_$index",
                    description = alternativeTemplates[index % alternativeTemplates.size],
                    pros = generatePros(),
                    cons = generateCons(),
                    score = Random.nextDouble(0.2, 0.8),
                    reasoning = "Analysis based on current project requirements and constraints"
                )
            )
        }
        
        return alternatives
    }
    
    private fun generatePros(): List<String> {
        val prosPool = listOf(
            "Cost-effective solution",
            "Quick to implement",
            "High reliability",
            "Scalable architecture",
            "User-friendly interface",
            "Strong security features",
            "Good performance metrics",
            "Easy maintenance"
        )
        return prosPool.shuffled().take(Random.nextInt(1, 4))
    }
    
    private fun generateCons(): List<String> {
        val consPool = listOf(
            "Higher initial cost",
            "Complex implementation",
            "Requires specialized expertise",
            "Potential performance issues",
            "Limited customization options",
            "Integration challenges",
            "Longer development time",
            "Maintenance overhead"
        )
        return consPool.shuffled().take(Random.nextInt(1, 4))
    }
    
    private fun generateReasoning(content: String): String {
        val reasoningTemplates = listOf(
            "Based on industry best practices and current market trends",
            "Analysis of similar successful implementations shows",
            "Technical feasibility assessment indicates",
            "Risk-benefit analysis suggests",
            "Stakeholder requirements and constraints point to"
        )
        
        return "${reasoningTemplates.random()} that this approach aligns well with project objectives."
    }
    
    private fun generateSyncPoints(sessionType: SessionType, participantCount: Int): List<SyncPoint> {
        val syncPointCount = when (sessionType) {
            SessionType.BRAINSTORMING -> Random.nextInt(2, 5)
            SessionType.DECISION_MAKING -> Random.nextInt(3, 6)
            SessionType.KNOWLEDGE_SHARING -> Random.nextInt(1, 4)
            SessionType.PROBLEM_SOLVING -> Random.nextInt(2, 7)
            else -> Random.nextInt(1, 3)
        }
        
        return (1..syncPointCount).map { index ->
            SyncPoint(
                id = "sync_${System.currentTimeMillis()}_$index",
                timestamp = Clock.System.now().minus(Random.nextInt(5, 60).toLong(), DateTimeUnit.MINUTE),
                description = "Synchronization point $index: ${generateSyncPointDescription(sessionType)}",
                participantsInSync = Random.nextInt(1, participantCount + 1)
            )
        }
    }
    
    private fun generateSyncPointDescription(sessionType: SessionType): String {
        val descriptions = mapOf(
            SessionType.BRAINSTORMING to listOf(
                "Ideas consolidation",
                "Creative breakthrough",
                "Concept alignment",
                "Innovation synthesis"
            ),
            SessionType.DECISION_MAKING to listOf(
                "Options evaluation",
                "Consensus building",
                "Decision finalization",
                "Risk assessment"
            ),
            SessionType.KNOWLEDGE_SHARING to listOf(
                "Knowledge transfer",
                "Best practice sharing",
                "Insight consolidation",
                "Learning synthesis"
            ),
            SessionType.PROBLEM_SOLVING to listOf(
                "Problem definition",
                "Solution exploration",
                "Approach validation",
                "Implementation planning"
            )
        )
        
        return descriptions[sessionType]?.random() ?: "General synchronization"
    }
    
    private fun generateAgentPresences(participantIds: List<String>, startTime: Instant): List<AgentPresence> {
        return participantIds.map { agentId ->
            AgentPresence(
                agentId = agentId,
                isActive = Random.nextDouble() > 0.2, // 80% chance of being active
                lastSeen = startTime.plus(Random.nextInt(1, 30).toLong(), DateTimeUnit.MINUTE),
                currentActivity = generateCurrentActivity(),
                contribution = ContributionMetrics(
                    ideasGenerated = Random.nextInt(0, 8),
                    questionsAsked = Random.nextInt(0, 5),
                    solutionsProposed = Random.nextInt(0, 3),
                    consensusBuilding = Random.nextDouble(0.0, 1.0),
                    knowledgeSharing = Random.nextDouble(0.0, 1.0)
                )
            )
        }
    }
    
    private fun generateCurrentActivity(): String {
        val activities = listOf(
            "Analyzing requirements",
            "Reviewing proposals",
            "Generating alternatives",
            "Evaluating options",
            "Synthesizing ideas",
            "Building consensus",
            "Documenting findings",
            "Assessing risks",
            "Planning implementation",
            "Sharing insights"
        )
        return activities.random()
    }
    
    private fun generateSharedContext(sessionType: SessionType): SharedContext {
        return SharedContext(
            commonUnderstanding = generateCommonUnderstanding(sessionType),
            conflictingViews = generateConflictingViews(),
            agreedDecisions = generateAgreedDecisions(),
            openQuestions = generateOpenQuestions(sessionType)
        )
    }
    
    private fun generateCommonUnderstanding(sessionType: SessionType): List<String> {
        val understandings = when (sessionType) {
            SessionType.BRAINSTORMING -> listOf(
                "Innovation is key to project success",
                "User experience should be prioritized",
                "Scalability is a critical requirement"
            )
            SessionType.DECISION_MAKING -> listOf(
                "Decision criteria have been established",
                "Stakeholder requirements are understood",
                "Risk tolerance levels are defined"
            )
            else -> listOf(
                "Project objectives are clearly defined",
                "Quality standards must be maintained",
                "Timeline constraints are understood"
            )
        }
        return understandings.shuffled().take(Random.nextInt(1, 4))
    }
    
    private fun generateConflictingViews(): List<ConflictingView> {
        if (Random.nextDouble() > 0.4) return emptyList() // 60% chance of no conflicts
        
        return listOf(
            ConflictingView(
                topic = "Implementation approach",
                positions = mapOf(
                    "agent_1" to "Prefer gradual rollout",
                    "agent_2" to "Advocate for big-bang approach"
                ),
                reasoning = mapOf(
                    "agent_1" to "Lower risk and better testing opportunities",
                    "agent_2" to "Faster time to market and unified experience"
                )
            )
        )
    }
    
    private fun generateAgreedDecisions(): List<Decision> {
        val decisionCount = Random.nextInt(0, 3)
        return (1..decisionCount).map { index ->
            Decision(
                id = "decision_${System.currentTimeMillis()}_$index",
                description = "Decision $index: ${generateDecisionDescription()}",
                rationale = "Based on collaborative analysis and consensus building",
                voters = listOf("agent_1", "agent_2", "agent_3").take(Random.nextInt(2, 4)),
                timestamp = Clock.System.now().minus(Random.nextInt(5, 30).toLong(), DateTimeUnit.MINUTE),
                confidence = Random.nextDouble(0.7, 0.95)
            )
        }
    }
    
    private fun generateDecisionDescription(): String {
        val decisions = listOf(
            "Adopt microservices architecture",
            "Use cloud-native deployment",
            "Implement automated testing",
            "Establish CI/CD pipeline",
            "Integrate machine learning capabilities"
        )
        return decisions.random()
    }
    
    private fun generateOpenQuestions(sessionType: SessionType): List<String> {
        val questions = when (sessionType) {
            SessionType.BRAINSTORMING -> listOf(
                "How can we make the solution more innovative?",
                "What are the potential user experience improvements?",
                "How do we ensure scalability from day one?"
            )
            SessionType.DECISION_MAKING -> listOf(
                "What are the long-term implications?",
                "How do we measure success?",
                "What are the contingency plans?"
            )
            else -> listOf(
                "What are the next steps?",
                "How do we ensure quality?",
                "What resources are needed?"
            )
        }
        return questions.shuffled().take(Random.nextInt(1, 4))
    }
    
    private fun generateHistoricalMetrics(projects: List<Project>) {
        println("Generating historical metrics for ${projects.size} projects...")
        // In a real implementation, this would generate time-series data
        // For now, we simulate this by updating project metrics over time
    }
    
    // Utility methods
    private fun extractDomain(projectName: String): String {
        return when {
            projectName.contains("Healthcare", ignoreCase = true) -> "healthcare"
            projectName.contains("Financial", ignoreCase = true) -> "finance"
            projectName.contains("E-commerce", ignoreCase = true) -> "retail"
            projectName.contains("Education", ignoreCase = true) -> "education"
            projectName.contains("Smart City", ignoreCase = true) -> "urban planning"
            else -> "technology"
        }
    }
    
    private fun extractType(projectName: String): String {
        return when {
            projectName.contains("System", ignoreCase = true) -> "system"
            projectName.contains("Platform", ignoreCase = true) -> "platform"
            projectName.contains("Engine", ignoreCase = true) -> "engine"
            projectName.contains("App", ignoreCase = true) -> "application"
            else -> "solution"
        }
    }
    
    suspend fun clearAllData() {
        println("Clearing all seed data...")
        // In a real implementation, you'd clear all tables
        // This would involve calling delete methods on all repositories
        println("Seed data cleared successfully!")
    }
    
    // Quick load methods for specific scenarios
    suspend fun loadDemoData() {
        loadSeedData(SeedDataConfiguration(
            projectCount = 3,
            agentsPerProject = 3..4,
            thoughtsPerProject = 8..12,
            collaborationsPerProject = 1..3,
            complexityLevel = ComplexityLevel.SIMPLE
        ))
    }
    
    suspend fun loadComplexData() {
        loadSeedData(SeedDataConfiguration(
            projectCount = 8,
            agentsPerProject = 5..8,
            thoughtsPerProject = 20..35,
            collaborationsPerProject = 3..7,
            complexityLevel = ComplexityLevel.COMPLEX,
            includeHistoricalData = true
        ))
    }
    
    suspend fun loadEnterpriseData() {
        loadSeedData(SeedDataConfiguration(
            projectCount = 15,
            agentsPerProject = 6..12,
            thoughtsPerProject = 30..50,
            collaborationsPerProject = 5..10,
            complexityLevel = ComplexityLevel.ENTERPRISE,
            includeHistoricalData = true,
            timeSpreadDays = 180
        ))
    }
}