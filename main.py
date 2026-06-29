import os
import google.generativeai as genai
from gtts import gTTS

# 1. API Key सेटअप (यह आपके GitHub Secrets से की उठाएगा)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY सेट नहीं है!")
else:
    genai.configure(api_key=api_key)

    # 2. Gemini के जरिए स्क्रिप्ट तैयार करना
    print("Gemini से स्क्रिप्ट बन रही है...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "YouTube Shorts के लिए एक 40 सेकंड का रोचक फैक्ट (तथ्य) हिंदी में लिखो।"
    response = model.generate_content(prompt)
    script_text = response.text

    print("Script तैयार है:", script_text)

    # 3. gTTS के जरिए ऑडियो बनाना (100% फ्री)
    print("ऑडियो फाइल बन रही है...")
    tts = gTTS(text=script_text, lang='hi')
    tts.save("audio.mp3")

    print("सफलता! audio.mp3 फाइल बन गई है।")
