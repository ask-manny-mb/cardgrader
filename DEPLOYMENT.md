# Deployment Instructions

## Card Grader Pro - Vercel Deployment

### Manual Deployment Steps

Since automated deployment requires interactive login, please complete these steps manually:

#### 1. Connect GitHub Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import from GitHub: `ask-manny-mb/cardgrader`
4. Configure project settings:
   - Framework Preset: **Other**
   - Root Directory: `./` (default)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

#### 2. Set Environment Variables

In the Vercel project settings, add these environment variables:

```
OPENAI_API_KEY=your_openai_api_key_from_credentials_file
```

**Note:** Use the OpenAI API key from `~/.openclaw/credentials/api_keys.json` under the "openai" field.

#### 3. Deploy

1. Click "Deploy" in Vercel
2. Wait for build to complete
3. Test the deployment URL

#### 4. Test the Application

Once deployed:

1. Visit the Vercel-provided URL
2. Test with sample card images:
   - Upload front and back photos
   - Click "Analyze Card"
   - Verify AI analysis works
   - Check mobile camera integration on iPhone

### Expected Deployment URL Format

```
https://cardgrader-[random-hash].vercel.app
```

### Troubleshooting

**If deployment fails:**

1. Check Vercel function logs for Python errors
2. Verify OpenAI API key is correctly set
3. Ensure requirements.txt includes all dependencies
4. Check vercel.json configuration

**If API calls fail:**

1. Verify OpenAI API key in environment variables
2. Check OpenAI account has GPT-4o Vision access
3. Monitor API usage and rate limits

**If mobile camera doesn't work:**

1. Ensure HTTPS deployment (required for camera API)
2. Test on multiple devices/browsers
3. Check console for JavaScript errors

### Production Considerations

**Before sharing with Philly:**

1. Test thoroughly on iPhone Safari
2. Verify all grading criteria work correctly
3. Test with various card types (Pokemon, sports, etc.)
4. Ensure error handling works for invalid images

**Future Improvements:**

1. Add real pricing API integration (PriceCharting, eBay)
2. Improve card identification accuracy
3. Add more grading services (BGS, etc.)
4. Implement user feedback collection