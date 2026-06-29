import os
import base64
import pickle
import random
import sys
import textwrap
import math
import re
import json
import urllib.parse
import io

# ============ STEP 1: Imports ============
try:
    import requests
    from google import genai
    from gtts import gTTS
    from moviepy.editor import (ImageClip, AudioFileClip, CompositeVideoClip, 
                                TextClip, ColorClip, ImageSequenceClip,
                                VideoFileClip, concatenate_videoclips)
    from moviepy.video.fx.all import fadein, fadeout
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError as e:
    print(f"❌ Missing: {e}")
    sys.exit(1)

# ============ STEP 2: Setup ============
print("🔐 Setup...")
try:
    with open("client_secret.json", "w", encoding="utf-8") as f:
        f.write(os.environ.get("YOUTUBE_CLIENT_SECRET", "{}"))
    
    token_data = base64.b64decode(os.environ.get("YOUTUBE_TOKEN_PICKLE_BASE64", ""))
    with open("token.pickle", "wb") as f:
        f.write(token_data)
    
    PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    
    print("✅ Ready")
except Exception as e:
    print(f"❌ Error: {e}")

# ============ STEP 3: PEXELS - Download Real Stock Videos ============
def search_pexels_videos(query, per_page=5):
    """Search and download free stock videos from Pexels"""
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
                        "duration": video.get("duration", 15),
                        "width": video.get("width", 1920),
                        "height": video.get("height", 1080),
                        "description": video.get("description", "")
                    })
        
        print(f"✅ Pexels: {len(videos)} videos found for '{query}'")
        return videos
        
    except Exception as e:
        print(f"❌ Pexels error: {e}")
        return []

def download_video(url, filename):
    """Download video from URL"""
    try:
        response = requests.get(url, stream=True, timeout=60)
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

