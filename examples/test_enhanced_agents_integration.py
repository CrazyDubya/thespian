"""
Test integration of enhanced agents with collaborative features.
"""

import sys
sys.path.append('.')

from thespian.agents_enhanced import (
    EnhancedDirectorAgent,
    EnhancedCharacterActorAgent,
    EnhancedSetCostumeDesignAgent,
    EnhancedStageManagerAgent
)


def test_enhanced_collaboration():
    """Test enhanced agents working together on a scene."""
    
    print("=== Testing Enhanced Agent Collaboration ===\n")
    
    # Create agents
    director = EnhancedDirectorAgent()
    hamlet = EnhancedCharacterActorAgent(
        character_name="Hamlet",
        character_data={
            "description": "The Prince of Denmark, melancholic and philosophical",
            "traits": ["intellectual", "indecisive", "passionate"]
        }
    )
    ophelia = EnhancedCharacterActorAgent(
        character_name="Ophelia",
        character_data={
            "description": "Polonius's daughter, torn between duty and love",
            "traits": ["innocent", "obedient", "fragile"]
        }
    )
    designer = EnhancedSetCostumeDesignAgent()
    stage_manager = EnhancedStageManagerAgent()
    
    # Sample scene for testing
    test_scene = """
    HAMLET: Get thee to a nunnery. Why wouldst thou be a breeder of sinners?
    
    OPHELIA: O, help him, you sweet heavens!
    
    HAMLET: I have heard of your paintings too, well enough. God has given you one face, 
    and you make yourselves another.
    """
    
    scene_requirements = {
        "theme": "madness and rejection",
        "mood": "intense confrontation",
        "location": "castle corridor"
    }
    
    print("1. Director provides scene notes:")
    print("-" * 40)
    try:
        director_notes = director.provide_scene_notes(test_scene, scene_requirements)
        print(f"Director Notes: {director_notes}")
    except Exception as e:
        print(f"Error getting director notes: {e}")
    
    print("\n2. Actors suggest dialogue improvements:")
    print("-" * 40)
    try:
        hamlet_suggestions = hamlet.suggest_dialogue_improvements(
            test_scene, 
            hamlet.character_data
        )
        print(f"Hamlet's suggestions: {hamlet_suggestions}")
    except Exception as e:
        print(f"Error getting Hamlet suggestions: {e}")
    
    print("\n3. Director workshops scene with actors:")
    print("-" * 40)
    try:
        workshop_result = director.workshop_scene(test_scene, [hamlet, ophelia])
        print(f"Workshop results: {workshop_result}")
    except Exception as e:
        print(f"Error in workshop: {e}")
    
    print("\n4. Designer creates atmosphere notes:")
    print("-" * 40)
    try:
        atmosphere = designer.create_atmosphere_notes(
            {"location": "castle", "time": "afternoon", "mood": "tense"},
            "escalating conflict"
        )
        print(f"Atmosphere design: {atmosphere}")
    except Exception as e:
        print(f"Error creating atmosphere: {e}")
    
    print("\n5. Stage Manager checks continuity:")
    print("-" * 40)
    try:
        continuity = stage_manager.check_continuity(
            [test_scene],
            [],  # No previous scenes
            {"props": {"letters": "Act 1"}, "costumes": {"Hamlet": "black doublet"}}
        )
        print(f"Continuity check: {continuity}")
    except Exception as e:
        print(f"Error checking continuity: {e}")
    
    print("\n=== Enhanced Collaboration Test Complete ===")


if __name__ == "__main__":
    test_enhanced_collaboration()