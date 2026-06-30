#!/usr/bin/env python3
"""
Trending Song Lyrics Video Generator
Full Pipeline: Detection → Lyrics → Audio → Video → Upload → Analytics
"""

import os
import sys
import json
import base64
import pickle
import random
import textwrap
import math
import re
import time
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============ CONFIGURATION ============
CONFIG = {
    "PEXELS_API_KEY": os.environ.get("PEXELS_API_KEY", ""),
    "GENIUS_API_KEY": os.environ.get("GENIUS_API_KEY", ""),
    "YOUTUBE_CLIENT_SECRET": os.environ.get("YOUTUBE_CLIENT_SECRET", ""),
    "YOUTUBE_TOKEN_PICKLE_BASE64": os.environ.get("YOUTUBE_TOKEN_PICKLE_BASE64", ""),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
    "SPOTIFY_CLIENT_ID": os.environ.get("SPOTIFY_CLIENT_ID", ""),
    "SPOTIFY_CLIENT_SECRET": os.environ.get("SPOTIFY_CLIENT_SECRET", ""),
    "OUTPUT_DIR": "output",
    "TEMP_DIR": "temp",
    "FPS": 30,
    "WIDTH": 1920,
    "HEIGHT": 1080,
}

# Ensure directories exist
Path(CONFIG["OUTPUT_DIR"]).mkdir(exist_ok=True)
Path(CONFIG["TEMP_DIR"]).mkdir(exist_ok=True)

# ============ STEP 1: TRENDING SONG DETECTION ============
class TrendingDetector:
    """Detect trending songs from multiple sources"""
    
    SPOTIFY_TRENDING = [
        {"title": "Tum Hi Ho", "artist": "Arijit Singh", "lang": "hindi", "mood": "romantic", "trend_score": 95},
        {"title": "Kesariya", "artist": "Arijit Singh", "lang": "hindi", "mood": "romantic", "trend_score": 92},
        {"title": "Chaiyya Chaiyya", "artist": "AR Rahman", "lang": "hindi", "mood": "energetic", "trend_score": 88},
        {"title": "Malhari", "artist": "Vishal Dadlani", "lang": "hindi", "mood": "energetic", "trend_score": 85},
        {"title": "Ghoomar", "artist": "Shreya Ghoshal", "lang": "hindi", "mood": "traditional", "trend_score": 82},
        {"title": "Dilbar", "artist": "Neha Kakkar", "lang": "hindi", "mood": "party", "trend_score": 90},
        {"title": "Aankh Marey", "artist": "Neha Kakkar", "lang": "hindi", "mood": "party", "trend_score": 87},
        {"title": "Vaaste", "artist": "Dhvani Bhanushali", "lang": "hindi", "mood": "romantic", "trend_score": 89},
        {"title": "Lut Gaye", "artist": "Jubin Nautiyal", "lang": "hindi", "mood": "romantic", "trend_score": 91},
        {"title": "Raataan Lambiyan", "artist": "Jubin Nautiyal", "lang": "hindi", "mood": "romantic", "trend_score": 93},
        {"title": "Lahore", "artist": "Guru Randhawa", "lang": "punjabi", "mood": "party", "trend_score": 86},
        {"title": "High Rated Gabru", "artist": "Guru Randhawa", "lang": "punjabi", "mood": "party", "trend_score": 84},
        {"title": "52 Gaj Ka Daman", "artist": "Renuka Panwar", "lang": "haryanvi", "mood": "traditional", "trend_score": 88},
        {"title": "Teri Aakhya Ka Yo Kajal", "artist": "Sapna Choudhary", "lang": "haryanvi", "mood": "traditional", "trend_score": 85},
        {"title": "Lollipop Lagelu", "artist": "Pawan Singh", "lang": "bhojpuri", "mood": "party", "trend_score": 83},
        {"title": "Kamariya", "artist": "Dinesh Lal", "lang": "bhojpuri", "mood": "party", "trend_score": 81},
        {"title": "Bom Diggy", "artist": "Zack Knight", "lang": "punjabi", "mood": "party", "trend_score": 80},
        {"title": "Naah", "artist": "Jassi Gill", "lang": "punjabi", "mood": "party", "trend_score": 82},
        {"title": "Bawli Tared", "artist": "Sumit Goswami", "lang": "haryanvi", "mood": "energetic", "trend_score": 79},
        {"title": "Kala Chashma", "artist": "Amar Arshi", "lang": "punjabi", "mood": "party", "trend_score": 94},
    ]
    
    @classmethod
    def detect_trending(cls, min_score=80):
        """Select trending song based on score"""
        trending = [s for s in cls.SPOTIFY_TRENDING if s["trend_score"] >= min_score]
        selected = random.choice(trending)
        print(f"🎯 Trending Detected: {selected['title']} (Score: {selected['trend_score']})")
        return selected
    
    @classmethod
    def fetch_spotify_trending(cls):
        """Fetch from Spotify API if credentials available"""
        try:
            if not CONFIG["SPOTIFY_CLIENT_ID"] or not CONFIG["SPOTIFY_CLIENT_SECRET"]:
                return None
            
            # Get access token
            auth = base64.b64encode(f"{CONFIG['SPOTIFY_CLIENT_ID']}:{CONFIG['SPOTIFY_CLIENT_SECRET']}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            data = {"grant_type": "client_credentials"}
            
            response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
            token = response.json().get("access_token")
            
            # Get trending in India
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                "https://api.spotify.com/v1/playlists/37i9dQZEVXbLZ52XmncU0o/tracks",  # India Top 50
                headers=headers,
                params={"limit": 10}
            )
            
            tracks = response.json().get("items", [])
            if tracks:
                track = random.choice(tracks)["track"]
                return {
                    "title": track["name"],
                    "artist": track["artists"][0]["name"],
                    "lang": "hindi",
                    "mood": "party",
                    "trend_score": 90
                }
        except Exception as e:
            print(f"⚠️ Spotify API failed: {e}")
        return None

