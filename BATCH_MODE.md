# Batch Mode - Process Multiple Profiles 🚀

This guide explains how to use the **batch checker** to analyze multiple Instagram profiles automatically.

## 📋 What is Batch Mode?

Batch mode allows you to:
- ✅ Analyze multiple Instagram profiles in one run
- ✅ Process usernames from a list file
- ✅ Get individual results for each profile
- ✅ Generate a comprehensive summary report
- ✅ Reuse login session across all profiles

## 🚀 Quick Start

### 1. Prepare Username List

Create or edit `usernames.txt` with one username per line:

```
MarcelaVelozo
IsabelleMathersx
CallanJensen
ElleTrowbridge
```

### 2. Configure Settings

Edit your `.env` file:

```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
MAX_POSTS_PER_PROFILE=10
USERNAMES_FILE=usernames.txt
```

### 3. Run Batch Mode

```bash
python batch_checker.py
```

## 📊 How It Works

```
1. Load username list from file
2. Login to Instagram once (or use saved session)
3. For each profile:
   - Navigate to profile
   - Collect posts (skip videos)
   - Download images
   - Analyze with GPT
   - Save individual results
4. Generate batch summary
5. Display final statistics
```

## 📁 Output Structure

After running batch mode, you'll get:

```
batch_results/
├── MarcelaVelozo_results.json      # Individual profile results
├── IsabelleMathersx_results.json
├── CallanJensen_results.json
└── batch_summary_20250113_143022.json  # Overall summary

images/
├── MarcelaVelozo_1.jpg
├── MarcelaVelozo_2.jpg
├── IsabelleMathersx_1.jpg
└── ...
```

## 📄 Result Format

### Individual Profile Result
```json
{
  "username": "MarcelaVelozo",
  "status": "success",
  "total_posts": 10,
  "swimsuit_count": 3,
  "results": [
    {
      "post_number": 1,
      "post_url": "https://instagram.com/p/xxxxx/",
      "image_path": "images/MarcelaVelozo_1.jpg",
      "has_swimsuit": "WEARING"
    }
  ]
}
```

### Batch Summary
```json
{
  "timestamp": "2025-01-13T14:30:22",
  "total_profiles": 28,
  "successful": 25,
  "failed": 2,
  "no_images": 1,
  "total_posts_analyzed": 250,
  "total_swimsuit_found": 45,
  "profiles": [...]
}
```

## 💻 Sample Output

```
╔══════════════════════════════════════════════════════════════════╗
║   Instagram Swimsuit Detector - BATCH MODE                      ║
║   Process multiple profiles automatically                        ║
╚══════════════════════════════════════════════════════════════════╝

🚀 BATCH MODE: Processing 28 profiles
📝 Posts per profile: 10
======================================================================

📂 Session file found. Loading saved session...
🔍 Verifying session validity...
✅ Session is valid! Already logged in.

======================================================================
🔍 Processing profile [1/28]: @MarcelaVelozo
======================================================================

🔍 Navigating to profile: MarcelaVelozo...
📊 Found posts: 45
  ✅ Image found: 1/10
  ✅ Image found: 2/10
  ...
📷 Found 10 images. Analyzing...

  [1/10] 🔍 Analyzing post...
    ✅ Result: WEARING
  [2/10] 🔍 Analyzing post...
    ✅ Result: NOT WEARING
  ...

📊 Profile Summary:
  Total analyzed: 10
  👙 Swimsuit found: 3
  👔 No swimsuit: 7

💾 Saved results to: batch_results/MarcelaVelozo_results.json

⏸️  Waiting 5 seconds before next profile...

======================================================================
🔍 Processing profile [2/28]: @IsabelleMathersx
======================================================================
...

======================================================================
🎉 BATCH PROCESSING COMPLETED!
======================================================================

📊 Overall Statistics:
  Total profiles processed: 28
  ✅ Successful: 25
  ❌ Failed: 2
  ⚠️  No images: 1
  📷 Total posts analyzed: 250
  👙 Total swimsuit found: 45

📋 Profile Results:
  ✅ @MarcelaVelozo: 10 posts, 3 with swimsuit
  ✅ @IsabelleMathersx: 10 posts, 5 with swimsuit
  ✅ @CallanJensen: 10 posts, 0 with swimsuit
  ...

📁 Results saved in: batch_results/
======================================================================
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `INSTAGRAM_USERNAME` | Your Instagram username | (required) |
| `INSTAGRAM_PASSWORD` | Your Instagram password | (required) |
| `OPENAI_API_KEY` | OpenAI API key | (required) |
| `MAX_POSTS_PER_PROFILE` | Posts to analyze per profile | 10 |
| `USERNAMES_FILE` | Path to username list file | usernames.txt |

### Customize Posts Per Profile

To analyze more or fewer posts per profile:

```env
MAX_POSTS_PER_PROFILE=20  # Analyze 20 posts per profile
```

### Use Different Username File

```env
USERNAMES_FILE=my_custom_list.txt
```

## ⏱️ Timing Estimates

**Processing time per profile:** ~2-5 minutes (10 posts)
- Navigate to profile: ~5 seconds
- Find images (scroll): ~10-20 seconds
- Download images: ~10 seconds (10 images)
- GPT analysis: ~10-30 seconds (10 images)

**For 28 profiles:**
- Minimum: ~56 minutes
- Average: ~90 minutes
- Maximum: ~140 minutes

**Note:** Includes 5-second delays between profiles to avoid rate limits.

## 💡 Tips for Batch Processing

### 1. Use Session Management
- Login once at the start
- Session persists across all profiles
- Saves time and reduces rate limit risk

### 2. Start with a Small Test
Test with 2-3 profiles first:
```bash
# Create test list
echo "MarcelaVelozo" > test_usernames.txt
echo "IsabelleMathersx" >> test_usernames.txt

