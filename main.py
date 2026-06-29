import os
import base64
import pickle
import random
import sys
import textwrap
import math

# ============ STEP 1: Setup & Imports ============
try:
    # ✅ NEW API: google-genai (NOT google.generativeai)
    from google import genai
    from google.genai import types
    from gtts import gTTS
    from moviepy.editor import (ImageClip, AudioFileClip, CompositeVideoClip, 
                                TextClip, ColorClip, concatenate_videoclips,
                                ImageSequenceClip)
    from moviepy.video.fx.all import fadein, fadeout
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)

# ============ STEP 2: Setup Secrets ============
print("🔐 Setting up credentials...")
try:
    with open("client_secret.json", "w", encoding="utf-8") as f:
        f.write(os.environ["CLIENT_SECRET_JSON"])
    
    token_data = base64.b64decode(os.environ["TOKEN_PICKLE_BASE64"])
    with open("token.pickle", "wb") as f:
        f.write(token_data)
    print("✅ Credentials setup complete!")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# ============ STEP 3: Topic Selection ============
topics = [
    {
        "title": "बच्चों के लिए 5 जादुई गणित ट्रिक्स",
        "hook": "2 सेकंड में गुणा करना सीखें!",
        "category": "education",
        "duration": 150
    },
    {
        "title": "बच्चों में आत्मविश्वास बढ़ाने के 3 सीक्रेट तरीके",
        "hook": "90% पेरेंट्स ये गलती करते हैं...",
        "category": "parenting",
        "duration": 180
    },
    {
        "title": "बच्चों के लिए कोडिंग क्यों ज़रूरी है? 2026",
        "hook": "भविष्य की सबसे बड़ी स्किल!",
        "category": "technology",
        "duration": 200
    },
    {
        "title": "बच्चों को पैसे की बचत कैसे सिखाएं?",
        "hook": "6 साल में Smart Investor!",
        "category": "finance",
        "duration": 160
    },
    {
        "title": "घर पर 3 आसान विज्ञान प्रयोग",
        "hook": "रसोई में Science Magic!",
        "category": "science",
        "duration": 170
    },
    {
        "title": "बच्चों का स्क्रीन टाइम कम करें",
        "hook": "बच्चा फोन छोड़ देगा!",
        "category": "parenting",
        "duration": 140
    },
    {
        "title": "बच्चों के लिए प्रेरणादायक कहानी",
        "hook": "एक कहानी जो बदल देगी सोच!",
        "category": "story",
        "duration": 220
    },
    {
        "title": "बच्चों की एकाग्रता बढ़ाने के 5 तरीके",
        "hook": "पढ़ाई में मन नहीं लगता?",
        "category": "education",
        "duration": 155
    },
    {
        "title": "बच्चों के लिए Best Memory Techniques",
        "hook": "कभी कुछ नहीं भूलेंगे!",
        "category": "education",
        "duration": 175
    },
    {
        "title": "बच्चों में Good Habits कैसे डालें?",
        "hook": "21 दिन में बदल जाएगा!",
        "category": "parenting",
        "duration": 165
    }
]

selected = random.choice(topics)
selected_topic = selected["title"]
selected_hook = selected["hook"]
target_duration = selected["duration"]
print(f"🎯 Topic: {selected_topic}")
print(f"🎣 Hook: {selected_hook}")
print(f"⏱️ Duration: {target_duration}s")

# ============ STEP 4: Generate Script with NEW Gemini API ============
print("🤖 Generating script with Gemini...")

try:
    # ✅ NEW API: google-genai
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""YouTube Video (2-3 minutes) के लिए स्क्रिप्ट लिखो।

TOPIC: {selected_topic}
HOOK: {selected_hook}

नियम:
- शुरुआत HOOK से
- 5-7 points, हर point विस्तार से
- Real examples
- CTA आखिर में
- {target_duration * 2} शब्द
- सिर्फ Hindi text, no emojis
- Output: सिर्फ स्क्रिप्ट"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    script = response.text.strip()
    print(f"✅ Script: {len(script.split())} words")
    
except Exception as e:
    print(f"❌ Gemini Error: {e}")
    script = f"{selected_hook}\n\n{selected_topic} के बारे में जानें। पहला: रोज़ाना अभ्यास। दूसरा: खेल-खेल में सीखना। तीसरा: प्रशंसा। चौथा: सही माहौल। पांचवां: धैर्य। Like, Share, Subscribe!"
    print("⚠️ Using fallback")

# ============ STEP 5: Create Audio ============
print("🔊 Creating audio...")
try:
    tts = gTTS(text=script, lang='hi', slow=False)
    tts.save("audio.mp3")
    print("✅ Audio saved")
except Exception as e:
    print(f"❌ Audio Error: {e}")
    sys.exit(1)

# ============ STEP 6: ANIMATED BACKGROUND ============
print("🎨 Creating animated backgrounds...")

W, H = 1920, 1080

