"""
Voice Recording Functions - FIXED VERSION
=========================================
Author: User 67991023
Current Date and Time (UTC): 2025-09-02 06:47:37

FIXES:
- More precise stop keyword detection
- Better handling of long sentences
- Improved microphone timeout settings
"""

import speech_recognition as sr
import pyttsx3
import datetime
from typing import Optional, List, Dict
import time
from config import AUDIO_CONFIG, APP_CONFIG

def configure_microphone() -> sr.Recognizer:
    """
    Configure microphone and speech recognizer
    
    Returns:
        sr.Recognizer: Configured speech recognizer
    """
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
    """
    Record a single audio input and convert to text
    
    Args:
        recognizer: Configured speech recognizer
        
    Returns:
        Optional[str]: Transcribed text or None if failed
    """
    microphone = sr.Microphone()
    
    try:
        print("🎙️ กำลังฟัง... พูดได้เลย!")
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # FIXED: Increased timeout and phrase limit for long sentences
            audio = recognizer.listen(
                source, 
                timeout=AUDIO_CONFIG['timeout'],
                phrase_time_limit=120  # Increased from 60 to 120 seconds for long sentences
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
    """
    FIXED: More precise stop command detection
    
    Args:
        text: Input text to check
        
    Returns:
        bool: True if it's a stop command
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Exact match stop commands (more precise)
    exact_stop_commands = [
        'หยุดบันทึก',
        'หยุด บันทึก', 
        'จบ',
        'เสร็จแล้ว',
        'หยุด',
        'stop',
        'end',
        'ออก',
        'เลิก',
        'พอ',
        'จบการบันทึก',
        'หยุดการบันทึก'
    ]
    
    # Check if the ENTIRE text is a stop command (not just contains it)
    for stop_cmd in exact_stop_commands:
        if text_lower == stop_cmd.lower():
            return True
    
    # Additional check: if text is very short and contains stop word
    if len(text_lower.split()) <= 3:  # Only for very short phrases
        short_stop_words = ['หยุด', 'จบ', 'stop', 'end']
        for stop_word in short_stop_words:
            if text_lower == stop_word.lower():
                return True
    
    return False

def continuous_recording_mode(recognizer: sr.Recognizer) -> List[str]:
    """
    FIXED: Continuous recording mode with better stop detection
    
    Args:
        recognizer: Configured speech recognizer
        
    Returns:
        List[str]: List of recorded texts
    """
    print("🔄 เริ่มโหมดบันทึกต่อเนื่อง - IMPROVED VERSION")
    print("📢 วิธีหยุด: พูดคำว่า 'หยุดบันทึก', 'จบ', หรือ 'stop' เพียงอย่างเดียว")
    print("⚠️ หมายเหตุ: ต้องพูดคำสั่งหยุดเพียงอย่างเดียว ไม่ใช่เป็นส่วนหนึ่งของประโยค")
    print("=" * 60)
    
    recorded_texts = []
    
    while True:
        text = record_single_audio(recognizer)
        
        if text:
            # FIXED: Use the new precise stop detection
            if is_stop_command(text):
                print("🛑 ตรวจพบคำสั่งหยุด - หยุดบันทึกต่อเนื่อง...")
                print(f"📝 คำสั่งที่ได้รับ: '{text}'")
                break
            
            recorded_texts.append(text)
            print(f"📊 บันทึกแล้ว {len(recorded_texts)} รายการ")
            print(f"📝 ข้อความล่าสุด: {text[:80]}{'...' if len(text) > 80 else ''}")
        
        time.sleep(0.5)
    
    print(f"✅ จบการบันทึก: ได้ {len(recorded_texts)} รายการ")
    return recorded_texts

def store_voice_record(text: str, record_id: int) -> Dict:
    """
    Create a voice record dictionary with metadata
    
    Args:
        text: The transcribed text
        record_id: Unique record ID
        
    Returns:
        Dict: Voice record with metadata
    """
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
    """
    Initialize text-to-speech engine
    
    Returns:
        Optional[pyttsx3.Engine]: TTS engine or None if failed
    """
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"⚠️ TTS initialization failed: {e}")
        return None

def speak_text(engine: Optional[pyttsx3.Engine], text: str) -> None:
    """
    Speak text using TTS engine
    
    Args:
        engine: TTS engine
        text: Text to speak
    """
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ TTS error: {e}")

def test_stop_detection():
    """
    Test function to verify stop detection works correctly
    """
    print("🧪 Testing stop detection function...")
    
    test_cases = [
        ("หยุดบันทึก", True),  # Should stop
        ("จบ", True),  # Should stop
        ("stop", True),  # Should stop
        ("หยุด", True),  # Should stop
        ("ฉันจะหยุดเดินไปที่ตลาด", False),  # Should NOT stop (contains stop word but not exact)
        ("การเมืองไทยในยุคปัจจุบันมีการพัฒนาอย่างต่อเนื่อง", False),  # Should NOT stop
        ("เรื่องนี้จบแล้วใช่ไหม", False),  # Should NOT stop (contains 'จบ' but not exact)
        ("หยุดบันทึกเลย", False),  # Should NOT stop (contains but not exact)
        ("เสร็จแล้ว", True),  # Should stop
    ]
    
    for text, expected in test_cases:
        result = is_stop_command(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
    
    print("🧪 Stop detection test completed!")

# Test the function when module is run directly
if __name__ == "__main__":
    test_stop_detection()