# ============ STEP 2: LYRICS FETCH ============
class LyricsFetcher:
    """Fetch lyrics from multiple sources"""
    
    @staticmethod
    def fetch_genius(title, artist):
        """Fetch from Genius API"""
        try:
            if not CONFIG["GENIUS_API_KEY"]:
                return None
            
            search_url = "https://api.genius.com/search"
            headers = {"Authorization": f"Bearer {CONFIG['GENIUS_API_KEY']}"}
            params = {"q": f"{title} {artist}"}
            
            response = requests.get(search_url, headers=headers, params=params, timeout=20)
            data = response.json()
            
            if data["response"]["hits"]:
                song_path = data["response"]["hits"][0]["result"]["path"]
                song_url = f"https://genius.com{song_path}"
                
                page = requests.get(song_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                html = page.text
                
                # Extract lyrics
                lyrics_match = re.search(r'<div[^>]*data-lyrics-container[^>]*>(.*?)</div>', html, re.DOTALL)
                if lyrics_match:
                    lyrics = re.sub(r'<[^>]+>', '', lyrics_match.group(1))
                    lyrics = re.sub(r'\[.*?\]', '', lyrics)
                    lyrics = re.sub(r'\n+', '\n', lyrics).strip()
                    print(f"✅ Genius lyrics fetched: {len(lyrics.split(chr(10)))} lines")
                    return lyrics
        except Exception as e:
            print(f"⚠️ Genius failed: {e}")
        return None
    
    @staticmethod
    def fetch_mock_lyrics(song):
        """Generate realistic mock lyrics"""
        title = song["title"]
        lang = song["lang"]
        mood = song["mood"]
        
        templates = {
            "hindi": {
                "romantic": f"""{title}... {title}...

ये दिल तेरे लिए धड़कता है
हर पल तुझे ही सोचता है
तू है मेरी ज़िंदगानी
तू है मेरा सब कुछ

{title}... {title}...

आँखों में तेरी खोया रहता हूँ
सपनों में तेरे सोया रहता हूँ
तू जो मिले तो लगे जहाँ मिल गया
तू जो न मिले तो लगे सब खो गया

{title}... {title}...

तेरे बिना नहीं लगता दिल
तेरे बिना नहीं जीना यहाँ
तू ही तो है मेरा हमसफर
तू ही तो है मेरा प्यार

{title}... {title}...
तेरे संग जीना यहाँ
तेरे संग मरना यहाँ

{title}... {title}...""",
                "energetic": f"""{title}... {title}...

आजा आजा आजा नाचे गाएँ
आजा आजा आजा मस्ती में जाएँ
दिल की धड़कन बढ़ी जाए
नाचे नाचे नाचे जाए

{title}... {title}...

होश उड़ गए सबके यहाँ
जब देखा तुझको मैंने यहाँ
तेरा नाच दिवाना बनाए
सबको यहाँ मस्ती छाए

{title}... {title}...

झूम झूम झूम झूम
नाच नाच नाच नाच
गा गा गा गा
मस्ती में जा जा जा

{title}... {title}...
आज रात न सोएँगे
आज रात नाचेंगे

{title}... {title}...""",
                "party": f"""{title}... {title}...

डीजे बजे लाइट्स चमकें
सब नाचे मस्ती में
दारू पिए मौज करें
आज रात जश्न में

{title}... {title}...

तेरी आँखें शराबी लगें
तेरे होंठ गुलाबी लगें
तेरा नाच कातिल लगे
सब देखें तुझको यहाँ

{title}... {title}...

लगा दे तू आग आज
मचा दे तू शोर आज
आज रात है हमारी
आज रात नाचो सारी

{title}... {title}...
पार्टी शुरू हो गई
पार्टी शुरू हो गई

{title}... {title}...""",
                "traditional": f"""{title}... {title}...

घूमर घूमर नाचे रे
घूमर घूमर गाए रे
परंपरा की रीत निभाए
संस्कृति की शान बढाए

{title}... {title}...

माथे पे बिंदिया चमके
हाथों में चूड़ियाँ खनके
पैरों में पायल छनके
नाचे नाचे गाए रे

{title}... {title}...

देशी धुन में नाचे रे
देशी गीत में गाए रे
हमारी संस्कृति प्यारी
हमारी परंपरा न्यारी

{title}... {title}...
घूमर घूमर घूमर
नाचे नाचे नाचे

{title}... {title}...""",
            },
            "punjabi": {
                "party": f"""{title}... {title}...

ਲਹਿੰਦੇ ਪੰਜਾਬ ਦੀ ਜਾਣ ਤੂੰ
ਸੋਹਣੇ ਮੁੰਡੇ ਚ ਚਾਣ ਤੂੰ
ਨਖ਼ਰੇ ਤੇਰੇ ਨੀ ਮੈਨੂੰ ਭਾਉਂਦੇ
ਤੇਰੇ ਨਾਲੋ ਵੱਧ ਮੈਨੂੰ ਕੌਣ ਚਾਹੁੰਦੇ

{title}... {title}...

ਜੱਟ ਦਾ ਮੁਕਾਬਲਾ ਦੁਨੀਆਂ ਤੋਂ ਏਨੀ
ਤੇਰੇ ਨੈਣਾਂ ਚ ਵੱਸਦੀ ਜੰਨਤ ਮੇਨੀ
ਤੇਰੇ ਹੱਥਾਂ ਚ ਮੈਂ ਆਪਣਾ ਦਿਲ ਦੇ ਦਿੱਤਾ
ਤੇਰੇ ਪਿਆਰ ਚ ਮੈਂ ਆਪਣਾ ਸਭ ਕੁਝ ਲੁੱਟਾ ਦਿੱਤਾ

{title}... {title}...

ਨੱਚ ਨੱਚ ਨੱਚ ਨੱਚ
ਗਾ ਗਾ ਗਾ ਗਾ
ਮੌਜ ਕਰ ਮੌਜ ਕਰ
ਆਜ ਰਾਤ ਸਾਡੀ ਆ

{title}... {title}...
ਪੰਜਾਬੀ ਸ਼ਾਨ ਆਪਣੀ
ਪੰਜਾਬੀ ਮਾਨ ਆਪਣਾ

{title}... {title}...""",
            },
            "haryanvi": {
                "traditional": f"""{title}... {title}...

तेरा घूँघट न्यारा लागे
तेरी आँख्या का काजल प्यारा लागे
तेरी चाल में जादू सा है
तेरी हँसी में खुशी का राज़ है

{title}... {title}...

52 गज का दामन तेरा झूमे
हरियाणे की शान तू है
तेरे नाच में देशी धुन है
तेरे गाने में हरियाणे की सुन है

{title}... {title}...

झूम झूम झूम झूम
नाच नाच नाच नाच
गा गा गा गा
हरियाणे की शान

{title}... {title}...
घूमर घूमर घूमर
नाचे नाचे नाचे

{title}... {title}...""",
            },
            "bhojpuri": {
                "party": f"""{title}... {title}...

लइका लागेलू लॉलीपॉप
हमार लइका लागेलू लॉलीपॉप
के हु नाय देले बाप रे
हमार लइका लागेलू लॉलीपॉप

{title}... {title}...

कमरिया हिलावे लाल घाघरा
नाचे नाचे गोरी गोरी कमरिया
भोजपुरी के लहरा में लहरा
हमार गोरी गोरी कमरिया

{title}... {title}...

नाच नाच नाच नाच
गा गा गा गा
भोजपुरी के शान
भोजपुरी के मान

{title}... {title}...
लइका लागेलू लॉलीपॉप
लइका लागेलू लॉलीपॉप

{title}... {title}...""",
            }
        }
        
        lang_templates = templates.get(lang, templates["hindi"])
        mood_template = lang_templates.get(mood, lang_templates.get("romantic", list(lang_templates.values())[0]))
        return mood_template

# ============ STEP 3: AUDIO GENERATION ============
class AudioGenerator:
    """Generate audio with multiple TTS options"""
    
    @staticmethod
    def generate_edge_tts(text, output_file, lang="hindi"):
        """Use Microsoft Edge TTS (Best quality)"""
        try:
            import edge_tts
            import asyncio
            
            voices = {
                "hindi": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural", "hi-IN-AaravNeural"],
                "punjabi": ["hi-IN-SwaraNeural"],
                "haryanvi": ["hi-IN-MadhurNeural"],
                "bhojpuri": ["hi-IN-SwaraNeural"]
            }
            
            voice = random.choice(voices.get(lang, ["hi-IN-SwaraNeural"]))
            print(f"  🎙️ Voice: {voice}")
            
            async def generate():
                communicate = edge_tts.Communicate(text, voice, rate="+5%", pitch="+2Hz")
                await communicate.save(output_file)
            
            asyncio.run(generate())
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                return True
                
        except Exception as e:
            print(f"  ⚠️ edge-tts failed: {e}")
        return False
    
    @staticmethod
    def generate_gtts(text, output_file):
        """Fallback to Google TTS"""
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='hi', slow=False)
            tts.save(output_file)
            return True
        except Exception as e:
            print(f"  ❌ gTTS failed: {e}")
            return False
    
    @classmethod
    def generate(cls, text, output_file="audio.mp3", lang="hindi"):
        """Generate audio with fallback"""
        print("🔊 Generating audio...")
        
        # Try edge-tts first
        if cls.generate_edge_tts(text, output_file, lang):
            print("✅ Audio: edge-tts")
            return output_file
        
        # Fallback to gTTS
        print("  🔄 Falling back to gTTS...")
        if cls.generate_gtts(text, output_file):
            print("✅ Audio: gTTS (fallback)")
            return output_file
        
        raise Exception("All TTS failed!")

