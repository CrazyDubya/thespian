"""
Runner script for enhanced playwright collaboration test.
"""

import os
from dotenv import load_dotenv
from tests.unit.test_playwrights import test_enhanced_playwright_collaboration


def main():
    # Load environment variables
    load_dotenv()

    # Check for required API keys
    if not os.getenv("XAI_API_KEY"):
        print("Warning: XAI_API_KEY not found. Grok playwright will not be available.")

    # Run the enhanced playwright test
    test_enhanced_playwright_collaboration()


if __name__ == "__main__":
    main()
