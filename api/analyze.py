import json
import base64
import os
from typing import Dict, Any, Tuple
import requests
from io import BytesIO
from PIL import Image

def handler(request):
    """
    Vercel serverless function to analyze trading card images
    """
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Get OpenAI API key from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'OpenAI API key not configured'})
            }

        # Parse form data
        if hasattr(request, 'files'):
            front_image = request.files.get('front_image')
            back_image = request.files.get('back_image')
        else:
            # Handle JSON upload if files not available
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No images provided'})
            }

        if not front_image or not back_image:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Both front and back images required'})
            }

        # Convert images to base64
        front_b64 = encode_image_to_base64(front_image)
        back_b64 = encode_image_to_base64(back_image)

        # Analyze the card with OpenAI GPT-4o Vision
        analysis_result = analyze_card_with_ai(front_b64, back_b64, openai_api_key)
        
        # Get pricing data
        pricing_result = get_pricing_data(analysis_result['card_info'])
        
        # Combine results
        final_result = {
            'card_info': analysis_result['card_info'],
            'grading': analysis_result['grading'],
            'values': pricing_result,
            'recommendation': generate_recommendation(
                analysis_result['grading'],
                pricing_result,
                analysis_result['card_info']
            )
        }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(final_result)
        }

    except Exception as e:
        print(f"Error in analyze handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Analysis failed: {str(e)}'})
        }


def encode_image_to_base64(image_file) -> str:
    """Convert uploaded image to base64 string"""
    try:
        # Read image data
        if hasattr(image_file, 'read'):
            image_data = image_file.read()
        else:
            image_data = image_file
        
        # Convert to base64
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to encode image: {str(e)}")


def analyze_card_with_ai(front_b64: str, back_b64: str, api_key: str) -> Dict[str, Any]:
    """Analyze card images with OpenAI GPT-4o Vision"""
    
    grading_prompt = """
    You are an expert trading card grader with extensive knowledge of PSA, CGC, and TAG grading standards. 
    
    Analyze these front and back images of a trading card and provide detailed grading assessment.
    
    For each image, evaluate these criteria on a 1-10 scale:
    - CENTERING: How well centered the image is within borders (front and back)
    - CORNERS: Sharpness, whitening, dings (all four corners)  
    - EDGES: Whitening, chipping, roughness (all edges)
    - SURFACE: Scratches, print defects, staining, gloss loss
    
    Grading scale reference:
    - 10 (GEM-MT): Perfect card, investment grade
    - 9 (MINT): Minor flaws barely visible under magnification
    - 8 (NM-MT): Minor flaws visible under scrutiny
    - 7 (NM): Slight surface wear, minor corner/edge wear
    - 6 (EX-MT): Light wear, corners may show slight rounding
    - 5 (EX): Moderate wear, corners show rounding
    - 4 (VG-EX): Obvious wear, corners well rounded
    - 3 (VG): Heavy wear, significant corner rounding
    - 2 (GOOD): Severe wear, possible creases
    - 1 (POOR): Major damage, heavily worn

    Also identify the card details from the images.

    Respond with this EXACT JSON structure:
    {
        "card_info": {
            "name": "Card name",
            "set": "Set name",
            "year": "Year or N/A",
            "type": "Pokemon/Sports/etc",
            "rarity": "Rarity if visible"
        },
        "grading": {
            "psa": {
                "overall": 8,
                "centering": 9,
                "corners": 8,
                "edges": 8,
                "surface": 7
            },
            "cgc": {
                "overall": 7,
                "centering": 9,
                "corners": 7,
                "edges": 7,
                "surface": 7
            },
            "tag": {
                "overall": 8,
                "centering": 9,
                "corners": 8,
                "edges": 8,
                "surface": 7
            },
            "details": {
                "centering": "Detailed centering assessment",
                "corners": "Detailed corner assessment", 
                "edges": "Detailed edge assessment",
                "surface": "Detailed surface assessment"
            }
        }
    }
    """

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": grading_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{front_b64}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{back_b64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.1
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse JSON from response
        try:
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError:
            # Try to extract JSON if wrapped in markdown
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(1))
                return analysis
            else:
                raise Exception("Failed to parse AI response as JSON")

    except Exception as e:
        raise Exception(f"AI analysis failed: {str(e)}")


def get_pricing_data(card_info: Dict[str, Any]) -> Dict[str, Any]:
    """Get pricing data from various sources"""
    # This is a simplified pricing lookup - in production you'd integrate with real APIs
    # For now, return mock data based on card info
    
    card_name = card_info.get('name', 'Unknown Card')
    card_type = card_info.get('type', 'Unknown')
    
    # Mock pricing data based on card type and name
    base_price = estimate_base_price(card_name, card_type)
    
    return {
        'current_market': {
            'min': base_price * 0.8,
            'max': base_price * 1.2
        },
        'psa': {
            'grade': 8,
            'value': base_price * 2.5
        },
        'cgc': {
            'grade': 7,
            'value': base_price * 2.0
        },
        'tag': {
            'grade': 8,
            'value': base_price * 2.2
        }
    }


def estimate_base_price(card_name: str, card_type: str) -> float:
    """Estimate base price for a card"""
    # Simple heuristic pricing - replace with real API calls
    if 'charizard' in card_name.lower():
        return 150.0
    elif 'pikachu' in card_name.lower():
        return 50.0
    elif card_type.lower() in ['pokemon', 'pokémon']:
        return 25.0
    elif card_type.lower() in ['baseball', 'basketball', 'football']:
        return 30.0
    else:
        return 15.0


def generate_recommendation(grading: Dict, pricing: Dict, card_info: Dict) -> Dict[str, Any]:
    """Generate grading recommendation based on analysis"""
    
    # Get highest potential grade
    highest_grade = max(
        grading['psa']['overall'],
        grading['cgc']['overall'],
        grading['tag']['overall']
    )
    
    # Get current market value
    current_value = pricing['current_market']['max']
    
    # Get highest graded value
    graded_values = [pricing['psa']['value'], pricing['cgc']['value'], pricing['tag']['value']]
    highest_graded_value = max(graded_values)
    
    # Estimate grading cost (typical ranges)
    grading_cost = 20 if highest_grade >= 8 else 15
    
    # Calculate potential ROI
    potential_profit = highest_graded_value - current_value - grading_cost
    roi_percentage = (potential_profit / (current_value + grading_cost)) * 100
    
    # Determine if worth grading
    worth_grading = highest_grade >= 7 and potential_profit > 10
    
    # Recommend best service
    best_service = "PSA"
    if pricing['cgc']['value'] > pricing['psa']['value'] and pricing['cgc']['value'] > pricing['tag']['value']:
        best_service = "CGC"
    elif pricing['tag']['value'] > pricing['psa']['value'] and pricing['tag']['value'] > pricing['cgc']['value']:
        best_service = "TAG"
    
    # Generate reason
    if worth_grading:
        reason = f"Card shows strong potential with estimated {highest_grade}/10 grade. Projected profit of ${potential_profit:.0f} after grading costs."
    else:
        if highest_grade < 7:
            reason = f"Card condition (estimated {highest_grade}/10) may not justify grading costs. Consider keeping raw or improve condition first."
        else:
            reason = f"While card grades well ({highest_grade}/10), current market values don't provide strong ROI after grading costs."
    
    return {
        'worth_grading': worth_grading,
        'reason': reason,
        'best_service': best_service,
        'estimated_cost': f"{grading_cost}",
        'potential_roi': f"{roi_percentage:.0f}%" if roi_percentage > 0 else "Negative ROI"
    }