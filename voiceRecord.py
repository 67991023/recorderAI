"""
Voice Recording Functions
Author: User 67991023
Current Date and Time (UTC): 2025-09-02 06:47:37
"""

import speech_recognition as sr
import pyttsx3
import datetime
from typing import Optional, List, Dict
import time
from config import AUDIO_CONFIG, APP_CONFIG

def configure_microphone() -> sr.Recognizer:
    """Configure microphone and speech recognizer"""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    try:
        with microphone as source:
            print("🔧 Configuring microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold = AUDIO_CONFIG['energy_threshold']
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = AUDIO_CONFIG['pause_threshold']
            recognizer.phrase_threshold = AUDIO_CONFIG['phrase_threshold']
            print("✅ Microphone configured successfully")
    except Exception as e:
        print(f"⚠️ Microphone configuration warning: {e}")
    
    return recognizer

def record_single_audio(recognizer: sr.Recognizer) -> Optional[str]:
    """Record a single audio input and convert to text"""
    microphone = sr.Microphone()
    
    try:
        print("🎙️ กำลังฟัง... พูดได้เลย!")
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source, 
                timeout=AUDIO_CONFIG['timeout'],
                phrase_time_limit=120
            )
            
        print("🔄 กำลังประมวลผล...")
        
        text = recognizer.recognize_google(
            audio, 
            language=AUDIO_CONFIG['language'],
            show_all=False
        )
        
        print(f"✅ ได้ข้อความ: {text[:50]}{'...' if len(text) > 50 else ''}")
        return text
        
    except sr.WaitTimeoutError:
        print("⏰ ไม่มีเสียงในช่วงเวลาที่กำหนด")
        return None
    except sr.UnknownValueError:
        print("❌ ไม่สามารถเข้าใจเสียงได้")
        return None
    except sr.RequestError as e:
        print(f"❌ ข้อผิดพลาดในการรู้จำเสียง: {e}")
        return None
    except Exception as e:
        print(f"❌ ข้อผิดพลาดอื่นๆ: {e}")
        return None

def is_stop_command(text: str) -> bool:
    """Check if text is a stop command"""
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    exact_stop_commands = [
        'หยุดบันทึก', 'หยุด บันทึก', 'จบ', 'เสร็จแล้ว', 'หยุด', 'stop', 'end',
        'ออก', 'เลิก', 'พอ', 'จบการบันทึก', 'หยุดการบันทึก'
    ]
    
    for stop_cmd in exact_stop_commands:
        if text_lower == stop_cmd.lower():
            return True
    
    if len(text_lower.split()) <= 3:
        short_stop_words = ['หยุด', 'จบ', 'stop', 'end']
        for stop_word in short_stop_words:
            if text_lower == stop_word.lower():
                return True
    
    return False

def continuous_recording_mode(recognizer: sr.Recognizer) -> List[str]:
    """Continuous recording mode with stop detection"""
    print("🔄 เริ่มโหมดบันทึกต่อเนื่อง")
    print("📢 วิธีหยุด: พูดคำว่า 'หยุดบันทึก', 'จบ', หรือ 'stop' เพียงอย่างเดียว")
    print("=" * 60)
    
    recorded_texts = []
    
    while True:
        text = record_single_audio(recognizer)
        
        if text:
            if is_stop_command(text):
                print("🛑 ตรวจพบคำสั่งหยุด - หยุดบันทึกต่อเนื่อง...")
                break
            
            recorded_texts.append(text)
            print(f"📊 บันทึกแล้ว {len(recorded_texts)} รายการ")
            print(f"📝 ข้อความล่าสุด: {text[:80]}{'...' if len(text) > 80 else ''}")
        
        time.sleep(0.5)
    
    print(f"✅ จบการบันทึก: ได้ {len(recorded_texts)} รายการ")
    return recorded_texts

def store_voice_record(text: str, record_id: int) -> Dict:
    """Create a voice record dictionary with metadata"""
    now = datetime.datetime.now()
    
    record = {
        'id': record_id,
        'text': text.strip(),
        'timestamp': now.isoformat(),
        'date': now.strftime("%Y-%m-%d"),
        'time': now.strftime("%H:%M:%S"),
        'day_of_week': now.strftime("%A"),
        'character_count': len(text),
        'user_id': APP_CONFIG['user_login'],
        'session_time': APP_CONFIG['current_datetime'],
        'version': APP_CONFIG['version']
    }
    
    return record

def initialize_tts_engine() -> Optional[pyttsx3.Engine]:
    """Initialize text-to-speech engine"""
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"⚠️ TTS initialization failed: {e}")
        return None

def speak_text(engine: Optional[pyttsx3.Engine], text: str) -> None:
    """Speak text using TTS engine"""
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ TTS error: {e}")

def test_stop_detection():
    """Test function to verify stop detection works correctly"""
    print("🧪 Testing stop detection function...")
    
    test_cases = [
        ("หยุดบันทึก", True), ("จบ", True), ("stop", True), ("หยุด", True),
        ("ฉันจะหยุดเดินไปที่ตลาด", False), ("การเมืองไทยในยุคปัจจุบันมีการพัฒนาอย่างต่อเนื่อง", False),
        ("เรื่องนี้จบแล้วใช่ไหม", False), ("หยุดบันทึกเลย", False), ("เสร็จแล้ว", True)
    ]
    
    for text, expected in test_cases:
        result = is_stop_command(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
    
    print("🧪 Stop detection test completed!")

if __name__ == "__main__":
    test_stop_detection()