"""
Test the integrated workflow with a minimal example.
"""

import sys
sys.path.append('.')

from thespian.production import ProductionWorkflowManager


def test_minimal_production():
    """Test minimal production to verify integration."""
    print("Testing Integrated Workflow...")
    print("-" * 50)
    
    # Create workflow manager with minimal settings
    workflow = ProductionWorkflowManager(
        target_scene_length=1000,  # Smaller target for testing
        max_workshop_iterations=1,  # Fewer iterations
        enable_all_enhancements=False,  # Disable some features for speed
        track_metrics=True
    )
    
    try:
        # Run a tiny production
        result = workflow.generate_enhanced_production(
            premise="A person discovers a mysterious letter.",
            themes=["discovery", "truth"],
            num_acts=1,
            scenes_per_act=2,
            style="mystery"
        )
        
        print("\n✅ Workflow integration successful!")
        print(f"Status: {result['status']}")
        print(f"Scenes generated: {result['metrics']['production_stats']['scenes_completed']}")
        print(f"Total length: {result['metrics']['length_metrics']['total_length']} characters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_minimal_production()
    sys.exit(0 if success else 1)