"""
Script to add the Grok API key to the environment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def main():
    # Load existing .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv()

    # Check if API key is already set
    if os.getenv("XAI_API_KEY"):
        print("XAI_API_KEY is already set in the environment.")
        return

    # Get API key from user
    api_key = input("Please enter your Grok API key: ").strip()

    if not api_key:
        print("No API key provided. Exiting.")
        return

    # Write to .env file
    with open(env_path, "a") as f:
        f.write(f"\nXAI_API_KEY={api_key}\n")

    print("API key has been added to .env file.")
    print("Please restart your terminal or run 'source .env' to apply the changes.")


if __name__ == "__main__":
    main()