def create_animated_bg(frame_num, total_frames, color_scheme="blue"):
    img = Image.new('RGB', (W, H), color=(10, 10, 30))
    draw = ImageDraw.Draw(img)
    progress = frame_num / total_frames
    
    # Moving circles
    for i in range(5):
        cx = int(W * 0.2 + (W * 0.6) * math.sin(progress * 2 * math.pi + i * 0.8))
        cy = int(H * 0.3 + (H * 0.4) * math.cos(progress * 2 * math.pi + i * 0.6))
        r = 150 + int(50 * math.sin(progress * 4 + i))
        
        if color_scheme == "blue":
            color = (30 + i*20, 60 + i*15, 120 + i*25)
        elif color_scheme == "purple":
            color = (80 + i*15, 30, 120 + i*20)
        else:
            color = (20, 100 + i*20, 80 + i*15)
        
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
    
    # Floating particles
    for i in range(30):
        px = int((W * (i / 30) + frame_num * 2) % W)
        py = int((H * 0.1 * (i % 7) + frame_num) % H)
        size = 3 + (i % 4)
        brightness = 150 + int(100 * math.sin(progress * 10 + i))
        draw.ellipse([px, py, px+size, py+size], fill=(brightness, brightness, 200))
    
    # Wave lines
    for i in range(8):
        y = int(H * 0.1 + (H * 0.8) * (i / 8))
        wave = int(50 * math.sin(progress * 4 + i * 0.5))
        draw.line([(0, y + wave), (W, y - wave)], fill=(40, 60, 100), width=2)
    
    return np.array(img)

