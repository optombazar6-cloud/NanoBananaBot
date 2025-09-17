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
            prompt = f"""O'zbek tilida, 400-600 so'z oralig'ida, o'qivchi uchun qiziqarli, batafsil, hayotiy misollar bilan, 
AI ni o'rganish haqida to'liq ma'lumot ber. Mavzu: {topic}. 
So'nggi qatorga: "➡️ {str(self.telegram_channel_id)} kanaliga obuna bo'ling!" yozing.

Talablar:
- Oddiy va tushunarli til
- Batafsil tushuntirish va praktik maslahatlar
- Ko'proq misollar va bosqichma-bosqich yo'riqnoma
- Aniq natijaviy ma'lumotlar berish
- Savol bilan tugashi (engagement uchun)
- Professional va do'stona ohang
- Matnni to'liq yozish, qisqartirmaslik
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
    
    def generate_topic_image(self, topic):
        """Generate topic-related image using Gemini 2.5 Flash Image Preview (no text in image)"""
        try:
            logger.info(f"Generating topic-related image with Gemini 2.5 Flash Image Preview for topic: {topic}")
            
            image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            
            # Generate image related to the topic without any text
            prompt = f"""Create a high-quality, professional image related to: '{topic}'. 
Show relevant objects, scenes, technology, or illustrations that represent this AI topic.
Style: modern, clean, professional, educational, suitable for social media.
NO TEXT, NO WORDS, NO LETTERS in the image - only visual elements.
16:9 aspect ratio, high detail, good lighting, colorful and engaging.
Examples of what to show:
- For ChatGPT/AI models: robot, computer brain, neural networks
- For image generation: artist tools, creative scenes, digital art
- For programming: code symbols, computers, development setup
- For learning AI: books, brain, lightbulb, education symbols
Background should be clean and modern."""
            
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
                            logger.info(f"Successfully generated topic image: {len(image_data)} bytes")
                            return BytesIO(image_data)
            
            logger.warning("No valid image data found in Gemini 2.5 Flash Image Preview response")
            return None
            
        except Exception as e:
            logger.error(f"Error generating topic image with Gemini 2.5 Flash Image Preview: {e}")
            return None
    
    def create_topic_graphic(self, topic):
        """Create topic-related graphic using PIL when AI image generation fails"""
        try:
            width, height = 1000, 562  # 16:9 aspect ratio
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Create modern gradient background
            for y in range(height):
                # Modern blue gradient
                blue_r = int(26 + (64 - 26) * (y / height))
                blue_g = int(26 + (128 - 26) * (y / height))  
                blue_b = int(46 + (200 - 46) * (y / height))
                color = (blue_r, blue_g, blue_b)
                draw.line([(0, y), (width, y)], fill=color)
            
            # Draw topic-related geometric shapes and symbols
            center_x, center_y = width // 2, height // 2
            
            # Draw AI-related geometric patterns
            # Circuit-like lines
            draw.line([(100, 100), (300, 100)], fill='#00ff88', width=3)
            draw.line([(300, 100), (350, 150)], fill='#00ff88', width=3)
            draw.line([(700, 200), (900, 200)], fill='#ff6b6b', width=3)
            draw.line([(900, 200), (850, 250)], fill='#ff6b6b', width=3)
            
            # Draw neural network nodes
            for i, (x, y) in enumerate([(200, 150), (400, 180), (600, 120), (800, 160)]):
                color = ['#00ff88', '#ff6b6b', '#4ecdc4', '#45b7d1'][i % 4]
                draw.ellipse([x-15, y-15, x+15, y+15], fill=color)
            
            # Draw brain-like pattern in center
            brain_x, brain_y = center_x - 50, center_y - 30
            for i in range(5):
                x_offset = i * 25
                draw.ellipse([brain_x + x_offset - 10, brain_y - 10, 
                             brain_x + x_offset + 10, brain_y + 10], 
                            outline='#ffd93d', width=2)
            
            # Add technology symbols
            # Gear-like circles
            for x, y in [(150, 300), (850, 350)]:
                for radius in [20, 15, 10]:
                    draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               outline='#6c5ce7', width=2)
            
            # Draw binary pattern (decorative)
            binary_color = '#a8e6cf'
            for i in range(0, width, 50):
                for j in range(0, height, 80):
                    if (i + j) % 100 == 0:
                        draw.ellipse([i-3, j-3, i+3, j+3], fill=binary_color)
            
            # Add AI-themed icons as simple shapes
            # Robot head outline
            robot_x, robot_y = center_x + 100, center_y + 50
            draw.rectangle((robot_x-20, robot_y-20, robot_x+20, robot_y+20), 
                          outline='#fd79a8', width=3)
            draw.ellipse([robot_x-15, robot_y-10, robot_x-5, robot_y], fill='#fd79a8')
            draw.ellipse([robot_x+5, robot_y-10, robot_x+15, robot_y], fill='#fd79a8')
            
            # CPU/chip pattern
            chip_x, chip_y = center_x - 100, center_y + 80
            draw.rectangle((chip_x-25, chip_y-15, chip_x+25, chip_y+15), 
                          outline='#00b894', width=2)
            for i in range(-20, 25, 10):
                draw.line([chip_x+i, chip_y-15, chip_x+i, chip_y+15], 
                         fill='#00b894', width=1)
            
            # Save to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error creating topic graphic: {e}")
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
        """Generate AI post with topic-related image (no text in image) and detailed text"""
        try:
            # Select random topic
            topic = random.choice(self.ai_topics)
            logger.info(f"Creating AI post with image for topic: {topic}")
            
            # Generate detailed Uzbek text content
            text_content = self.generate_uzbek_text(topic)
            
            # Try to generate topic-related image (without text)
            image_buffer = self.generate_topic_image(topic)
            
            # If AI image generation failed, create topic-related graphic fallback
            if not image_buffer:
                logger.info("AI image generation failed, creating topic-related graphic fallback")
                image_buffer = self.create_topic_graphic(topic)
            
            # Post to Telegram with image and text caption
            success = self.post_to_telegram(text_content, image_buffer)
            
            if success:
                logger.info("✅ AI post with image and text published successfully")
            else:
                logger.error("❌ Failed to publish AI post")
                
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
        
        # Get port from environment (default to 5000 for Replit)
        port = int(os.getenv('PORT', 5000))  # Use port 5000 for Replit frontend
        
        # Start Flask web server
        logger.info(f"🌐 Starting Flask web server on 0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start nano banana AI bot: {e}")
        exit(1)

if __name__ == "__main__":
    main()