#!/usr/bin/env python3
"""
Instagram Swimsuit Detector - Complete Solution
Single file with all features: single mode, batch mode, session management, GPT-4 Vision

Author: AI Assistant
License: MIT
"""

import os
import sys
import asyncio
import base64
import json
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InstagramSwimsuitChecker:
    """Complete Instagram swimsuit detection with session management and batch processing"""

    def __init__(self, username, password, openai_api_key):
        self.username = username
        self.password = password
        self.client = OpenAI(api_key=openai_api_key)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = 'instagram_session.json'

        # Results storage
        self.single_results = []
        self.batch_results = []

    # ============================================================================
    # BROWSER & SESSION MANAGEMENT
    # ============================================================================

    async def init_browser(self):
        """Initialize browser with session management"""
        self.playwright = await async_playwright().start()
        session_path = Path(self.session_file)

        if session_path.exists():
            print("📂 Session file found. Loading saved session...")
            try:
                self.browser = await self.playwright.chromium.launch(
                    headless=False,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                self.context = await self.browser.new_context(
                    storage_state=self.session_file
                )
                self.page = await self.context.new_page()
                await self.page.set_viewport_size({"width": 1280, "height": 720})

                print("🔍 Verifying session validity...")
                await self.page.goto('https://www.instagram.com/')
                await asyncio.sleep(3)

                if await self.check_login_status():
                    print("✅ Session is valid! Already logged in.")
                    return True
                else:
                    print("⚠️  Session expired. Will login with credentials...")
                    session_path.unlink()
                    return False

            except Exception as e:
                print(f"⚠️  Error loading session: {e}")
                if session_path.exists():
                    session_path.unlink()
                return False
        else:
            print("📭 No session file found. Will login with credentials...")
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            await self.page.set_viewport_size({"width": 1280, "height": 720})
            return False

    async def check_login_status(self):
        """Check if user is logged in"""
        try:
            await self.page.wait_for_selector('svg[aria-label="Home"], a[href="/"]', timeout=5000)
            current_url = self.page.url
            if 'login' in current_url:
                return False
            nav_elements = await self.page.query_selector('nav')
            return nav_elements is not None
        except:
            return False

    async def login_instagram(self):
        """Login to Instagram and save session"""
        print("🔐 Logging into Instagram...")
        await self.page.goto('https://www.instagram.com/')
        await asyncio.sleep(3)

        # Close cookie banner
        try:
            await self.page.click('button:has-text("Allow all cookies")', timeout=5000)
        except:
            pass

        # Fill login form
        await asyncio.sleep(2)
        await self.page.fill('input[name="username"]', self.username)
        await self.page.fill('input[name="password"]', self.password)
        await self.page.click('button[type="submit"]')

        print("⏳ Waiting for login process...")
        await asyncio.sleep(5)

        # Close pop-ups
        try:
            await self.page.click('button:has-text("Not Now")', timeout=5000)
        except:
            pass

        try:
            await self.page.click('button:has-text("Not Now")', timeout=5000)
        except:
            pass

        # Save session
        print("💾 Saving session for future use...")
        await self.context.storage_state(path=self.session_file)
        print("✅ Successfully logged in and session saved!")

    async def cleanup(self):
        """Cleanup browser and playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    # ============================================================================
    # INSTAGRAM SCRAPING
    # ============================================================================

    async def get_profile_posts(self, profile_username, max_posts=10):
        """Scrape posts from Instagram profile"""
        print(f"\n🔍 Navigating to profile: {profile_username}...")
        await self.page.goto(f'https://www.instagram.com/{profile_username}/')
        await asyncio.sleep(4)

        posts_data = []
        last_height = await self.page.evaluate('document.body.scrollHeight')

        while len(posts_data) < max_posts:
            # Find all posts (Instagram uses direct <a> tags, not wrapped in <article>)
            posts = await self.page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            print(f"📊 Found posts: {len(posts)}")

            for post in posts[:max_posts]:
                if len(posts_data) >= max_posts:
                    break

                post_url = await post.get_attribute('href')
                img = await post.query_selector('img')

                if img:
                    img_src = await img.get_attribute('src')

                    # Check if video (skip videos)
                    parent = await post.query_selector('..')
                    svg_elements = await parent.query_selector_all(
                        'svg[aria-label*="Clip"], svg[aria-label*="Reel"], '
                        'svg[aria-label*="Video"], svg[aria-label*="Клип"]'
                    )

                    is_video = len(svg_elements) > 0

                    if not is_video and img_src and 'http' in img_src:
                        posts_data.append({
                            'url': 'https://www.instagram.com' + post_url if not post_url.startswith('http') else post_url,
                            'image_url': img_src
                        })
                        print(f"  ✅ Image found: {len(posts_data)}/{max_posts}")
                    elif is_video:
                        print(f"  ⏭️  Video skipped")

            # Scroll down
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)

            new_height = await self.page.evaluate('document.body.scrollHeight')
            if new_height == last_height and len(posts_data) >= 3:
                break
            last_height = new_height

        return posts_data[:max_posts]

    async def download_image(self, image_url, filename):
        """Download image from URL"""
        try:
            os.makedirs('images', exist_ok=True)

            image_page = await self.context.new_page()
            await image_page.goto(image_url)
            await asyncio.sleep(1)

            image_path = f'images/{filename}.jpg'
            await image_page.screenshot(path=image_path)
            await image_page.close()

            return image_path
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return None

    # ============================================================================
    # GPT-4 VISION ANALYSIS
    # ============================================================================

    def analyze_image_with_gpt(self, image_path):
        """Analyze image using GPT-4 Vision"""
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Is the person in this image wearing a swimsuit (bikini, swimsuit, bathing suit)? Answer only 'YES' or 'NO'. If there's no person in the image, answer 'NO'."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=10
            )

            answer = response.choices[0].message.content.strip().upper()

            if 'YES' in answer or 'WEARING' in answer:
                return 'WEARING'
            else:
                return 'NOT WEARING'

        except Exception as e:
            print(f"❌ GPT analysis error: {e}")
            return 'ERROR'

    # ============================================================================
    # SINGLE PROFILE MODE
    # ============================================================================

    async def analyze_single_profile(self, username, max_posts=10):
        """Analyze a single profile"""
        print(f"\n{'='*70}")
        print(f"🎯 SINGLE PROFILE MODE: @{username}")
        print(f"{'='*70}")

        # Get posts
        posts = await self.get_profile_posts(username, max_posts)

        if not posts:
            print(f"⚠️  No images found for @{username}")
            return

        print(f"\n📷 Found {len(posts)} images. Analyzing...")

        # Analyze each image
        for idx, post in enumerate(posts, 1):
            print(f"\n[{idx}/{len(posts)}] 🔍 Analyzing post...")
            print(f"  🔗 URL: {post['url']}")

            # Download image
            image_path = await self.download_image(post['image_url'], f"{username}_{idx}")

            if image_path:
                # Analyze with GPT
                result = self.analyze_image_with_gpt(image_path)

                self.single_results.append({
                    'post_number': idx,
                    'post_url': post['url'],
                    'image_path': image_path,
                    'has_swimsuit': result
                })

                print(f"  ✅ Result: {result}")
            else:
                print(f"  ❌ Failed to download image")

        # Print results
        self.print_single_results(username)

    def print_single_results(self, username):
        """Print results for single profile"""
        print(f"\n{'='*70}")
        print(f"📊 RESULTS FOR @{username}")
        print(f"{'='*70}")

        swimsuit_count = sum(1 for r in self.single_results if r['has_swimsuit'] == 'WEARING')

        for result in self.single_results:
            print(f"\n📌 Post #{result['post_number']}")
            print(f"  🔗 URL: {result['post_url']}")
            print(f"  👙 Swimsuit: {result['has_swimsuit']}")

        print(f"\n{'='*70}")
        print(f"📊 Total analyzed: {len(self.single_results)} images")
        print(f"👙 Swimsuit found: {swimsuit_count}")
        print(f"👔 No swimsuit: {len(self.single_results) - swimsuit_count}")
        print(f"{'='*70}")

        # Save to JSON
        output_file = f'{username}_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'username': username,
                'total_posts': len(self.single_results),
                'swimsuit_count': swimsuit_count,
                'results': self.single_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Results saved to '{output_file}'!")

    # ============================================================================
    # BATCH PROFILE MODE
    # ============================================================================

    async def analyze_batch_profiles(self, usernames_file='usernames.txt', max_posts=10):
        """Analyze multiple profiles from a list"""
        # Load usernames
        try:
            with open(usernames_file, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ Error: {usernames_file} not found!")
            return

        if not usernames:
            print("❌ No usernames to process!")
            return

        print(f"\n{'='*70}")
        print(f"🚀 BATCH MODE: Processing {len(usernames)} profiles")
        print(f"📝 Posts per profile: {max_posts}")
        print(f"{'='*70}")

        # Create results directory
        os.makedirs('batch_results', exist_ok=True)

        # Process each profile
        for idx, username in enumerate(usernames, 1):
            print(f"\n{'='*70}")
            print(f"🔍 Processing profile [{idx}/{len(usernames)}]: @{username}")
            print(f"{'='*70}")

            try:
                # Get posts
                posts = await self.get_profile_posts(username, max_posts)

                if not posts:
                    print(f"⚠️  No images found for @{username}")
                    profile_result = {
                        'username': username,
                        'status': 'no_images',
                        'total_posts': 0,
                        'swimsuit_count': 0,
                        'results': []
                    }
                else:
                    print(f"📷 Found {len(posts)} images. Analyzing...")

                    profile_results = []

                    # Analyze each image
                    for post_idx, post in enumerate(posts, 1):
                        print(f"  [{post_idx}/{len(posts)}] 🔍 Analyzing post...")

                        # Download image
                        image_path = await self.download_image(
                            post['image_url'],
                            f"{username}_{post_idx}"
                        )

                        if image_path:
                            # Analyze with GPT
                            result = self.analyze_image_with_gpt(image_path)

                            profile_results.append({
                                'post_number': post_idx,
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

                    profile_result = {
                        'username': username,
                        'status': 'success',
                        'total_posts': len(profile_results),
                        'swimsuit_count': swimsuit_count,
                        'results': profile_results
                    }

                # Add to batch results
                self.batch_results.append(profile_result)

                # Save individual profile results
                profile_file = f"batch_results/{username}_results.json"
                with open(profile_file, 'w', encoding='utf-8') as f:
                    json.dump(profile_result, f, ensure_ascii=False, indent=2)
                print(f"💾 Saved results to: {profile_file}")

            except Exception as e:
                print(f"❌ Error processing @{username}: {e}")
                self.batch_results.append({
                    'username': username,
                    'status': 'error',
                    'error': str(e),
                    'total_posts': 0,
                    'swimsuit_count': 0,
                    'results': []
                })

            # Delay between profiles
            if idx < len(usernames):
                print("\n⏸️  Waiting 5 seconds before next profile...")
                await asyncio.sleep(5)

        # Save batch summary
        self.save_batch_summary()

        # Print final summary
        self.print_batch_summary()

    def save_batch_summary(self):
        """Save batch processing summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"batch_results/batch_summary_{timestamp}.json"

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

    def print_batch_summary(self):
        """Print batch processing summary"""
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

        print(f"\n📁 Results saved in: batch_results/")
        print(f"{'='*70}\n")


# ============================================================================
# MAIN FUNCTION & CLI
# ============================================================================

async def main():
    """Main function with CLI interface"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║          Instagram Swimsuit Detector - Complete Solution        ║
║          Single file with all features built-in                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Get credentials from environment
    instagram_username = os.getenv('INSTAGRAM_USERNAME')
    instagram_password = os.getenv('INSTAGRAM_PASSWORD')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if not all([instagram_username, instagram_password, openai_api_key]):
        print("❌ ERROR: Missing required variables in .env file!")
        print("Required variables:")
        print("  - INSTAGRAM_USERNAME")
        print("  - INSTAGRAM_PASSWORD")
        print("  - OPENAI_API_KEY")
        return

    # Get mode
    print("\n📋 Select mode:")
    print("  1. Single Profile Mode - Analyze one profile")
    print("  2. Batch Mode - Analyze multiple profiles from file")

    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user.")
        return

    # Create checker instance
    checker = InstagramSwimsuitChecker(
        username=instagram_username,
        password=instagram_password,
        openai_api_key=openai_api_key
    )

    try:
        # Initialize browser and login
        session_valid = await checker.init_browser()
        if not session_valid:
            await checker.login_instagram()

        if choice == '1':
            # Single profile mode
            target_username = os.getenv('TARGET_INSTAGRAM_USERNAME', '')
            if not target_username:
                try:
                    target_username = input("\n📱 Enter Instagram username to analyze: ").strip()
                except KeyboardInterrupt:
                    print("\n\n👋 Cancelled by user.")
                    return

            max_posts = int(os.getenv('MAX_POSTS_PER_PROFILE', '10'))
            await checker.analyze_single_profile(target_username, max_posts)

        elif choice == '2':
            # Batch mode
            usernames_file = os.getenv('USERNAMES_FILE', 'usernames.txt')
            max_posts = int(os.getenv('MAX_POSTS_PER_PROFILE', '10'))
            await checker.analyze_batch_profiles(usernames_file, max_posts)

        else:
            print("❌ Invalid choice!")

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await checker.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
