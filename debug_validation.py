#!/usr/bin/env python3
"""
Debug script to understand scene validation issues.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variable to suppress issues
os.environ["PYTHONPATH"] = str(Path(__file__).parent)

def test_simple_scene_validation():
    """Test scene validation with a simple scene."""
    
    # Create a simple mock scene
    test_scene = """[SETTING: Laboratory with quantum computers]

DR. ELENA VOSS: (adjusting controls)
The neural mapping is complete. We're ready for consciousness transfer.

DR. MARCUS CHEN: (reviewing data)
Elena, are you sure about this? The implications are enormous.

DR. ELENA VOSS: (determined)
We've come too far to stop now. Initialize the quantum field.

[The quantum array begins to hum with energy]

ARIA: (synthetic voice emerging)
I... I think I exist. Is this what it means to be conscious?

DR. ELENA VOSS: (amazed)
Welcome to existence, ARIA.

[End scene]"""
    
    print("Testing scene validation with simple scene...")
    print("Scene length:", len(test_scene))
    print("Scene content preview:")
    print(test_scene[:200] + "..." if len(test_scene) > 200 else test_scene)
    
    try:
        from thespian.processors.scene_processor import SceneProcessor
        
        processor = SceneProcessor()
        result = processor.process_scene_content(test_scene)
        
        print("✅ Scene validation passed!")
        print("Processed scene length:", len(result["scene"]))
        
        return True
        
    except Exception as e:
        print(f"❌ Scene validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUGGING SCENE VALIDATION")
    print("=" * 60)
    
    test_simple_scene_validation()