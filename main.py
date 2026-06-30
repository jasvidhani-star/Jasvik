#!/usr/bin/env python3
"""
Trending Song Lyrics Video Generator
Full Pipeline: Detection -> Lyrics -> Audio -> Video -> Upload -> Analytics
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
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ============ CONFIGURATION ============
CONFIG = {
    "PEXELS_API_KEY": os.environ.get("PEXELS_API_KEY", ""),
    "YOUTUBE_CLIENT_SECRET": os.environ.get("YOUTUBE_CLIENT_SECRET", ""),
    "YOUTUBE_TOKEN_PICKLE_BASE64": os.environ.get("YOUTUBE_TOKEN_PICKLE_BASE64", ""),
    "OUTPUT_DIR": "output",
    "TEMP_DIR": "temp",
    "FPS": 30,
    "WIDTH": 1920,
    "HEIGHT": 1080,
    "SHORTS_WIDTH": 1080,
    "SHORTS_HEIGHT": 1920,
}

Path(CONFIG["OUTPUT_DIR"]).mkdir(exist_ok=True)
Path(CONFIG["TEMP_DIR"]).mkdir(exist_ok=True)

# ============ HINDI KIDS STORIES DATABASE ============
STORIES = [
    {
        "title": "Chaalak Khargosh aur Dheemi Kachhua",
        "title_en": "The Clever Rabbit and Slow Tortoise",
        "moral": "Dheere aur sthir jeetate hain",
        "category": "moral",
        "characters": ["Khargosh", "Kachhua"],
        "color_theme": "forest",
        "content": """Ek samay ki baat hai, ek ghane jangal mein ek chaalak khargosh rehta tha. Vah bahut tez daud sakta tha aur hamesha apni gati par garv karta tha.

Usi jangal mein ek dheemi kachhua bhi rehta tha. Kachhua har kaam dheere-dheere karta tha.

Ek din khargosh ne kachhue se kaha, "Are kachhue, tum to bahut dheere ho! Kya tum kabhi daud sakte ho?"

Kachhua muskuraya aur bola, "Haan, main dheera hoon lekin main sthir hoon. Chalo, ek daud lagate hain."

Khargosh hansa aur kaha, "Theek hai! Kaun pehle us pahadi tak pahunchega, vahi jeetega."

Daud shuru hui. Khargosh tezi se aage nikal gaya. Thodi door jaakar usne peeche dekha, kachhua kahi dikhai nahi diya.

Khargosh socha, "Kachhua to bahut peeche hai. Main thoda aaram kar leta hoon."

Khargosh ek ped ke neeche so gaya.

Kachhua dheere-dheere chalta raha. Usne khargosh ko sote hue dekha lekin ruka nahi.

Kachhua lagataar chalta raha aur ant mein pahadi tak pahunch gaya.

Jab khargosh ki aankh khuli, to vah jaldi se utha aur dauda. Lekin jab vah pahuncha, kachhua pehle se hi vahan tha.

Khargosh ne kaha, "Main haar gaya! Tum jeete kachhue."

Kachhua bola, "Dheere aur sthir jeetate hain. Gati nahi, dridhta mayne rakhti hai."

Sab janwaron ne kachhue ki jeet ka jashn manaya. Khargosh ne apni ghamand chhod di.

Tabhi se kahawat bani: Dheere-dheere re mana, dheere sab kuchh hoe."""
    },
    {
        "title": "Laalchi Kauva aur Jutha Roti",
        "title_en": "The Greedy Crow and the Stale Bread",
        "moral": "Laalach buri bala hai",
        "category": "moral",
        "characters": ["Kauva", "Lomdi"],
        "color_theme": "village",
        "content": """Ek gaon mein ek kauva rehta tha. Vah bahut laalchi tha. Hamesha aur se adhik khana chahta tha.

Ek din use ek roti mili. Roti thodi jutthi thi lekin kaue ko bahut pasand aayi.

Vah socha, "Main ise kisi ko nahi doonga. Main akele khaunga."

Kaue ne roti apni chonch mein dabai aur ek ped ki dali par baith gaya.

Tabhi ek chaalak lomdi vahan se guzri. Usne kaue ko roti dekhi.

Lomdi ne socha, "Mujhe yah roti chahiye."

Lomdi ne kaue se kaha, "He kaue bhai, tumhari aawaz bahut surili hai. Kya tum ek geet suna sakte ho?"