# Update .env
USERNAMES_FILE=test_usernames.txt

# Run
python batch_checker.py
```

### 3. Monitor Progress
- Watch terminal output for errors
- Check `batch_results/` folder for saved files
- Look for failed profiles in summary

### 4. Handle Failures
If some profiles fail:
1. Check error message in terminal
2. Review individual result files
3. Create new list with only failed profiles
4. Re-run batch mode

### 5. Avoid Rate Limits
- Don't process too many profiles at once
- 5-second delay between profiles (built-in)
- Spread large batches across multiple days
- Use session management to reduce logins

## ⚠️ Important Notes

### Instagram Rate Limits
- Instagram may block if too many requests
- Recommended: Max 50-100 profiles per day
- Wait 1-2 hours if you see "Too many requests"

### API Costs
- OpenAI charges per image analyzed
- 28 profiles × 10 posts = 280 images
- Estimated cost: $2.80 - $8.40 (at $0.01-0.03/image)
- Check your OpenAI usage dashboard

### Privacy & Ethics
- Only analyze public profiles
- Respect Instagram Terms of Service
- Don't harass or stalk users
- Use for legitimate purposes only

## 🐛 Troubleshooting

### "Error loading session"
- Delete `instagram_session.json`
- Restart batch mode (will re-login)

### "Profile not found"
- Check username spelling in `usernames.txt`
- Verify profile is public
- Profile may be deleted/suspended

### "No images found"
- Profile has no posts
- All posts are videos/reels
- Posts are not accessible

### High API costs
- Reduce `MAX_POSTS_PER_PROFILE`
- Process fewer profiles
- Monitor OpenAI dashboard

## 📝 Example Use Cases

### Fashion Brand Monitoring
Monitor competitor swimwear posts:
```
# competitors.txt
CompetitorBrand1
CompetitorBrand2
CompetitorBrand3
```

### Influencer Analysis
Analyze influencer swimsuit content:
```
# influencers.txt
FashionInfluencer1
FashionInfluencer2
BeachLifestyleBlogger
```

### Market Research
Research swimwear trends:
```
# research_profiles.txt
SwimwearDesigner1
BeachFashionHub
SummerStyleGuide
```

## 🔧 Advanced Usage

### Custom Delay Between Profiles

Edit `batch_checker.py`:
```python
# Change from 5 seconds to 10 seconds
await asyncio.sleep(10)  # Line ~XX
```

### Filter by Swimsuit Count

Process results to find profiles with most swimsuit posts:
```python
import json

# Load batch summary
with open('batch_results/batch_summary_XXXXXX.json') as f:
    data = json.load(f)

# Sort by swimsuit count
profiles = sorted(data['profiles'],
                 key=lambda x: x['swimsuit_count'],
                 reverse=True)

# Top 5 profiles with most swimsuit posts
for p in profiles[:5]:
    print(f"{p['username']}: {p['swimsuit_count']} swimsuit posts")
```

## 📊 Export Results to CSV

Create a simple CSV export script:
```python
import json
import csv

with open('batch_results/batch_summary_XXXXXX.json') as f:
    data = json.load(f)

with open('results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Username', 'Total Posts', 'Swimsuit Count', 'Percentage'])

    for p in data['profiles']:
        if p['status'] == 'success':
            percentage = (p['swimsuit_count'] / p['total_posts'] * 100) if p['total_posts'] > 0 else 0
            writer.writerow([
                p['username'],
                p['total_posts'],
                p['swimsuit_count'],
                f"{percentage:.1f}%"
            ])
```

---

**Need help?** Check the main README.md or open an issue on GitHub!