def create_text_frame(text, subtext="", frame_num=0, total_frames=1, anim_type="bounce"):
    base = create_animated_bg(frame_num, total_frames)
    img = Image.fromarray(base)
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
        sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
    except:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
    
    # Text animation
    if anim_type == "bounce":
        bounce = int(15 * abs(math.sin(frame_num * 0.3)))
        y_offset = 280 + bounce
    elif anim_type == "slide":
        slide = int(30 * (1 - math.exp(-frame_num * 0.1)))
        y_offset = 280 + slide
    else:
        y_offset = 280
    
    # Title with glow
    lines = textwrap.wrap(text, width=28)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        
        for glow in range(5, 0, -1):
            alpha = int(50 / glow)
            draw.text((x, y_offset), line, fill=(alpha, alpha, 150 + alpha), font=title_font)
        draw.text((x, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 85
    
    # Subtext
    if subtext:
        sub_lines = textwrap.wrap(subtext, width=40)
        y_offset = 520
        for line in sub_lines:
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            draw.text((x, y_offset), line, fill=(255, 215, 0), font=sub_font)
            y_offset += 50
    
    # Progress bar
    bar_width = int(W * 0.8 * (frame_num / total_frames))
    draw.rectangle([W*0.1, H-30, W*0.9, H-20], outline=(100, 100, 150), width=2)
    draw.rectangle([W*0.1, H-30, W*0.1 + bar_width, H-20], fill=(0, 200, 255))
    
    # Corner decorations
    size = 20 + int(10 * math.sin(frame_num * 0.15))
    draw.polygon([(50, 50), (50+size, 50), (50, 50+size)], fill=(0, 255, 200))
    draw.polygon([(W-50, 50), (W-50-size, 50), (W-50, 50+size)], fill=(0, 255, 200))
    draw.polygon([(50, H-50), (50+size, H-50), (50, H-50-size)], fill=(255, 100, 100))
    draw.polygon([(W-50, H-50), (W-50-size, H-50), (W-50, H-50-size)], fill=(255, 100, 100))
    
    return np.array(img)

# ============ STEP 7: Generate Video Frames ============
print("🎬 Generating animated video...")

fps = 24
audio = AudioFileClip("audio.mp3")
duration = min(audio.duration, target_duration)
total_frames = int(duration * fps)

sections = [s.strip() for s in script.split('\n') if s.strip() and len(s.strip()) > 10]
if len(sections) < 3:
    sections = [selected_topic, selected_hook] + sections

frames_per_section = total_frames // max(len(sections), 1)

all_frames = []
color_schemes = ["blue", "purple", "green", "blue", "purple", "green"]

print(f"Generating {total_frames} frames...")

for sec_idx, section in enumerate(sections[:6]):
    scheme = color_schemes[sec_idx % len(color_schemes)]
    
    for f in range(frames_per_section):
        frame_num = sec_idx * frames_per_section + f
        if frame_num >= total_frames:
            break
            
        anim_types = ["bounce", "slide", "pulse"]
        anim = anim_types[sec_idx % 3]
        
        frame = create_text_frame(section[:60], f"Tip {sec_idx + 1}" if sec_idx > 0 else selected_hook,
                                  frame_num, total_frames, anim)
        all_frames.append(frame)
        
        if frame_num % 60 == 0:
            print(f"  Frame {frame_num}/{total_frames}")

print(f"✅ Generated {len(all_frames)} frames")

# ============ STEP 8: Create Video ============
print("🎬 Creating video...")

try:
    # Save frames
    frame_files = []
    for i, frame in enumerate(all_frames):
        img = Image.fromarray(frame)
        fname = f"frame_{i:05d}.png"
        img.save(fname)
        frame_files.append(fname)
    
    # Create video
    clip = ImageSequenceClip(frame_files, fps=fps)
    
    # Subtitles
    subtitle_clips = []
    words = script.split()
    words_per_seg = max(1, len(words) // 8)
    
    segments = []
    current = []
    for i, word in enumerate(words):
        current.append(word)
        if len(current) >= words_per_seg or i == len(words) - 1:
            segments.append(" ".join(current))
            current = []
    
    seg_duration = duration / max(len(segments), 1)
    
    for i, segment in enumerate(segments):
        txt = TextClip(segment, fontsize=40, color='white', font='DejaVu-Sans',
                       stroke_color='black', stroke_width=2, method='caption',
                       size=(1600, None), align='center', bg_color='rgba(0,0,0,0.6)')
        txt = txt.set_position(('center', 850))
        txt = txt.set_start(i * seg_duration).set_duration(seg_duration)
        txt = fadein(txt, 0.2).fadeout(0.2)
        subtitle_clips.append(txt)
    
    # Intro
    intro = TextClip(selected_topic, fontsize=80, color='yellow', font='DejaVu-Sans-Bold',
                     stroke_color='red', stroke_width=3, method='caption',
                     size=(1800, None), align='center')
    intro = intro.set_position('center').set_duration(2)
    intro = intro.fx(fadein, 0.5).fadeout(0.5)
    
    # Outro
    outro = TextClip("Like, Share & Subscribe!", fontsize=70, color='white',
                     font='DejaVu-Sans-Bold', stroke_color='blue', stroke_width=3,
                     method='caption', size=(1600, None), align='center')
    outro = outro.set_position('center').set_start(duration - 3).set_duration(3)
    outro = fadein(outro, 0.5)
    
    # Composite
    final = CompositeVideoClip([clip] + subtitle_clips + [intro, outro])
    final = final.set_audio(audio.subclip(0, duration))
    
    # Write
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
    print("🧹 Temp frames cleaned")
    
except Exception as e:
    print(f"❌ Video Error: {e}")
    try:
        audio = AudioFileClip("audio.mp3")
        bg = ColorClip(size=(1920, 1080), color=(30, 30, 60)).set_duration(min(audio.duration, 180))
        video = bg.set_audio(audio)
        video.write_videofile("final_video.mp4", fps=24)
        print("⚠️ Fallback video created")
    except Exception as e2:
        print(f"❌ Critical: {e2}")
        sys.exit(1)

# ============ STEP 9: Upload to YouTube ============
print("📤 Uploading to YouTube...")
try:
    with open("token.pickle", "rb") as f:
        credentials = pickle.load(f)
    
    youtube = build("youtube", "v3", credentials=credentials)
    
    base_tags = ["hindi", "education", "kids", "bachche", "parenting", "animated"]
    cat_tags = {
        "education": ["math", "learning", "study", "school", "tips"],
        "parenting": ["motherhood", "childcare", "parenting tips", "baby"],
        "technology": ["coding", "scratch", "ai", "future", "tech"],
        "finance": ["money", "saving", "investment", "smart"],
        "science": ["experiment", "diy", "science", "stem"],
        "story": ["moral", "inspiration", "kahaniya", "story"]
    }
    
    tags = base_tags + cat_tags.get(selected.get("category", "education"), [])
    
    sections_desc = [s[:50] for s in sections[:6] if s.strip()]
    timestamps = ""
    for i, sec in enumerate(sections_desc):
        t = int(i * (duration / max(len(sections_desc), 1)))
        timestamps += f"{t//60}:{t%60:02d} {sec}...\n"
    
    body = {
        "snippet": {
            "title": f"🎬 {selected_topic} | Animated | बच्चों के लिए Best Tips",
            "description": f"""{selected_hook}

🎥 {selected_topic} - Fully Animated Video!

📌 Topics:
{chr(10).join([f"• {s[:60]}" for s in sections_desc])}

⏱️ Timestamps:
{timestamps}

✨ Features:
• Animated backgrounds
• Moving text effects
• Professional transitions
• Hindi subtitles

👨‍👩‍👧‍👦 Subscribe for more!

#Hindi #Education #Kids #Animated #Parenting""",
            "tags": tags[:15],
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
    print(f"❌ Upload Error: {e}")
    sys.exit(1)

# ============ STEP 10: Cleanup ============
print("🧹 Cleaning up...")
for f in ["audio.mp3", "client_secret.json", "token.pickle", "temp-audio.m4a"]:
    if os.path.exists(f):
        os.remove(f)

print(f"\n🎉 DONE! https://youtube.com/watch?v={vid}")
