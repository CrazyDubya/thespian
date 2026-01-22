#!/usr/bin/env python3
"""
Aggressive Quantum Narrative Demo - Forces Maximum LLM Usage

This demo modifies the quantum exploration to be extremely aggressive:
- Forces deep iteration through all depth levels
- Generates branches for EVERY character at EVERY level
- Uses multiple exploration cycles
- Calls LLMs extensively for branch generation
- Bypasses early termination conditions
"""

import os
import sys
from pathlib import Path
import time

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "thespian"))

def main():
    # Check API keys
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'XAI_API_KEY': os.getenv('XAI_API_KEY')
    }
    
    available = {k: v for k, v in api_keys.items() if v}
    if not available:
        print("❌ NO API KEYS FOUND")
        sys.exit(1)
    
    print(f"🔑 Using API keys: {list(available.keys())}")
    
    # Import components
    try:
        from thespian.llm.manager import LLMManager
        from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
        from thespian.llm.quantum_playwright import QuantumPlaywright, QuantumExplorationMode
        from thespian.llm.consolidated_playwright import PlaywrightCapability, SceneRequirements
        from thespian.llm.theatrical_memory import StoryOutline
        from thespian.llm.quantum_narrative import QuantumBranchGenerator
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    
    print("✓ All components imported")
    
    # Initialize systems
    llm_manager = LLMManager()
    memory = EnhancedTheatricalMemory()
    
    # Create rich characters
    maya = create_complex_maya()
    david = create_complex_david()
    
    memory.update_character_profile("maya", maya)
    memory.update_character_profile("david", david)
    
    # Create story
    story_outline = create_simple_story()
    
    # Initialize quantum playwright
    quantum_playwright = QuantumPlaywright(
        name="aggressive_quantum",
        llm_manager=llm_manager,
        memory=memory,
        story_outline=story_outline,
        enabled_capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.MEMORY_ENHANCEMENT,
            PlaywrightCapability.CHARACTER_TRACKING,
            PlaywrightCapability.NARRATIVE_STRUCTURE
        ]
    )
    
    # Enable MAXIMUM quantum exploration
    quantum_playwright.enable_quantum_exploration(
        mode=QuantumExplorationMode.FULL_EXPLORATION,
        max_depth=8,    # Deep enough to see multiple levels
        max_breadth=12  # Wide enough for thorough exploration
    )
    
    print("✓ Aggressive quantum playwright initialized")
    print(f"Max depth: {quantum_playwright.max_exploration_depth}")
    print(f"Max breadth: {quantum_playwright.exploration_breadth}")
    
    # Create demanding scene requirements
    scene_requirements = SceneRequirements(
        setting="Maya's apartment, evening confrontation",
        characters=["MAYA", "DAVID"],
        props=["legal documents", "childhood photo"],
        lighting="Dramatic lighting",
        style="Psychological realism",
        period="Present day",
        act_number=2,
        scene_number=3,
        premise="Maya confronts David about his corporate work representing the pipeline company",
        key_conflict="Personal loyalty vs environmental principles",
        emotional_arc="Anger through vulnerability to painful choice"
    )
    
    print(f"\n🚀 STARTING AGGRESSIVE QUANTUM EXPLORATION")
    print("Forcing maximum LLM usage...")
    
    llm_call_count = 0
    branch_count = 0
    
    def aggressive_progress_callback(data):
        nonlocal llm_call_count, branch_count
        phase = data.get('phase', 'unknown')
        message = data.get('message', '')
        
        if 'llm_call' in message.lower() or 'generating' in message.lower():
            llm_call_count += 1
        if 'branch' in message.lower():
            branch_count += 1
            
        print(f"  [{phase.upper()}] {message}")
        print(f"    LLM calls: {llm_call_count}, Branches: {branch_count}")
    
    start_time = time.time()
    
    # Run multiple exploration cycles to force more LLM usage
    print("\n🌀 CYCLE 1: Initial quantum exploration")
    result1 = quantum_playwright.generate_scene_with_quantum_exploration(
        requirements=scene_requirements,
        explore_alternatives=True,
        force_collapse=False,
        exploration_focus="MAYA",
        progress_callback=aggressive_progress_callback
    )
    
    # Force additional exploration rounds
    print(f"\n🌀 CYCLE 2: Extended exploration on different character focus")
    result2 = quantum_playwright.generate_scene_with_quantum_exploration(
        requirements=scene_requirements,
        explore_alternatives=True,
        force_collapse=False,
        exploration_focus="DAVID",
        progress_callback=aggressive_progress_callback
    )
    
    # Force manual branch generation
    print(f"\n🔧 MANUAL BRANCH GENERATION")
    force_manual_branch_generation(quantum_playwright, scene_requirements)
    
    exploration_time = time.time() - start_time
    
    # Get final state
    viz_data = quantum_playwright.get_quantum_visualization_data()
    
    print(f"\n✨ AGGRESSIVE EXPLORATION COMPLETE!")
    print(f"Total time: {exploration_time:.1f} seconds")
    print(f"LLM calls made: {llm_call_count}")
    print(f"Branches tracked: {branch_count}")
    
    if viz_data:
        metadata = viz_data.get("metadata", {})
        print(f"Active branches: {metadata.get('total_active_branches', 0)}")
        print(f"Max depth: {metadata.get('max_depth_explored', 0)}")
        print(f"Average quality: {metadata.get('average_branch_quality', 0):.3f}")
    
    # Final collapse
    print(f"\n🎯 FINAL COLLAPSE")
    final_result = quantum_playwright.collapse_quantum_state("aggressive_exploration_complete")
    
    if final_result:
        print(f"Final quality: {final_result.get('quality_score', 0):.3f}")
        print(f"Final content preview:")
        content = final_result.get('final_content', '')
        print(content[:300] + "..." if len(content) > 300 else content)

