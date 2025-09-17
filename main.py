#!/usr/bin/env python3
"""
AI Post Bot for Telegram - Production Ready
Generates 20 daily posts with AI content and images using Google Gemini models
Optimized for Render.com deployment
"""

import os
import time
import schedule
import random
import requests
from datetime import datetime, timezone
from io import BytesIO
import logging
import base64

# Core libraries
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# Retry mechanism
def retry_with_backoff(func, max_retries=3, backoff_factor=2, initial_delay=1):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                logger.error(f"Max retries ({max_retries}) exceeded: {e}")
                raise
            
            # Check if it's a retryable error
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code < 500:  # Don't retry 4xx errors
                    logger.error(f"Non-retryable error {status_code}: {e}")
                    raise
            
            delay = initial_delay * (backoff_factor ** attempt)
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay}s...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Non-retryable error: {e}")
            raise

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIPostBot:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not all([self.google_api_key, self.telegram_bot_token, self.telegram_channel_id]):
            raise ValueError("Missing required environment variables: GOOGLE_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID")
        
        # Initialize Google AI
        genai.configure(api_key=self.google_api_key)
        self.text_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Initialize Telegram API URL
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}"
        
        # Post topics for AI content
        self.ai_topics = [
            "ChatGPT vs Gemini: qaysi biri yaxshiroq?",
            "AI promptlarni qanday yozish kerak?",
            "Midjourney bilan professional rasmlar yaratish",
            "AI yordamida biznes g'oyalarini rivojlantirish",
            "Copilot va dasturlash: kelajak bugun",
            "AI detektorlar: qanday ishlaydi?",
            "Stable Diffusion: bepul AI rasm generatori",
            "AI chatbotlar: biznes uchun foydasi",
            "OpenAI API bilan dastur yaratish",
            "AI va ma'lumotlar xavfsizligi",
            "AutoGPT va avtomatik vazifalar",
            "AI bilan kontentni optimallashtirish",
            "Hugging Face: AI modellar markazi",
            "AI yordamida video montaj qilish",
            "Bing AI va Google Bard taqqoslash",
            "AI promptlarda rol-playing texnikasi",
            "Notion AI: produktivlik uchun yordamchi",
            "AI bilan SEO optimizatsiya qilish",
            "Claude AI: Anthropic'ning yutug'i",
            "AI tools for creative writing"
        ]
        
        logger.info("🤖 AI Post Bot initialized successfully")
    
    def generate_uzbek_text(self, topic):
        """Generate Uzbek text content about AI topics using Gemini with robust error handling"""
        try:
            prompt = f"""
Mavzu: {topic}

O'zbek tilida AI va texnologiya haqida 200-300 so'zlik ma'lumotli va qiziqarli post yozing. Post quyidagi talablarga javob berishi kerak:
- Oddiy va tushunarli til
- Praktik maslahatlar berish
- Misollar keltirish
- Savol bilan tugashi (engagement uchun)
- Professional va do'stona ohang

Postda hashtag ishlatmang, faqat sof matn bo'lsin.
"""
            
            logger.info(f"Generating Uzbek text for topic: {topic}")
            response = self.text_model.generate_content(prompt)
            
            # Validate response
            if not response:
                logger.error("Gemini returned empty response for text generation")
                raise ValueError("Empty response from Gemini")
                
            if not hasattr(response, 'text') or not response.text:
                logger.error("Gemini response missing text attribute or empty text")
                raise ValueError("Invalid response structure from Gemini")
            
            generated_text = response.text.strip()
            if len(generated_text) < 50:  # Sanity check for minimum length
                logger.warning(f"Generated text seems too short ({len(generated_text)} chars): {generated_text[:100]}...")
            
            logger.info(f"Successfully generated {len(generated_text)} characters of Uzbek text")
            return generated_text
            
        except ValueError as e:
            logger.error(f"Gemini API validation error: {e}")
            return self._get_fallback_text(topic)
        except Exception as e:
            logger.error(f"Unexpected error generating Uzbek text: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            return self._get_fallback_text(topic)
    
    def _get_fallback_text(self, topic):
        """Generate fallback text when Gemini fails"""
        return f"""AI texnologiyalari kundan-kunga rivojlanmoqda va bizning hayotimizni o'zgartirmoqda. {topic} mavzusi bo'yicha ko'proq o'rganish juda muhim.

Bugungi kunda AI asboblari bizga vaqt tejash, samaradorlikni oshirish va yangi imkoniyatlar ochishda yordam bermoqda. Har bir yangi AI texnologiyasi o'z afzalliklari va cheklovlariga ega.

Bu sohadagi yangiliklar va rivojlanishlar doimo kuzatib borish zarur. Professional rivojlanish uchun doimiy o'rganish va amaliyot qilish muhim.

Sizning fikringizcha, AI texnologiyalari kelajakda qanday rivojlanadi?"""
    
    def generate_nano_banana_image(self, topic):
        """Generate image using Gemini 2.5 Flash Image with robust error handling"""
        try:
            logger.info(f"Initializing image generation model for topic: {topic}")
            
            # Initialize image generation model with error checking
            try:
                image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            except Exception as e:
                logger.error(f"Failed to initialize Gemini image model: {e}")
                return None
            
            prompt = f"""Create a high-quality, educational infographic-style image about: '{topic}'. Visualize the concept using creative metaphors. Include a small, glowing nano-banana (1cm size, made of golden circuit boards and neon-blue wires, smiling, floating in zero gravity) as the central symbol of AI intelligence. Surround it with icons: brain, robot, code brackets, speech bubble with 'Prompt', lightbulb, gears. Background: soft gradient purple-cyan cosmic space. Style: futuristic educational infographic, clean vector art, professional design, no text overlay, 16:9 aspect ratio, ultra-detailed, photorealistic lighting."""
            
            logger.info("Sending image generation request to Gemini")
            response = image_model.generate_content(prompt)
            
            # Comprehensive response validation
            if not response:
                logger.error("Gemini returned empty response for image generation")
                return None
            
            if not hasattr(response, 'parts'):
                logger.error("Gemini response missing 'parts' attribute")
                return None
                
            if not response.parts:
                logger.error("Gemini response has empty parts list")
                return None
                
            logger.info(f"Received response with {len(response.parts)} parts")
            
            # Process response parts
            for i, part in enumerate(response.parts):
                logger.info(f"Processing part {i+1}/{len(response.parts)}")
                
                if not hasattr(part, 'inline_data'):
                    logger.warning(f"Part {i+1} missing inline_data attribute")
                    continue
                    
                if not part.inline_data:
                    logger.warning(f"Part {i+1} has empty inline_data")
                    continue
                
                if not hasattr(part.inline_data, 'data'):
                    logger.warning(f"Part {i+1} inline_data missing data attribute")
                    continue
                
                logger.info(f"Found valid inline_data in part {i+1}")
                
                # Decode base64 image data properly
                try:
                    image_data_b64 = part.inline_data.data
                    if isinstance(image_data_b64, str):
                        image_data = base64.b64decode(image_data_b64)
                    else:
                        # If already bytes, use directly
                        image_data = image_data_b64
                    
                    if len(image_data) == 0:
                        logger.error("Decoded image data is empty")
                        continue
                        
                    logger.info(f"Successfully decoded image data: {len(image_data)} bytes")
                    return BytesIO(image_data)
                    
                except Exception as decode_error:
                    logger.error(f"Failed to decode image data from part {i+1}: {decode_error}")
                    continue
            
            logger.warning("No valid image data found in any response part")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            # Log additional context for debugging
            if hasattr(e, 'args') and e.args:
                logger.error(f"Exception args: {e.args}")
            return None
    
    def create_fallback_image(self, text):
        """Create fallback image with text using PIL when AI generation fails"""
        try:
            # Create image
            width, height = 1200, 675  # 16:9 aspect ratio
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            for y in range(height):
                gradient_color = int(26 + (64 - 26) * (y / height))
                color = (gradient_color, gradient_color, 100 + int(55 * (y / height)))
                draw.line([(0, y), (width, y)], fill=color)
            
            # Try to use a system font, fallback to default
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Add title
            title = "AI Post - Nano Banana Bot"
            title_bbox = draw.textbbox((0, 0), title, font=font_large)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, 50), title, fill='#ffd700', font=font_large)
            
            # Add main text (word wrap)
            words = text.split()
            lines = []
            current_line = ""
            max_width = width - 100
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_bbox = draw.textbbox((0, 0), test_line, font=font_medium)
                test_width = test_bbox[2] - test_bbox[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Limit to max 15 lines
            if len(lines) > 15:
                lines = lines[:14]
                lines.append("...")
            
            # Draw text lines
            y_offset = 150
            line_height = 40
            for line in lines:
                line_bbox = draw.textbbox((0, 0), line, font=font_medium)
                line_width = line_bbox[2] - line_bbox[0]
                x = (width - line_width) // 2
                draw.text((x, y_offset), line, fill='#ffffff', font=font_medium)
                y_offset += line_height
            
            # Add nano banana emoji representation
            banana_text = "🍌✨🤖"
            banana_bbox = draw.textbbox((0, 0), banana_text, font=font_large)
            banana_width = banana_bbox[2] - banana_bbox[0]
            banana_x = (width - banana_width) // 2
            draw.text((banana_x, height - 100), banana_text, fill='#ffd700', font=font_large)
            
            # Save to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error creating fallback image: {e}")
            return None
    
    def post_to_telegram(self, text, image_buffer):
        """Post content to Telegram channel with proper caption length handling"""
        try:
            TELEGRAM_CAPTION_LIMIT = 1024
            
            if image_buffer:
                image_buffer.seek(0)
                
                # Handle caption length limit
                if len(text) <= TELEGRAM_CAPTION_LIMIT:
                    # Send photo with full caption
                    files = {'photo': ('image.png', image_buffer, 'image/png')}
                    data = {
                        'chat_id': self.telegram_channel_id,
                        'caption': text
                    }
                    
                    def send_photo():
                        return requests.post(
                            f"{self.telegram_api_url}/sendPhoto",
                            files=files,
                            data=data,
                            timeout=30
                        )
                    
                    response = retry_with_backoff(send_photo)
                    if response.status_code == 200:
                        logger.info("Posted to Telegram with image and full caption")
                        return True
                    else:
                        logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                        return False
                else:
                    # Caption too long - send photo with truncated caption, then full text
                    logger.info(f"Caption too long ({len(text)} chars), truncating and sending full text separately")
                    
                    # Create truncated caption
                    truncated_caption = text[:TELEGRAM_CAPTION_LIMIT-20] + "... (davomi keyingi xabarda)"
                    
                    # Send photo with truncated caption
                    files = {'photo': ('image.png', image_buffer, 'image/png')}
                    data = {
                        'chat_id': self.telegram_channel_id,
                        'caption': truncated_caption
                    }
                    
                    def send_photo_truncated():
                        return requests.post(
                            f"{self.telegram_api_url}/sendPhoto",
                            files=files,
                            data=data,
                            timeout=30
                        )
                    
                    response = retry_with_backoff(send_photo_truncated)
                    if response.status_code != 200:
                        logger.error(f"Telegram API error (photo): {response.status_code} - {response.text}")
                        return False
                    
                    # Send full text as separate message
                    data = {
                        'chat_id': self.telegram_channel_id,
                        'text': text
                    }
                    
                    def send_full_text():
                        return requests.post(
                            f"{self.telegram_api_url}/sendMessage",
                            data=data,
                            timeout=30
                        )
                    
                    response = retry_with_backoff(send_full_text)
                    if response.status_code == 200:
                        logger.info("Posted to Telegram with image and full text in separate message")
                        return True
                    else:
                        logger.error(f"Telegram API error (text): {response.status_code} - {response.text}")
                        return False
            else:
                # Send text message using requests
                data = {
                    'chat_id': self.telegram_channel_id,
                    'text': text
                }
                
                def send_text_only():
                    return requests.post(
                        f"{self.telegram_api_url}/sendMessage",
                        data=data,
                        timeout=30
                    )
                
                response = retry_with_backoff(send_text_only)
                if response.status_code == 200:
                    logger.info("Posted to Telegram (text only)")
                    return True
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False
            
        except Exception as e:
            logger.error(f"Error posting to Telegram: {e}")
            return False
    
    def generate_and_post(self):
        """Generate content and post to Telegram"""
        try:
            # Select random topic
            topic = random.choice(self.ai_topics)
            logger.info(f"Generating post for topic: {topic}")
            
            # Generate text content
            text_content = self.generate_uzbek_text(topic)
            
            # Try to generate AI image first
            image_buffer = self.generate_nano_banana_image(topic)
            
            # If AI image generation failed, create fallback image
            if not image_buffer:
                logger.info("AI image generation failed, creating fallback image")
                image_buffer = self.create_fallback_image(text_content[:200] + "...")
            
            # Post to Telegram
            success = self.post_to_telegram(text_content, image_buffer)
            
            if success:
                logger.info("✅ Post generated and published successfully")
            else:
                logger.error("❌ Failed to publish post")
                
        except Exception as e:
            logger.error(f"Error in generate_and_post: {e}")
    
    def setup_schedule(self):
        """Setup posting schedule - 20 posts from 07:00 to 21:00 UTC (every 42 minutes)"""
        post_times = []
        start_hour = 7
        end_hour = 21
        
        # Calculate 20 post times evenly distributed
        total_minutes = (end_hour - start_hour) * 60  # 14 hours = 840 minutes
        interval = total_minutes // 19  # 19 intervals for 20 posts
        
        for i in range(20):
            minutes_from_start = i * interval
            hour = start_hour + (minutes_from_start // 60)
            minute = minutes_from_start % 60
            
            time_str = f"{hour:02d}:{minute:02d}"
            post_times.append(time_str)
            
            schedule.every().day.at(time_str).do(self.generate_and_post)
            logger.info(f"Scheduled post at {time_str} UTC")
        
        logger.info(f"✅ Scheduled {len(post_times)} daily posts from {post_times[0]} to {post_times[-1]} UTC")
    
    def run(self):
        """Main run loop"""
        logger.info("🤖 AI Post Bot started on Render.com. Generating 20 posts daily from 07:00 to 21:00 UTC.")
        
        # Setup posting schedule
        self.setup_schedule()
        
        # Check current time and log next post
        now_utc = datetime.now(timezone.utc)
        logger.info(f"Current UTC time: {now_utc.strftime('%H:%M:%S')}")
        
        # Run scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    """Main entry point"""
    try:
        bot = AIPostBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)

if __name__ == "__main__":
    main()