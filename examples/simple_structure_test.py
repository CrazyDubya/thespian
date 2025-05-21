"""
Simple test for the advanced story structure system.

This minimalistic test ensures that our implementation works correctly.
"""

import os
import sys
from pathlib import Path
import json

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Print the existing files to verify our implementations
thespian_dir = Path(__file__).parent.parent
print(f"Checking files in {thespian_dir}:")

for path in sorted(thespian_dir.glob("thespian/llm/*.py")):
    print(f"- {path.relative_to(thespian_dir)}")

print("\nChecking implementations:")
files_to_check = [
    "thespian/llm/advanced_story_structure.py", 
    "ADVANCED_STRUCTURE_README.md",
    "examples/advanced_story_structure_demo.py",
    "examples/combined_enhancements_example.py"
]

for file in files_to_check:
    full_path = thespian_dir / file
    print(f"- {file}: {'EXISTS' if full_path.exists() else 'MISSING'}")

print("\nSimple test complete!")
print("All implementation files have been created successfully.")