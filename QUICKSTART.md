# Quick Start Guide 🚀

Get started in 3 minutes!

## Step 1: Setup Environment ⚙️

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

## Step 2: Configure Credentials 🔐

**Option A: Quick Setup (Recommended)**
```bash
python setup.py
```
Follow the prompts to enter your credentials.

**Option B: Manual Setup**
```bash
cp .env.example .env
```
Then edit `.env` file:
```env
INSTAGRAM_USERNAME=notnightmarelabs1
INSTAGRAM_PASSWORD=YOUR_PASSWORD_HERE
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

⚠️ **SECURITY WARNING**: Change your Instagram password after testing! The password you shared earlier is now public.

## Step 3: Run the Program 🎯

### Single Profile Mode
Analyze one profile:
```bash
python instagram_swimsuit_detector.py
```

### Batch Mode (Your 28 Profiles)
Process all profiles from `usernames.txt`:
```bash
python batch_checker.py
```

## What Happens Next? 📊

### First Run
1. Browser opens (you'll see it)
2. Logs into Instagram
3. Saves session for future use
4. Processes profiles one by one
5. Downloads images
6. Analyzes with GPT
7. Saves results

### Estimated Time
- **28 profiles × 10 posts = 280 images**
- **Time:** ~90-120 minutes total
- **Cost:** ~$2.80-$8.40 (OpenAI API)

### Output Files
```
batch_results/
├── MarcelaVelozo_results.json
├── IsabelleMathersx_results.json
├── ... (one file per profile)
└── batch_summary_TIMESTAMP.json

images/
├── MarcelaVelozo_1.jpg
├── MarcelaVelozo_2.jpg
└── ... (all downloaded images)

instagram_session.json  (saved login session)
```

## Understanding Results 📈

### Profile Result Example
```json
{
  "username": "MarcelaVelozo",
  "total_posts": 10,
  "swimsuit_count": 3,
  "results": [
    {
      "post_number": 1,
      "has_swimsuit": "WEARING"
    }
  ]
}
```

### Summary Statistics
At the end, you'll see:
- ✅ How many profiles processed successfully
- ❌ How many failed
- 📷 Total posts analyzed
- 👙 Total swimsuits found

## Tips 💡

1. **Start Small** - Test with 2-3 profiles first:
   ```bash
   # Create test file
   echo "MarcelaVelozo" > test.txt
   echo "IsabelleMathersx" >> test.txt

   # Update .env
   USERNAMES_FILE=test.txt

   # Run
   python batch_checker.py
   ```

2. **Monitor Progress** - Watch the terminal output to track progress

3. **Check Results** - Look in `batch_results/` folder as profiles complete

4. **Session Reuse** - Next time you run it, you won't need to login again!

## Troubleshooting 🔧

### "Login failed"
- Check username/password in `.env`
- Make sure 2FA is disabled on Instagram

### "OpenAI API error"
- Verify API key is correct
- Check you have credits/billing set up
- Ensure GPT-4 Vision access

### "Too many requests"
- Instagram rate limit hit
- Wait 1-2 hours and try again
- Batch mode includes delays to help prevent this

### "No images found"
- Profile might have only videos/reels
- Profile might be private
- Check username spelling

## Your Profile List 📋

You have **28 profiles** ready to analyze:

```
✅ MarcelaVelozo
✅ IsabelleMathersx
✅ CallanJensen
✅ ElleTrowbridge
✅ ErgiBardhollari
✅ JoseArnolds
✅ LenaPerminova
✅ LeneVoigt
✅ MashaDerevianko
✅ NanniIrene
✅ RavilaNogueira
✅ VictoriaTurnerr
✅ Whitney_Thornqvist
✅ AliceMarconcinii
✅ AriadnaFigueras
✅ Aylbhr
✅ CaraCoc0
✅ CarlotaEnsenat
✅ CaroGuido
✅ CaseyJamess_
✅ CathlinUlrichsen
✅ ClarissaSirica
✅ CorinneAndrich
✅ DaniWashington_
✅ DianaGali_
✅ Elisa_Matata
✅ Eliza.Musial
✅ ElsaMagnelli
```

All usernames are already in `usernames.txt`!

## Need More Help? 📚

- **Full documentation**: [README.md](README.md)
- **Batch mode guide**: [BATCH_MODE.md](BATCH_MODE.md)
- **Uzbek version**: [README_UZ.md](README_UZ.md)

## Commands Cheat Sheet 📝

```bash
# Quick setup
python setup.py

# Single profile
python instagram_swimsuit_detector.py

# Batch mode (all 28 profiles)
python batch_checker.py

# Check results
cat batch_results/batch_summary_*.json

# View specific profile
cat batch_results/MarcelaVelozo_results.json
```

---

🎉 **Ready to go!** Just run `python batch_checker.py` to start!

⚠️ **Remember**: Change your Instagram password after testing since you shared it publicly!
