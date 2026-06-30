#!/usr/bin/env python3
"""
Universal Trending Content Video Generator
Auto-fetches viral content from: YouTube, TikTok, Facebook, Wikipedia, Spotify, News
Generates animated videos with Hindi TTS voice
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
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import quote, urlparse

import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============ CONFIGURATION ============
CONFIG = {
    "PEXELS_API_KEY": os.environ.get("PEXELS_API_KEY", ""),
    "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY", ""),
    "YOUTUBE_CLIENT_SECRET": os.environ.get("YOUTUBE_CLIENT_SECRET", ""),
    "YOUTUBE_TOKEN_PICKLE_BASE64": os.environ.get("YOUTUBE_TOKEN_PICKLE_BASE64", ""),
    "SPOTIFY_CLIENT_ID": os.environ.get("SPOTIFY_CLIENT_ID", ""),
    "SPOTIFY_CLIENT_SECRET": os.environ.get("SPOTIFY_CLIENT_SECRET", ""),
    "TIKTOK_API_KEY": os.environ.get("TIKTOK_API_KEY", ""),
    "FACEBOOK_ACCESS_TOKEN": os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
    "NEWS_API_KEY": os.environ.get("NEWS_API_KEY", ""),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
    "OUTPUT_DIR": "output",
    "TEMP_DIR": "temp",
    "FPS": 30,
    "WIDTH": 1920,
    "HEIGHT": 1080,
}

Path(CONFIG["OUTPUT_DIR"]).mkdir(exist_ok=True)
Path(CONFIG["TEMP_DIR"]).mkdir(exist_ok=True)

# ============ CONTENT SOURCES ============
class TrendingContentScraper:
    """Scrape trending content from multiple platforms"""

    SOURCES = ["youtube", "tiktok", "facebook", "wikipedia", "spotify", "news"]

    @classmethod
    def fetch_trending(cls) -> Dict:
        """Fetch trending content from all available sources"""
        print("Fetching trending content from multiple sources...")

        contents = []

        # Try each source
        if CONFIG["YOUTUBE_API_KEY"]:
            try:
                yt = cls._fetch_youtube_trending()
                if yt:
                    contents.append(yt)
                    print(f"  YouTube: {yt['title'][:50]}...")
            except Exception as e:
                print(f"  YouTube failed: {e}")

        if CONFIG["TIKTOK_API_KEY"]:
            try:
                tt = cls._fetch_tiktok_trending()
                if tt:
                    contents.append(tt)
                    print(f"  TikTok: {tt['title'][:50]}...")
            except Exception as e:
                print(f"  TikTok failed: {e}")

        if CONFIG["FACEBOOK_ACCESS_TOKEN"]:
            try:
                fb = cls._fetch_facebook_trending()
                if fb:
                    contents.append(fb)
                    print(f"  Facebook: {fb['title'][:50]}...")
            except Exception as e:
                print(f"  Facebook failed: {e}")

        if CONFIG["SPOTIFY_CLIENT_ID"] and CONFIG["SPOTIFY_CLIENT_SECRET"]:
            try:
                sp = cls._fetch_spotify_trending()
                if sp:
                    contents.append(sp)
                    print(f"  Spotify: {sp['title'][:50]}...")
            except Exception as e:
                print(f"  Spotify failed: {e}")

        if CONFIG["NEWS_API_KEY"]:
            try:
                news = cls._fetch_news_trending()
                if news:
                    contents.append(news)
                    print(f"  News: {news['title'][:50]}...")
            except Exception as e:
                print(f"  News failed: {e}")

        # Always try Wikipedia (no API key needed)
        try:
            wiki = cls._fetch_wikipedia_trending()
            if wiki:
                contents.append(wiki)
                print(f"  Wikipedia: {wiki['title'][:50]}...")
        except Exception as e:
            print(f"  Wikipedia failed: {e}")

        if not contents:
            print("No online sources available, using fallback content...")
            return cls._generate_fallback_content()

        # Select best content based on engagement score
        best = max(contents, key=lambda x: x.get("engagement_score", 0))
        print(f"Selected: {best['source']} | {best['title']}")
        return best

    @classmethod
    def _fetch_youtube_trending(cls) -> Optional[Dict]:
        """Fetch trending videos from YouTube"""
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": "IN",
            "maxResults": 10,
            "key": CONFIG["YOUTUBE_API_KEY"]
        }
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        if "items" not in data or not data["items"]:
            return None

        # Pick random trending video
        video = random.choice(data["items"])
        snippet = video["snippet"]
        stats = video.get("statistics", {})

        engagement = int(stats.get("viewCount", 0)) + int(stats.get("likeCount", 0)) * 100

        return {
            "source": "youtube",
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "content": snippet.get("description", snippet["title"]),
            "tags": snippet.get("tags", []),
            "thumbnail": snippet["thumbnails"]["high"]["url"] if "high" in snippet.get("thumbnails", {}) else "",
            "engagement_score": engagement,
            "url": f"https://youtube.com/watch?v={video['id']}",
            "category": "trending",
            "language": "hindi"
        }

    @classmethod
    def _fetch_tiktok_trending(cls) -> Optional[Dict]:
        """Fetch trending from TikTok (using unofficial API)"""
        # Using rapidapi or similar
        url = "https://tiktok-api6.p.rapidapi.com/trending/feed"
        headers = {
            "X-RapidAPI-Key": CONFIG["TIKTOK_API_KEY"],
            "X-RapidAPI-Host": "tiktok-api6.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, timeout=20)
        data = response.json()

        if not data or "data" not in data:
            return None

        item = random.choice(data["data"])

        return {
            "source": "tiktok",
            "title": item.get("title", "TikTok Trending"),
            "description": item.get("desc", ""),
            "content": item.get("desc", item.get("title", "")),
            "tags": item.get("hashtags", []),
            "thumbnail": item.get("cover", ""),
            "engagement_score": item.get("play_count", 0) + item.get("digg_count", 0) * 10,
            "url": item.get("share_url", ""),
            "category": "viral",
            "language": "hindi"
        }

    @classmethod
    def _fetch_facebook_trending(cls) -> Optional[Dict]:
        """Fetch trending from Facebook"""
        url = "https://graph.facebook.com/v18.0/search"
        params = {
            "q": "trending india",
            "type": "page",
            "access_token": CONFIG["FACEBOOK_ACCESS_TOKEN"],
            "limit": 10
        }
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        if "data" not in data or not data["data"]:
            return None

        page = random.choice(data["data"])

        return {
            "source": "facebook",
            "title": page.get("name", "Facebook Trending"),
            "description": page.get("about", ""),
            "content": page.get("about", page.get("name", "")),
            "tags": ["trending", "viral"],
            "thumbnail": "",
            "engagement_score": page.get("fan_count", 0),
            "url": f"https://facebook.com/{page.get('id', '')}",
            "category": "social",
            "language": "hindi"
        }

    @classmethod
    def _fetch_spotify_trending(cls) -> Optional[Dict]:
        """Fetch trending from Spotify"""
        # Get access token
        auth = base64.b64encode(
            f"{CONFIG['SPOTIFY_CLIENT_ID']}:{CONFIG['SPOTIFY_CLIENT_SECRET']}".encode()
        ).decode()

        token_resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth}"},
            data={"grant_type": "client_credentials"},
            timeout=10
        )
        token = token_resp.json().get("access_token")

        # Get trending playlist
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://api.spotify.com/v1/playlists/37i9dQZEVXbLZ52XmncU0o/tracks",
            headers=headers,
            params={"limit": 10},
            timeout=10
        )
        data = response.json()

        if "items" not in data or not data["items"]:
            return None

        track = random.choice(data["items"])["track"]

        return {
            "source": "spotify",
            "title": track["name"],
            "description": f"By {track['artists'][0]['name']}",
            "content": f"{track['name']} by {track['artists'][0]['name']}. A trending song everyone is listening to.",
            "tags": [track["artists"][0]["name"], "trending", "music"],
            "thumbnail": track["album"]["images"][0]["url"] if track["album"]["images"] else "",
            "engagement_score": track.get("popularity", 50) * 10000,
            "url": track["external_urls"].get("spotify", ""),
            "category": "music",
            "language": "hindi"
        }

    @classmethod
    def _fetch_news_trending(cls) -> Optional[Dict]:
        """Fetch trending news"""
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "in",
            "apiKey": CONFIG["NEWS_API_KEY"],
            "pageSize": 10
        }
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        if "articles" not in data or not data["articles"]:
            return None

        article = random.choice(data["articles"])

        return {
            "source": "news",
            "title": article["title"],
            "description": article.get("description", ""),
            "content": article.get("content", article.get("description", article["title"])),
            "tags": [article.get("source", {}).get("name", "news"), "trending"],
            "thumbnail": article.get("urlToImage", ""),
            "engagement_score": 500000,  # News always high priority
            "url": article["url"],
            "category": "news",
            "language": "hindi"
        }

    @classmethod
    def _fetch_wikipedia_trending(cls) -> Optional[Dict]:
        """Fetch trending Wikipedia article"""
        # Get trending pages
        url = "https://en.wikipedia.org/api/rest_v1/feed/featured/" + datetime.now().strftime("%Y/%m/%d")
        response = requests.get(url, timeout=20)
        data = response.json()

        # Try to get "most read" or "tfa" (today's featured article)
        article = None
        if "tfa" in data:
            article = data["tfa"]
        elif "mostread" in data and data["mostread"]:
            article = random.choice(data["mostread"][:5])

        if not article:
            # Fallback: random article
            response = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/random/summary",
                timeout=20
            )
            article = response.json()

        title = article.get("titles", {}).get("normalized", article.get("title", "Wikipedia"))
        extract = article.get("extract", article.get("description", title))

        return {
            "source": "wikipedia",
            "title": title,
            "description": extract[:200],
            "content": extract,
            "tags": ["knowledge", "trending", "wikipedia"],
            "thumbnail": article.get("thumbnail", {}).get("source", ""),
            "engagement_score": 100000,
            "url": article.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{quote(title)}"),
            "category": "knowledge",
            "language": "hindi"
        }

    @classmethod
    def _generate_fallback_content(cls) -> Dict:
        """Generate content when no APIs available"""
        fallbacks = [
            {
                "title": "AI Technology Revolution 2026",
                "content": "Artificial Intelligence is transforming every industry. From healthcare to education, AI is making life easier. Machine learning models can now predict diseases before symptoms appear. Self-driving cars are becoming safer every day. The future is here.",
                "category": "technology"
            },
            {
                "title": "Space Exploration: Mars Mission",
                "content": "Humanity's next giant leap is Mars. Scientists are working on sustainable habitats for the red planet. New rocket technology will make the journey faster than ever before. The dream of becoming a multi-planetary species is closer than we think.",
                "category": "science"
            },
            {
                "title": "Climate Change Solutions",
                "content": "Renewable energy is the key to our future. Solar panels are becoming more efficient and affordable. Wind farms are powering entire cities. Electric vehicles are replacing gas cars. Together, we can save our planet for future generations.",
                "category": "environment"
            },
            {
                "title": "Healthy Living Tips",
                "content": "Exercise daily for at least 30 minutes. Eat fresh fruits and vegetables. Drink plenty of water. Get 8 hours of sleep. Practice meditation for mental peace. Small changes in daily habits can lead to a healthier, happier life.",
                "category": "health"
            }
        ]

        selected = random.choice(fallbacks)
        return {
            "source": "fallback",
            "title": selected["title"],
            "description": selected["content"][:200],
            "content": selected["content"],
            "tags": [selected["category"], "trending"],
            "thumbnail": "",
            "engagement_score": 1000,
            "url": "",
            "category": selected["category"],
            "language": "hindi"
        }

# ============ HINDI TRANSLATION ============
class HindiTranslator:
    """Translate content to Hindi using free APIs"""

    @staticmethod
    def translate(text: str) -> str:
        """Translate English text to Hindi"""
        print("Translating to Hindi...")

        # Try Google Translate API (free tier)
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "en",
                "tl": "hi",
                "dt": "t",
                "q": text[:5000]  # Limit length
            }
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if data and len(data) > 0 and len(data[0]) > 0:
                translated = "".join([item[0] for item in data[0] if item[0]])
                if translated and len(translated) > 10:
                    print("Translation successful")
                    return translated
        except Exception as e:
            print(f"Google Translate failed: {e}")

        # Try MyMemory API
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text[:500],
                "langpair": "en|hi"
            }
            response = requests.get(url, params=params, timeout=20)
            data = response.json()

            if data.get("responseStatus") == 200:
                translated = data.get("responseData", {}).get("translatedText", "")
                if translated and len(translated) > 10:
                    print("MyMemory translation successful")
                    return translated
        except Exception as e:
            print(f"MyMemory failed: {e}")

        # Fallback: return original with note
        print("Translation failed, using original text")
        return text

# ============ HINDI TTS ============
class HindiTTSGenerator:
    """Generate Hindi audio"""

    HINDI_VOICES = [
        "hi-IN-SwaraNeural",
        "hi-IN-MadhurNeural",
        "hi-IN-AaravNeural",
    ]

    @classmethod
    def generate(cls, text: str, output_file: str = "audio.mp3") -> str:
        print("Generating Hindi audio...")

        voice = random.choice(cls.HINDI_VOICES)
        print(f"   Voice: {voice}")

        try:
            import edge_tts

            async def _generate():
                communicate = edge_tts.Communicate(
                    text, voice, rate="-5%", pitch="+5Hz", volume="+10%"
                )
                await communicate.save(output_file)

            asyncio.run(_generate())

            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                print(f"Audio: {output_file}")
                return output_file
        except Exception as e:
            print(f"edge-tts failed: {e}")

        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='hi', slow=False)
            tts.save(output_file)
            print(f"Audio (gTTS): {output_file}")
            return output_file
        except Exception as e:
            print(f"gTTS failed: {e}")
            raise

# ============ AUDIO ANALYSIS ============
class AudioAnalyzer:
    @staticmethod
    def analyze(audio_file: str) -> Tuple[List[float], float]:
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
            print(f"Duration: {duration:.1f}s")
            return beats, duration
        except Exception as e:
            print(f"Analysis failed: {e}")
            return [i * 2.0 for i in range(60)], 120

# ============ BACKGROUND VIDEO ============
class BackgroundVideoFetcher:
    THEME_QUERIES = {
        "technology": "technology futuristic digital animation",
        "science": "space galaxy stars universe animation",
        "environment": "nature green earth environment",
        "health": "healthy lifestyle fitness nature",
        "music": "music concert lights party",
        "news": "news broadcast breaking",
        "social": "social media people city",
        "viral": "trending viral popular",
        "knowledge": "education learning books",
        "trending": "trending popular viral",
    }

    @classmethod
    def fetch(cls, category: str, duration: float) -> Optional[str]:
        print("Fetching background video...")

        if not CONFIG["PEXELS_API_KEY"]:
            print("No Pexels key, using gradient")
            return None

        query = cls.THEME_QUERIES.get(category, "abstract colorful animation")

        try:
            url = "https://api.pexels.com/videos/search"
            headers = {"Authorization": CONFIG["PEXELS_API_KEY"]}
            params = {"query": query, "per_page": 3, "orientation": "landscape", "size": "large"}
            response = requests.get(url, headers=headers, params=params, timeout=30)
            data = response.json()

            videos = []
            if "videos" in data:
                for video in data["videos"]:
                    for file in video.get("video_files", []):
                        if file.get("file_type") == "video/mp4" and file.get("width", 0) >= 1280:
                            videos.append({"url": file["link"], "duration": video.get("duration", 15)})
                            break

            if not videos:
                return None

            video_files = []
            for i, v in enumerate(videos[:2]):
                fname = f"{CONFIG['TEMP_DIR']}/bg_{i}.mp4"
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

# ============ COLOR THEMES ============
COLOR_THEMES = {
    "technology": {"bg": [(10, 20, 40), (5, 10, 25)], "accent": (0, 200, 255), "text": (220, 240, 255)},
    "science": {"bg": [(5, 5, 30), (2, 2, 15)], "accent": (150, 100, 255), "text": (230, 220, 255)},
    "environment": {"bg": [(10, 40, 15), (5, 25, 10)], "accent": (100, 255, 100), "text": (220, 255, 220)},
    "health": {"bg": [(40, 20, 20), (25, 10, 10)], "accent": (255, 100, 100), "text": (255, 220, 220)},
    "music": {"bg": [(30, 10, 30), (15, 5, 15)], "accent": (255, 50, 200), "text": (255, 200, 240)},
    "news": {"bg": [(20, 20, 40), (10, 10, 25)], "accent": (255, 200, 50), "text": (255, 240, 200)},
    "social": {"bg": [(20, 30, 50), (10, 15, 30)], "accent": (50, 150, 255), "text": (200, 220, 255)},
    "viral": {"bg": [(40, 20, 10), (25, 10, 5)], "accent": (255, 150, 50), "text": (255, 230, 200)},
    "knowledge": {"bg": [(20, 30, 20), (10, 20, 10)], "accent": (200, 255, 100), "text": (240, 255, 220)},
    "trending": {"bg": [(30, 15, 30), (15, 5, 15)], "accent": (255, 100, 150), "text": (255, 220, 230)},
}

# ============ VIDEO RENDERER ============
class VideoRenderer:
    def __init__(self, content: Dict, beats: List[float], duration: float):
        self.content = content
        self.beats = beats
        self.duration = duration
        self.colors = COLOR_THEMES.get(content["category"], COLOR_THEMES["trending"])
        self.W, self.H = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        self.fps = CONFIG["FPS"]
        self.total_frames = int(duration * self.fps)

        text = content.get("content", content["title"])
        self.sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if s.strip()]
        self.words = []
        self._build_word_timings()

    def _build_word_timings(self):
        all_text = " ".join(self.sentences)
        words = all_text.split()
        if not words:
            return

        time_per_word = self.duration / len(words)
        current_time = 0

        for word in words:
            clean = re.sub(r'[^\w\s]', '', word).strip()
            if clean:
                self.words.append({
                    "word": clean,
                    "start_time": current_time,
                    "end_time": current_time + time_per_word,
                    "duration": time_per_word
                })
                current_time += time_per_word

    def _get_current_word(self, t: float) -> Optional[Dict]:
        for wd in self.words:
            if wd["start_time"] <= t < wd["end_time"]:
                return wd
        return None

    def _get_beat_pulse(self, t: float) -> float:
        nearest = min(self.beats, key=lambda x: abs(x - t))
        return max(0, 1 - abs(nearest - t) * 3)

    def _create_background(self, frame_num: int, bg_frames: Optional[List] = None) -> Image.Image:
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
            color = (
                min(255, self.colors["accent"][0] + random.randint(-30, 30)),
                min(255, self.colors["accent"][1] + random.randint(-30, 30)),
                min(255, self.colors["accent"][2] + random.randint(-30, 30))
            )
            draw.ellipse([x, y, x+size, y+size], fill=color)

        return img

    def render_frame(self, frame_num: int, bg_frames: Optional[List] = None) -> np.ndarray:
        t = frame_num / self.fps
        img = self._create_background(frame_num, bg_frames)
        draw = ImageDraw.Draw(img)

        beat_pulse = self._get_beat_pulse(t)
        current_word = self._get_current_word(t)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            content_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
            word_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            source_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            word_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            source_font = ImageFont.load_default()

        # Title bar
        draw.rectangle([0, 0, self.W, 100], fill=(0, 0, 0, 200))
        title = f"{self.content['title']}"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((self.W - tw) // 2, 30), title, fill=(255, 255, 255), font=title_font)

        # Source badge
        source_text = f"Source: {self.content['source'].upper()}"
        bbox = draw.textbbox((0, 0), source_text, font=source_font)
        tw = bbox[2] - bbox[0]
        draw.rectangle([self.W - tw - 30, 110, self.W - 20, 145], fill=self.colors["accent"])
        draw.text((self.W - tw - 20, 115), source_text, fill=(0, 0, 0), font=source_font)

        # Current sentence with word highlighting
        if current_word and self.sentences:
            all_text = " ".join(self.sentences)
            all_words = all_text.split()

            word_count = 0
            current_sentence = self.sentences[0]
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
                            min(255, self.colors["accent"][0] + int(pulse * 60)),
                            min(255, self.colors["accent"][1] + int(pulse * 60)),
                            min(255, self.colors["accent"][2] + int(pulse * 60))
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

            # Previous sentence
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

            # Next sentence
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

        # Visualizer
        bar_count = 40
        bar_width = self.W * 0.8 / bar_count
        for i in range(bar_count):
            bar_h = int(12 + beat_pulse * 35 * (0.5 + 0.5 * math.sin(i * 0.6 + t * 8)))
            x = self.W * 0.1 + i * bar_width
            y = self.H - 45 - bar_h
            color = (
                min(255, self.colors["accent"][0] + random.randint(-20, 20)),
                min(255, self.colors["accent"][1] + random.randint(-20, 20)),
                min(255, self.colors["accent"][2] + random.randint(-20, 20))
            )
            draw.rounded_rectangle([x, y, x + bar_width - 3, self.H - 45], radius=3, fill=color)

        # Progress bar
        progress = t / self.duration
        bar_width = int(self.W * 0.8 * progress)
        draw.rectangle([self.W*0.1, self.H-20, self.W*0.9, self.H-15], fill=(50, 50, 50))
        draw.rectangle([self.W*0.1, self.H-20, self.W*0.1 + bar_width, self.H-15], fill=self.colors["accent"])

        # Time
        time_str = f"{int(t//60):02d}:{int(t%60):02d}"
        bbox = draw.textbbox((0, 0), time_str, font=small_font)
        tw = bbox[2] - bbox[0]
        draw.text((self.W - tw - 60, self.H - 50), time_str, fill=(255, 255, 255), font=small_font)

        return np.array(img)

    def render(self, bg_video: Optional[str] = None) -> str:
        print(f"Rendering {self.total_frames} frames...")

        bg_frames = []
        if bg_video and os.path.exists(bg_video):
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
        output_file = f"{CONFIG['OUTPUT_DIR']}/video.mp4"
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

# ============ THUMBNAIL GENERATOR ============
class ThumbnailGenerator:
    @staticmethod
    def generate(content: Dict, output_file: str = "thumbnail.jpg") -> str:
        print("Generating thumbnail...")

        W, H = 1280, 720
        colors = COLOR_THEMES.get(content["category"], COLOR_THEMES["trending"])
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
            color = colors["accent"]
            draw.ellipse([x, y, x+size, y+size], fill=color)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            source_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            tag_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            source_font = ImageFont.load_default()
            tag_font = ImageFont.load_default()

        title = content["title"]
        lines = textwrap.wrap(title, width=18)
        y = 150
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2 + 4, y + 4), line, fill=(0, 0, 0), font=title_font)
            draw.text(((W - tw) // 2, y), line, fill=(255, 255, 255), font=title_font)
            y += 100

        source = f"Source: {content['source'].upper()}"
        bbox = draw.textbbox((0, 0), source, font=source_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 400), source, fill=(255, 255, 200), font=source_font)

        tag = f"#{content['category'].upper()} #TRENDING #HINDI"
        bbox = draw.textbbox((0, 0), tag, font=tag_font)
        tw = bbox[2] - bbox[0]
        draw.rectangle([(W - tw) // 2 - 20, 500, (W + tw) // 2 + 20, 550], fill=(0, 0, 0, 180))
        draw.text(((W - tw) // 2, 510), tag, fill=(255, 255, 100), font=tag_font)

        draw.rounded_rectangle([50, 50, 300, 110], radius=10, fill=(255, 0, 0), outline=(255, 255, 255), width=3)
        draw.text((70, 60), "TRENDING", fill=(255, 255, 255), font=tag_font)

        img.save(output_file)
        print(f"Thumbnail: {output_file}")
        return output_file

# ============ METADATA GENERATOR ============
class MetadataGenerator:
    @staticmethod
    def generate(content: Dict) -> Dict:
        print("Generating metadata...")

        title = f"{content['title']} | Trending {content['source'].title()} | Hindi"

        desc = f"""{content['title']}

