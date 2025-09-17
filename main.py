#!/usr/bin/env python3
"""
AI Post Bot for Telegram - Render.com Web Service
Generates 20 daily posts with AI content and nano banana images using Google Gemini models
Optimized for Render.com Web Service deployment with nano banana metaphor
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
            "Prompt engineering nima? AI ga qanday buyruq berish kerak?",
            "ChatGPT va Gemini farqi nima? Qaysi biri yaxshi?",
            "Midjourney qanday ishlaydi? Rasm generatsiyasi uchun eng yaxshi promptlar",
            "AI bilan qanday dasturlash qilish mumkin? Python + AI misoli",
            "AI qanday o'qiydi? Neuronlar nima?",
            "Stable Diffusion vs DALL·E 3: qaysi rasm yaxshiroq?",
            "AI bilan CV yozish — qanday prompt berish kerak?",
            "AI yordamida video script yozish — qo'lda emas!",
            "AI bilan o'zbek tilida matn yozish — qanday muvaffaqiyatli?",
            "AI qanday o'qishni o'rgatadi? O'qituvchi o'rniga AI?",
            "AI bilan blog yozish — 1 daqiqada 500 so'z!",
            "AI qanday xatolar qiladi? Va ularni qanday tuzatish mumkin?",
            "AI bilan rasmga sarlavha yozish — promptlar namunalari",
            "AI bilan dastur yozish — kodni tushuntirish",
            "AI bilan tarjima qilish — qanchalik aniqlik?",
            "AI bilan musiqa yaratish — qanday?",
            "AI bilan o'yin yaratish — qanday dasturlash kerak?",
            "AI bilan biznes fikrlarini yaratish — 10 ta fikr!",
            "AI bilan kunlik reja tuzish — qanday prompt berish kerak?",
            "AI ni o'rganish — boshlang'ich darajada nimalar kerak?"
        ]
        
        print("🤖 AI Post Bot Render.com Web Service da ishga tushdi. 07:00-21:00 UTC oralig'ida 20 ta post jo'natiladi.")
    
    def generate_uzbek_text(self, topic):
        """Generate Uzbek text content about AI topics using Gemini 1.5 Flash"""
        try:
            prompt = f"""O'zbek tilida, 200-300 so'z oralig'ida, o'qivchi uchun qiziqarli, oddiy, hayotiy misollar bilan, 
AI ni o'rganish haqida ma'lumot ber. Mavzu: {topic}. 
So'nggi qatorga: "➡️ {self.telegram_channel_id} kanaliga obuna bo'ling!" yozing.

Talablar:
- Oddiy va tushunarli til
- Praktik maslahatlar berish
- Misollar keltirish
- Savol bilan tugashi (engagement uchun)
- Professional va do'stona ohang
Postda hashtag ishlatmang, faqat sof matn bo'lsin."""
            
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

Sizning fikringizcha, AI texnologiyalari kelajakda qanday rivojlanadi?