Kauva khush ho gaya. Usne socha, "Lomdi meri tarif kar rahi hai. Main gata hoon."

Jaise hi kaue ne munh khola, roti neeche gir gayi.

Lomdi ne turant roti uthai aur bhaag gayi.

Kauva rone laga. Use apni laalach par pachhtava hua.

Ek panchhi ne kaha, "Laalach buri bala hai. Jo aapke paas hai, usme santosh karo."

Kaue ne seekh li: Kabhi bhi laalchi mat bano."""
    },
    {
        "title": "Bahadur Chooha aur Sher",
        "title_en": "The Brave Mouse and the Lion",
        "moral": "Koi bhi chhota nahi hota",
        "category": "courage",
        "characters": ["Chooha", "Sher"],
        "color_theme": "jungle",
        "content": """Ek vishal jangal mein ek sher rehta tha. Vah jangal ka raja tha. Sabhi janwar usse darte the.

Ek din sher so raha tha. Ek chhota chooha vahan se guzra.

Choohe ne dekha ki sher so raha hai. Vah dara hua tha lekin sher ke paas se jana zaroori tha.

Chooha dheere-dheere chal raha tha. Achank uska pair sher ki poonchh par pad gaya.

Sher jaag gaya. Usne choohe ko dekha aur gusse mein dahada.

"Tumne mujhe jagaya! Ab main tumhe kha jaunga!" sher bola.

Chooha kaanpata hua bola, "He maharaj, kripya mujhe maaf kar do. Maine jaanbujhkar nahi kiya."

Sher hansa, "Tum jaise chhote choohe se mujhe kya madad milegi?"

Chooha bola, "Maharaj, chhota ho ya bada, har koi kisi na kisi kaam aa sakta hai."

Sher muskuraya aur choohe ko chhod diya.

Kuchh dino baad, sher ek jaal mein phans gaya. Vah bahut dahada lekin koi nahi aaya.

Chooha vahan se guzra. Usne sher ko jaal mein phansa dekha.

Choohe ne turant jaal kaatna shuru kiya. Dheere-dheere usne jaal kaat diya.

Sher azaad ho gaya. Usne choohe ko gale lagaya.

Sher bola, "Tumne meri jaan bachai. Tum sach mein bahadur ho."

Chooha muskuraya, "Maine kaha tha na, koi bhi chhota nahi hota."

Tabhi se sab janwar ek-doosre ka samman karne lage."""
    },
    {
        "title": "Mehnati Chinti aur Aalasi Tidda",
        "title_en": "The Hardworking Ant and Lazy Grasshopper",
        "moral": "Mehnat ka fal meetha hota hai",
        "category": "moral",
        "characters": ["Chinti", "Tidda"],
        "color_theme": "meadow",
        "content": """Ek sundar maidan mein ek chinti ka parivar rehta tha. Ve sab bahut mehnati the.

Garmiyon mein jab dhoop chamakti thi, chintiyan khane ka sangrah karti thin.

Usi maidan mein ek tidda rehta tha. Vah bahut aalasi tha. Sara din gata aur nachata rehta.

Chintiyon ne tidde se kaha, "Bhai, garmi mein khana ikattha kar lo. Sardi mein bhookh lagegi."

Tidda hansa, "Abhi to bahut samay hai. Main baad mein kar loonga."

Chintiyan din-raat mehnat karti rahin. Unhone bahut sara anaaj ikattha kiya.

Tidda har roz gata, "Chhoti-chhoti chintiyan, kaam mein lagi rahati hain."

Jaise hi barish ka mausam aaya, sab kuchh bheeg gaya. Phir sardi aayi.

Maidan mein sab kuchh sookh gaya. Koi patta, koi dana nahi bacha.

Tidda bhookha tha. Usne chintiyon ke ghar jaakar dekha, vahan anaaj bhara pada tha.

Tidda sharminda hokar bola, "Mujhe maaf kar do. Maine tumhari baat nahi mani."

Chintiyon ne daya dikhayi. Unhone tidde ko khana diya.

Tidda ne kaha, "Maine seekh liya. Mehnat ka fal meetha hota hai."

Tabhi se tidda bhi mehnati ban gaya."""
    },
    {
        "title": "Chamakdaar Taare aur Andhera Aakaash",
        "title_en": "The Shining Stars and the Dark Sky",
        "moral": "Har andhere ke baad ujaala aata hai",
        "category": "inspirational",
        "characters": ["Chhota Taara", "Chaand"],
        "color_theme": "night",
        "content": """Aakaash mein hazaaron taare rehte the. Ve raat ko chamakate aur sabko roshni dete.

