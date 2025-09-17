#!/usr/bin/env python3
"""
AI Post Bot for Telegram - Render.com Web Service
Generates 20 daily posts with AI content and images using Google Gemini models
Optimized for Render.com Web Service deployment
"""

import os
import time
import schedule
import random
import requests
import threading
from datetime import datetime, timezone
from io import BytesIO
import logging
import base64
import json

# Core libraries
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, jsonify

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
        
        # AI topics in Uzbek
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
        
        print("🤖 AI Post Bot Render.com Web Service da ishga tushdi. 07:00-21:00 UTC oralig'ida 20 ta post jo'natiladi.")
    
    def generate_uzbek_text(self, topic):
        """Generate Uzbek text content about AI topics using Gemini"""
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
            
            if response and hasattr(response, 'text') and response.text:
                generated_text = response.text.strip()
                logger.info(f"Successfully generated {len(generated_text)} characters of Uzbek text")
                return generated_text
            else:
                return self._get_fallback_text(topic)
                
        except Exception as e:
            logger.error(f"Error generating Uzbek text: {e}")
            return self._get_fallback_text(topic)
    
    def _get_fallback_text(self, topic):
        """Generate fallback text when Gemini fails"""
        return f"""AI texnologiyalari kundan-kunga rivojlanmoqda va bizning hayotimizni o'zgartirmoqda. {topic} mavzusi bo'yicha ko'proq o'rganish juda muhim.

Bugungi kunda AI asboblari bizga vaqt tejash, samaradorlikni oshirish va yangi imkoniyatlar ochishda yordam bermoqda. Har bir yangi AI texnologiyasi o'z afzalliklari va cheklovlariga ega.

Bu sohadagi yangiliklar va rivojlanishlar doimo kuzatib borish zarur. Professional rivojlanish uchun doimiy o'rganish va amaliyot qilish muhim.

Sizning fikringizcha, AI texnologiyalari kelajakda qanday rivojlanadi?"""
    
    def generate_image_with_gemini(self, topic):
        """Generate image using Gemini 2.5 Flash Image"""
        try:
            logger.info(f"Generating image with Gemini 2.5 Flash Image for topic: {topic}")
            
            image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            prompt = f"""Create a high-quality, educational infographic-style image about: '{topic}'. 
Professional design with AI technology elements, modern graphics, clean layout, 
futuristic style, technology icons, AI symbols, 16:9 aspect ratio, no text overlay."""
            
            response = image_model.generate_content(prompt)
            
            if response and hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and hasattr(part.inline_data, 'data'):
                        image_data_b64 = part.inline_data.data
                        if isinstance(image_data_b64, str):
                            image_data = base64.b64decode(image_data_b64)
                        else:
                            image_data = image_data_b64
                        
                        if len(image_data) > 0:
                            logger.info(f"Successfully generated image: {len(image_data)} bytes")
                            return BytesIO(image_data)
            
            logger.warning("No valid image data found in Gemini response")
            return None
            
        except Exception as e:
            logger.error(f"Error generating image with Gemini: {e}")
            return None
    
    def create_fallback_image(self, text):
        """Create fallback image with text using PIL"""
        try:
            width, height = 1200, 675  # 16:9 aspect ratio
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            for y in range(height):
                gradient_color = int(26 + (64 - 26) * (y / height))
                color = (gradient_color, gradient_color, 100 + int(55 * (y / height)))
                draw.line([(0, y), (width, y)], fill=color)
            
            # Try to use system font
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Add title
            title = "AI Post - Uzbek AI Channel"
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
            
            # Add AI emoji
            ai_text = "🤖🧠💡"
            ai_bbox = draw.textbbox((0, 0), ai_text, font=font_large)
            ai_width = ai_bbox[2] - ai_bbox[0]
            ai_x = (width - ai_width) // 2
            draw.text((ai_x, height - 100), ai_text, fill='#ffd700', font=font_large)
            
            # Save to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error creating fallback image: {e}")
            return None
    
    def post_to_telegram(self, text, image_buffer):
        """Post content to Telegram channel"""
        try:
            if image_buffer:
                image_buffer.seek(0)
                
                # Send photo with caption
                files = {'photo': ('image.png', image_buffer, 'image/png')}
                data = {
                    'chat_id': self.telegram_channel_id,
                    'caption': text[:1024]  # Telegram caption limit
                }
                
                response = requests.post(
                    f"{self.telegram_api_url}/sendPhoto",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info("Posted to Telegram with image")
                    return True
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False
            else:
                # Send text message only
                data = {
                    'chat_id': self.telegram_channel_id,
                    'text': text
                }
                
                response = requests.post(
                    f"{self.telegram_api_url}/sendMessage",
                    data=data,
                    timeout=30
                )
                
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
            
            # Try to generate image with Gemini first
            image_buffer = self.generate_image_with_gemini(topic)
            
            # If Gemini image generation failed, create PIL fallback
            if not image_buffer:
                logger.info("Gemini image generation failed, creating PIL fallback image")
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
        """Setup posting schedule - 20 posts from 07:00 to 21:00 UTC (every ~42 minutes)"""
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
    
    def run_scheduler(self):
        """Run scheduler in background thread"""
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(60)

# Flask app setup
app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint returning JSON status"""
    return {"status": "alive"}

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

def main():
    """Main entry point"""
    try:
        # Initialize bot
        bot = AIPostBot()
        bot.setup_schedule()
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=bot.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Get port from environment (Render.com sets PORT)
        port = int(os.getenv('PORT', 8000))
        
        # Start Flask web server
        logger.info(f"🌐 Starting Flask web server on 0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)

if __name__ == "__main__":
    main()