# ============ STEP 4: WIKIPEDIA CONTENT ============
def fetch_wikipedia(topic):
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query", "list": "search", "srsearch": topic,
            "format": "json", "srlimit": 1
        }
        r = requests.get(search_url, params=params, timeout=20)
        data = r.json()
        
        if not data["query"]["search"]:
            return None
            
        title = data["query"]["search"][0]["title"]
        
        params = {
            "action": "query", "prop": "extracts", "titles": title,
            "explaintext": True, "exchars": 3000, "format": "json"
        }
        r = requests.get(search_url, params=params, timeout=20)
        data = r.json()
        
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        content = pages[page_id].get("extract", "")
        
        return {
            "title": title,
            "content": content[:2500],
            "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        }
    except Exception as e:
        print(f"❌ Wiki error: {e}")
        return None

# ============ STEP 5: TOPIC & CONTENT ============
story_topics = [
    ("Albert Einstein childhood", "child scientist learning"),
    ("Marie Curie biography", "woman scientist laboratory"),
    ("Isaac Newton early life", "apple tree thinking"),
    ("Helen Keller biography", "blind girl reading"),
    ("Thomas Edison childhood", "boy experimenting"),
    ("Mother Teresa biography", "woman helping children"),
    ("Mahatma Gandhi childhood", "Indian boy studying"),
    ("APJ Abdul Kalam biography", "Indian scientist rocket"),
    ("Swami Vivekananda biography", "Indian monk meditation"),
    ("Srinivasa Ramanujan biography", "mathematician equations"),
    ("Kalpana Chawla biography", "woman astronaut space"),
    ("Sachin Tendulkar childhood", "boy playing cricket"),
    ("Mary Kom biography", "woman boxing training"),
    ("Malala Yousafzai biography", "girl studying school"),
    ("Anne Frank biography", "girl writing diary"),
    ("Charlie Chaplin childhood", "boy acting comedy"),
    ("Walt Disney childhood", "boy drawing cartoon"),
    ("Steve Jobs childhood", "boy computer garage"),
    ("Oprah Winfrey childhood", "girl reading books"),
    ("J.K. Rowling childhood", "woman writing story")
]

selected_topic, pexels_query = random.choice(story_topics)
print(f"🎯 Topic: {selected_topic}")
print(f"🎬 Pexels search: {pexels_query}")

# Get real content
wiki_data = fetch_wikipedia(selected_topic)
real_content = wiki_data["content"] if wiki_data else ""

# Download stock videos
print("📥 Downloading stock videos...")
pexels_videos = search_pexels_videos(pexels_query, per_page=3)

video_files = []
for i, video in enumerate(pexels_videos):
    fname = f"stock_{i}.mp4"
    if download_video(video["url"], fname):
        video_files.append({
            "file": fname,
            "duration": video["duration"]
        })

if not video_files:
    print("⚠️ No stock videos, will use animated backgrounds")

# ============ STEP 6: GENERATE SCRIPT ============
print("🤖 Generating script...")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""YouTube Kids Story (3-4 minutes) के लिए DRAMATIC Hindi script.

TOPIC: {selected_topic}
FACTS: {real_content[:1500]}

नियम:
- Real facts use karo
- Story: Setup → Struggle → Success → Lesson
- 500-600 words
- Hindi में
- Emotions: [HAPPY], [SAD], [THINKING], [EXCITED], [PROUD]
- Moral end mein
- Output: sirf script"""

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    script = response.text.strip()
    print(f"✅ Script: {len(script.split())} words")
    
except Exception as e:
    print(f"❌ Error: {e}")
    script = f"""[HAPPY] एक छोटे से गाँव में एक बच्चा रहता था। [THINKING] उसे हमेशा सवाल पूछने की आदत थी। [SAD] लोग उसे चिढ़ाते थे। [EXCITED] लेकिन वो हार नहीं माना! [PROUD] और आज वो दुनिया का सबसे बड़ा Scientist है! Like, Share, Subscribe!"""

# ============ STEP 7: PARSE SCENES ============
emotions = ["HAPPY", "SAD", "THINKING", "EXCITED", "ANGRY", "SURPRISED", "PROUD"]
scene_data = []

script_clean = script
for emotion in emotions:
    if f"[{emotion}]" in script:
        parts = script.split(f"[{emotion}]")
        for part in parts[1:]:
            scene_text = part.split("[")[0].strip()[:250]
            if scene_text:
                scene_data.append({"emotion": emotion, "text": scene_text})

if not scene_data:
    paragraphs = [p.strip() for p in script.split('\n') if p.strip() and len(p.strip()) > 20]
    emotion_cycle = ["HAPPY", "THINKING", "SAD", "EXCITED", "PROUD"]
    for i, para in enumerate(paragraphs[:5]):
        scene_data.append({"emotion": emotion_cycle[i % len(emotion_cycle)], "text": para[:250]})

print(f"✅ {len(scene_data)} scenes")

# ============ STEP 8: CREATE CARTOON CHARACTER ============
def create_cartoon_character(emotion, width=400, height=500):
    """Create cartoon character with emotion"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    skin = (255, 220, 180)
    hair = (80, 50, 30)
    shirt = (100, 150, 200)
    pants = (60, 80, 120)
    
    cx, cy = width // 2, height // 2
    
    # Body
    draw.ellipse([cx-60, cy+20, cx+60, cy+120], fill=shirt)
    # Head
    draw.ellipse([cx-50, cy-80, cx+50, cy+20], fill=skin)
    # Hair
    draw.ellipse([cx-55, cy-90, cx+55, cy-40], fill=hair)
    
    # Eyes based on emotion
    if emotion == "HAPPY":
        draw.ellipse([cx-35, cy-50, cx-15, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx+15, cy-50, cx+35, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx-30, cy-45, cx-20, cy-35], fill=(0, 0, 0))
        draw.ellipse([cx+20, cy-45, cx+30, cy-35], fill=(0, 0, 0))
        # Smile
        draw.arc([cx-30, cy-30, cx+30, cy], 0, 180, fill=(200, 50, 50), width=4)
        # Cheeks
        draw.ellipse([cx-45, cy-25, cx-35, cy-15], fill=(255, 180, 180))
        draw.ellipse([cx+35, cy-25, cx+45, cy-15], fill=(255, 180, 180))
        
    elif emotion == "SAD":
        draw.ellipse([cx-35, cy-50, cx-15, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx+15, cy-50, cx+35, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx-30, cy-45, cx-20, cy-35], fill=(0, 0, 0))
        draw.ellipse([cx+20, cy-45, cx+30, cy-35], fill=(0, 0, 0))
        # Sad mouth
        draw.arc([cx-30, cy-20, cx+30, cy+10], 180, 360, fill=(100, 50, 50), width=4)
        # Tear
        draw.ellipse([cx+35, cy-40, cx+42, cy-25], fill=(100, 150, 255))
        
    elif emotion == "THINKING":
        draw.ellipse([cx-35, cy-50, cx-15, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx+15, cy-50, cx+35, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx-30, cy-45, cx-20, cy-35], fill=(0, 0, 0))
        draw.ellipse([cx+20, cy-45, cx+30, cy-35], fill=(0, 0, 0))
        # Thinking line
        draw.line([(cx-20, cy-10), (cx+20, cy-10)], fill=(100, 50, 50), width=3)
        # Light bulb
        draw.ellipse([cx+50, cy-100, cx+80, cy-70], fill=(255, 255, 100))
        draw.polygon([(cx+55, cy-70), (cx+75, cy-70), (cx+65, cy-55)], fill=(255, 200, 50))
        
    elif emotion == "EXCITED":
        # Star eyes
        for ox, oy in [(cx-25, cy-40), (cx+25, cy-40)]:
            points = [(ox, oy-15), (ox+5, oy-5), (ox+15, oy), (ox+5, oy+5), 
                     (ox, oy+15), (ox-5, oy+5), (ox-15, oy), (ox-5, oy-5)]
            draw.polygon(points, fill=(255, 255, 0))
        # Big smile
        draw.arc([cx-40, cy-30, cx+40, cy+20], 0, 180, fill=(200, 50, 50), width=5)
        # Arms up
        draw.line([cx-60, cy+40, cx-100, cy-20], fill=skin, width=15)
        draw.line([cx+60, cy+40, cx+100, cy-20], fill=skin, width=15)
        
    elif emotion == "PROUD":
        draw.ellipse([cx-35, cy-50, cx-15, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx+15, cy-50, cx+35, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx-30, cy-45, cx-20, cy-35], fill=(0, 0, 0))
        draw.ellipse([cx+20, cy-45, cx+30, cy-35], fill=(0, 0, 0))
        # Confident smile
        draw.arc([cx-30, cy-30, cx+30, cy], 0, 180, fill=(200, 50, 50), width=4)
        # Medal
        draw.ellipse([cx+40, cy+10, cx+60, cy+30], fill=(255, 215, 0))
        draw.rectangle([cx+48, cy+30, cx+52, cy+50], fill=(200, 150, 50))
        
    else:
        draw.ellipse([cx-35, cy-50, cx-15, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx+15, cy-50, cx+35, cy-30], fill=(255, 255, 255))
        draw.ellipse([cx-30, cy-45, cx-20, cy-35], fill=(0, 0, 0))
        draw.ellipse([cx+20, cy-45, cx+30, cy-35], fill=(0, 0, 0))
        draw.arc([cx-30, cy-30, cx+30, cy], 0, 180, fill=(200, 50, 50), width=3)
    
    # Arms (if not excited)
    if emotion != "EXCITED":
        draw.line([cx-60, cy+60, cx-90, cy+100], fill=skin, width=15)
        draw.line([cx+60, cy+60, cx+90, cy+100], fill=skin, width=15)
    
    # Legs
    draw.line([cx-30, cy+120, cx-40, cy+180], fill=pants, width=20)
    draw.line([cx+30, cy+120, cx+40, cy+180], fill=pants, width=20)
    
    # Shoes
    draw.ellipse([cx-55, cy+170, cx-25, cy+190], fill=(80, 50, 30))
    draw.ellipse([cx+25, cy+170, cx+55, cy+190], fill=(80, 50, 30))
    
    return img

# Generate characters for each scene
print("🎨 Creating cartoon characters...")
character_images = []
for i, scene in enumerate(scene_data[:5]):
    print(f"  Character {i+1}: {scene['emotion']}")
    char = create_cartoon_character(scene["emotion"])
    char_path = f"char_{i}.png"
    char.save(char_path)
    character_images.append({
        "path": char_path,
        "emotion": scene["emotion"],
        "text": scene["text"]
    })

# ============ STEP 9: CREATE AUDIO ============
print("🔊 Creating audio...")

clean_script = script
for emotion in emotions:
    clean_script = clean_script.replace(f"[{emotion}]", "")

try:
    tts = gTTS(text=clean_script, lang='hi', slow=False)
    tts.save("audio.mp3")
except Exception as e:
    print(f"❌ Audio error: {e}")
    sys.exit(1)

audio = AudioFileClip("audio.mp3")
audio_duration = audio.duration
target_duration = max(audio_duration, 180)
duration = min(target_duration, 300)
print(f"⏱️ Audio: {duration:.1f}s")
audio.close()

# ============ STEP 10: CREATE FINAL VIDEO ============
print("🎬 Creating final video...")

W, H = 1920, 1080
fps = 24
total_frames = int(duration * fps)

# If we have stock videos, use them as background
if video_files:
    print("🎬 Using Pexels stock videos as background...")
    
    # Load and concatenate stock videos
    stock_clips = []
    for vf in video_files:
        try:
            clip = VideoFileClip(vf["file"])
            # Resize to 1920x1080
            clip = clip.resize((W, H))
            stock_clips.append(clip)
        except Exception as e:
            print(f"  ⚠️ Error loading {vf['file']}: {e}")
    
    if stock_clips:
        # Concatenate all stock videos
        background = concatenate_videoclips(stock_clips, method="compose")
        # Loop if too short
        if background.duration < duration:
            background = background.loop(duration=duration)
        else:
            background = background.subclip(0, duration)
    else:
        background = None
else:
    background = None

# Generate frames with cartoon overlay
frame_files = []
frames_per_scene = total_frames // len(character_images)

for scene_idx, char_data in enumerate(character_images):
    print(f"  🎬 Scene {scene_idx+1}: {char_data['emotion']}")
    
    char_img = Image.open(char_data["path"]).convert("RGBA")
    
    for f in range(frames_per_scene):
        frame_num = scene_idx * frames_per_scene + f
        if frame_num >= total_frames:
            break
        
        # If we have stock video background, extract frame
        if background:
            t = frame_num / fps
            bg_frame = background.get_frame(t)
            bg = Image.fromarray(bg_frame).convert("RGB")
        else:
            # Create animated gradient background
            bg = Image.new('RGB', (W, H), (20, 20, 40))
            draw = ImageDraw.Draw(bg)
            
            progress = frame_num / total_frames
            emotion_colors = {
                "HAPPY": (40, 60, 40),
                "SAD": (30, 40, 60),
                "THINKING": (40, 50, 70),
                "EXCITED": (60, 50, 40),
                "PROUD": (50, 60, 40)
            }
            base = emotion_colors.get(char_data["emotion"], (40, 40, 60))
            
            for y in range(H):
                r = int(base[0] * (0.5 + y/H * 0.5))
                g = int(base[1] * (0.5 + y/H * 0.5))
                b = int(base[2] * (0.5 + y/H * 0.5))
                draw.line([(0, y), (W, y)], fill=(r, g, b))
        
        # Character animation
        bounce = int(15 * math.sin(f * 0.15))
        char_size = 350
        char_x = W - char_size - 100
        char_y = H - char_size - 150 + bounce
        
        # Resize character
        char_resized = char_img.resize((char_size, char_size), Image.Resampling.LANCZOS)
        
        # Paste character
        bg.paste(char_resized, (char_x, char_y), char_resized)
        
        # Speech bubble
        bubble_text = char_data["text"][:120]
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            font = ImageFont.load_default()
            font_bold = font
        
        lines = textwrap.wrap(bubble_text, width=50)
        line_h = 30
        bubble_h = len(lines) * line_h + 40
        bubble_w = min(900, max(len(l) * 15 for l in lines) + 60)
        
        bx = 100
        by = 100
        
        # Bubble
        draw = ImageDraw.Draw(bg)
        draw.rounded_rectangle([bx, by, bx + bubble_w, by + bubble_h], 
                              radius=20, fill=(255, 255, 255, 230), outline=(0, 0, 0), width=2)
        
        # Pointer to character
        draw.polygon([(bx + bubble_w - 50, by + bubble_h), 
                     (bx + bubble_w, by + bubble_h),
                     (char_x + 50, char_y)], 
                    fill=(255, 255, 255), outline=(0, 0, 0))
        
        # Text
        ty = by + 20
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((bx + 20, ty), line, fill=(0, 0, 0), font=font)
            ty += line_h
        
        # Progress bar
        bar_width = int(W * 0.85 * (frame_num / total_frames))
        draw.rectangle([W*0.075, H-15, W*0.925, H-10], fill=(80, 80, 80))
        draw.rectangle([W*0.075, H-15, W*0.075 + bar_width, H-10], fill=(0, 255, 150))
        
        # Save
        fname = f"frame_{frame_num:05d}.png"
        bg.save(fname)
        frame_files.append(fname)
        
        if f % 24 == 0:
            print(f"    Frame {f}/{frames_per_scene}")

print(f"✅ {len(frame_files)} frames generated")

# ============ STEP 11: RENDER VIDEO ============
print("🎬 Rendering...")

try:
    clip = ImageSequenceClip(frame_files, fps=fps)
    audio = AudioFileClip("audio.mp3")
    final = clip.set_audio(audio.subclip(0, duration))
    
    final.write_videofile("final_video.mp4", fps=fps, codec='libx264',
                          audio_codec='aac', temp_audiofile='temp-audio.m4a',
                          remove_temp=True, threads=4, preset='ultrafast', logger=None)
    
    print("✅ Video created!")
    
    final.close()
    clip.close()
    audio.close()
    
    # Cleanup
    for f in frame_files:
        if os.path.exists(f):
            os.remove(f)
    for c in character_images:
        if os.path.exists(c["path"]):
            os.remove(c["path"])
    for v in video_files:
        if os.path.exists(v["file"]):
            os.remove(v["file"])
            
except Exception as e:
    print(f"❌ Video error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============ STEP 12: UPLOAD TO YOUTUBE ============
print("📤 Uploading...")

try:
    with open("token.pickle", "rb") as f:
        credentials = pickle.load(f)
    
    youtube = build("youtube", "v3", credentials=credentials)
    
    clean_desc = clean_script[:800]
    source = f"\n\n📚 Source: {wiki_data['url']}" if wiki_data else ""
    
    body = {
        "snippet": {
            "title": f"🎬 {selected_topic} | Real Story | Animated Cartoon for Kids",
            "description": f"""🎨 AI-Generated Cartoon Animation with Real Stock Footage!

{clean_desc}...

✨ Features:
• Real Stock Videos (Pexels)
• Animated Cartoon Characters
• Emotional Expressions
• Hindi Storytelling
• Wikipedia Facts

{source}

👨‍👩‍👧‍👦 Subscribe for daily animated stories!

#CartoonStory #HindiAnimation #KidsStory #RealVideo #Educational""",
            "tags": ["cartoon", "animation", "hindi story", "kids", "real footage", 
                    "stock video", "educational", "animated", "children", "inspiration"],
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