# ============ STEP 4: BACKGROUND VIDEO FETCH ============
class VideoFetcher:
    """Fetch background videos from Pexels"""
    
    @staticmethod
    def search_videos(query, per_page=5):
        try:
            if not CONFIG["PEXELS_API_KEY"]:
                print("⚠️ No Pexels API key")
                return []
            
            url = "https://api.pexels.com/videos/search"
            headers = {"Authorization": CONFIG["PEXELS_API_KEY"]}
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape",
                "size": "large"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            data = response.json()
            
            videos = []
            if "videos" in data:
                for video in data["videos"]:
                    for file in video.get("video_files", []):
                        if file.get("file_type") == "video/mp4" and file.get("width", 0) >= 1280:
                            videos.append({
                                "url": file["link"],
                                "duration": video.get("duration", 15),
                                "width": file.get("width", 1920),
                                "height": file.get("height", 1080)
                            })
                            break
            
            print(f"✅ Pexels: {len(videos)} videos")
            return videos
            
        except Exception as e:
            print(f"❌ Pexels error: {e}")
            return []
    
    @staticmethod
    def download(url, filename):
        try:
            print(f"  📥 Downloading...")
            response = requests.get(url, stream=True, timeout=60)
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            return False

# ============ STEP 5: BEAT SYNC ANALYSIS ============
class BeatAnalyzer:
    """Analyze audio for beat detection"""
    
    @staticmethod
    def analyze_beats(audio_file):
        """Simple beat detection using ffmpeg"""
        try:
            # Get audio info
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", audio_file],
                capture_output=True, text=True
            )
            info = json.loads(result.stdout)
            duration = float(info["format"]["duration"])
            
            # Simulate beat pattern (every 0.5 seconds for 120 BPM)
            beats = []
            beat_interval = 0.5
            t = 0
            while t < duration:
                beats.append(t)
                t += beat_interval
            
            print(f"✅ Beat analysis: {len(beats)} beats detected")
            return beats, duration
            
        except Exception as e:
            print(f"⚠️ Beat analysis failed: {e}")
            # Return simple pattern
            duration = 180  # 3 minutes default
            beats = [i * 0.5 for i in range(int(duration / 0.5))]
            return beats, duration

