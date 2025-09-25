#!/usr/bin/env python3
"""
AI Post Bot for Telegram - Simple Clean Version
"""

import os
import time
import schedule
import random
import requests
import threading
from datetime import datetime
from io import BytesIO
import logging

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
        
        # Store missing vars for later validation
        self.missing_vars = []
        if not self.google_api_key:
            self.missing_vars.append('GOOGLE_API_KEY')
        if not self.telegram_bot_token:
            self.missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not self.telegram_channel_id:
            self.missing_vars.append('TELEGRAM_CHANNEL_ID')
            
        if self.missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(self.missing_vars)}. Bot functionality will be limited.")
            return  # Don't initialize AI services without API keys
        
        # Initialize Google AI
        genai.configure(api_key=self.google_api_key)
        self.text_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Initialize Telegram API URL
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}"
        
        # AI topics list
        self.ai_topics = [
            "Prompt engineering sirli formulasi — AI dan 10x yaxshi natija olish yo'llari",
            "AI bilan pul ishlash — real misollar va bosqichma-bosqich yo'riqnoma", 
            "Midjourney va DALL-E dan ajoyib rasmlar — professional promptlar va triklar",
            "ChatGPT bilan dasturlash — zero dan hero gacha yo'l",
            "AI bilan biznes-ideya yaratish — startup uchun 100 ta fikr 1 daqiqada",
            "CV yozishda AI mahorati — HR ni hayratda qoldiradigan resume yaratish"
        ]
        
        print("AI Post Bot ishga tushdi. 7:00-21:00 UTC oraligida 20 ta post jonatiladi.")
    
    def generate_uzbek_text(self, topic):
        """Generate Uzbek text content with practical prompts"""
        try:
            prompt = f"""O'zbek tilida amaliy va o'rgatuvchi post yoz. Mavzu: {topic}

TALABLAR:
- Kamida 3 ta aniq PROMPT misoli berish
- Har birini "PROMPT:" deb belgilab yozish  
- Copy-paste qilib ishlatish mumkin bo'lgan formatda
- Bosqichma-bosqich yo'riqnoma
- Amaliy maslahatlar

STRUKTURA:
1. Qiziq fakt
2. Muammo
3. Yechim
4. PROMPT MISOLLARI (kamida 3 ta)
5. Bosqichma-bosqich yo'riqnoma
6. Amaliy maslahat
7. Savol

Oxirida: "https://t.me/nanobanananews kanaliga obuna bo'ling!" yoz.

Aniq va amaliy prompt misollar ber!"""
            
            response = self.text_model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_text(topic)
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return self._get_fallback_text(topic)
    
    def _get_fallback_text(self, topic):
        """Simple fallback text with prompts"""
        return f"""AI AMALIY YO'RIQNOMA: {topic}

Bilasizmi, professional promptlarni yozish - bu san'at! Keling, aniq misollar orqali o'rganamiz.

AMALIY PROMPT MISOLLARI:

PROMPT 1: "Menga [mavzu] haqida batafsil va tushunarli tarzda tushuntir. 5 yoshli bolaga tushuntirgandek oddiy tildan foydalanib, misollar kel"

NATIJA: Har qanday murakkab mavzuni osonroq tushunasiz

PROMPT 2: "Quyidagi matnni professional va rasmiy tarzda qayta yoz: [matn]. Ishbilarmon email uchun mos shaklda tayyorla"

NATIJA: Har qanday matnni professional ko'rinishga keltiradi

PROMPT 3: "Menga {topic.split('-')[0].strip() if '-' in topic else topic} bo'yicha 10 ta konkret maslahat ber. Har biri amaliy va darhol qo'llash mumkin bo'lsin"

NATIJA: To'g'ridan-to'g'ri amaliyotga tatbiq qilish mumkin

PRO MASLAHAT:
- Har doim aniq va konkret so'rov qiling
- Kontekst bering
- Format ko'rsating

HOZIROQ SINAB KO'RING: Yuqoridagi promptlardan birini copy qilib, o'z mavzungiz bilan sinang!

Siz qaysi promptni sinab ko'rdingiz va qanday natija oldingiz?

https://t.me/nanobanananews kanaliga obuna bo'ling!"""
    
    def create_simple_image(self, topic):
        """Create simple image with PIL"""
        try:
            width, height = 1000, 562  # 16:9 aspect ratio
            
            # Create gradient background
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Simple gradient
            for y in range(height):
                ratio = y / height
                r = int(26 + (100 - 26) * ratio)
                g = int(26 + (150 - 26) * ratio) 
                b = int(46 + (200 - 46) * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add some decorative elements
            for i in range(10):
                x = random.randint(100, width-100)
                y = random.randint(100, height-100)
                size = random.randint(20, 50)
                draw.ellipse([x-size, y-size, x+size, y+size], outline='#00ff88', width=3)
            
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return None
    
    def post_to_telegram(self, text, image_buffer):
        """Post content to Telegram channel with smart text handling"""
        try:
            if image_buffer:
                image_buffer.seek(0)
                
                # Check if text is too long for caption (1024 char limit)
                if len(text) <= 1024:
                    # Send photo with full caption
                    files = {'photo': ('ai_image.png', image_buffer, 'image/png')}
                    data = {
                        'chat_id': self.telegram_channel_id,
                        'caption': text
                    }
                    
                    response = requests.post(
                        f"{self.telegram_api_url}/sendPhoto",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        logger.info("Posted complete content to Telegram with image")
                        return True
                    else:
                        logger.error(f"Telegram API error: {response.status_code}")
                        return False
                else:
                    # Text is too long, send image with short caption and full text separately
                    # Send photo with short caption
                    short_caption = "AI haqida qiziqarli ma'lumot"
                    files = {'photo': ('ai_image.png', image_buffer, 'image/png')}
                    data = {
                        'chat_id': self.telegram_channel_id,
                        'caption': short_caption
                    }
                    
                    photo_response = requests.post(
                        f"{self.telegram_api_url}/sendPhoto",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if photo_response.status_code != 200:
                        logger.error(f"Telegram photo error: {photo_response.status_code}")
                        return False
                    
                    # Send full text as separate message
                    text_data = {
                        'chat_id': self.telegram_channel_id,
                        'text': text
                    }
                    
                    text_response = requests.post(
                        f"{self.telegram_api_url}/sendMessage",
                        data=text_data,
                        timeout=30
                    )
                    
                    if text_response.status_code == 200:
                        logger.info("Posted long content with image and separate text message")
                        return True
                    else:
                        logger.error(f"Telegram text error: {text_response.status_code}")
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
                    logger.error(f"Telegram API error: {response.status_code}")
                    return False
            
        except Exception as e:
            logger.error(f"Error posting to Telegram: {e}")
            return False
    
    def create_and_post_ai_post(self):
        """Generate AI post with practical prompts and post to Telegram"""
        try:
            # Select random topic
            topic = random.choice(self.ai_topics)
            logger.info(f"Creating AI post for topic: {topic}")
            
            # Generate Uzbek text content with practical prompts
            text_content = self.generate_uzbek_text(topic)
            
            # Create simple image
            image_buffer = self.create_simple_image(topic)
            
            # Post to Telegram
            success = self.post_to_telegram(text_content, image_buffer)
            
            if success:
                logger.info("AI post published successfully")
            else:
                logger.error("Failed to publish AI post")
                
        except Exception as e:
            logger.error(f"Error in create_and_post_ai_post: {e}")
    
    def setup_schedule(self):
        """Setup posting schedule - 20 posts from 7:00 to 21:00 UTC"""
        post_times = []
        start_hour = 7
        end_hour = 21
        
        # Calculate 20 post times evenly distributed across 14 hours
        total_minutes = (end_hour - start_hour) * 60  # 14 hours = 840 minutes
        interval = total_minutes // 19  # 19 intervals for 20 posts (42 minutes)
        
        for i in range(20):
            minutes_from_start = i * interval
            hour = start_hour + (minutes_from_start // 60)
            minute = minutes_from_start % 60
            
            time_str = f"{hour:02d}:{minute:02d}"
            post_times.append(time_str)
            
            schedule.every().day.at(time_str).do(self.create_and_post_ai_post)
            logger.info(f"Scheduled post at {time_str} UTC")
        
        logger.info(f"Scheduled {len(post_times)} daily posts from {post_times[0]} to {post_times[-1]} UTC")
    
    def run_scheduler(self):
        """Run scheduler in background thread"""
        logger.info("Starting scheduler thread...")
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
    return {"status": "alive"}

@app.route('/health')
def health():
    return {"status": "healthy"}

@app.route('/status')
def status():
    try:
        bot = AIPostBot()
        return {
            "status": "running",
            "environment_configured": len(bot.missing_vars) == 0,
            "missing_variables": bot.missing_vars,
            "scheduler_active": len(bot.missing_vars) == 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/test_post')
def test_post():
    try:
        bot = AIPostBot()
        if bot.missing_vars:
            return {"status": "error", "message": f"Missing environment variables: {', '.join(bot.missing_vars)}"}
        bot.create_and_post_ai_post()
        return {"status": "Test post sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    """Main entry point"""
    try:
        # Initialize bot
        bot = AIPostBot()
        
        # Only start scheduling if we have all required environment variables
        if not bot.missing_vars:
            bot.setup_schedule()
            # Start scheduler in background thread
            scheduler_thread = threading.Thread(target=bot.run_scheduler, daemon=True)
            scheduler_thread.start()
            logger.info("Bot scheduler started successfully")
        else:
            logger.info("Bot scheduler not started due to missing environment variables")
        
        # Get port from environment (default to 5000 for Replit)
        port = int(os.getenv('PORT', 5000))
        
        # Start Flask web server
        logger.info(f"Starting Flask web server on 0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        exit(1)

if __name__ == "__main__":
    main()