➡️ {self.telegram_channel_id} kanaliga obuna bo'ling!"""
    
    def generate_nano_banana_image(self, topic):
        """Generate image using Gemini 2.5 Flash Image Preview with nano banana metaphor"""
        try:
            logger.info(f"Generating nano banana image with Gemini 2.5 Flash Image Preview for topic: {topic}")
            
            image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            
            # Nano banana prompt with specific metaphor as requested
            prompt = f"""Create a high-quality, educational infographic-style image about: '{topic}'. 
Visualize the concept using creative metaphors. Include a small, glowing nano-banana 
(1cm size, made of golden circuit boards and neon-blue wires, smiling, floating in zero gravity) 
as the central symbol of AI intelligence. Surround it with icons: brain, robot, code brackets, 
speech bubble with 'Prompt', lightbulb, gears. Background: soft gradient purple-cyan cosmic space. 
Style: futuristic educational poster for teenagers, clean vector art, professional design, 
no text overlay, 16:9 aspect ratio, ultra-detailed, cinematic lighting. 
SynthID watermark is allowed but must be subtle and in bottom-right corner."""
            
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
                            logger.info(f"Successfully generated nano banana image: {len(image_data)} bytes")
                            return BytesIO(image_data)
            
            logger.warning("No valid image data found in Gemini 2.5 Flash Image Preview response")
            return None
            
        except Exception as e:
            logger.error(f"Error generating nano banana image with Gemini 2.5 Flash Image Preview: {e}")
            return None
    
    def create_fallback_image(self, text):
        """Create improved fallback image with complete text using PIL when nano banana image generation fails"""
        try:
            width, height = 1000, 1400  # Vertical format for better text readability
            img = Image.new('RGB', (width, height), color='#0f0f23')
            draw = ImageDraw.Draw(img)
            
            # Create nano banana cosmic gradient background
            for y in range(height):
                # Purple to cyan gradient like in nano banana theme
                purple_r = int(15 + (138 - 15) * (y / height))
                purple_g = int(15 + (43 - 15) * (y / height))  
                purple_b = int(35 + (226 - 35) * (y / height))
                color = (purple_r, purple_g, purple_b)
                draw.line([(0, y), (width, y)], fill=color)
            
            # Try to use system font with better sizes
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
                font_emoji = ImageFont.load_default()
            
            # Add nano banana title with glow effect
            title = "🍌 NANO BANANA AI CHANNEL"
            title_bbox = draw.textbbox((0, 0), title, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            
            # Add glow effect
            for offset in range(3, 0, -1):
                alpha = 100 - (offset * 20)
                glow_color = (255, 215, 0)  # Golden glow
                for dx in [-offset, 0, offset]:
                    for dy in [-offset, 0, offset]:
                        if dx != 0 or dy != 0:
                            draw.text((title_x + dx, 30 + dy), title, fill=glow_color, font=font_title)
            
            draw.text((title_x, 30), title, fill='#FFD700', font=font_title)
            
            # Process and wrap text more efficiently
            clean_text = text.replace('➡️ ' + self.telegram_channel_id + ' kanaliga obuna bo\'ling!', '').strip()
            words = clean_text.split()
            lines = []
            current_line = ""
            max_width = width - 60  # More padding
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_bbox = draw.textbbox((0, 0), test_line, font=font_text)
                test_width = test_bbox[2] - test_bbox[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw text lines with better spacing
            y_offset = 90
            line_height = 26
            
            for line in lines:
                if y_offset + line_height > height - 150:  # Stop if we're getting too close to bottom
                    break
                    
                # Center align text
                line_bbox = draw.textbbox((0, 0), line, font=font_text)
                line_width = line_bbox[2] - line_bbox[0]
                x = max(30, (width - line_width) // 2)  # Center but not less than 30px margin
                
                # Add subtle text shadow
                draw.text((x + 1, y_offset + 1), line, fill='#000020', font=font_text)
                draw.text((x, y_offset), line, fill='#FFFFFF', font=font_text)
                y_offset += line_height
            
            # Add nano banana footer with channel info
            footer_text = "🤖 AI o'rganish - Nano Banana metaforasi bilan"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=font_emoji)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = (width - footer_width) // 2
            draw.text((footer_x, height - 100), footer_text, fill='#FFD700', font=font_emoji)
            
            # Add subscription call to action
            cta_text = f"➡️ {self.telegram_channel_id} kanaliga obuna bo'ling!"
            cta_bbox = draw.textbbox((0, 0), cta_text, font=font_emoji)
            cta_width = cta_bbox[2] - cta_bbox[0]
            cta_x = (width - cta_width) // 2
            draw.text((cta_x, height - 60), cta_text, fill='#00FFFF', font=font_emoji)
            
            # Save to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error creating improved fallback image: {e}")
            return None
    
    def post_to_telegram(self, text, image_buffer):
        """Post content to Telegram channel"""
        try:
            if image_buffer:
                image_buffer.seek(0)
                
                # Send photo with caption
                files = {'photo': ('nano_banana_image.png', image_buffer, 'image/png')}
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
                    logger.info("Posted nano banana content to Telegram with image")
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
    
    def create_and_post_ai_post(self):
        """Generate nano banana AI post and send to Telegram"""
        try:
            # Select random topic
            topic = random.choice(self.ai_topics)
            logger.info(f"Creating nano banana AI post for topic: {topic}")
            
            # Generate Uzbek text content
            text_content = self.generate_uzbek_text(topic)
            
            # Try to generate nano banana image with Gemini 2.5 Flash Image Preview first
            image_buffer = self.generate_nano_banana_image(topic)
            
            # If nano banana image generation failed, create PIL fallback
            if not image_buffer:
                logger.info("Nano banana image generation failed, creating PIL fallback image")
                image_buffer = self.create_fallback_image(text_content)
            
            # Post to Telegram
            success = self.post_to_telegram(text_content, image_buffer)
            
            if success:
                logger.info("✅ Nano banana AI post generated and published successfully")
            else:
                logger.error("❌ Failed to publish nano banana AI post")
                
        except Exception as e:
            logger.error(f"Error in create_and_post_ai_post: {e}")
    
    def setup_schedule(self):
        """Setup posting schedule - 20 posts from 07:00 to 21:00 UTC (every ~42 minutes)"""
        post_times = []
        start_hour = 7
        end_hour = 21
        
        # Calculate 20 post times evenly distributed across 14 hours
        total_minutes = (end_hour - start_hour) * 60  # 14 hours = 840 minutes
        interval = total_minutes // 19  # 19 intervals for 20 posts (42 minutes approximately)
        
        for i in range(20):
            minutes_from_start = i * interval
            hour = start_hour + (minutes_from_start // 60)
            minute = minutes_from_start % 60
            
            time_str = f"{hour:02d}:{minute:02d}"
            post_times.append(time_str)
            
            schedule.every().day.at(time_str).do(self.create_and_post_ai_post)
            logger.info(f"Scheduled nano banana post at {time_str} UTC")
        
        logger.info(f"✅ Scheduled {len(post_times)} daily nano banana posts from {post_times[0]} to {post_times[-1]} UTC")
    
    def run_scheduler(self):
        """Run scheduler in background thread"""
        logger.info("Starting nano banana scheduler thread...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in nano banana scheduler: {e}")
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
        # Initialize nano banana bot
        bot = AIPostBot()
        bot.setup_schedule()
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=bot.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Get port from environment (Render.com sets PORT, default to 8000 for Replit)
        port = int(os.getenv('PORT', 8000))  # Replit doesn't support 10000
        
        # Start Flask web server
        logger.info(f"🌐 Starting Flask web server on 0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start nano banana AI bot: {e}")
        exit(1)

if __name__ == "__main__":
    main()