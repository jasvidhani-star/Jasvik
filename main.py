import os
import random
import requests
import base64
import pickle
import sys
import textwrap
import math

from google.generativeai import configure, GenerativeModel
from gtts import gTTS
from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeVideoClip,
                            concatenate_videoclips, ImageSequenceClip)
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ============ SETUP ============
print("🔐 Setup...")

# YouTube credentials
try:
    with open("client_secret.json", "w", encoding="utf-8") as f:
        f.write(os.environ.get("YOUTUBE_CLIENT_SECRET", "{}"))
    
    token_data = base64.b64decode(os.environ.get("YOUTUBE_TOKEN_PICKLE_BASE64", ""))
    with open("token.pickle", "wb") as f:
        f.write(token_data)
    print("✅ YouTube credentials ready")
except Exception as e:
    print(f"⚠️ Credential warning: {e}")

# Gemini setup
configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = GenerativeModel('gemini-1.5-pro')

# ============ STEP 1: TOPIC & SCRIPT ============
print("🎯 Generating content...")

topics = [
    "बच्चों में आत्मविश्वास कैसे बढ़ाएं",
    "बच्चों के लिए कोडिंग सीखना",
    "गणित की जादुई ट्रिक्स",
    "बच्चों की एकाग्रता बढ़ाने के तरीके",
    "बच्चों में अच्छी आदतें कैसे डालें",
    "बच्चों के लिए प्रेरणादायक कहानी",
    "बच्चों का स्क्रीन टाइम कम करें",
    "बच्चों को पैसे की बचत सिखाएं",
    "बच्चों के लिए विज्ञान प्रयोग",
    "बच्चों की यादाश्त बढ़ाएं"
]

topic = random.choice(topics)
print(f"🎯 Topic: {topic}")

# Generate 500-word script (3+ minutes)
try:
    script = model.generate_content(
        f"""{topic} पर 500 शब्दों की Hindi script लिखो। 
        YouTube video के लिए, 3-4 minutes की।
        शुरुआत में hook, बीच में 5-7 points, आखिर में CTA।
        सिर्फ Hindi, no emojis।"""
    ).text
    print(f"✅ Script: {len(script.split())} words")
except Exception as e:
    print(f"❌ Gemini error: {e}")
    script = f"""{topic} - आज हम इसके बारे में विस्तार से जानेंगे।

पहला तरीका: रोज़ाना अभ्यास। बच्चे को हर दिन थोड़ा समय दें।

दूसरा: खेल-खेल में सीखना। बच्चे खेलते हुए ज़्यादा तेज़ी से सीखते हैं।

तीसरा: प्रशंसा और प्रोत्साहन। बच्चे की छोटी-छोटी उपलब्धियों की तारीफ करें।

चौथा: सही माहौल बनाएं। बच्चे के लिए पढ़ने का अच्छा माहौल तैयार करें।

पांचवां: धैर्य रखें। हर बच्चा अलग होता है।

अगर ये वीडियो अच्छा लगा तो Like, Share और Subscribe करें!"""

# ============ STEP 2: AUDIO ============
print("🔊 Creating audio...")
try:
    tts = gTTS(text=script, lang='hi', slow=False)
    tts.save("audio.mp3")
    
    audio = AudioFileClip("audio.mp3")
    audio_duration = audio.duration
    target_duration = max(audio_duration, 180)  # Minimum 3 minutes
    duration = min(target_duration, 300)  # Maximum 5 minutes
    print(f"✅ Audio: {duration:.1f}s ({duration/60:.1f} min)")
    audio.close()
except Exception as e:
    print(f"❌ Audio error: {e}")
    sys.exit(1)

# ============ STEP 3: PEXELS STOCK VIDEOS ============
print("📥 Downloading Pexels videos...")

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

def search_pexels_videos(query, per_page=5):
    try:
        if not PEXELS_API_KEY:
            print("⚠️ No Pexels API key")
            return []
            
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape",
            "size": "medium"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()
        
        videos = []
        if "videos" in data:
            for video in data["videos"]:
                # Get best quality MP4
                best_url = None
                best_quality = 0
                
                for file in video.get("video_files", []):
                    if file.get("file_type") == "video/mp4":
                        quality = file.get("width", 0) * file.get("height", 0)
                        if quality > best_quality:
                            best_quality = quality
                            best_url = file.get("link")
                
                if best_url:
                    videos.append({
                        "url": best_url,
                        "duration": video.get("duration", 15)
                    })
        
        return videos
    except Exception as e:
        print(f"❌ Pexels error: {e}")
        return []

def download_video(url, filename):
    try:
        print(f"  Downloading: {url[:50]}...")
        response = requests.get(url, stream=True, timeout=60)
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  ❌ Download error: {e}")
        return False

# Search with English query for better results
pexels_query = topic.replace("बच्चों में", "children").replace("बच्चों के लिए", "kids").replace("कैसे", "how to").replace("की", "")
pexels_query = pexels_query.replace("आत्मविश्वास", "confidence").replace("कोडिंग", "coding").replace("गणित", "math").replace("ट्रिक्स", "tricks")

pexels_videos = search_pexels_videos(pexels_query, per_page=5)

video_files = []
for i, video in enumerate(pexels_videos):
    fname = f"stock_{i}.mp4"
    if download_video(video["url"], fname):
        video_files.append({
            "file": fname,
            "duration": video["duration"]
        })

if not video_files:
    print("⚠️ No stock videos, will use animated background")

# ============ STEP 4: CREATE VIDEO ============
print("🎬 Creating video...")

