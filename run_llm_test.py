"""
Run the LLM integration test.
"""

import os
from dotenv import load_dotenv
from tests.test_llm_integration import test_llm_integration


def main():
    """Run the LLM integration test."""
    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    if not os.getenv("XAI_API_KEY"):
        print("Warning: XAI_API_KEY not found in environment variables")
        print("Grok model will not be available")

    # Run the test
    test_llm_integration()


if __name__ == "__main__":
    main()
