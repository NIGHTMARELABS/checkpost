# Instagram Suzish Kiyimi Aniqlagich

Bu dastur Instagram profilidan postlarni olib, rasmlarni OpenAI GPT orqali tahlil qilib, odamda suzish kiyimi (bikini, mayo) borligini aniqlaydi.

## Xususiyatlari

- ✅ Playwright orqali Instagram'ga kirish
- ✅ Profil postlarini avtomatik scroll qilib olish
- ✅ Faqat rasmli postlarni olish (videolarni o'tkazib yuboradi)
- ✅ OpenAI GPT-4 Vision orqali rasmlarni tahlil qilish
- ✅ Suzish kiyimi borligini aniqlash
- ✅ Natijalarni JSON faylga saqlash

## O'rnatish

1. Repository'ni clone qiling yoki yuklab oling

2. Virtual environment yarating va faollashtiring:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

3. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

4. Playwright browserlarni o'rnating:
```bash
playwright install chromium
```

5. `.env` faylni yarating va to'ldiring:
```bash
cp .env.example .env
```

`.env` faylni tahrirlab, o'z ma'lumotlaringizni kiriting:
```env
INSTAGRAM_USERNAME=sizning_username
INSTAGRAM_PASSWORD=sizning_parol
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
TARGET_INSTAGRAM_USERNAME=tahlil_qilinadigan_profil
```

## Ishlatish

Dasturni ishga tushiring:
```bash
python instagram_swimsuit_detector.py
```

## Natijalar

Dastur:
1. Instagram'ga kirib, ko'rsatilgan profilga o'tadi
2. 10 ta rasmli postni topadi (videolarni o'tkazib yuboradi)
3. Har bir rasmni GPT orqali tahlil qiladi
4. Natijalarni terminalda ko'rsatadi
5. Natijalarni `results.json` faylga saqlaydi
6. Rasmlarni `images/` papkaga yuklab qo'yadi

## Natija formati

```json
[
  {
    "post_number": 1,
    "post_url": "https://instagram.com/p/xxxxx/",
    "image_path": "images/post_1.jpg",
    "has_swimsuit": "KIYGAN"
  }
]
```

## Talablar

- Python 3.8+
- Instagram hisobi
- OpenAI API key (GPT-4 Vision kirish)

## Muhim eslatmalar

⚠️ **Instagram xavfsizligi**: Instagram'ning rate limit va bot detection xususiyatlariga e'tibor bering. Juda tez-tez so'rov yubormaslik tavsiya etiladi.

⚠️ **API xarajatlari**: OpenAI GPT-4 VisionAPIsi pullik. Har bir rasm tahlili uchun haq to'lanadi.

⚠️ **Maxfiylik**: Login ma'lumotlaringizni xavfsiz saqlang va `.env` faylni git'ga qo'shmang.

## Muammolarni hal qilish

**"Login failed"**: Instagram parol yoki username noto'g'ri. Yoki Instagram 2FA yoqilgan bo'lsa, uni o'chirib ko'ring.

**"Too many requests"**: Instagram sizni bloklagan. Bir oz kutib qaytadan urinib ko'ring.

**"OpenAI API error"**: API key noto'g'ri yoki limitga yetgan.

## Litsenziya

MIT License

## Muallif

Dastur AI yordamida yaratilgan.