W, H = 1920, 1080
fps = 24

try:
    # Load stock videos
    clips = []
    if video_files:
        for vf in video_files:
            try:
                clip = VideoFileClip(vf["file"])
                # Resize to 1920x1080
                if clip.w / clip.h != 16/9:
                    clip = clip.resize(height=1080)
                    x_center = clip.w // 2
                    clip = clip.crop(x1=x_center-960, y1=0, x2=x_center+960, y2=1080)
                else:
                    clip = clip.resize((W, H))
                
                clips.append(clip)
                print(f"  ✅ Loaded: {vf['file']}")
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
    
    # Create background
    if clips:
        background = concatenate_videoclips(clips, method="compose")
        # Loop if too short
        if background.duration < duration:
            background = background.loop(duration=duration)
        else:
            background = background.subclip(0, duration)
    else:
        # Create animated background
        print("🎨 Creating animated background...")
        bg_color = ColorClip(size=(W, H), color=(30, 40, 60)).set_duration(duration)
        background = bg_color
    
    # Create subtitles
    words = script.split()
    words_per_seg = max(1, len(words) // 12)
    segments = []
    current = []
    
    for word in words:
        current.append(word)
        if len(current) >= words_per_seg:
            segments.append(" ".join(current))
            current = []
    if current:
        segments.append(" ".join(current))
    
    seg_duration = duration / max(len(segments), 1)
    
    # Generate frames with subtitles
    total_frames = int(duration * fps)
    frame_files = []
    
    print(f"🎬 Generating {total_frames} frames...")
    
    for frame_num in range(total_frames):
        t = frame_num / fps
        
        # Get background frame
        if hasattr(background, 'get_frame'):
            bg_frame = background.get_frame(t)
            bg = Image.fromarray(bg_frame).convert("RGB")
        else:
            bg = Image.new('RGB', (W, H), (30, 40, 60))
        
        draw = ImageDraw.Draw(bg)
        
        # Subtitle
        seg_idx = min(int(t / seg_duration), len(segments) - 1)
        subtitle_text = segments[seg_idx][:120]
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Subtitle box
        lines = textwrap.wrap(subtitle_text, width=50)
        line_h = 45
        sub_h = len(lines) * line_h + 30
        sub_w = min(1100, max(len(l) * 20 for l in lines) + 40)
        
        bx = (W - sub_w) // 2
        by = H - sub_h - 100
        
        # Background
        draw.rounded_rectangle([bx, by, bx + sub_w, by + sub_h], 
                              radius=15, fill=(0, 0, 0, 180), outline=(255, 255, 255), width=2)
        
        # Text
        ty = by + 15
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, ty), line, fill=(255, 255, 255), font=font)
            ty += line_h
        
        # Progress bar
        bar_width = int(W * 0.9 * (frame_num / total_frames))
        draw.rectangle([W*0.05, H-12, W*0.95, H-8], fill=(80, 80, 80))
        draw.rectangle([W*0.05, H-12, W*0.05 + bar_width, H-8], fill=(0, 255, 150))
        
        # Save
        fname = f"frame_{frame_num:05d}.png"
        bg.save(fname)
        frame_files.append(fname)
        
        if frame_num % 60 == 0:
            print(f"  Frame {frame_num}/{total_frames}")
    
    # Render video
    print("🎬 Rendering final video...")
    clip = ImageSequenceClip(frame_files, fps=fps)
    audio = AudioFileClip("audio.mp3")
    final = clip.set_audio(audio.subclip(0, duration))
    
    final.write_videofile("final_video.mp4", fps=fps, codec='libx264',
                          audio_codec='aac', temp_audiofile='temp-audio.m4a',
                          remove_temp=True, threads=4, preset='ultrafast', logger=None)
    
    print("✅ Video created!")
    
    # Cleanup
    final.close()
    clip.close()
    audio.close()
    
    for f in frame_files:
        if os.path.exists(f):
            os.remove(f)
    for vf in video_files:
        if os.path.exists(vf["file"]):
            os.remove(vf["file"])
    
except Exception as e:
    print(f"❌ Video error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============ STEP 5: UPLOAD TO YOUTUBE ============
print("📤 Uploading to YouTube...")

try:
    with open("token.pickle", "rb") as f:
        credentials = pickle.load(f)
    
    youtube = build("youtube", "v3", credentials=credentials)
    
    desc_lines = [l.strip() for l in script.split('\n') if l.strip() and len(l.strip()) > 10]
    
    body = {
        "snippet": {
            "title": f"🎬 {topic} | Kids Tips | Hindi",
            "description": f"""🎬 {topic}

{chr(10).join([f"• {l[:80]}" for l in desc_lines[:6]])}

✨ Features:
• Real Stock Footage
• Hindi Subtitles
• Professional Editing

👨‍👩‍👧‍👦 Subscribe for more!

#Hindi #Kids #Parenting #Education""",
            "tags": ["hindi", "kids", "parenting", "education", "tips"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload("final_video.mp4", chunksize=-1, resumable=True)
    )
    
    response = request.execute()
    vid = response.get('id')
    print(f"✅ Uploaded! https://youtube.com/watch?v={vid}")
    
except Exception as e:
    print(f"❌ Upload error: {e}")

# Cleanup
for f in ["audio.mp3", "client_secret.json", "token.pickle", "temp-audio.m4a"]:
    if os.path.exists(f):
        os.remove(f)

print(f"\n🎉 DONE! {duration/60:.1f} min video uploaded!")
print(f"🔗 https://youtube.com/watch?v={vid}")
