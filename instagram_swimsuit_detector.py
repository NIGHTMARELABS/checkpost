"""
Instagram Swimsuit Detector
This program scrapes Instagram posts, analyzes images using GPT,
and detects if people are wearing swimsuits.
"""

import os
import asyncio
import base64
import json
from pathlib import Path
from playwright.async_api import async_playwright
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InstagramSwimsuitDetector:
    def __init__(self, username, password, openai_api_key):
        self.username = username
        self.password = password
        self.client = OpenAI(api_key=openai_api_key)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.results = []
        self.session_file = 'instagram_session.json'

    async def init_browser(self):
        """Initialize browser with or without saved session"""
        self.playwright = await async_playwright().start()

        # Check if session file exists
        session_path = Path(self.session_file)

        if session_path.exists():
            print("📂 Session file found. Loading saved session...")
            try:
                # Launch browser with saved session
                self.browser = await self.playwright.chromium.launch(
                    headless=False,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                self.context = await self.browser.new_context(
                    storage_state=self.session_file
                )
                self.page = await self.context.new_page()
                await self.page.set_viewport_size({"width": 1280, "height": 720})

                # Verify if session is still valid
                print("🔍 Verifying session validity...")
                await self.page.goto('https://www.instagram.com/')
                await asyncio.sleep(3)

                # Check if we're logged in (look for specific elements)
                is_logged_in = await self.check_login_status()

                if is_logged_in:
                    print("✅ Session is valid! Already logged in.")
                    return True
                else:
                    print("⚠️  Session expired. Will login with credentials...")
                    session_path.unlink()  # Delete expired session
                    return False

            except Exception as e:
                print(f"⚠️  Error loading session: {e}")
                print("Will login with credentials...")
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
            # Look for elements that only appear when logged in
            await self.page.wait_for_selector('svg[aria-label="Home"], a[href="/"]', timeout=5000)

            # Check if we're on login page
            current_url = self.page.url
            if 'login' in current_url:
                return False

            # Additional check: look for profile icon or navigation elements
            nav_elements = await self.page.query_selector('nav')
            return nav_elements is not None

        except:
            return False

    async def login_instagram(self):
        """Login to Instagram and save session"""
        print("🔐 Logging into Instagram...")
        await self.page.goto('https://www.instagram.com/')
        await asyncio.sleep(3)

        # Close cookie banner if present
        try:
            await self.page.click('button:has-text("Allow all cookies")', timeout=5000)
        except:
            pass

        # Fill in login credentials
        await asyncio.sleep(2)
        await self.page.fill('input[name="username"]', self.username)
        await self.page.fill('input[name="password"]', self.password)
        await self.page.click('button[type="submit"]')

        print("⏳ Waiting for login process...")
        await asyncio.sleep(5)

        # Close "Save Info" and other pop-ups
        try:
            await self.page.click('button:has-text("Not Now")', timeout=5000)
        except:
            pass

        try:
            await self.page.click('button:has-text("Not Now")', timeout=5000)
        except:
            pass

        # Save session after successful login
        print("💾 Saving session for future use...")
        await self.context.storage_state(path=self.session_file)

        print("✅ Successfully logged in and session saved!")

    async def get_profile_posts(self, profile_username, max_posts=10):
        """Get posts from profile"""
        print(f"\n🔍 Navigating to profile: {profile_username}...")
        await self.page.goto(f'https://www.instagram.com/{profile_username}/')
        await asyncio.sleep(4)

        posts_data = []

        # Scroll to get posts
        last_height = await self.page.evaluate('document.body.scrollHeight')

        while len(posts_data) < max_posts:
            # Find all posts
            posts = await self.page.query_selector_all('article a[href*="/p/"], article a[href*="/reel/"]')

            print(f"📊 Found posts: {len(posts)}")

            for post in posts[:max_posts]:
                if len(posts_data) >= max_posts:
                    break

                # Get post link
                post_url = await post.get_attribute('href')

                # Check if it's not a reel or video
                img = await post.query_selector('img')

                if img:
                    img_src = await img.get_attribute('src')

                    # Skip if SVG icon present (reel/video icon)
                    parent = await post.query_selector('..')
                    svg_elements = await parent.query_selector_all('svg[aria-label*="Clip"], svg[aria-label*="Reel"], svg[aria-label*="Video"], svg[aria-label*="Клип"]')

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

    async def download_image(self, image_url, index):
        """Download image"""
        try:
            # Create images directory
            os.makedirs('images', exist_ok=True)

            # Open image in new tab and download
            image_page = await self.context.new_page()
            await image_page.goto(image_url)
            await asyncio.sleep(1)

            # Take screenshot
            image_path = f'images/post_{index}.jpg'
            await image_page.screenshot(path=image_path)
            await image_page.close()

            return image_path
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return None

    def analyze_image_with_gpt(self, image_path):
        """Analyze image using GPT"""
        try:
            # Convert image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Send request to GPT
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

            # Parse answer
            if 'YES' in answer or 'WEARING' in answer:
                return 'WEARING'
            else:
                return 'NOT WEARING'

        except Exception as e:
            print(f"❌ GPT analysis error: {e}")
            return 'ERROR'

    async def run(self, target_username, max_posts=10):
        """Main program"""
        try:
            # Initialize browser and check session
            session_valid = await self.init_browser()

            # Login if session is not valid
            if not session_valid:
                await self.login_instagram()

            # Get posts
            posts = await self.get_profile_posts(target_username, max_posts)

            print(f"\n{'='*60}")
            print(f"📷 Found {len(posts)} images. Analyzing...")
            print(f"{'='*60}\n")

            # Analyze each image
            for idx, post in enumerate(posts, 1):
                print(f"\n[{idx}/{len(posts)}] 🔍 Analyzing post...")
                print(f"  🔗 URL: {post['url']}")

                # Download image
                image_path = await self.download_image(post['image_url'], idx)

                if image_path:
                    # Analyze with GPT
                    result = self.analyze_image_with_gpt(image_path)

                    self.results.append({
                        'post_number': idx,
                        'post_url': post['url'],
                        'image_path': image_path,
                        'has_swimsuit': result
                    })

                    print(f"  ✅ Result: {result}")
                else:
                    print(f"  ❌ Failed to download image")

            # Final results
            print(f"\n{'='*60}")
            print("📊 FINAL RESULTS")
            print(f"{'='*60}")

            swimsuit_count = sum(1 for r in self.results if r['has_swimsuit'] == 'WEARING')

            for result in self.results:
                print(f"\n📌 Post #{result['post_number']}")
                print(f"  🔗 URL: {result['post_url']}")
                print(f"  👙 Swimsuit: {result['has_swimsuit']}")

            print(f"\n{'='*60}")
            print(f"📊 Total analyzed: {len(self.results)} images")
            print(f"👙 Swimsuit found: {swimsuit_count}")
            print(f"👔 No swimsuit: {len(self.results) - swimsuit_count}")
            print(f"{'='*60}")

            # Save to JSON file
            with open('results.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)

            print("\n💾 Results saved to 'results.json'!")

        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()


async def main():
    """Main function"""
    # Get credentials from .env file
    instagram_username = os.getenv('INSTAGRAM_USERNAME')
    instagram_password = os.getenv('INSTAGRAM_PASSWORD')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    target_username = os.getenv('TARGET_INSTAGRAM_USERNAME', 'boitumar_osh')  # Default value

    if not all([instagram_username, instagram_password, openai_api_key]):
        print("❌ ERROR: Missing required variables in .env file!")
        print("Required variables:")
        print("  - INSTAGRAM_USERNAME")
        print("  - INSTAGRAM_PASSWORD")
        print("  - OPENAI_API_KEY")
        print("  - TARGET_INSTAGRAM_USERNAME (optional)")
        return

    detector = InstagramSwimsuitDetector(
        username=instagram_username,
        password=instagram_password,
        openai_api_key=openai_api_key
    )

    # Analyze 10 posts
    await detector.run(target_username, max_posts=10)


if __name__ == "__main__":
    asyncio.run(main())
