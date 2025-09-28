#!/usr/bin/env python3

"""
Simple script to validate that the consolidated_playwright.py file can be imported.
"""

import sys
from pathlib import Path

# Directly import the specific module we want to test
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    print("Trying to import consolidated_playwright...")
    from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability
    
    print("✅ Success! Module can be imported.")
    print(f"- Found class: {Playwright.__name__}")
    print(f"- Found class: {SceneRequirements.__name__}")
    print(f"- Found enum: {PlaywrightCapability.__name__}")
    
    # Check enum values
    print("\nPlaywright capabilities:")
    for capability in PlaywrightCapability:
        print(f"- {capability.name}: {capability.value}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")