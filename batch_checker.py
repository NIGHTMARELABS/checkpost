"""
Instagram Swimsuit Detector - Batch Mode
Process multiple Instagram profiles from a list
"""

import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from instagram_swimsuit_detector import InstagramSwimsuitDetector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BatchChecker:
    def __init__(self, username, password, openai_api_key, usernames_file='usernames.txt'):
        self.detector = InstagramSwimsuitDetector(username, password, openai_api_key)
        self.usernames_file = usernames_file
        self.batch_results = []
        self.results_dir = 'batch_results'

    def load_usernames(self):
        """Load usernames from file"""
        try:
            with open(self.usernames_file, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
            return usernames
        except FileNotFoundError:
            print(f"❌ Error: {self.usernames_file} not found!")
            return []

    async def process_profile(self, username, index, total, max_posts=10):
        """Process a single profile"""
        print(f"\n{'='*70}")
        print(f"🔍 Processing profile [{index}/{total}]: @{username}")
        print(f"{'='*70}")

        try:
            # Get posts from this profile
            posts = await self.detector.get_profile_posts(username, max_posts)

            if not posts:
                print(f"⚠️  No images found for @{username}")
                return {
                    'username': username,
                    'status': 'no_images',
                    'total_posts': 0,
                    'swimsuit_count': 0,
                    'results': []
                }

            print(f"📷 Found {len(posts)} images. Analyzing...")

            profile_results = []

            # Analyze each image
            for idx, post in enumerate(posts, 1):
                print(f"  [{idx}/{len(posts)}] 🔍 Analyzing post...")

                # Download image
                image_path = await self.detector.download_image(post['image_url'], f"{username}_{idx}")

                if image_path:
                    # Analyze with GPT
                    result = self.detector.analyze_image_with_gpt(image_path)

                    profile_results.append({
                        'post_number': idx,
                        'post_url': post['url'],
                        'image_path': image_path,
                        'has_swimsuit': result
                    })

                    print(f"    ✅ Result: {result}")
                else:
                    print(f"    ❌ Failed to download")

            # Calculate statistics
            swimsuit_count = sum(1 for r in profile_results if r['has_swimsuit'] == 'WEARING')

            print(f"\n📊 Profile Summary:")
            print(f"  Total analyzed: {len(profile_results)}")
            print(f"  👙 Swimsuit found: {swimsuit_count}")
            print(f"  👔 No swimsuit: {len(profile_results) - swimsuit_count}")

            return {
                'username': username,
                'status': 'success',
                'total_posts': len(profile_results),
                'swimsuit_count': swimsuit_count,
                'results': profile_results
            }

        except Exception as e:
            print(f"❌ Error processing @{username}: {e}")
            return {
                'username': username,
                'status': 'error',
                'error': str(e),
                'total_posts': 0,
                'swimsuit_count': 0,
                'results': []
            }

    async def run(self, max_posts_per_profile=10):
        """Process all profiles"""
        # Load usernames
        usernames = self.load_usernames()

        if not usernames:
            print("❌ No usernames to process!")
            return

        print(f"\n{'='*70}")
        print(f"🚀 BATCH MODE: Processing {len(usernames)} profiles")
        print(f"📝 Posts per profile: {max_posts_per_profile}")
        print(f"{'='*70}")

        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)

        try:
            # Initialize browser and login once
            session_valid = await self.detector.init_browser()
            if not session_valid:
                await self.detector.login_instagram()

            # Process each profile
            for idx, username in enumerate(usernames, 1):
                profile_result = await self.process_profile(
                    username,
                    idx,
                    len(usernames),
                    max_posts_per_profile
                )
                self.batch_results.append(profile_result)

                # Save individual profile results
                profile_file = f"{self.results_dir}/{username}_results.json"
                with open(profile_file, 'w', encoding='utf-8') as f:
                    json.dump(profile_result, f, ensure_ascii=False, indent=2)
                print(f"💾 Saved results to: {profile_file}")

                # Small delay between profiles
                if idx < len(usernames):
                    print("\n⏸️  Waiting 5 seconds before next profile...")
                    await asyncio.sleep(5)

            # Save batch summary
            await self.save_batch_summary()

            # Print final summary
            self.print_final_summary()

        finally:
            if self.detector.browser:
                await self.detector.browser.close()
            if self.detector.playwright:
                await self.detector.playwright.stop()

    async def save_batch_summary(self):
        """Save batch processing summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"{self.results_dir}/batch_summary_{timestamp}.json"

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_profiles': len(self.batch_results),
            'successful': sum(1 for r in self.batch_results if r['status'] == 'success'),
            'failed': sum(1 for r in self.batch_results if r['status'] == 'error'),
            'no_images': sum(1 for r in self.batch_results if r['status'] == 'no_images'),
            'total_posts_analyzed': sum(r['total_posts'] for r in self.batch_results),
            'total_swimsuit_found': sum(r['swimsuit_count'] for r in self.batch_results),
            'profiles': self.batch_results
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Batch summary saved to: {summary_file}")

    def print_final_summary(self):
        """Print final batch summary"""
        print(f"\n{'='*70}")
        print("🎉 BATCH PROCESSING COMPLETED!")
        print(f"{'='*70}")

        total_profiles = len(self.batch_results)
        successful = sum(1 for r in self.batch_results if r['status'] == 'success')
        failed = sum(1 for r in self.batch_results if r['status'] == 'error')
        no_images = sum(1 for r in self.batch_results if r['status'] == 'no_images')
        total_posts = sum(r['total_posts'] for r in self.batch_results)
        total_swimsuit = sum(r['swimsuit_count'] for r in self.batch_results)

        print(f"\n📊 Overall Statistics:")
        print(f"  Total profiles processed: {total_profiles}")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  No images: {no_images}")
        print(f"  📷 Total posts analyzed: {total_posts}")
        print(f"  👙 Total swimsuit found: {total_swimsuit}")

        print(f"\n📋 Profile Results:")
        for result in self.batch_results:
            status_emoji = {
                'success': '✅',
                'error': '❌',
                'no_images': '⚠️'
            }.get(result['status'], '❓')

            print(f"  {status_emoji} @{result['username']}: "
                  f"{result['total_posts']} posts, "
                  f"{result['swimsuit_count']} with swimsuit")

        print(f"\n📁 Results saved in: {self.results_dir}/")
        print(f"{'='*70}\n")


async def main():
    """Main function"""
    # Get credentials from .env file
    instagram_username = os.getenv('INSTAGRAM_USERNAME')
    instagram_password = os.getenv('INSTAGRAM_PASSWORD')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Get configuration
    max_posts_per_profile = int(os.getenv('MAX_POSTS_PER_PROFILE', '10'))
    usernames_file = os.getenv('USERNAMES_FILE', 'usernames.txt')

    if not all([instagram_username, instagram_password, openai_api_key]):
        print("❌ ERROR: Missing required variables in .env file!")
        print("Required variables:")
        print("  - INSTAGRAM_USERNAME")
        print("  - INSTAGRAM_PASSWORD")
        print("  - OPENAI_API_KEY")
        return

    # Create batch checker
    checker = BatchChecker(
        username=instagram_username,
        password=instagram_password,
        openai_api_key=openai_api_key,
        usernames_file=usernames_file
    )

    # Run batch processing
    await checker.run(max_posts_per_profile=max_posts_per_profile)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   Instagram Swimsuit Detector - BATCH MODE                      ║
║   Process multiple profiles automatically                        ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    asyncio.run(main())