Ek chhota taara tha jo bahut kamzor tha. Uski roshni bahut dhimi thi.

Chhote taare ne chaand se poocha, "Main kyon itna kamzor hoon?"

Chaand muskuraya, "Tum abhi chhote ho. Samay ke saath tum bhi chamakoge."

Ek raat bahut baadal aa gaye. Sab taare baadalon ke peeche chhip gaye.

Andhera ho gaya. Dharti par sab dar gaye.

Chhote taare ne socha, "Mujhe kuchh karna hoga."

Chhote taare ne apni saari taakat lagai. Dheere-dheere vah chamakne laga.

Uski roshni baadalon se hokar dharti tak pahunchi.

Logon ne dekha, "Wah! Ek taara chamak raha hai!"

Chhote taare ki roshni se doosaron taaron ko bhi himmat mili. Ve bhi chamakne lage.

Baadal hat gaye. Poora aakaash chamak utha.

Chaand ne kaha, "Dekha? Har andhere ke baad ujaala aata hai."

Chhota taara khush ho gaya. Usne seekha ki kabhi haar nahi manani chahiye.

Tabhi se vah sabse chamakdaar taara ban gaya."""
    }
]

# ============ COLOR THEMES FOR STORIES ============
COLOR_THEMES = {
    "forest": {
        "bg": [(20, 60, 20), (10, 40, 10)],
        "accent": (100, 255, 100),
        "glow": (50, 255, 50),
        "text": (255, 255, 220),
        "highlight": (255, 255, 150),
        "particle_colors": [(100, 255, 100), (50, 200, 50), (150, 255, 150)],
    },
    "village": {
        "bg": [(60, 40, 20), (40, 25, 10)],
        "accent": (255, 200, 100),
        "glow": (255, 150, 50),
        "text": (255, 240, 200),
        "highlight": (255, 220, 150),
        "particle_colors": [(255, 200, 100), (200, 150, 50), (255, 180, 80)],
    },
    "jungle": {
        "bg": [(10, 50, 20), (5, 35, 15)],
        "accent": (255, 180, 50),
        "glow": (255, 150, 0),
        "text": (255, 250, 200),
        "highlight": (255, 220, 100),
        "particle_colors": [(255, 200, 50), (200, 150, 30), (255, 180, 60)],
    },
    "meadow": {
        "bg": [(40, 60, 20), (25, 45, 10)],
        "accent": (200, 255, 100),
        "glow": (150, 255, 50),
        "text": (240, 255, 220),
        "highlight": (220, 255, 150),
        "particle_colors": [(200, 255, 100), (150, 220, 50), (180, 255, 80)],
    },
    "night": {
        "bg": [(10, 10, 40), (5, 5, 25)],
        "accent": (150, 200, 255),
        "glow": (100, 150, 255),
        "text": (220, 230, 255),
        "highlight": (180, 200, 255),
        "particle_colors": [(150, 200, 255), (100, 150, 255), (200, 220, 255)],
    },
}

# ============ STEP 1: STORY SELECTION ============
class StorySelector:
    """Select a story from the database"""

    @classmethod
    def select_story(cls, category: Optional[str] = None) -> Dict:
        """Select a story, optionally by category"""
        if category:
            stories = [s for s in STORIES if s["category"] == category]
            if not stories:
                stories = STORIES
        else:
            stories = STORIES

        selected = random.choice(stories)
        print(f"Story Selected: {selected['title']}")
        print(f"   Category: {selected['category']}")
        print(f"   Moral: {selected['moral']}")
        print(f"   Characters: {', '.join(selected['characters'])}")
        return selected

    @classmethod
    def list_stories(cls) -> List[Dict]:
        """List all available stories"""
        return [{"title": s["title"], "category": s["category"], "moral": s["moral"]} for s in STORIES]

# ============ STEP 2: HINDI TTS AUDIO GENERATION ============
class HindiTTSGenerator:
    """Generate Hindi audio using edge-tts with kid-friendly voices"""

    HINDI_VOICES = [
        "hi-IN-SwaraNeural",
        "hi-IN-MadhurNeural",
        "hi-IN-AaravNeural",
    ]

    @classmethod
    def generate(cls, text: str, output_file: str = "audio.mp3", voice: Optional[str] = None) -> str:
        """Generate Hindi audio with edge-tts"""
        print("Generating Hindi audio...")

        if not voice:
            voice = random.choice(cls.HINDI_VOICES)

        print(f"   Voice: {voice}")

        try:
            import edge_tts

            async def _generate():
                communicate = edge_tts.Communicate(
                    text, 
                    voice, 
                    rate="-5%",
                    pitch="+5Hz",
                    volume="+10%"
                )
                await communicate.save(output_file)

            asyncio.run(_generate())

            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                print(f"Audio generated: {output_file}")
                return output_file

        except Exception as e:
            print(f"edge-tts failed: {e}")

        print("   Falling back to gTTS...")
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='hi', slow=False)
            tts.save(output_file)
            print(f"Audio generated (gTTS fallback): {output_file}")
            return output_file
        except Exception as e:
            print(f"gTTS also failed: {e}")
            raise

# ============ STEP 3: AUDIO ANALYSIS ============
class AudioAnalyzer:
    """Analyze audio for duration and simple beat patterns"""

    @staticmethod
    def analyze(audio_file: str) -> Tuple[List[float], float]:
        """Get audio duration and create word-timing beats"""
        print("Analyzing audio...")

        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", audio_file],
                capture_output=True, text=True, timeout=10
            )
            info = json.loads(result.stdout)
            duration = float(info["format"]["duration"])

            beats = [i * 2.0 for i in range(int(duration / 2.0) + 1)]

            print(f"Duration: {duration:.1f}s, Beats: {len(beats)}")
            return beats, duration

        except Exception as e:
            print(f"Analysis failed: {e}")
            duration = 120
            beats = [i * 2.0 for i in range(60)]
            return beats, duration

# ============ STEP 4: BACKGROUND VIDEO FETCH ============
class BackgroundVideoFetcher:
    """Fetch kid-friendly background videos from Pexels"""

    THEME_QUERIES = {
        "forest": "forest animals nature kids cartoon",
        "village": "village india countryside kids",
        "jungle": "jungle animals lion elephant kids",
        "meadow": "meadow flowers butterflies kids nature",
        "night": "night sky stars moon kids dreamy",
    }

    @classmethod
    def fetch(cls, theme: str, duration: float) -> Optional[str]:
        """Fetch and prepare background video"""
        print("Fetching background video...")

        if not CONFIG["PEXELS_API_KEY"]:
            print("No Pexels API key, using animated gradient background")
            return None

        query = cls.THEME_QUERIES.get(theme, "kids animated nature")

        try:
            url = "https://api.pexels.com/videos/search"
            headers = {"Authorization": CONFIG["PEXELS_API_KEY"]}
            params = {
                "query": query,
                "per_page": 3,
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
                                "duration": video.get("duration", 15)
                            })
                            break

            if not videos:
                print("No videos found, using animated gradient")
                return None

            video_files = []
            for i, v in enumerate(videos[:2]):
                fname = f"{CONFIG['TEMP_DIR']}/bg_{i}.mp4"
                print(f"   Downloading video {i+1}...")
                r = requests.get(v["url"], stream=True, timeout=60)
                with open(fname, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                video_files.append({"file": fname, "duration": v["duration"]})

            if len(video_files) > 1:
                with open(f"{CONFIG['TEMP_DIR']}/concat.txt", "w") as f:
                    for vf in video_files:
                        f.write(f"file '{vf['file']}'\n")

                bg_file = f"{CONFIG['TEMP_DIR']}/background.mp4"
                subprocess.run([
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", f"{CONFIG['TEMP_DIR']}/concat.txt",
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                    "-t", str(duration), "-an", "-c:v", "libx264", "-preset", "fast",
                    bg_file
                ], check=True, capture_output=True)

                return bg_file
            elif video_files:
                bg_file = f"{CONFIG['TEMP_DIR']}/background.mp4"
                subprocess.run([
                    "ffmpeg", "-y", "-i", video_files[0]["file"],
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                    "-t", str(duration), "-an", "-c:v", "libx264", "-preset", "fast",
                    bg_file
                ], check=True, capture_output=True)
                return bg_file

        except Exception as e:
            print(f"Video fetch failed: {e}")

        return None

# ============ STEP 5: STORY VIDEO RENDERER ============
class StoryVideoRenderer:
    """Render animated story video with word-by-word highlighting"""

    def __init__(self, story: Dict, beats: List[float], duration: float):
        self.story = story
        self.beats = beats
        self.duration = duration
        self.colors = COLOR_THEMES.get(story["color_theme"], COLOR_THEMES["forest"])
        self.W, self.H = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        self.fps = CONFIG["FPS"]
        self.total_frames = int(duration * self.fps)

        self.sentences = [s.strip() for s in story["content"].split("\n") if s.strip()]
        self.words = []
        self._build_word_timings()

    def _build_word_timings(self):
        """Calculate timing for each word"""
        all_text = " ".join(self.sentences)
        words = all_text.split()

        if not words:
            return

        time_per_word = self.duration / len(words)
        current_time = 0

        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word).strip()
            if clean_word:
                self.words.append({
                    "word": clean_word,
                    "start_time": current_time,
                    "end_time": current_time + time_per_word,
                    "duration": time_per_word
                })
                current_time += time_per_word

    def _get_current_word(self, t: float) -> Optional[Dict]:
        """Get the word at current time"""
        for wd in self.words:
            if wd["start_time"] <= t < wd["end_time"]:
                return wd
        return None

    def _get_beat_pulse(self, t: float) -> float:
        """Get visual pulse intensity at time t"""
        nearest = min(self.beats, key=lambda x: abs(x - t))
        distance = abs(nearest - t)
        return max(0, 1 - distance * 3)

    def _create_background(self, frame_num: int, bg_frames: Optional[List] = None) -> Image.Image:
        """Create animated background"""
        if bg_frames and frame_num < len(bg_frames):
            return Image.fromarray(bg_frames[frame_num]).convert("RGB")

        img = Image.new('RGB', (self.W, self.H), self.colors["bg"][0])
        draw = ImageDraw.Draw(img)

        progress = frame_num / max(self.total_frames, 1)

        for y in range(self.H):
            ratio = y / self.H
            r = int(self.colors["bg"][0][0] + (self.colors["bg"][1][0] - self.colors["bg"][0][0]) * ratio)
            g = int(self.colors["bg"][0][1] + (self.colors["bg"][1][1] - self.colors["bg"][0][1]) * ratio)
            b = int(self.colors["bg"][0][2] + (self.colors["bg"][1][2] - self.colors["bg"][0][2]) * ratio)
            draw.line([(0, y), (self.W, y)], fill=(r, g, b))

        for i in range(50):
            x = int((self.W * (i / 50) + frame_num * 2) % self.W)
            y = int((self.H * 0.3 * (i % 7) + frame_num * 1.5) % self.H)
            size = int(3 + 5 * abs(math.sin(progress * 6 + i)))
            color = random.choice(self.colors["particle_colors"])
            draw.ellipse([x, y, x+size, y+size], fill=color)

        return img

    def render_frame(self, frame_num: int, bg_frames: Optional[List] = None) -> np.ndarray:
        """Render a single frame"""
        t = frame_num / self.fps

        img = self._create_background(frame_num, bg_frames)
        draw = ImageDraw.Draw(img)

        beat_pulse = self._get_beat_pulse(t)
        current_word = self._get_current_word(t)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            story_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
            word_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            moral_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            story_font = ImageFont.load_default()
            word_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            moral_font = ImageFont.load_default()

        draw.rectangle([0, 0, self.W, 100], fill=(0, 0, 0, 200))
        title = f"{self.story['title']}"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((self.W - tw) // 2, 30), title, fill=(255, 255, 255), font=title_font)

        if current_word:
            all_text = " ".join(self.sentences)
            all_words = all_text.split()

            word_count = 0
            current_sentence = self.sentences[0] if self.sentences else ""
            for sent in self.sentences:
                sent_words = sent.split()
                if word_count <= len([w for w in self.words if w["start_time"] <= t]) < word_count + len(sent_words):
                    current_sentence = sent
                    break
                word_count += len(sent_words)

            lines = textwrap.wrap(current_sentence, width=35)
            y = 280
            for line in lines:
                words = line.split()
                x_start = self.W // 2
                total_width = 0
                word_widths = []
                for word in words:
                    bbox = draw.textbbox((0, 0), word + " ", font=word_font)
                    w = bbox[2] - bbox[0]
                    word_widths.append(w)
                    total_width += w

                x = x_start - total_width // 2

                for i, word in enumerate(words):
                    clean = re.sub(r'[^\w\s]', '', word).strip()
                    is_active = current_word and clean.lower() == current_word["word"].lower()

                    if is_active:
                        pulse = beat_pulse
                        color = (
                            min(255, self.colors["highlight"][0] + int(pulse * 60)),
                            min(255, self.colors["highlight"][1] + int(pulse * 60)),
                            min(255, self.colors["highlight"][2] + int(pulse * 60))
                        )
                        for glow in range(4, 0, -1):
                            draw.text((x, y), word, 
                                     fill=(color[0]//glow, color[1]//glow, color[2]//glow), 
                                     font=word_font)
                    else:
                        color = self.colors["text"]

                    draw.text((x, y), word, fill=color, font=word_font)
                    x += word_widths[i]

                y += 85

            prev_sent_idx = -1
            wc = 0
            for idx, sent in enumerate(self.sentences):
                sw = sent.split()
                if wc + len(sw) > len([w for w in self.words if w["start_time"] <= t]):
                    prev_sent_idx = idx - 1
                    break
                wc += len(sw)

            if prev_sent_idx >= 0:
                prev_lines = textwrap.wrap(self.sentences[prev_sent_idx], width=40)
                y = 180
                for line in prev_lines:
                    bbox = draw.textbbox((0, 0), line, font=small_font)
                    tw = bbox[2] - bbox[0]
                    draw.text(((self.W - tw) // 2, y), line, fill=(130, 130, 130), font=small_font)
                    y += 40

            next_sent_idx = -1
            wc = 0
            for idx, sent in enumerate(self.sentences):
                sw = sent.split()
                if wc + len(sw) > len([w for w in self.words if w["start_time"] <= t]):
                    next_sent_idx = idx + 1
                    break
                wc += len(sw)

            if 0 <= next_sent_idx < len(self.sentences):
                next_lines = textwrap.wrap(self.sentences[next_sent_idx], width=40)
                y = 550
                for line in next_lines:
                    bbox = draw.textbbox((0, 0), line, font=small_font)
                    tw = bbox[2] - bbox[0]
                    draw.text(((self.W - tw) // 2, y), line, fill=(180, 180, 180), font=small_font)
                    y += 40

        if t > self.duration * 0.8:
            moral_alpha = min(255, int((t - self.duration * 0.8) / (self.duration * 0.2) * 255))
            moral_text = f"Seekh: {self.story['moral']}"
            bbox = draw.textbbox((0, 0), moral_text, font=moral_font)
            tw = bbox[2] - bbox[0]
            draw.rectangle([self.W*0.1, self.H-120, self.W*0.9, self.H-60], 
                          fill=(0, 0, 0, moral_alpha))
            draw.text(((self.W - tw) // 2, self.H - 105), moral_text, 
                     fill=(255, 255, 200), font=moral_font)

        bar_count = 40
        bar_width = self.W * 0.8 / bar_count
        for i in range(bar_count):
            bar_h = int(12 + beat_pulse * 35 * (0.5 + 0.5 * math.sin(i * 0.6 + t * 8)))
            x = self.W * 0.1 + i * bar_width
            y = self.H - 45 - bar_h
            color = random.choice(self.colors["particle_colors"])
            draw.rounded_rectangle([x, y, x + bar_width - 3, self.H - 45], 
                                    radius=3, fill=color)

        progress = t / self.duration
        bar_width = int(self.W * 0.8 * progress)
        draw.rectangle([self.W*0.1, self.H-20, self.W*0.9, self.H-15], fill=(50, 50, 50))
        draw.rectangle([self.W*0.1, self.H-20, self.W*0.1 + bar_width, self.H-15], 
                      fill=self.colors["accent"])

        time_str = f"{int(t//60):02d}:{int(t%60):02d}"
        bbox = draw.textbbox((0, 0), time_str, font=small_font)
        tw = bbox[2] - bbox[0]
        draw.text((self.W - tw - 60, self.H - 50), time_str, fill=(255, 255, 255), font=small_font)

        return np.array(img)

    def render(self, bg_video: Optional[str] = None) -> str:
        """Render complete video"""
        print(f"Rendering {self.total_frames} frames...")

        bg_frames = []
        if bg_video and os.path.exists(bg_video):
            print("   Extracting background frames...")
            frame_dir = f"{CONFIG['TEMP_DIR']}/bg_frames"
            Path(frame_dir).mkdir(exist_ok=True)

            subprocess.run([
                "ffmpeg", "-y", "-i", bg_video,
                "-vf", f"fps={self.fps},scale={self.W}:{self.H}",
                "-q:v", "2", f"{frame_dir}/frame_%05d.jpg"
            ], check=True, capture_output=True)

            for f in sorted(os.listdir(frame_dir)):
                if f.endswith('.jpg'):
                    img = Image.open(f"{frame_dir}/{f}").convert("RGB")
                    bg_frames.append(np.array(img))

            while len(bg_frames) < self.total_frames:
                bg_frames.extend(bg_frames[:min(len(bg_frames), self.total_frames - len(bg_frames))])

            shutil.rmtree(frame_dir)

        output_dir = f"{CONFIG['TEMP_DIR']}/frames"
        Path(output_dir).mkdir(exist_ok=True)

        for i in range(self.total_frames):
            frame = self.render_frame(i, bg_frames if i < len(bg_frames) else None)
            Image.fromarray(frame).save(f"{output_dir}/frame_{i:05d}.png")

            if i % 60 == 0:
                print(f"   Frame {i}/{self.total_frames}")

        print("Compiling video...")
        output_file = f"{CONFIG['OUTPUT_DIR']}/story_video.mp4"

        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(self.fps),
            "-i", f"{output_dir}/frame_%05d.png",
            "-i", "audio.mp3",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_file
        ], check=True, capture_output=True)

        shutil.rmtree(output_dir)

        print(f"Video: {output_file}")
        return output_file

# ============ STEP 6: THUMBNAIL GENERATION ============
class StoryThumbnailGenerator:
    """Generate kid-friendly YouTube thumbnail"""

    @staticmethod
    def generate(story: Dict, output_file: str = "thumbnail.jpg") -> str:
        print("Generating thumbnail...")

        W, H = 1280, 720
        colors = COLOR_THEMES.get(story["color_theme"], COLOR_THEMES["forest"])
        c1, c2 = colors["bg"][0], colors["bg"][1]

        img = Image.new('RGB', (W, H), c1)
        draw = ImageDraw.Draw(img)

        for y in range(H):
            ratio = y / H
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            draw.line([(0, y), (W, y)], fill=(r, g, b))

        for _ in range(30):
            x = random.randint(0, W)
            y = random.randint(0, H)
            size = random.randint(10, 60)
            color = random.choice(colors["particle_colors"])
            draw.ellipse([x, y, x+size, y+size], fill=color)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            moral_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            tag_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            moral_font = ImageFont.load_default()
            tag_font = ImageFont.load_default()

        title = story["title"]
        lines = textwrap.wrap(title, width=15)
        y = 150
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2 + 4, y + 4), line, fill=(0, 0, 0), font=title_font)
            draw.text(((W - tw) // 2, y), line, fill=(255, 255, 255), font=title_font)
            y += 105

        moral = f"{story['moral']}"
        bbox = draw.textbbox((0, 0), moral, font=moral_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 420), moral, fill=(255, 255, 200), font=moral_font)

        tag = f"#{story['category'].upper()} #HINDI #KIDS #STORY"
        bbox = draw.textbbox((0, 0), tag, font=tag_font)
        tw = bbox[2] - bbox[0]
        draw.rectangle([(W - tw) // 2 - 20, 520, (W + tw) // 2 + 20, 570], fill=(0, 0, 0, 180))
        draw.text(((W - tw) // 2, 530), tag, fill=(255, 255, 100), font=tag_font)

        draw.rounded_rectangle([50, 50, 280, 110], radius=10, fill=(255, 100, 100), outline=(255, 255, 255), width=3)
        draw.text((70, 60), "KIDS STORY", fill=(255, 255, 255), font=tag_font)

        draw.rounded_rectangle([W-280, 50, W-50, 110], radius=10, fill=(100, 200, 100), outline=(255, 255, 255), width=3)
        draw.text((W-260, 60), "HINDI", fill=(255, 255, 255), font=tag_font)

        img.save(output_file)
        print(f"Thumbnail: {output_file}")
        return output_file

# ============ STEP 7: METADATA GENERATION ============
class StoryMetadataGenerator:
    """Generate YouTube metadata for kids stories"""

    @staticmethod
    def generate(story: Dict) -> Dict:
        print("Generating metadata...")

        title_templates = [
            f"{story['title']} | Hindi Kids Story | Moral Story",
            f"{story['title']} | Animated Hindi Story for Children",
            f"Hindi Kahani: {story['title']} | Kids Moral Story",
        ]
        title = random.choice(title_templates)

        description = f"""{story['title']}

