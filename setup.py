#!/usr/bin/env python3
"""
Quick Setup Script for Instagram Swimsuit Detector
Creates .env file with your credentials
"""

import os
from pathlib import Path


def setup():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   Instagram Swimsuit Detector - Setup                           ║
║   Quick configuration wizard                                     ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (yes/no): ").lower()
        if response != 'yes':
            print("❌ Setup cancelled.")
            return

    print("\n🔐 Enter your credentials:")
    print("(These will be saved to .env file)")
    print("-" * 70)

    # Get Instagram credentials
    instagram_username = input("\n📱 Instagram Username: ").strip()
    instagram_password = input("🔑 Instagram Password: ").strip()

    # Get OpenAI API key
    openai_api_key = input("\n🤖 OpenAI API Key: ").strip()

    # Get optional settings
    print("\n⚙️  Optional settings (press Enter for defaults):")
    target_username = input("📍 Target profile (default: boitumar_osh): ").strip() or "boitumar_osh"
    max_posts = input("📊 Max posts per profile (default: 10): ").strip() or "10"

    # Validate inputs
    if not instagram_username or not instagram_password or not openai_api_key:
        print("\n❌ Error: All required fields must be filled!")
        return

    # Create .env content
    env_content = f"""# Instagram credentials
INSTAGRAM_USERNAME={instagram_username}
INSTAGRAM_PASSWORD={instagram_password}

# OpenAI API key
OPENAI_API_KEY={openai_api_key}

# Single profile mode (for instagram_swimsuit_detector.py)
TARGET_INSTAGRAM_USERNAME={target_username}

# Batch mode settings (for batch_checker.py)
MAX_POSTS_PER_PROFILE={max_posts}
USERNAMES_FILE=usernames.txt
"""

    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)

        print("\n✅ Success! .env file created.")
        print("\n📋 Your configuration:")
        print(f"  Instagram: @{instagram_username}")
        print(f"  OpenAI: {openai_api_key[:20]}...")
        print(f"  Target: {target_username}")
        print(f"  Max posts: {max_posts}")

        print("\n🚀 Next steps:")
        print("  1. Single profile: python instagram_swimsuit_detector.py")
        print("  2. Batch mode:     python batch_checker.py")
        print("\n📚 Documentation:")
        print("  - README.md - Main documentation")
        print("  - BATCH_MODE.md - Batch processing guide")

    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")


if __name__ == "__main__":
    setup()
