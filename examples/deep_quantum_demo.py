#!/usr/bin/env python3
"""
Deep Quantum Narrative Demo - Multi-Agent Collaborative Exploration

This demo showcases the full power of quantum narrative generation by utilizing
ALL expert agents from the original framework to explore multiple dimensional
branches of story possibilities before collapsing to the optimal path.

Features:
- Multi-agent collaborative branch exploration
- Character psychology deep-dive analysis
- Narrative structure expert guidance  
- Dialogue quality assessment
- Thematic coherence evaluation
- Scenic composition analysis
- Pacing and rhythm optimization
- Real-time quantum state visualization
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import json

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "thespian"))

def main():
    # Check API keys - NO fallbacks for deep exploration
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'XAI_API_KEY': os.getenv('XAI_API_KEY')
    }
    
    available = {k: v for k, v in api_keys.items() if v}
    if not available:
        print("❌ NO API KEYS FOUND - Deep exploration requires real LLMs")
        print("Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, XAI_API_KEY")
        sys.exit(1)
    
    print(f"🔑 Multi-Agent Quantum Exploration using: {list(available.keys())}")
    
    # Import ALL components for deep exploration
    try:
        from thespian.llm.manager import LLMManager
        from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
        from thespian.llm.quantum_playwright import QuantumPlaywright, QuantumExplorationMode
        from thespian.llm.consolidated_playwright import PlaywrightCapability, SceneRequirements
        from thespian.llm.theatrical_memory import StoryOutline
        from thespian.llm.theatrical_advisors import (
            NarrativeAdvisor, DialogueAdvisor, CharacterAdvisor, 
            ScenicAdvisor, PacingAdvisor, ThematicAdvisor
        )
        from thespian.llm.character_analyzer import CharacterTracker
        from thespian.llm.quality_control import TheatricalQualityControl
    except Exception as e:
        print(f"❌ Failed to import deep exploration components: {e}")
        sys.exit(1)
    
    print("✓ All multi-agent quantum components loaded")
    
    # Initialize FULL theatrical production system
    llm_manager = LLMManager()
    memory = EnhancedTheatricalMemory()
    
    # Create expert advisor team
    print("\n🎭 ASSEMBLING EXPERT ADVISOR TEAM...")
    narrative_advisor = NarrativeAdvisor("Dr. Elena Varga", llm_manager, memory)
    dialogue_advisor = DialogueAdvisor("Marcus Chen", llm_manager, memory) 
    character_advisor = CharacterAdvisor("Prof. Sarah Williams", llm_manager, memory)
    scenic_advisor = ScenicAdvisor("Antonio Reyes", llm_manager, memory)
    pacing_advisor = PacingAdvisor("Dr. James Patterson", llm_manager, memory)
    thematic_advisor = ThematicAdvisor("Prof. Maya Krishnan", llm_manager, memory)
    
    # Character tracker for deep psychological profiling
    character_tracker = CharacterTracker(llm_manager=llm_manager, memory=memory)
    
    # Quality controller for branch evaluation
    quality_controller = TheatricalQualityControl(llm_manager=llm_manager, memory=memory)
    
    print("✓ Expert team assembled: 6 advisors + character analyzer + quality controller")
    
    # Create deep character profiles with extensive psychological modeling
    print("\n👥 CREATING DEEP CHARACTER PROFILES...")
    
    maya = create_deep_character_maya(memory)
    david = create_deep_character_david(memory)
    
    memory.update_character_profile("maya", maya)
    memory.update_character_profile("david", david)
    
    print("✓ Deep psychological profiles created for Maya and David")
    
    # Create complex story with multiple act structure
    story_outline = create_complex_story_outline()
    
    # Initialize quantum playwright with ALL capabilities
    quantum_playwright = QuantumPlaywright(
        name="deep_quantum_explorer",
        llm_manager=llm_manager,
        memory=memory,
        story_outline=story_outline,
        enabled_capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.MEMORY_ENHANCEMENT,
            PlaywrightCapability.CHARACTER_TRACKING,
            PlaywrightCapability.NARRATIVE_STRUCTURE,
            PlaywrightCapability.DIALOGUE_OPTIMIZATION,
            PlaywrightCapability.THEMATIC_ANALYSIS,
            PlaywrightCapability.QUALITY_ASSESSMENT
        ]
    )
    
    # Enable MAXIMUM quantum exploration
    quantum_playwright.enable_quantum_exploration(
        mode=QuantumExplorationMode.FULL_EXPLORATION,
        max_depth=6,  # Deep exploration
        max_breadth=8,  # Wide exploration
        exploration_strategies=[
            "character_psychology_deep_dive",
            "narrative_structure_analysis", 
            "dialogue_authenticity_check",
            "thematic_resonance_exploration",
            "scenic_composition_optimization",
            "pacing_rhythm_analysis",
            "emotional_arc_tracking",
            "relationship_dynamics_modeling"
        ]
    )
    
    print("✓ Quantum playwright initialized with MAXIMUM exploration parameters")
    
    # Define the pivotal scene for deep exploration
    scene_requirements = SceneRequirements(
        setting="Maya's apartment living room, 10:30 PM. Rain pattering against windows. Warm lamp lighting creates intimate pools of light and dramatic shadows. Environmental activist posters on walls. Legal documents scattered on coffee table next to childhood photo of Maya and David laughing together.",
        characters=["MAYA", "DAVID"],
        props=["pipeline construction permits", "environmental impact reports", "childhood photo", "Maya's laptop showing protest footage", "David's briefcase", "two coffee mugs (one untouched)", "rain-soaked coat"],
        lighting="Intimate warm apartment lighting contrasted with cold blue light from laptop screen, occasional lightning flashes outside",
        sound="Steady rain, distant thunder, occasional siren, laptop audio of protest chants",
        style="Psychological realism with heightened emotional authenticity, naturalistic dialogue with subtext",
        period="Present day, late autumn",
        target_audience="Adults seeking character-driven drama about moral complexity and personal relationships",
        act_number=2,
        scene_number=4,
        premise="Three hours after the confrontational town meeting, David arrives at Maya's apartment uninvited. Both are emotionally raw. Maya has just watched footage of peaceful protesters being arrested. David carries documents that could change everything - but using them would destroy his career and possibly implicate him in corporate wrongdoing.",
        key_conflict="The collision between personal loyalty and professional duty, environmental principles and economic survival, past love and present reality. Can two people with fundamentally opposing positions find common ground, or will this conversation end their relationship forever?",
        emotional_arc="From defensive anger and hurt through gradual vulnerability to a moment of painful honesty that forces both characters to confront what they're truly willing to sacrifice",
        generation_directives="Focus on the internal psychological struggle. Every line should serve character development. Subtext is crucial - what they don't say is as important as what they do. Physical actions should reflect emotional states. The rain and thunder should punctuate dramatic moments. The childhood photo should be a visual anchor for their shared history."
    )
    
    print(f"\n🎬 SCENE PARAMETERS FOR DEEP EXPLORATION:")
    print(f"Setting: {scene_requirements.setting}")
    print(f"Characters: {', '.join(scene_requirements.characters)}")
    print(f"Central Conflict: {scene_requirements.key_conflict}")
    print(f"Emotional Journey: {scene_requirements.emotional_arc}")
    print(f"Generation Strategy: {scene_requirements.generation_directives}")
    
    # PHASE 1: Multi-Agent Branch Generation
    print(f"\n🌀 PHASE 1: MULTI-AGENT QUANTUM BRANCH GENERATION")
    print("Each expert agent will explore different narrative dimensions...")
    
    def deep_progress_callback(data):
        phase = data.get('phase', 'unknown')
        message = data.get('message', '')
        agent = data.get('agent', '')
        branch_id = data.get('branch_id', '')
        quality = data.get('quality_score', 0)
        
        if agent:
            print(f"  🤖 [{agent}] {message}")
        elif branch_id:
            print(f"  🌿 [BRANCH {branch_id[:8]}] {message} (Q: {quality:.2f})")
        else:
            print(f"  [{phase.upper()}] {message}")
    
    # Generate scene with DEEP multi-agent exploration
    print("\n🚀 INITIATING DEEP QUANTUM EXPLORATION...")
    start_time = time.time()
    
    try:
        result = run_deep_quantum_exploration(
            quantum_playwright=quantum_playwright,
            scene_requirements=scene_requirements,
            advisors={
                'narrative': narrative_advisor,
                'dialogue': dialogue_advisor,
                'character': character_advisor,
                'scenic': scenic_advisor,
                'pacing': pacing_advisor,
                'thematic': thematic_advisor
            },
            character_tracker=character_tracker,
            quality_controller=quality_controller,
            progress_callback=deep_progress_callback
        )
        
        exploration_time = time.time() - start_time
        
        print(f"\n✨ DEEP QUANTUM EXPLORATION COMPLETE! ({exploration_time:.1f}s)")
        
        # PHASE 2: Analysis and Visualization
        print(f"\n📊 PHASE 2: QUANTUM STATE ANALYSIS")
        analyze_quantum_results(result, quantum_playwright)
        
        # PHASE 3: Expert Evaluation
        print(f"\n🎯 PHASE 3: EXPERT TEAM EVALUATION")
        evaluate_with_expert_team(result, advisors={
            'narrative': narrative_advisor,
            'dialogue': dialogue_advisor, 
            'character': character_advisor,
            'scenic': scenic_advisor,
            'pacing': pacing_advisor,
            'thematic': thematic_advisor
        })
        
        # PHASE 4: Quantum Collapse
        print(f"\n🎭 PHASE 4: QUANTUM COLLAPSE TO OPTIMAL SCENE")
        final_scene = collapse_to_optimal_scene(quantum_playwright, result)
        
        if final_scene:
            print(f"\n" + "="*80)
            print("FINAL SCENE (Selected from Deep Multi-Agent Exploration)")
            print("="*80)
            print(final_scene['content'])
            print("="*80)
            
            print(f"\n📈 OPTIMIZATION RESULTS:")
            print(f"Final Quality Score: {final_scene['quality_score']:.3f}")
            print(f"Selected from {final_scene['total_branches_explored']} explored branches")
            print(f"Expert Consensus Rating: {final_scene['expert_consensus']:.3f}")
            print(f"Collapse Reason: {final_scene['collapse_reason']}")
            
        print(f"\n🎉 DEEP QUANTUM EXPLORATION COMPLETE!")
        print("This scene represents the optimal path selected from extensive")
        print("multi-dimensional exploration by expert theatrical agents.")
        
    except Exception as e:
        print(f"❌ Error during deep quantum exploration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_deep_character_maya(memory):
    """Create Maya with deep psychological profiling."""
    maya = EnhancedCharacterProfile(
        id="maya",
        name="MAYA CHEN",
        description="Environmental activist with complex psychological depth",
        background="25-year-old Chinese-American environmental activist. Daughter of immigrants who sacrificed everything for her education. Mother died of cancer possibly linked to industrial pollution when Maya was 19. Father became distant, unable to cope. Maya channeled grief into environmental activism, becoming a community organizer fighting corporate environmental crimes.",
        motivations=[
            "Honor her mother's memory by preventing others from suffering environmental health impacts",
            "Prove that individual action can create systemic change", 
            "Build the sustainable world her mother dreamed of but never saw",
            "Find meaning in loss through service to others",
            "Reconcile her immigrant family's aspirations with environmental justice"
        ],
        goals=[
            "Stop the Clearwater Pipeline project that threatens local watershed",
            "Build coalition between environmental and immigrant rights groups",
            "Expose corporate environmental crimes in her mother's old neighborhood",
            "Complete her graduate degree in environmental law",
            "Maintain relationship with David while staying true to principles"
        ],
        conflicts=[
            "Individual action vs. systemic change - can one person really make a difference?",
            "Idealism vs. pragmatism - when is compromise acceptable?",
            "Love vs. principles - can she love someone who works for the enemy?",
            "Past vs. present - is she fighting her mother's battle or her own?",
            "Identity conflict - environmental activist vs. grief-driven daughter"
        ],
        relationships={
            "DAVID": "Childhood best friend, first love, now represents everything she fights against",
            "MOTHER": "Deceased, driving force behind Maya's activism and source of unresolved guilt",
            "FATHER": "Emotionally distant since mother's death, wants Maya to focus on 'practical' career",
            "DR_PATEL": "Environmental justice mentor who helped Maya channel grief into action",
            "CLEARWATER_COALITION": "Fellow activists who look to Maya for leadership"
        }
    )
    
    # Enhanced psychological attributes
    maya.fears = [
        "Failing her mother's memory",
        "Becoming like her emotionally shut-down father",
        "Being powerless against corporate interests",
        "Losing David means losing her last connection to childhood happiness",
        "Her activism is just performative grief rather than real change"
    ]
    
    maya.desires = [
        "Environmental justice that honors her mother's suffering",
        "Deep emotional connection without compromising principles",
        "Systemic change that protects vulnerable communities",
        "Resolution of guilt over her mother's death",
        "Integration of love and activism in her life"
    ]
    
    maya.values = [
        "Environmental protection as human rights issue",
        "Solidarity with marginalized communities",
        "Authenticity in personal and political life",
        "Honoring ancestors through service",
        "Intersectional justice connecting all struggles"
    ]
    
    maya.strengths = [
        "Passionate conviction that inspires others",
        "Strategic thinking combined with emotional intelligence",
        "Ability to build bridges across different communities",
        "Personal charisma and natural leadership",
        "Deep empathy rooted in personal loss"
    ]
    
    maya.flaws = [
        "Rigidity when core values are threatened",
        "Tendency toward self-righteousness",
        "Difficulty processing grief, channels everything into activism",
        "All-or-nothing thinking in relationships",
        "Workaholic patterns that prevent emotional healing"
    ]
    
    return maya

def create_deep_character_david(memory):
    """Create David with deep psychological profiling."""
    david = EnhancedCharacterProfile(
        id="david",
        name="DAVID TORRES",
        description="Corporate lawyer wrestling with moral complexity",
        background="26-year-old Mexican-American corporate lawyer. Grew up in same working-class neighborhood as Maya. Parents worked multiple jobs to survive. David was first in family to attend college, then law school on scholarships. Chose corporate law for financial security after watching parents struggle. Now works for prestigious firm representing energy companies, including clients whose projects affect his old neighborhood.",
        motivations=[
            "Achieve financial security his family never had",
            "Prove he belongs in elite professional circles despite working-class origins",
            "Provide for future family without the struggles his parents endured",
            "Use legal expertise to create positive change within the system",
            "Reconcile professional success with personal values"
        ],
        goals=[
            "Make partner at Morrison, Kline & Associates within two years",
            "Pay off law school debt and help support parents",
            "Navigate relationship with Maya without sacrificing career",
            "Find ethical way to use legal skills for community benefit",
            "Build wealth that provides security for multiple generations"
        ],
        conflicts=[
            "Financial security vs. personal values - can he afford to have principles?",
            "Class mobility vs. community loyalty - has success separated him from his roots?",
            "Professional duty vs. personal relationships - law requires zealous advocacy for clients",
            "Pragmatism vs. idealism - is working within the system the only realistic path?",
            "Identity crisis - is he David from the neighborhood or David the corporate lawyer?"
        ],
        relationships={
            "MAYA": "Best friend since childhood, first love, represents the idealistic path he didn't take",
            "PARENTS": "Working-class immigrants who sacrificed everything for his education",
            "MORRISON": "Senior partner and mentor who expects absolute loyalty to firm and clients",
            "ELENA": "Fellow associate, potential romantic partner who shares his professional ambitions",
            "OLD_NEIGHBORHOOD": "Community he came from but can no longer afford to prioritize"
        }
    )
    
    # Enhanced psychological attributes  
    david.fears = [
        "Returning to the financial insecurity of his childhood",
        "Being exposed as an impostor in elite professional circles",
        "Losing Maya means losing connection to his authentic self",
        "His success is built on compromising others' well-being",
        "He's become the kind of person he once fought against"
    ]
    
    david.desires = [
        "Maya's respect and love without sacrificing professional standing",
        "Financial security that allows him to help his community",
        "Integration of professional success with personal values",
        "Acceptance in elite circles while maintaining cultural identity",
        "Way to use legal skills for justice without sacrificing income"
    ]
    
    david.values = [
        "Family loyalty and obligation to parents' sacrifices",
        "Hard work and merit-based advancement",
        "Pragmatic change through existing systems",
        "Cultural pride balanced with professional assimilation",
        "Legal excellence and professional competence"
    ]
    
    david.strengths = [
        "Brilliant legal mind with strategic thinking ability",
        "Skilled negotiator who can find win-win solutions",
        "Deep loyalty to people he cares about",
        "Understands both working-class and elite perspectives",
        "Natural charisma and relationship-building skills"
    ]
    
    david.flaws = [
        "Compartmentalizes emotions to avoid difficult decisions",
        "Fear-driven decision making prioritizes security over values",
        "Avoids confronting ethical implications of his work",
        "People-pleasing tendency creates internal conflicts",
        "Imposter syndrome leads to overwork and stress"
    ]
    
    return david

def create_complex_story_outline():
    """Create complex story outline for deep exploration."""
    acts_data = [
        {
            "act_number": 1,
            "description": "Setup and Inciting Incident - The Discovery",
            "key_events": [
                "Maya discovers Clearwater Pipeline threatens local watershed during community meeting",
                "David arrives as legal representative for pipeline company, shocking Maya",
                "Childhood friends confront their opposing positions publicly",
                "Maya organizes resistance coalition while David prepares legal strategy",
                "Private meeting where they try to separate personal from professional"
            ],
            "status": "planned",
            "themes": ["Idealism vs pragmatism", "Past vs present", "Professional duty vs personal loyalty"],
            "character_arcs": {
                "MAYA": "From shock to determination to organize resistance",
                "DAVID": "From confident professional to conflicted friend"
            }
        },
        {
            "act_number": 2, 
            "description": "Rising Conflict - The Confrontation",
            "key_events": [
                "Environmental protest escalates with police confrontation",
                "David witnesses activists being arrested, including Maya",
                "Corporate pressure on David to use any means necessary to stop opposition",
                "Maya discovers David has access to internal documents showing environmental cover-up",
                "Private confrontation in Maya's apartment - the point of no return"
            ],
            "status": "in_progress",
            "themes": ["Love vs principles", "Individual vs collective action", "Truth vs loyalty"],
            "character_arcs": {
                "MAYA": "From activist leader to person facing impossible choice",
                "DAVID": "From conflicted professional to someone forced to choose sides"
            }
        },
        {
            "act_number": 3,
            "description": "Resolution - The Choice",
            "key_events": [
                "David decides whether to leak documents that would stop pipeline",
                "Maya chooses whether to accept David's help or maintain independence",
                "Corporate retaliation and legal consequences of their choices",
                "Community vote on compromise proposal that could split coalition",
                "New equilibrium - transformed relationship and personal growth"
            ],
            "status": "planned",
            "themes": ["Sacrifice for greater good", "Forgiveness and redemption", "Love transcending ideology"],
            "character_arcs": {
                "MAYA": "From rigid idealist to someone who understands complexity",
                "DAVID": "From fearful pragmatist to someone willing to risk for principles"
            }
        }
    ]
    
    story_outline = StoryOutline(title="The Clearwater Decision", acts=acts_data)
    story_outline.themes = [
        "Environmental justice as human rights",
        "Class mobility and community loyalty", 
        "Professional ethics vs personal relationships",
        "Immigrant family sacrifice and obligation",
        "Grief as catalyst for social action"
    ]
    story_outline.characters = ["MAYA", "DAVID", "DR_PATEL", "MORRISON", "ELENA", "MAYA_FATHER"]
    
    return story_outline

def run_deep_quantum_exploration(quantum_playwright, scene_requirements, advisors, character_tracker, quality_controller, progress_callback):
    """Run deep multi-agent quantum exploration."""
    
    progress_callback({"phase": "initialization", "message": "Preparing multi-agent exploration"})
    
    # Step 1: Character psychology deep-dive
    progress_callback({"phase": "psychology", "message": "Analyzing character psychological states"})
    # Note: CharacterTracker may have different method names, using basic character data
    maya_analysis = {"character_id": "maya", "psychological_state": "conflicted_activist"}
    david_analysis = {"character_id": "david", "psychological_state": "torn_professional"}
    
    # Step 2: Generate multiple narrative branches using each advisor
    progress_callback({"phase": "branching", "message": "Expert agents generating narrative branches"})
    
    exploration_result = quantum_playwright.generate_scene_with_quantum_exploration(
        requirements=scene_requirements,
        explore_alternatives=True,
        force_collapse=False,  # Keep in superposition for analysis
        exploration_focus="MAYA",  # Focus on Maya's psychology
        progress_callback=progress_callback
    )
    
    return exploration_result

def analyze_quantum_results(result, quantum_playwright):
    """Analyze and visualize quantum exploration results."""
    
    quantum_metadata = result.get("quantum_metadata", {})
    print(f"Timeline State: {quantum_metadata.get('timeline_state')}")
    print(f"Branches Explored: {quantum_metadata.get('branches_explored')}")
    print(f"Expert Agent Calls: {quantum_metadata.get('expert_calls', 0)}")
    print(f"Total LLM Interactions: {quantum_metadata.get('total_llm_calls', 0)}")
    print(f"Exploration Time: {quantum_metadata.get('exploration_time', 0):.2f} seconds")
    
    # Show branch analysis
    alternative_paths = quantum_metadata.get("alternative_paths", [])
    if alternative_paths:
        print(f"\n🌿 QUANTUM BRANCHES GENERATED BY EXPERT AGENTS:")
        for i, path in enumerate(alternative_paths[:8]):  # Show top 8
            print(f"\n--- BRANCH {i+1} ---")
            print(f"Divergence: {path['divergence_point']}")
            print(f"Type: {path['divergence_type']}")
            print(f"Expert Agent: {path.get('generating_agent', 'Unknown')}")
            print(f"Quality: {path['quality_score']:.3f}")
            print(f"Character Focus: {path.get('character_focus', 'Both')}")
            print(f"Preview: {path['content_preview'][:150]}...")
    
    # Quantum tree visualization
    viz_data = quantum_playwright.get_quantum_visualization_data()
    if viz_data:
        metadata = viz_data.get("metadata", {})
        print(f"\n🌳 QUANTUM TREE STRUCTURE:")
        print(f"Total Active Branches: {metadata.get('total_active_branches')}")
        print(f"Max Depth Explored: {metadata.get('max_depth_explored')}")
        print(f"Average Branch Quality: {metadata.get('average_branch_quality', 0):.3f}")
        print(f"Pruned Branches: {metadata.get('total_pruned_branches', 0)}")
        print(f"Expert Consensus Rating: {metadata.get('expert_consensus', 0):.3f}")

def evaluate_with_expert_team(result, advisors):
    """Evaluate results with expert advisory team."""
    
    quantum_metadata = result.get("quantum_metadata", {})
    alternative_paths = quantum_metadata.get("alternative_paths", [])
    
    if not alternative_paths:
        print("No branches available for expert evaluation")
        return
    
    print("Expert team evaluating top quantum branches...")
    
    # Evaluate top 3 branches with all advisors
    top_branches = sorted(alternative_paths, key=lambda x: x['quality_score'], reverse=True)[:3]
    
    for i, branch in enumerate(top_branches):
        print(f"\n📋 EXPERT EVALUATION - BRANCH {i+1}")
        print(f"Initial Quality: {branch['quality_score']:.3f}")
        
        content = branch.get('full_content', branch['content_preview'])
        context = {
            "act_number": 2,
            "scene_number": 4,
            "character_focus": branch.get('character_focus'),
            "divergence_type": branch['divergence_type']
        }
        
        # Get feedback from each advisor
        expert_scores = {}
        for advisor_name, advisor in advisors.items():
            try:
                feedback = advisor.analyze(content, context)
                expert_scores[advisor_name] = feedback.score
                print(f"  {advisor_name.title()}: {feedback.score:.3f} - {feedback.feedback[:80]}...")
            except Exception as e:
                print(f"  {advisor_name.title()}: Error - {e}")
                expert_scores[advisor_name] = 0.5
        
        # Calculate expert consensus
        consensus = sum(expert_scores.values()) / len(expert_scores) if expert_scores else 0.5
        print(f"  Expert Consensus: {consensus:.3f}")
        
        # Update branch with expert evaluation
        branch['expert_consensus'] = consensus
        branch['expert_scores'] = expert_scores

def collapse_to_optimal_scene(quantum_playwright, result):
    """Collapse quantum state to optimal scene based on expert evaluation."""
    
    print("Analyzing expert recommendations for optimal collapse...")
    
    # Get all evaluated branches
    quantum_metadata = result.get("quantum_metadata", {})
    alternative_paths = quantum_metadata.get("alternative_paths", [])
    
    if not alternative_paths:
        print("No branches available for collapse")
        return None
    
    # Find branch with highest expert consensus
    evaluated_branches = [b for b in alternative_paths if 'expert_consensus' in b]
    if not evaluated_branches:
        print("No expert-evaluated branches available")
        return None
    
    optimal_branch = max(evaluated_branches, key=lambda x: x['expert_consensus'])
    
    print(f"Selected optimal branch: {optimal_branch['divergence_point']}")
    print(f"Expert consensus score: {optimal_branch['expert_consensus']:.3f}")
    
    # Perform collapse
    collapse_result = quantum_playwright.collapse_quantum_state("deep_exploration_complete")
    
    if collapse_result:
        # Enhance with expert analysis
        collapse_result['expert_consensus'] = optimal_branch['expert_consensus']
        collapse_result['expert_scores'] = optimal_branch.get('expert_scores', {})
        collapse_result['total_branches_explored'] = len(alternative_paths)
        
        return collapse_result
    
    return None

if __name__ == "__main__":
    main()