{story['title_en']}

Moral: {story['moral']}
Category: {story['category'].capitalize()}
Characters: {', '.join(story['characters'])}

Enjoy this beautiful Hindi moral story for kids!

Features:
- Animated Text with Word Highlighting
- Kid-Friendly Visuals
- Clear Hindi Voice
- Moral Learning

#HindiStories #KidsStories #MoralStories #HindiKahani #ChildrenStories #BedtimeStories"""

        tags = [
            story["title"], "hindi story", "kids story", "moral story",
            "hindi kahani", "children story", "bedtime story", story["category"],
            "animated story", "hindi moral story", "kids learning",
            "hindi cartoon", "bachon ki kahani", "hindi kids content"
        ]

        print("Metadata generated")
        return {"title": title, "description": description, "tags": tags}

# ============ STEP 8: YOUTUBE UPLOAD ============
class YouTubeUploader:
    """Upload video to YouTube"""

    @staticmethod
    def upload(video_file: str, thumbnail_file: str, metadata: Dict) -> Optional[str]:
        print("Uploading to YouTube...")

        try:
            try:
                with open("client_secret.json", "w", encoding="utf-8") as f:
                    f.write(CONFIG["YOUTUBE_CLIENT_SECRET"])

                if CONFIG["YOUTUBE_TOKEN_PICKLE_BASE64"]:
                    token_data = base64.b64decode(CONFIG["YOUTUBE_TOKEN_PICKLE_BASE64"])
                    with open("token.pickle", "wb") as f:
                        f.write(token_data)
            except Exception as e:
                print(f"   Auth setup warning: {e}")

            with open("token.pickle", "rb") as f:
                credentials = pickle.load(f)

            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload

            youtube = build("youtube", "v3", credentials=credentials)

            body = {
                "snippet": {
                    "title": metadata["title"][:100],
                    "description": metadata["description"][:5000],
                    "tags": metadata["tags"][:500],
                    "categoryId": "1",
                    "defaultLanguage": "hi",
                    "defaultAudioLanguage": "hi"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": True,
                    "publishAt": None
                }
            }

            print("   Uploading video...")
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
            )

            response = request.execute()
            video_id = response.get('id')
            print(f"Video uploaded: https://youtube.com/watch?v={video_id}")

            if thumbnail_file and os.path.exists(thumbnail_file):
                print("   Uploading thumbnail...")
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_file)
                ).execute()
                print("Thumbnail uploaded")

            return video_id

        except Exception as e:
            print(f"Upload failed: {e}")
            return None
        finally:
            for f in ["client_secret.json", "token.pickle"]:
                if os.path.exists(f):
                    os.remove(f)

