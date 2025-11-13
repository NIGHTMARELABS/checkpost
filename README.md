# Instagram Swimsuit Detector 👙

This program scrapes Instagram profiles, downloads images from posts, and uses OpenAI GPT-4 Vision to detect whether people are wearing swimsuits (bikini, swimsuit, bathing suit).

## ✨ Features

- ✅ **Session Management** - Login once, reuse session on next runs
- ✅ **Batch Mode** - Process multiple profiles automatically from a list
- ✅ **Automated Instagram Login** - Uses Playwright for full browser automation
- ✅ **Smart Post Scraping** - Automatically scrolls and collects posts
- ✅ **Video Filtering** - Detects and skips videos (only processes images)
- ✅ **AI Image Analysis** - Uses OpenAI GPT-4 Vision for accurate detection
- ✅ **Result Export** - Saves results to JSON file
- ✅ **Image Archive** - Downloads and saves all analyzed images

## 🔄 Session Management

The program automatically saves your Instagram login session after the first successful login:
- **First run**: Logs in with username/password and saves session to `instagram_session.json`
- **Subsequent runs**: Reuses saved session (no login required)
- **Auto-cleanup**: Detects expired sessions and automatically re-logins

This means you only need to login once! 🎉

## 📋 Requirements

- Python 3.8+
- Instagram account
- OpenAI API key (with GPT-4 Vision access)

## 🚀 Installation

1. **Clone or download this repository**

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install required packages:**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers:**
```bash
playwright install chromium
```

5. **Create `.env` file:**
```bash
cp .env.example .env
```

6. **Edit `.env` file with your credentials:**
```env
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
TARGET_INSTAGRAM_USERNAME=profile_to_analyze
```

## 💻 Usage

### Main Program (Recommended) ⭐

**One file with all features:**
```bash
python instagram_checker.py
```

Choose your mode:
- **Option 1**: Single Profile Mode - Analyze one profile
- **Option 2**: Batch Mode - Analyze multiple profiles from usernames.txt

### Alternative (Separate Scripts)

Single profile:
```bash
python instagram_swimsuit_detector.py
```

Batch mode:
```bash
python batch_checker.py
```

See [BATCH_MODE.md](BATCH_MODE.md) for detailed documentation.

### First Run
```
📭 No session file found. Will login with credentials...
🔐 Logging into Instagram...
⏳ Waiting for login process...
💾 Saving session for future use...
✅ Successfully logged in and session saved!
```

### Subsequent Runs
```
📂 Session file found. Loading saved session...
🔍 Verifying session validity...
✅ Session is valid! Already logged in.
```

## 📊 How It Works

1. **Session Check** - Looks for saved session, validates if still active
2. **Login (if needed)** - Logs in with credentials only if session expired
3. **Profile Navigation** - Goes to target Instagram profile
4. **Post Collection** - Scrolls through profile and collects posts
5. **Video Filtering** - Identifies and skips video posts (reels, videos)
6. **Image Download** - Downloads images from posts
7. **AI Analysis** - Sends each image to GPT-4 Vision for analysis
8. **Results** - Displays and saves results

## 📁 Output

The program generates:

### Terminal Output
```
📊 FINAL RESULTS
============================================================
📌 Post #1
  🔗 URL: https://instagram.com/p/xxxxx/
  👙 Swimsuit: WEARING

📌 Post #2
  🔗 URL: https://instagram.com/p/yyyyy/
  👙 Swimsuit: NOT WEARING

============================================================
📊 Total analyzed: 10 images
👙 Swimsuit found: 3
👔 No swimsuit: 7
============================================================
```

### Files Created
- `results.json` - Analysis results in JSON format
- `images/` - Directory with downloaded images
- `instagram_session.json` - Saved login session

### JSON Format
```json
[
  {
    "post_number": 1,
    "post_url": "https://instagram.com/p/xxxxx/",
    "image_path": "images/post_1.jpg",
    "has_swimsuit": "WEARING"
  },
  {
    "post_number": 2,
    "post_url": "https://instagram.com/p/yyyyy/",
    "image_path": "images/post_2.jpg",
    "has_swimsuit": "NOT WEARING"
  }
]
```

## ⚙️ Configuration

Edit `.env` file to change settings:

```env
# Instagram credentials (required)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# OpenAI API key (required)
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Target profile to analyze (optional, defaults to 'boitumar_osh')
TARGET_INSTAGRAM_USERNAME=username_to_analyze
```

## ⚠️ Important Notes

### Instagram Security
- Instagram has rate limits and bot detection
- Don't run the script too frequently to avoid being flagged
- If you have 2FA enabled, you may need to disable it temporarily
- Session files help reduce login frequency

### API Costs
- OpenAI GPT-4 Vision is a paid API
- Each image analysis costs money
- Typical cost: ~$0.01-0.03 per image
- Check OpenAI pricing for current rates

### Privacy & Security
- Keep your `.env` file secure (never commit to git)
- Session file contains authentication data (excluded from git)
- Only use this on accounts you own or have permission to scrape

## 🐛 Troubleshooting

### "Login failed"
- Check username/password in `.env`
- Disable 2FA on Instagram temporarily
- Instagram may be blocking automated logins (wait and try again)

### "Session expired"
- Normal behavior after some time
- Program will automatically detect and re-login
- Session files typically last 7-30 days

### "Too many requests"
- Instagram rate limit reached
- Wait 1-2 hours before running again
- Use session feature to reduce login frequency

### "OpenAI API error"
- Check your API key is correct
- Ensure you have GPT-4 Vision access
- Check your API usage limits and billing

### Videos not skipped properly
- Instagram changes their HTML structure frequently
- Script checks for video/reel icons
- May need updates if Instagram changes their layout

## 🔒 Security Best Practices

1. **Never commit sensitive files:**
   - `.env` (credentials)
   - `instagram_session.json` (session data)
   - These are in `.gitignore`

2. **Use strong passwords:**
   - Consider using a dedicated Instagram account

3. **Monitor API usage:**
   - Track OpenAI API costs
   - Set usage limits in OpenAI dashboard

## 📝 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Issues and pull requests welcome!

## 📧 Support

For issues, please check the Troubleshooting section first.

---

**Disclaimer**: This tool is for educational and research purposes. Always comply with Instagram's Terms of Service and respect user privacy. Use responsibly and ethically.
