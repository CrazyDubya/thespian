"""
Demonstration of collaborative scene generation with enhanced agents.
"""

import sys
sys.path.append('.')

from thespian.llm.collaborative_playwright import CollaborativePlaywright
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
import json


def demonstrate_collaborative_generation():
    """Show how collaborative scene generation improves output quality."""
    
    print("=== Collaborative Scene Generation Demo ===\n")
    
    # Initialize collaborative playwright
    memory = EnhancedTheatricalMemory()
    playwright = CollaborativePlaywright(
        memory=memory,
        enable_pre_production=True,
        enable_workshops=True,
        iteration_limit=2  # Keep it reasonable for demo
    )
    
    # Define premise and themes
    premise = """
    A brilliant scientist discovers a way to communicate with their past self, 
    but each message sent changes the present in unexpected ways. As they try 
    to prevent a personal tragedy, they must grapple with the ethics of 
    altering history and the butterfly effect of their actions.
    """
    
    themes = ["fate vs free will", "consequences of knowledge", "sacrifice", "identity"]
    
    # Create story outline
    print("1. Creating story outline...")
    story_outline = playwright.create_story_outline(premise, themes)
    print(f"   - Title: {story_outline.get('title', 'Untitled')}")
    print(f"   - Characters: {len(story_outline.get('characters', []))}")
    print(f"   - Acts: {len(story_outline.get('acts', []))}")
    
    # Conduct pre-production meeting
    print("\n2. Conducting pre-production meeting...")
    pre_production = playwright.conduct_pre_production_meeting(
        premise,
        story_outline.get('characters', []),
        themes
    )
    print("   - Director vision captured")
    print("   - Design concept developed")
    print("   - Technical requirements noted")
    
    # Generate a single scene with collaboration
    print("\n3. Generating Act 1, Scene 1 with collaboration...")
    
    act_1_scenes = story_outline['acts'][0]['scenes']
    first_scene_guide = act_1_scenes[0]
    
    scene = playwright.generate_scene(
        act_number=1,
        scene_number=1,
        scene_guide=first_scene_guide,
        previous_scenes=[],
        word_count=1500
    )
    
    print(f"\n4. Scene Generation Results:")
    print(f"   - Base length: ~1500 words requested")
    print(f"   - Final length: {len(scene['content'])} characters")
    print(f"   - Workshop iterations: {scene.get('workshop_iterations', 0)}")
    
    # Display workshop improvements
    if 'workshop_notes' in scene:
        print(f"\n5. Workshop Improvements:")
        notes = scene['workshop_notes']
        for i, iteration in enumerate(notes.get('iterations', [])):
            print(f"\n   Iteration {i+1}:")
            
            # Director feedback
            if iteration.get('director_feedback'):
                print("   - Director provided scene notes")
            
            # Actor suggestions
            actor_sugg = iteration.get('actor_suggestions', {})
            if actor_sugg:
                print(f"   - Actors made suggestions: {list(actor_sugg.keys())}")
            
            # Atmosphere
            if iteration.get('atmosphere_notes'):
                print("   - Designer added atmosphere elements")
            
            # Continuity
            if iteration.get('continuity_check'):
                print("   - Stage manager checked continuity")
    
    # Save the scene
    print(f"\n6. Saving scene to file...")
    with open('data/output/collaborative_scene_demo.txt', 'w') as f:
        f.write(f"COLLABORATIVE SCENE GENERATION DEMO\n")
        f.write(f"{'=' * 50}\n\n")
        f.write(f"Premise: {premise}\n")
        f.write(f"Themes: {', '.join(themes)}\n")
        f.write(f"Workshop Iterations: {scene.get('workshop_iterations', 0)}\n")
        f.write(f"\n{'=' * 50}\n\n")
        f.write(scene['content'])
    
    # Save workshop notes
    with open('data/output/collaborative_workshop_notes.json', 'w') as f:
        json.dump(scene.get('workshop_notes', {}), f, indent=2)
    
    print("   - Scene saved to data/output/collaborative_scene_demo.txt")
    print("   - Workshop notes saved to data/output/collaborative_workshop_notes.json")
    
    # Display excerpt
    print(f"\n7. Scene Excerpt (first 500 chars):")
    print("-" * 50)
    print(scene['content'][:500] + "...")
    
    return scene


def compare_with_standard_generation():
    """Compare collaborative vs standard generation."""
    
    print("\n\n=== Comparison: Collaborative vs Standard ===\n")
    
    premise = "Two strangers meet in a coffee shop during a power outage."
    
    # Standard generation
    print("1. Standard Generation:")
    from thespian.llm.playwright import EnhancedPlaywright
    standard_playwright = EnhancedPlaywright()
    standard_outline = standard_playwright.create_story_outline(premise, ["connection", "chance"])
    standard_scene = standard_playwright.generate_scene(
        1, 1, 
        standard_outline['acts'][0]['scenes'][0],
        word_count=1000
    )
    print(f"   - Length: {len(standard_scene['content'])} characters")
    print(f"   - No workshops or agent collaboration")
    
    # Collaborative generation
    print("\n2. Collaborative Generation:")
    collab_playwright = CollaborativePlaywright(
        enable_pre_production=False,  # Skip for quick comparison
        enable_workshops=True,
        iteration_limit=1
    )
    collab_outline = collab_playwright.create_story_outline(premise, ["connection", "chance"])
    collab_scene = collab_playwright.generate_scene(
        1, 1,
        collab_outline['acts'][0]['scenes'][0],
        word_count=1000
    )
    print(f"   - Length: {len(collab_scene['content'])} characters")
    print(f"   - Workshop iterations: {collab_scene.get('workshop_iterations', 0)}")
    print(f"   - Improvement: {len(collab_scene['content']) - len(standard_scene['content'])} characters")


if __name__ == "__main__":
    # Run main demonstration
    scene = demonstrate_collaborative_generation()
    
    # Run comparison
    compare_with_standard_generation()
    
    print("\n\n=== Collaborative Generation Demo Complete ===")