# ============ STEP 9: ANALYTICS ============
class AnalyticsTracker:
    """Track video performance"""

    @staticmethod
    def track(video_id: str, story: Dict) -> Dict:
        print("Tracking analytics...")

        analytics = {
            "timestamp": datetime.now().isoformat(),
            "video_id": video_id,
            "story": {
                "title": story["title"],
                "category": story["category"],
                "moral": story["moral"]
            },
            "platform": "youtube",
            "metrics": {"views": 0, "likes": 0, "comments": 0}
        }

        with open(f"{CONFIG['OUTPUT_DIR']}/analytics.json", "w", encoding="utf-8") as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)

        print("Analytics saved")
        return analytics

# ============ MAIN PIPELINE ============
def main():
    print("=" * 60)
    print("HINDI KIDS STORIES VIDEO GENERATOR")
    print("=" * 60)

    start_time = time.time()

    story = StorySelector.select_story()

    audio_file = HindiTTSGenerator.generate(story["content"], "audio.mp3")

    beats, duration = AudioAnalyzer.analyze(audio_file)

    bg_video = BackgroundVideoFetcher.fetch(story["color_theme"], duration)

    renderer = StoryVideoRenderer(story, beats, duration)
    video_file = renderer.render(bg_video)

    thumbnail_file = StoryThumbnailGenerator.generate(story, f"{CONFIG['OUTPUT_DIR']}/thumbnail.jpg")

    metadata = StoryMetadataGenerator.generate(story)

    video_id = YouTubeUploader.upload(video_file, thumbnail_file, metadata)

    if video_id:
        AnalyticsTracker.track(video_id, story)

    if os.path.exists(CONFIG["TEMP_DIR"]):
        shutil.rmtree(CONFIG["TEMP_DIR"])

    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"PIPELINE COMPLETE!")
    print(f"Time: {elapsed:.1f}s")
    if video_id:
        print(f"Video: https://youtube.com/watch?v={video_id}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
