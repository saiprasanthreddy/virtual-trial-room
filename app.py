import base64
import os
import re
from flask import Flask, render_template, request, jsonify, send_file, Response
from google import genai
from google.genai import types
from google.genai.types import HarmBlockThreshold
from PIL import Image
from io import BytesIO
import tempfile
from dotenv import load_dotenv
import warnings
import io
import time
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store for progressive loading
generation_store = {}

def swap_clothing(person_image, clothing_image, size='M'):
    """
    Generate an image where the person from the first image is wearing clothing from the second image.
    
    Args:
        person_image: The image containing the person
        clothing_image: The image containing the clothing to swap
        size: Size of clothing - 'S' (tight fit), 'M' (normal fit), 'L' (loose fit)
    
    Returns:
        The generated image with the clothing swapped and any relevant messages
    """
    # Define size descriptions
    size_descriptions = {
        'S': 'small size with a tight, snug fit that closely follows the body contours',
        'M': 'medium size with a normal, comfortable fit',
        'L': 'large size with a loose, relaxed fit with extra room'
    }
    
    size_desc = size_descriptions.get(size, size_descriptions['M'])
    
    # Capture warnings in a string buffer
    warning_buffer = io.StringIO()
    warnings.filterwarnings('always')  # Ensure all warnings are shown
    
    # Initialize variables outside the try block
    temp_files = []
    uploaded_files = []
    client = None
    output_image = None
    output_text = ""
    
    with warnings.catch_warnings(record=True) as warning_list:
        try:
            # Check if both images are provided
            if person_image is None or clothing_image is None:
                return None, "Please upload both images."
            
            # Get API key from environment variables
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return None, "GEMINI_API_KEY not found in environment variables."
            
            # Create a fresh client instance for each request
            client = genai.Client(api_key=api_key)
            
            # Save both uploaded images to temporary files
            for img, prefix in [(person_image, "person"), (clothing_image, "clothing")]:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    img.save(temp_file.name)
                    temp_files.append(temp_file.name)
            
            # Upload both files to Gemini with fresh file uploads
            uploaded_files = [
                client.files.upload(file=temp_files[0]),  # person image
                client.files.upload(file=temp_files[1]),  # clothing image
            ]
            
            # Create the prompt with size specification
            prompt = f'''
                Edit the person's clothing by swapping it with the clothing in the clothing image.
                Retain the same face, facial features, pose and background from the person image.
                
                IMPORTANT - Size Specification:
                Apply the clothing in {size_desc}.
                The fit should be: {size_desc}.
                Adjust the clothing proportions, draping, and tightness to match this size specification.
                
                The output image should show the person wearing the new clothing with the specified fit.
                The image pose and background should remain the same as the person image.
            '''
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="This is the person image. Do not change the face or features of the person. Pay attention and retain the face, environment, background, pose, facial features."),
                        types.Part.from_uri(
                            file_uri=uploaded_files[0].uri,
                            mime_type=uploaded_files[0].mime_type,
                        ),
                        types.Part.from_text(text=f"This is the clothing image. Swap the clothing onto the person with {size_desc}."),
                        types.Part.from_uri(
                            file_uri=uploaded_files[1].uri,
                            mime_type=uploaded_files[1].mime_type,
                        ),
                        types.Part.from_text(text=prompt),
                        types.Part.from_uri(
                            file_uri=uploaded_files[0].uri,
                            mime_type=uploaded_files[0].mime_type,
                        ),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=0.099,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_modalities=[
                    "image",
                    "text",
                ],
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                ],
                response_mime_type="text/plain",
            )

            response = client.models.generate_content(
                model="models/gemini-2.0-flash-exp",
                contents=contents,
                config=generate_content_config,
            )
            
            # Add any warnings to the output text
            if warning_list:
                output_text += "\nWarnings:\n"
                for warning in warning_list:
                    output_text += f"- {warning.message}\n"
            
            # Process the response
            if response and hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    for part in candidate.content.parts:
                        if part.text is not None:
                            output_text += part.text + "\n"
                        elif part.inline_data is not None:
                            try:
                                if isinstance(part.inline_data.data, bytes):
                                    image_data = part.inline_data.data
                                else:
                                    image_data = base64.b64decode(part.inline_data.data)
                                
                                output_image = Image.open(BytesIO(image_data))
                                
                            except Exception as img_error:
                                output_text += f"Error processing image: {str(img_error)}\n"
            else:
                output_text = "The model did not generate a valid response. Please try again with different images."
        
        except Exception as e:
            error_details = f"Error: {str(e)}\n\nType: {type(e).__name__}"
            if warning_list:
                error_details += "\n\nWarnings:\n"
                for warning in warning_list:
                    error_details += f"- {warning.message}\n"
            print(f"Exception occurred: {error_details}")
            return None, error_details
        
        finally:
            # Clean up all temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
            
            # Clean up any uploaded files if possible
            for uploaded_file in uploaded_files:
                try:
                    if hasattr(client, 'files') and hasattr(client.files, 'delete') and uploaded_file:
                        client.files.delete(uploaded_file.uri)
                except:
                    pass  # Best effort cleanup
    
    return output_image, output_text if output_text else f"Successfully generated the image with size {size}!"