def force_manual_branch_generation(quantum_playwright, scene_requirements):
    """Force manual branch generation to increase LLM usage."""
    
    print("  🔨 Forcing manual branch generation...")
    
    if not quantum_playwright.branch_generator:
        print("    No branch generator available")
        return
    
    # Get current quantum tree state
    if not quantum_playwright.quantum_tree or not quantum_playwright.quantum_tree.active_branches:
        print("    No active branches to expand")
        return
    
    # For each active branch, force additional character exploration
    active_branches = list(quantum_playwright.quantum_tree.active_branches.values())
    print(f"    Found {len(active_branches)} active branches to expand")
    
    for i, branch in enumerate(active_branches[:3]):  # Limit to prevent explosion
        print(f"    Expanding branch {i+1}: {branch.branch_id}")
        
        # Force character psychology branches for both characters
        for char_name in ["MAYA", "DAVID"]:
            print(f"      Generating {char_name} psychology branches...")
            
            decision_context = f"Character {char_name} responds to the dramatic situation"
            
            try:
                char_branches = quantum_playwright.branch_generator.generate_character_psychology_branches(
                    character_name=char_name,
                    decision_context=decision_context,
                    current_state=branch,
                    llm_invoke_func=lambda prompt: quantum_playwright.get_llm().invoke(prompt)
                )
                
                print(f"        Generated {len(char_branches)} branches for {char_name}")
                
                # Add branches to quantum tree
                for new_branch in char_branches:
                    quantum_playwright.quantum_tree.add_branch(branch.branch_id, new_branch)
                    
            except Exception as e:
                print(f"        Error generating {char_name} branches: {e}")

def create_complex_maya():
    """Create complex Maya character."""
    maya = EnhancedCharacterProfile(
        id="maya",
        name="MAYA",
        description="Environmental activist with deep emotional complexity",
        background="25-year-old activist fighting environmental injustice while dealing with personal trauma",
        motivations=["Save the environment", "Honor her mother's memory", "Find meaning in loss"],
        goals=["Stop the pipeline", "Build sustainable community", "Heal from trauma"],
        conflicts=["Individual vs collective action", "Idealism vs pragmatism", "Love vs principles"],
        relationships={"DAVID": "childhood friend, now opponent"}
    )
    
    maya.fears = ["Failing her mission", "Being powerless", "Losing David forever"]
    maya.desires = ["Environmental justice", "Deep connection", "Inner peace"]
    maya.values = ["Environmental protection", "Social justice", "Authenticity"]
    maya.strengths = ["Passionate conviction", "Strategic thinking", "Inspiring others"]
    maya.flaws = ["Rigidity", "Self-righteousness", "Avoiding grief"]
    
    return maya

def create_complex_david():
    """Create complex David character."""
    david = EnhancedCharacterProfile(
        id="david",
        name="DAVID",
        description="Corporate lawyer torn between values and security",
        background="26-year-old lawyer who chose financial security over idealism",
        motivations=["Financial security", "Professional success", "Maintain relationships"],
        goals=["Make partner", "Reconcile with Maya", "Find ethical balance"],
        conflicts=["Security vs values", "Past vs present", "Love vs career"],
        relationships={"MAYA": "childhood friend, love interest"}
    )
    
    david.fears = ["Poverty", "Losing Maya", "Being seen as sellout"]
    david.desires = ["Maya's respect", "Financial freedom", "Moral clarity"]
    david.values = ["Family security", "Hard work", "Loyalty"]
    david.strengths = ["Legal expertise", "Negotiation", "Strategic thinking"]
    david.flaws = ["Fear-driven decisions", "Avoiding emotions", "Compartmentalization"]
    
    return david

def create_simple_story():
    """Create simple story outline."""
    acts_data = [
        {
            "act_number": 2,
            "description": "The confrontation",
            "key_events": ["Maya confronts David"],
            "status": "planned"
        }
    ]
    
    story_outline = StoryOutline(title="The Confrontation", acts=acts_data)
    return story_outline

if __name__ == "__main__":
    main()