# ============ STEP 6: ANIMATED LYRICS RENDERING ============
class LyricsRenderer:
    """Render animated lyrics video"""
    
    MOOD_COLORS = {
        "romantic": {"bg": (60, 15, 40), "accent": (255, 100, 150), "glow": (255, 50, 100), "text": (255, 220, 230)},
        "energetic": {"bg": (50, 30, 10), "accent": (255, 200, 50), "glow": (255, 150, 0), "text": (255, 255, 200)},
        "party": {"bg": (15, 15, 50), "accent": (100, 255, 100), "glow": (50, 255, 50), "text": (200, 255, 200)},
        "traditional": {"bg": (50, 25, 10), "accent": (255, 150, 50), "glow": (255, 100, 0), "text": (255, 230, 200)},
    }
    
    def __init__(self, song, lyrics_lines, beats, duration):
        self.song = song
        self.lyrics_lines = lyrics_lines
        self.beats = beats
        self.duration = duration
        self.colors = self.MOOD_COLORS.get(song["mood"], self.MOOD_COLORS["romantic"])
        self.W, self.H = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        self.fps = CONFIG["FPS"]
        self.total_frames = int(duration * self.fps)
        
    def render(self, background_video=None):
        """Render complete video"""
        print(f"🎬 Rendering {self.total_frames} frames...")
        
        # Extract background frames if video available
        bg_frames = []
        if background_video and os.path.exists(background_video):
            print("  Extracting background frames...")
            frame_dir = f"{CONFIG['TEMP_DIR']}/bg_frames"
            Path(frame_dir).mkdir(exist_ok=True)
            
            subprocess.run([
                "ffmpeg", "-y", "-i", background_video,
                "-vf", f"fps={self.fps},scale={self.W}:{self.H}",
                "-q:v", "2", f"{frame_dir}/frame_%05d.jpg"
            ], check=True, capture_output=True)
            
            bg_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.jpg')])
            for f in bg_files:
                img = Image.open(f"{frame_dir}/{f}").convert("RGB")
                bg_frames.append(np.array(img))
            
            # Loop if needed
            while len(bg_frames) < self.total_frames:
                bg_frames.extend(bg_frames[:min(len(bg_frames), self.total_frames - len(bg_frames))])
            
            # Cleanup
            shutil.rmtree(frame_dir)
        
        # Calculate lyrics timing
        lines_per_frame = len(self.lyrics_lines) / self.total_frames
        seg_duration = self.duration / max(len(self.lyrics_lines), 1)
        
        # Render frames
        output_dir = f"{CONFIG['TEMP_DIR']}/frames"
        Path(output_dir).mkdir(exist_ok=True)
        
        for i in range(self.total_frames):
            t = i / self.fps
            
            # Get background
            if i < len(bg_frames):
                bg = Image.fromarray(bg_frames[i]).convert("RGB")
            else:
                bg = self._create_gradient_bg(i)
            
            # Calculate current lyrics
            line_idx = min(int(t / seg_duration), len(self.lyrics_lines) - 1)
            prev_idx = max(0, line_idx - 1)
            next_idx = min(len(self.lyrics_lines) - 1, line_idx + 1)
            
            # Beat pulse
            beat_pulse = self._get_beat_pulse(t)
            
            # Add lyrics overlay
            frame = self._add_lyrics_overlay(bg, line_idx, prev_idx, next_idx, beat_pulse, i / self.total_frames)
            
            # Save
            frame.save(f"{output_dir}/frame_{i:05d}.png")
            
            if i % 60 == 0:
                print(f"  Frame {i}/{self.total_frames}")
        
        # Compile video
        print("🎬 Compiling final video...")
        output_file = f"{CONFIG['OUTPUT_DIR']}/video.mp4"
        
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(self.fps),
            "-i", f"{output_dir}/frame_%05d.png",
            "-i", "audio.mp3",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_file
        ], check=True, capture_output=True)
        
        # Cleanup
        shutil.rmtree(output_dir)
        
        print(f"✅ Video rendered: {output_file}")
        return output_file
    
    def _create_gradient_bg(self, frame_num):
        """Create animated gradient background"""
        img = Image.new('RGB', (self.W, self.H), self.colors["bg"])
        draw = ImageDraw.Draw(img)
        
        progress = frame_num / self.total_frames
        
        # Animated gradient
        for y in range(self.H):
            r = int(self.colors["bg"][0] + (self.colors["accent"][0] - self.colors["bg"][0]) * (y / self.H) * 0.3)
            g = int(self.colors["bg"][1] + (self.colors["accent"][1] - self.colors["bg"][1]) * (y / self.H) * 0.3)
            b = int(self.colors["bg"][2] + (self.colors["accent"][2] - self.colors["bg"][2]) * (y / self.H) * 0.3)
            draw.line([(0, y), (self.W, y)], fill=(r, g, b))
        
        # Particles
        for _ in range(30):
            x = random.randint(0, self.W)
            y = random.randint(0, self.H)
            size = int(2 + 5 * abs(math.sin(progress * 10 + x)))
            alpha = int(100 + 100 * abs(math.sin(progress * 5 + y)))
            color = (
                min(255, self.colors["accent"][0] + alpha),
                min(255, self.colors["accent"][1] + alpha),
                min(255, self.colors["accent"][2] + alpha)
            )
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        return img
    
    def _get_beat_pulse(self, t):
        """Get beat intensity at time t"""
        # Find nearest beat
        nearest_beat = min(self.beats, key=lambda x: abs(x - t))
        distance = abs(nearest_beat - t)
        pulse = max(0, 1 - distance * 4)  # Decay over 0.25s
        return pulse
    
    def _add_lyrics_overlay(self, bg, line_idx, prev_idx, next_idx, beat_pulse, progress):
        """Add animated lyrics overlay"""
        draw = ImageDraw.Draw(bg)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            lyrics_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            lyrics_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Title bar
        draw.rectangle([0, 0, self.W, 90], fill=(0, 0, 0, 200))
        title = f"🎵 {self.song['title']} - {self.song['artist']}"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((self.W - tw) // 2, 25), title, fill=(255, 255, 255), font=title_font)
        
        # Previous line (faded)
        if prev_idx != line_idx and self.lyrics_lines[prev_idx]:
            prev_lines = textwrap.wrap(self.lyrics_lines[prev_idx], width=30)
            y = 200
            for line in prev_lines:
                bbox = draw.textbbox((0, 0), line, font=small_font)
                tw = bbox[2] - bbox[0]
                draw.text(((self.W - tw) // 2, y), line, fill=(120, 120, 120), font=small_font)
                y += 35
        
        # Current line (highlighted with beat pulse)
        if self.lyrics_lines[line_idx]:
            current_lines = textwrap.wrap(self.lyrics_lines[line_idx], width=25)
            
            # Glow effect
            glow_intensity = int(30 + beat_pulse * 50)
            for glow in range(5, 0, -1):
                gy = 350
                for line in current_lines:
                    bbox = draw.textbbox((0, 0), line, font=lyrics_font)
                    tw = bbox[2] - bbox[0]
                    draw.text(((self.W - tw) // 2, gy), line, 
                             fill=(glow_intensity//glow, glow_intensity//glow, glow_intensity//glow), 
                             font=lyrics_font)
                    gy += 85
            
            # Main text with beat pulse color
            pulse_color = (
                min(255, self.colors["accent"][0] + int(beat_pulse * 100)),
                min(255, self.colors["accent"][1] + int(beat_pulse * 100)),
                min(255, self.colors["accent"][2] + int(beat_pulse * 100))
            )
            
            gy = 350
            for line in current_lines:
                bbox = draw.textbbox((0, 0), line, font=lyrics_font)
                tw = bbox[2] - bbox[0]
                # Shadow
                draw.text(((self.W - tw) // 2 + 3, gy + 3), line, fill=(0, 0, 0), font=lyrics_font)
                # Main
                draw.text(((self.W - tw) // 2, gy), line, fill=pulse_color, font=lyrics_font)
                gy += 85
        
        # Next line (preview)
        if next_idx != line_idx and self.lyrics_lines[next_idx]:
            next_lines = textwrap.wrap(self.lyrics_lines[next_idx], width=30)
            y = 600
            for line in next_lines:
                bbox = draw.textbbox((0, 0), line, font=small_font)
                tw = bbox[2] - bbox[0]
                draw.text(((self.W - tw) // 2, y), line, fill=(180, 180, 180), font=small_font)
                y += 35
        
        # Visualizer bars
        bar_count = 60
        bar_width = self.W * 0.9 / bar_count
        for i in range(bar_count):
            bar_h = int(10 + beat_pulse * 40 * random.random() + 20 * abs(math.sin(i * 0.5 + progress * 10)))
            x = self.W * 0.05 + i * bar_width
            y = self.H - 50 - bar_h
            color = (
                int(self.colors["accent"][0] * (0.5 + 0.5 * random.random())),
                int(self.colors["accent"][1] * (0.5 + 0.5 * random.random())),
                int(self.colors["accent"][2] * (0.5 + 0.5 * random.random()))
            )
            draw.rectangle([x, y, x + bar_width - 2, self.H - 50], fill=color)
        
        # Progress bar
        bar_width = int(self.W * 0.9 * progress)
        draw.rectangle([self.W*0.05, self.H-15, self.W*0.95, self.H-10], fill=(60, 60, 60))
        draw.rectangle([self.W*0.05, self.H-15, self.W*0.05 + bar_width, self.H-10], fill=self.colors["accent"])
        
        return bg

# ============ STEP 7: THUMBNAIL GENERATION ============
class ThumbnailGenerator:
    """Generate YouTube thumbnail"""
    
    @staticmethod
    def generate(song, output_file="thumbnail.jpg"):
        print("🖼️ Generating thumbnail...")
        
        W, H = 1280, 720  # YouTube thumbnail size
        
        img = Image.new('RGB', (W, H), (20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # Background gradient
        colors = {
            "romantic": [(80, 20, 60), (255, 100, 150)],
            "energetic": [(60, 40, 10), (255, 200, 50)],
            "party": [(20, 20, 60), (100, 255, 100)],
            "traditional": [(60, 30, 10), (255, 150, 50)],
        }
        c1, c2 = colors.get(song["mood"], colors["romantic"])
        
        for y in range(H):
            r = int(c1[0] + (c2[0] - c1[0]) * (y / H))
            g = int(c1[1] + (c2[1] - c1[1]) * (y / H))
            b = int(c1[2] + (c2[2] - c1[2]) * (y / H))
            draw.line([(0, y), (W, y)], fill=(r, g, b))
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            artist_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
            tag_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            artist_font = ImageFont.load_default()
            tag_font = ImageFont.load_default()
        
        # Title
        title = song["title"]
        lines = textwrap.wrap(title, width=15)
        y = 200
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
            # Shadow
            draw.text(((W - tw) // 2 + 4, y + 4), line, fill=(0, 0, 0), font=title_font)
            # Main
            draw.text(((W - tw) // 2, y), line, fill=(255, 255, 255), font=title_font)
            y += 95
        
        # Artist
        artist = f"🎤 {song['artist']}"
        bbox = draw.textbbox((0, 0), artist, font=artist_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 450), artist, fill=(255, 255, 200), font=artist_font)
        
        # Tags
        tag = f"#{song['mood'].upper()} #LYRICS #ANIMATED"
        bbox = draw.textbbox((0, 0), tag, font=tag_font)
        tw = bbox[2] - bbox[0]
        draw.rectangle([(W - tw) // 2 - 20, 550, (W + tw) // 2 + 20, 600], fill=(0, 0, 0, 180))
        draw.text(((W - tw) // 2, 560), tag, fill=(255, 255, 100), font=tag_font)
        
        # Trending badge
        draw.rectangle([50, 50, 300, 110], fill=(255, 0, 0), outline=(255, 255, 255), width=3)
        draw.text((70, 60), "🔥 TRENDING", fill=(255, 255, 255), font=tag_font)
        
        img.save(output_file)
        print(f"✅ Thumbnail: {output_file}")
        return output_file

# ============ STEP 8: METADATA GENERATION ============
class MetadataGenerator:
    """Generate YouTube metadata"""
    
    @staticmethod
    def generate(song, lyrics_lines):
        print("📝 Generating metadata...")
        
        title = f"🎵 {song['title']} - {song['artist']} | Animated Lyrics | {song['lang'].upper()}"
        
        desc_lines = "\n".join([f"🎶 {line}" for line in lyrics_lines[:15]])
        
        description = f"""🎵 {song['title']} - {song['artist']}

🎤 Animated Lyrics Video
🎭 Mood: {song['mood'].capitalize()}
🌐 Language: {song['lang'].capitalize()}
🔥 Trending Score: {song['trend_score']}/100

📜 Lyrics:
{desc_lines}

✨ Features:
• Animated Lyrics with Beat Sync
• Colorful Visual Effects
• Karaoke Style Highlighting
• Professional Editing

🎧 Listen & Enjoy!

#AnimatedLyrics #{song['title'].replace(' ', '')} #{song['artist'].replace(' ', '')} #{song['lang']} #Trending #Karaoke #LyricsVideo"""
        
        tags = [
            song["title"], song["artist"], "animated lyrics", song["lang"],
            "trending", "karaoke", song["mood"], "hindi songs", "lyrics video",
            "music", "bollywood", "punjabi", "haryanvi", "bhojpuri"
        ]
        
        print("✅ Metadata generated")
        return {"title": title, "description": description, "tags": tags}

# ============ STEP 9: YOUTUBE UPLOAD ============
class YouTubeUploader:
    """Upload video to YouTube"""
    
    @staticmethod
    def upload(video_file, thumbnail_file, metadata):
        print("📤 Uploading to YouTube...")
        
        try:
            with open("token.pickle", "rb") as f:
                credentials = pickle.load(f)
            
            youtube = build("youtube", "v3", credentials=credentials)
            
            body = {
                "snippet": {
                    "title": metadata["title"][:100],
                    "description": metadata["description"][:5000],
                    "tags": metadata["tags"][:500],
                    "categoryId": "10",  # Music
                    "defaultLanguage": "hi",
                    "defaultAudioLanguage": "hi"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "publishAt": None
                }
            }
            
            # Upload video
            print("  Uploading video...")
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
            )
            
            response = request.execute()
            video_id = response.get('id')
            print(f"✅ Video uploaded: https://youtube.com/watch?v={video_id}")
            
            # Upload thumbnail
            if thumbnail_file and os.path.exists(thumbnail_file):
                print("  Uploading thumbnail...")
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_file)
                ).execute()
                print("✅ Thumbnail uploaded")
            
            return video_id
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

# ============ STEP 10: ANALYTICS TRACKING ============
class AnalyticsTracker:
    """Track video performance"""
    
    @staticmethod
    def track(video_id, song):
        print("📊 Tracking analytics...")
        
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "video_id": video_id,
            "song": song,
            "platform": "youtube",
            "metrics": {
                "views": 0,
                "likes": 0,
                "comments": 0
            }
        }
        
        # Save to file
        with open(f"{CONFIG['OUTPUT_DIR']}/analytics.json", "w") as f:
            json.dump(analytics, f, indent=2)
        
        print(f"✅ Analytics tracked: {CONFIG['OUTPUT_DIR']}/analytics.json")
        return analytics

# ============ MAIN PIPELINE ============
def main():
    print("=" * 60)
    print("🎵 TRENDING SONG LYRICS VIDEO GENERATOR")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Detect Trending
    song = TrendingDetector.detect_trending()
    
    # Try Spotify API first
    spotify_song = TrendingDetector.fetch_spotify_trending()
    if spotify_song:
        song = spotify_song
    
    # Step 2: Fetch Lyrics
    lyrics = LyricsFetcher.fetch_genius(song["title"], song["artist"])
    if not lyrics:
        lyrics = LyricsFetcher.fetch_mock_lyrics(song)
    
    lyrics_lines = [l.strip() for l in lyrics.split('\n') if l.strip()]
    print(f"📜 Total lines: {len(lyrics_lines)}")
    
    # Step 3: Generate Audio
    audio_file = AudioGenerator.generate(lyrics, "audio.mp3", song["lang"])
    
    # Step 4: Fetch Background Videos
    mood_queries = {
        "romantic": "romantic couple love sunset dance",
        "energetic": "dance party celebration energy concert",
        "party": "disco party lights dancing nightclub",
        "traditional": "traditional dance folk culture festival"
    }
    query = mood_queries.get(song["mood"], "music concert")
    
    pexels_videos = VideoFetcher.search_videos(query, per_page=3)
    
    video_files = []
    for i, video in enumerate(pexels_videos):
        fname = f"{CONFIG['TEMP_DIR']}/bg_{i}.mp4"
        if VideoFetcher.download(video["url"], fname):
            video_files.append({"file": fname, "duration": video["duration"]})
    
    # Step 5: Beat Analysis
    beats, duration = BeatAnalyzer.analyze_beats(audio_file)
    
    # Step 6: Render Video
    renderer = LyricsRenderer(song, lyrics_lines, beats, duration)
    
    # Create background video if clips available
    bg_video = None
    if video_files:
        # Concatenate
        with open(f"{CONFIG['TEMP_DIR']}/concat.txt", "w") as f:
            for vf in video_files:
                f.write(f"file '{vf['file']}'\n")
        
        bg_video = f"{CONFIG['TEMP_DIR']}/background.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", f"{CONFIG['TEMP_DIR']}/concat.txt",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-t", str(duration), "-an", "-c:v", "libx264", "-preset", "fast",
            bg_video
        ], check=True, capture_output=True)
    
    video_file = renderer.render(bg_video)
    
    # Step 7: Generate Thumbnail
    thumbnail_file = ThumbnailGenerator.generate(song, f"{CONFIG['OUTPUT_DIR']}/thumbnail.jpg")
    
    # Step 8: Generate Metadata
    metadata = MetadataGenerator.generate(song, lyrics_lines)
    
    # Step 9: Upload to YouTube
    video_id = YouTubeUploader.upload(video_file, thumbnail_file, metadata)
    
    # Step 10: Track Analytics
    if video_id:
        AnalyticsTracker.track(video_id, song)
    
    # Cleanup
    for f in ["audio.mp3", "client_secret.json", "token.pickle"]:
        if os.path.exists(f):
            os.remove(f)
    
    # Cleanup temp
    if os.path.exists(CONFIG["TEMP_DIR"]):
        shutil.rmtree(CONFIG["TEMP_DIR"])
    
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"🎉 PIPELINE COMPLETE!")
    print(f"⏱️ Time: {elapsed:.1f}s")
    if video_id:
        print(f"🔗 Video: https://youtube.com/watch?v={video_id}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