Source: {content['source'].title()}
Category: {content['category'].capitalize()}

{content.get('description', '')}

Features:
- Auto-fetched trending content
- Hindi voice narration
- Animated word highlighting
- Professional editing

Original URL: {content.get('url', 'N/A')}

#Trending #Hindi #Viral #{content['source']} #{content['category']}"""

        tags = [
            content["title"], "trending", "hindi", content["source"],
            content["category"], "viral", "news", "music", "technology"
        ] + content.get("tags", [])

        print("Metadata generated")
        return {"title": title, "description": desc, "tags": list(set(tags))[:15]}

# ============ YOUTUBE UPLOADER ============
class YouTubeUploader:
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
                print(f"Auth setup warning: {e}")

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
                    "categoryId": "24",  # Entertainment
                    "defaultLanguage": "hi",
                    "defaultAudioLanguage": "hi"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "publishAt": None
                }
            }

            print("Uploading video...")
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
            )

            response = request.execute()
            video_id = response.get('id')
            print(f"Video uploaded: https://youtube.com/watch?v={video_id}")

            if thumbnail_file and os.path.exists(thumbnail_file):
                print("Uploading thumbnail...")
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

# ============ MAIN ============
def main():
    print("=" * 60)
    print("UNIVERSAL TRENDING CONTENT VIDEO GENERATOR")
    print("Sources: YouTube, TikTok, Facebook, Spotify, Wikipedia, News")
    print("=" * 60)

    start_time = time.time()

    # Step 1: Fetch trending content
    content = TrendingContentScraper.fetch_trending()

    # Step 2: Translate to Hindi
    hindi_text = HindiTranslator.translate(content["content"])
    content["hindi_content"] = hindi_text

    # Step 3: Generate Hindi Audio
    audio_file = HindiTTSGenerator.generate(hindi_text, "audio.mp3")

    # Step 4: Analyze Audio
    beats, duration = AudioAnalyzer.analyze(audio_file)

    # Step 5: Fetch Background Video
    bg_video = BackgroundVideoFetcher.fetch(content["category"], duration)

    # Step 6: Render Video
    renderer = VideoRenderer(content, beats, duration)
    video_file = renderer.render(bg_video)

    # Step 7: Generate Thumbnail
    thumbnail_file = ThumbnailGenerator.generate(content, f"{CONFIG['OUTPUT_DIR']}/thumbnail.jpg")

    # Step 8: Generate Metadata
    metadata = MetadataGenerator.generate(content)

    # Step 9: Upload to YouTube
    video_id = YouTubeUploader.upload(video_file, thumbnail_file, metadata)

    # Cleanup
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