def generate_angle_view(person_image, clothing_image, angle_description, size='M', max_retries=3):
    """Generate a view of the person from a specific angle with size specification and automatic retry for rate limits."""
    
    # Define size descriptions
    size_descriptions = {
        'S': 'small size with a tight, snug fit',
        'M': 'medium size with a normal fit',
        'L': 'large size with a loose, relaxed fit'
    }
    size_desc = size_descriptions.get(size, size_descriptions['M'])
    
    for attempt in range(max_retries):
        temp_files = []
        uploaded_files = []
        client = None
        
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return None, "API key not found"
            
            client = genai.Client(api_key=api_key)
            
            # Save images
            for img in [person_image, clothing_image]:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    img.save(temp_file.name)
                    temp_files.append(temp_file.name)
            
            # Upload files
            uploaded_files = [
                client.files.upload(file=temp_files[0]),
                client.files.upload(file=temp_files[1]),
            ]
            
            prompt = f'''
                Create an image showing {angle_description}.
                
                Requirements:
                1. Swap the person's clothing with the clothing from the clothing image
                2. Apply the clothing in {size_desc} - adjust fit, draping, and proportions accordingly
                3. Show the person from the {angle_description}
                4. Maintain the same face, body proportions, and pose style
                5. Keep realistic lighting and shadows
                6. Ensure the clothing fits naturally with the specified size
                
                The output should show the person wearing the new clothing in {size_desc} from the specified angle.
            '''
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="Person image - preserve identity and features:"),
                        types.Part.from_uri(
                            file_uri=uploaded_files[0].uri,
                            mime_type=uploaded_files[0].mime_type,
                        ),
                        types.Part.from_text(text=f"Clothing to apply in {size_desc}:"),
                        types.Part.from_uri(
                            file_uri=uploaded_files[1].uri,
                            mime_type=uploaded_files[1].mime_type,
                        ),
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            config = types.GenerateContentConfig(
                temperature=0.099,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_modalities=["image", "text"],
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold=HarmBlockThreshold.BLOCK_NONE,
                    ),
                ],
            )
            
            response = client.models.generate_content(
                model="models/gemini-2.0-flash-exp",
                contents=contents,
                config=config,
            )
            
            if response and hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        if isinstance(part.inline_data.data, bytes):
                            image_data = part.inline_data.data
                        else:
                            image_data = base64.b64decode(part.inline_data.data)
                        return Image.open(BytesIO(image_data)), "Success"
            
            return None, "No image generated"
            
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)', error_str)
                if retry_match:
                    retry_delay = float(retry_match.group(1)) + 2
                else:
                    retry_delay = 15 * (2 ** attempt)
                
                if attempt < max_retries - 1:
                    print(f"⏳ Rate limit hit. Waiting {retry_delay:.0f}s before retry ({attempt + 2}/{max_retries})...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None, "⚠️ API rate limit exceeded. Please wait and try again later."
            else:
                return None, error_str
                
        finally:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
            for uploaded_file in uploaded_files:
                try:
                    if hasattr(client, 'files') and hasattr(client.files, 'delete') and uploaded_file:
                        client.files.delete(uploaded_file.uri)
                except:
                    pass
    
    return None, "Max retries reached"


def generate_combined_tryon(person_image, clothing_image, size, session_id):
    """
    Generate both 2D and 360° views progressively.
    Yields results as they're generated for progressive loading.
    """
    angles = [
        ("front view", "Front", "2d"),  # Start with 2D front view
        ("45-degree angle from the right", "45° Right", "360"),
        ("right side profile view", "Right Side", "360"),
        ("back-right three-quarter view", "Back Right", "360"),
        ("direct back view - showing the back of the person", "Back", "360"),
        ("back-left three-quarter view", "Back Left", "360"),
        ("left side profile view", "Left Side", "360"),
        ("45-degree angle from the left", "45° Left", "360"),
    ]
    
    results = []
    
    for i, (angle_desc, label, view_type) in enumerate(angles):
        # Add delay between requests (except first one)
        if i > 0:
            time.sleep(5)
        
        # Generate the image
        img, msg = generate_angle_view(person_image, clothing_image, angle_desc, size)
        
        if img:
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = f'data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}'
            
            results.append({
                'index': i,
                'label': label,
                'type': view_type,
                'image': img_base64,
                'success': True
            })
            
            # Yield this result immediately
            yield {
                'type': 'image',
                'data': results[-1],
                'progress': f"{i+1}/8",
                'message': f"✓ {label} completed"
            }
        else:
            # Yield error
            yield {
                'type': 'error',
                'data': {
                    'index': i,
                    'label': label,
                    'type': view_type,
                    'message': msg
                },
                'progress': f"{i+1}/8",
                'message': f"✗ {label} failed: {msg}"
            }
            
            # If rate limit, wait longer
            if "rate limit" in msg.lower() or "quota" in msg.lower():
                if i < len(angles) - 1:
                    yield {
                        'type': 'status',
                        'message': '⏳ Waiting 60s due to rate limit...'
                    }
                    time.sleep(60)
    
    # Create GIF from successful results
    successful_images = [r for r in results if r.get('success')]
    if len(successful_images) > 1:
        try:
            # Get PIL images
            pil_images = []
            for result in successful_images:
                img_data = result['image'].split(',')[1]
                img_bytes = base64.b64decode(img_data)
                pil_images.append(Image.open(BytesIO(img_bytes)))
            
            # Create GIF
            gif_buffer = BytesIO()
            pil_images[0].save(
                gif_buffer,
                format='GIF',
                save_all=True,
                append_images=pil_images[1:],
                duration=800,
                loop=0
            )
            gif_buffer.seek(0)
            gif_base64 = f'data:image/gif;base64,{base64.b64encode(gif_buffer.getvalue()).decode()}'
            
            yield {
                'type': 'gif',
                'data': gif_base64,
                'message': f'✓ Created animated GIF from {len(successful_images)} views'
            }
        except Exception as e:
            yield {
                'type': 'error',
                'message': f'✗ GIF creation failed: {str(e)}'
            }
    
    # Final completion message
    yield {
        'type': 'complete',
        'total': len(successful_images),
        'failed': 8 - len(successful_images),
        'message': f'Generation complete! {len(successful_images)}/8 views created.'
    }


# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/combined-tryon', methods=['POST'])
def combined_tryon():
    """Combined 2D + 360° try-on with progressive loading via Server-Sent Events"""
    try:
        person_file = request.files.get('person_image')
        clothing_file = request.files.get('clothing_image')
        size = request.form.get('size', 'M')
        
        if not person_file or not clothing_file:
            return jsonify({'error': 'Both images are required'}), 400
        
        if size not in ['S', 'M', 'L']:
            size = 'M'
        
        person_image = Image.open(person_file.stream).convert('RGB')
        clothing_image = Image.open(clothing_file.stream).convert('RGB')
        
        # Generate unique session ID
        session_id = str(time.time())
        
        def generate():
            for update in generate_combined_tryon(person_image, clothing_image, size, session_id):
                yield f"data: {json.dumps(update)}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quick-tryon', methods=['POST'])
def quick_tryon():
    """Quick 2D try-on with size selection"""
    try:
        person_file = request.files.get('person_image')
        clothing_file = request.files.get('clothing_image')
        size = request.form.get('size', 'M')
        
        if not person_file or not clothing_file:
            return jsonify({'error': 'Both images are required'}), 400
        
        if size not in ['S', 'M', 'L']:
            size = 'M'
        
        person_image = Image.open(person_file.stream).convert('RGB')
        clothing_image = Image.open(clothing_file.stream).convert('RGB')
        
        result_image, message = swap_clothing(person_image, clothing_image, size)
        
        if result_image is None:
            return jsonify({'error': message}), 500
        
        # Convert image to base64
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_str}',
            'message': message,
            'size': size
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
