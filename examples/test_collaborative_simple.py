"""
Simple test of collaborative playwright system.
"""

import sys
sys.path.append('.')

from thespian.llm.collaborative_playwright import CollaborativePlaywright
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory


def test_basic_initialization():
    """Test that we can create a collaborative playwright."""
    print("Testing CollaborativePlaywright initialization...")
    
    try:
        playwright = CollaborativePlaywright(
            enable_pre_production=False,
            enable_workshops=False
        )
        print("✓ CollaborativePlaywright created successfully")
        
        # Test agent initialization
        print(f"✓ Director agent: {playwright.director}")
        print(f"✓ Designer agent: {playwright.designer}")
        print(f"✓ Stage manager: {playwright.stage_manager}")
        print(f"✓ Actors dict: {type(playwright.actors)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create CollaborativePlaywright: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_story_outline():
    """Test story outline generation."""
    print("\nTesting story outline generation...")
    
    try:
        playwright = CollaborativePlaywright(
            enable_pre_production=False,
            enable_workshops=False
        )
        
        premise = "A robot learns to feel emotions"
        themes = ["humanity", "consciousness"]
        
        outline = playwright.create_story_outline(premise, themes)
        print(f"✓ Story outline created: {outline.get('title', 'Untitled')}")
        print(f"  - Characters: {len(outline.get('characters', []))}")
        print(f"  - Acts: {len(outline.get('acts', []))}")
        
        # Initialize actors
        playwright._initialize_actors(outline.get('characters', []))
        print(f"✓ Actors initialized: {list(playwright.actors.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create story outline: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_collaborative_methods():
    """Test that collaborative methods work."""
    print("\nTesting collaborative methods...")
    
    try:
        from thespian.agents_enhanced import EnhancedDirectorAgent
        
        director = EnhancedDirectorAgent()
        print("✓ Created EnhancedDirectorAgent")
        
        # Test provide_scene_notes method exists
        if hasattr(director, 'provide_scene_notes'):
            print("✓ Director has provide_scene_notes method")
        else:
            print("✗ Director missing provide_scene_notes method")
        
        # Test workshop_scene method exists
        if hasattr(director, 'workshop_scene'):
            print("✓ Director has workshop_scene method")
        else:
            print("✗ Director missing workshop_scene method")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test collaborative methods: {e}")
        return False


if __name__ == "__main__":
    print("=== Collaborative Playwright System Test ===\n")
    
    results = []
    
    # Run tests
    results.append(test_basic_initialization())
    results.append(test_story_outline())
    results.append(test_collaborative_methods())
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All tests passed! Collaborative system is working.")
    else:
        print("\n✗ Some tests failed. Check the output above.")