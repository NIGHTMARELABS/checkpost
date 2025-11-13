"""
Instagram Swimsuit Detector
Bu dastur Instagram'dan postlarni olib, rasmlarni GPT orqali tahlil qilib,
suzish kiyimi borligini aniqlaydi.
"""

import os
import time
import asyncio
import base64
from pathlib import Path
from playwright.async_api import async_playwright
from openai import OpenAI
from dotenv import load_dotenv
import json

# .env fayldan o'qish
load_dotenv()


class InstagramSwimsuitDetector:
    def __init__(self, username, password, openai_api_key):
        self.username = username
        self.password = password
        self.client = OpenAI(api_key=openai_api_key)
        self.browser = None
        self.page = None
        self.results = []

    async def init_browser(self):
        """Browserni ishga tushirish"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Ko'rish uchun False qilgan
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.page = await self.browser.new_page()
        # User agent o'rnatish
        await self.page.set_viewport_size({"width": 1280, "height": 720})

    async def login_instagram(self):
        """Instagram'ga kirish"""
        print("Instagram'ga kirilmoqda...")
        await self.page.goto('https://www.instagram.com/')
        await asyncio.sleep(3)

        # Cookie banner yopish (agar bo'lsa)
        try:
            await self.page.click('button:has-text("Allow all cookies")', timeout=5000)
        except:
            pass

        # Login ma'lumotlarini kiritish
        await asyncio.sleep(2)
        await self.page.fill('input[name="username"]', self.username)
        await self.page.fill('input[name="password"]', self.password)
        await self.page.click('button[type="submit"]')

        print("Kirish jarayoni kutilmoqda...")
        await asyncio.sleep(5)

        # "Save Info" va boshqa pop-uplarni yopish
        try:
            await self.page.click('button:has-text("Not Now")', timeout=5000)
        except:
            pass

        try:
            await self.page.click('button:has-text("Not Now")', timeout=5000)
        except:
            pass

        print("Muvaffaqiyatli kirildi!")

    async def get_profile_posts(self, profile_username, max_posts=10):
        """Profil postlarini olish"""
        print(f"\n{profile_username} profiliga o'tilmoqda...")
        await self.page.goto(f'https://www.instagram.com/{profile_username}/')
        await asyncio.sleep(4)

        posts_data = []

        # Postlarni scroll qilib olish
        last_height = await self.page.evaluate('document.body.scrollHeight')

        while len(posts_data) < max_posts:
            # Barcha postlarni topish
            posts = await self.page.query_selector_all('article a[href*="/p/"], article a[href*="/reel/"]')

            print(f"Topilgan postlar: {len(posts)}")

            for post in posts[:max_posts]:
                if len(posts_data) >= max_posts:
                    break

                # Post linkini olish
                post_url = await post.get_attribute('href')

                # Reel yoki video emasligini tekshirish
                # IMG tagini topish
                img = await post.query_selector('img')

                if img:
                    img_src = await img.get_attribute('src')

                    # SVG icon bo'lsa o'tkazib yuborish (reel/video icon)
                    parent = await post.query_selector('..')
                    svg_elements = await parent.query_selector_all('svg[aria-label*="Клип"], svg[aria-label*="Reel"], svg[aria-label*="Video"]')

                    is_video = len(svg_elements) > 0

                    if not is_video and img_src and 'http' in img_src:
                        posts_data.append({
                            'url': 'https://www.instagram.com' + post_url if not post_url.startswith('http') else post_url,
                            'image_url': img_src
                        })
                        print(f"  ✓ Rasm topildi: {len(posts_data)}/{max_posts}")
                    elif is_video:
                        print(f"  ✗ Video o'tkazib yuborildi")

            # Scroll qilish
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)

            new_height = await self.page.evaluate('document.body.scrollHeight')
            if new_height == last_height and len(posts_data) >= 3:
                break
            last_height = new_height

        return posts_data[:max_posts]

    async def download_image(self, image_url, index):
        """Rasmni yuklab olish"""
        try:
            # Rasm papkasini yaratish
            os.makedirs('images', exist_ok=True)

            # Rasmni yangi tabda ochish va yuklab olish
            image_page = await self.browser.new_page()
            await image_page.goto(image_url)
            await asyncio.sleep(1)

            # Screenshot olish
            image_path = f'images/post_{index}.jpg'
            await image_page.screenshot(path=image_path)
            await image_page.close()

            return image_path
        except Exception as e:
            print(f"Rasmni yuklab olishda xatolik: {e}")
            return None

    def analyze_image_with_gpt(self, image_path):
        """GPT orqali rasmni tahlil qilish"""
        try:
            # Rasmni base64 ga o'girish
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # GPT ga so'rov yuborish
            response = self.client.chat.completions.create(
                model="gpt-4o",  # yoki gpt-4-vision-preview
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Bu rasmda odam suzish kiyimi (bikini, mayo, swim suit) kiyganmi? Faqat 'HA' yoki 'YO'Q' deb javob bering. Agar rasmda odam bo'lmasa ham 'YO'Q' deb javob bering."
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

            # Javobni aniqroq qilish
            if 'HA' in answer or 'YES' in answer or 'KIYGAN' in answer:
                return 'KIYGAN'
            else:
                return 'KIYMAGAN'

        except Exception as e:
            print(f"GPT tahlilida xatolik: {e}")
            return 'XATOLIK'

    async def run(self, target_username, max_posts=10):
        """Asosiy dastur"""
        try:
            await self.init_browser()
            await self.login_instagram()

            # Postlarni olish
            posts = await self.get_profile_posts(target_username, max_posts)

            print(f"\n{'='*60}")
            print(f"Jami {len(posts)} ta rasm topildi. Tahlil qilinmoqda...")
            print(f"{'='*60}\n")

            # Har bir rasmni tahlil qilish
            for idx, post in enumerate(posts, 1):
                print(f"\n[{idx}/{len(posts)}] Post tahlil qilinmoqda...")
                print(f"  URL: {post['url']}")

                # Rasmni yuklab olish
                image_path = await self.download_image(post['image_url'], idx)

                if image_path:
                    # GPT orqali tahlil qilish
                    result = self.analyze_image_with_gpt(image_path)

                    self.results.append({
                        'post_number': idx,
                        'post_url': post['url'],
                        'image_path': image_path,
                        'has_swimsuit': result
                    })

                    print(f"  ✓ Natija: {result}")
                else:
                    print(f"  ✗ Rasmni yuklab bo'lmadi")

            # Yakuniy natijalar
            print(f"\n{'='*60}")
            print("YAKUNIY NATIJALAR")
            print(f"{'='*60}")

            swimsuit_count = sum(1 for r in self.results if r['has_swimsuit'] == 'KIYGAN')

            for result in self.results:
                print(f"\nPost #{result['post_number']}")
                print(f"  URL: {result['post_url']}")
                print(f"  Suzish kiyimi: {result['has_swimsuit']}")

            print(f"\n{'='*60}")
            print(f"Jami tahlil qilingan: {len(self.results)} ta rasm")
            print(f"Suzish kiyimi topilgan: {swimsuit_count} ta")
            print(f"Suzish kiyimi topilmagan: {len(self.results) - swimsuit_count} ta")
            print(f"{'='*60}")

            # JSON faylga saqlash
            with open('results.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)

            print("\nNatijalar 'results.json' faylga saqlandi!")

        finally:
            if self.browser:
                await self.browser.close()


async def main():
    """Asosiy funksiya"""
    # .env fayldan ma'lumotlarni olish
    instagram_username = os.getenv('INSTAGRAM_USERNAME')
    instagram_password = os.getenv('INSTAGRAM_PASSWORD')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    target_username = os.getenv('TARGET_INSTAGRAM_USERNAME', 'boitumar_osh')  # Default qiymat

    if not all([instagram_username, instagram_password, openai_api_key]):
        print("XATOLIK: .env faylda barcha kerakli ma'lumotlar yo'q!")
        print("Kerakli o'zgaruvchilar:")
        print("  - INSTAGRAM_USERNAME")
        print("  - INSTAGRAM_PASSWORD")
        print("  - OPENAI_API_KEY")
        print("  - TARGET_INSTAGRAM_USERNAME (ixtiyoriy)")
        return

    detector = InstagramSwimsuitDetector(
        username=instagram_username,
        password=instagram_password,
        openai_api_key=openai_api_key
    )

    # 10 ta post tahlil qilish
    await detector.run(target_username, max_posts=10)


if __name__ == "__main__":
    asyncio.run(main())
