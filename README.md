# Card Grader Pro

AI-powered trading card grading and valuation tool for Pokemon, sports cards, and other collectibles.

## Features

- **AI Visual Analysis**: Uses OpenAI GPT-4o Vision to analyze card condition
- **Multi-Service Grading**: Provides estimates for PSA, CGC, and TAG grading scales
- **Value Assessment**: Cross-references pricing data for market valuations
- **Grading Recommendations**: Advises whether cards are worth professional grading
- **Mobile-First Design**: Optimized for iPhone camera uploads and mobile use

## How It Works

1. Upload clear photos of your card's front and back
2. AI analyzes the card against professional grading criteria:
   - **Centering**: Image alignment within borders
   - **Corners**: Sharpness and wear assessment
   - **Edges**: Whitening, chipping, roughness evaluation
   - **Surface**: Scratches, print defects, staining analysis
3. Receive grading estimates for PSA, CGC, and TAG (1-10 scale)
4. View market value estimates at different grade levels
5. Get recommendation on whether grading is financially worthwhile

## Tech Stack

- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Backend**: Python (Flask/FastAPI) on Vercel serverless functions
- **AI Vision**: OpenAI GPT-4o Vision API
- **Hosting**: Vercel (free tier)
- **Mobile**: Native camera integration for iOS/Android

## Deployment

### Prerequisites
- Vercel account connected to GitHub
- OpenAI API key with GPT-4o Vision access

### Environment Variables (Vercel)
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Deploy Steps
1. Push code to GitHub repository
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy automatically triggers on push to main branch

## Usage Instructions

### For Testing
1. Visit the deployed app URL
2. Tap "Click to upload front photo" and take/select card front image
3. Tap "Click to upload back photo" and take/select card back image  
4. Tap "Analyze Card" button
5. Wait for AI analysis (usually 10-30 seconds)
6. Review grading estimates, value projections, and recommendations

### Camera Tips
- Use good lighting (natural light preferred)
- Keep card flat and fully in frame
- Avoid shadows, glare, or reflections
- Ensure all text and details are clearly visible
- Hold camera steady for sharp focus

## Grading Scale Reference

### PSA Scale (1-10)
- **10 GEM-MT**: Perfect card, investment grade
- **9 MINT**: Minor flaws barely visible under magnification  
- **8 NM-MT**: Minor flaws visible under scrutiny
- **7 NM**: Slight surface wear, minor corner/edge wear
- **6 EX-MT**: Light wear, corners may show slight rounding
- **5 EX**: Moderate wear, corners show rounding
- **4 VG-EX**: Obvious wear, corners well rounded
- **3 VG**: Heavy wear, significant corner rounding
- **2 GOOD**: Severe wear, possible creases
- **1 POOR**: Major damage, heavily worn

### CGC Scale
Generally stricter than PSA, especially for higher grades.

### TAG Scale  
Similar to PSA but may vary on specific criteria.

## Important Notes

- **Estimates Only**: Results are AI-powered estimates, not official grades
- **Professional Grading**: Only official services provide certified grades
- **Market Fluctuations**: Values change based on market conditions
- **Prototype**: This is a testing prototype for evaluation purposes

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires vercel CLI)
vercel dev
```

### API Endpoints
- `POST /api/analyze` - Analyze card images
  - Form data: `front_image`, `back_image` (image files)
  - Returns: JSON with grading analysis and recommendations

## Created For
Andy Lihani (Philly) - Card grading evaluation prototype
Approved by: Matt Mirick
Built by: Manny (AI Assistant)

## Contact
For questions or issues with this prototype, contact the development team.