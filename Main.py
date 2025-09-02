from config import APP_CONFIG, FILE_CONFIG, AUDIO_CONFIG
from voiceRecord import configure_microphone, record_single_audio, continuous_recording_mode, store_voice_record
from Thai_textProcessing import fix_thai_word_count, validate_voice_records
from KMean import ml_text_classification, ML_LIBS_AVAILABLE
from dataVisualize import configure_matplotlib, create_word_count_distribution_chart, create_ml_classification_charts, create_comprehensive_dashboard
from dataManagement import load_voice_records, save_voice_records, create_directories, cleanup_voice_records, export_to_csv, search_voice_records
from analysisReport import generate_basic_summary, generate_ml_analysis_report, save_analysis_report, create_project_summary

class ThaiVoiceRecorderML:
    
    def __init__(self):
        self.user_login = "67991023"
        self.current_datetime = "2025-09-02 06:47:37"
        self.version = "ml-focused-1.0"
        self.voice_records = []
        self.recognizer = None
        self._initialize_application()
    
    def _initialize_application(self):
        """Initialize the application"""
        print(f"🚀 Initializing Thai Voice Recorder with ML Analytics...")
        print(f"👤 User: {self.user_login}")
        print(f"📅 Current Time: {self.current_datetime}")
        print(f"🔖 Version: {self.version}")
        
        create_directories()
        configure_matplotlib()
        self.recognizer = configure_microphone()
        self.voice_records = load_voice_records()
        self.voice_records = cleanup_voice_records(self.voice_records)
        self._check_capabilities()
        print("✅ Application initialized successfully!")
    
    def _check_capabilities(self):
        """Check available capabilities"""
        print(f"\n🔍 System capabilities:")
        print(f"   • Machine Learning: {'✅' if ML_LIBS_AVAILABLE else '❌'}")
        print(f"   • Voice Records: {len(self.voice_records)} loaded")
        
        if not ML_LIBS_AVAILABLE:
            print("⚠️ Install scikit-learn for ML features: pip install scikit-learn")
    
    def record_voice_continuously(self):
        """Start continuous voice recording mode"""
        if not self.recognizer:
            print("❌ Microphone not configured")
            return
        
        print("\n🔄 Starting continuous voice recording...")
        recorded_texts = continuous_recording_mode(self.recognizer)
        
        new_records_count = 0
        for text in recorded_texts:
            if text.strip():
                record = store_voice_record(text, len(self.voice_records) + new_records_count + 1)
                record['word_count'] = fix_thai_word_count(text)
                self.voice_records.append(record)
                new_records_count += 1
        
        if new_records_count > 0:
            save_voice_records(self.voice_records)
            print(f"💾 Saved {new_records_count} new recordings")
        
        if new_records_count >= 2:
            choice = input("\n🔬 ต้องการวิเคราะห์ข้อมูลทันทีไหม? (y/n): ")
            if choice.lower() in ['y', 'yes', 'ใช่']:
                self.run_complete_analysis()
    
    def view_all_recordings(self):
        """Display all voice recordings"""
        if not self.voice_records:
            print("❌ ไม่มีการบันทึกเสียงใดๆ")
            return
        
        print(f"""
📋 การบันทึกเสียงทั้งหมด
{'=' * 50}
👤 ผู้ใช้: {self.user_login}
📅 เวลาปัจจุบัน: {self.current_datetime}
📊 จำนวนรวม: {len(self.voice_records)} รายการ
{'=' * 50}""")
        
        for i, record in enumerate(self.voice_records, 1):
            word_count = record.get('word_count', 0)
            char_count = record.get('character_count', len(record.get('text', '')))
            timestamp = record.get('timestamp', 'N/A')
            
            print(f"""
{i}. ID: {record.get('id', i)} | คำ: {word_count} | ตัวอักษร: {char_count}
   📅 {timestamp[:19] if timestamp != 'N/A' else 'N/A'}
   📝 {record['text'][:100]}{'...' if len(record['text']) > 100 else ''}""")
        
        print(f"\n📊 สรุป: {len(self.voice_records)} รายการ")
    
    def create_word_count_distribution(self):
        """Generate word count distribution chart"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับสร้างกราฟ")
            return
        
        print("📊 กำลังสร้างกราฟการกระจายของจำนวนคำ...")
        chart_path = create_word_count_distribution_chart(self.voice_records)
        if chart_path:
            print(f"✅ สร้างกราฟเสร็จแล้ว: {chart_path}")
    
    def run_ml_classification(self):
        """Run machine learning classification"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับ ML")
            return None
        
        if not ML_LIBS_AVAILABLE:
            print("❌ ML libraries ไม่พร้อมใช้งาน")
            return None
        
        print("🤖 เริ่มการจำแนกข้อมูลด้วย Machine Learning...")
        results_df = ml_text_classification(self.voice_records)
        
        if results_df is not None and not results_df.empty:
            print("✅ ML Classification เสร็จสิ้น!")
            return results_df
        else:
            print("❌ ML Classification ล้มเหลว")
            return None
    
    def run_complete_analysis(self):
        """Run comprehensive analysis with ML features"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับวิเคราะห์")
            return
        
        print("\n🔬 เริ่มการวิเคราะห์ข้อมูลแบบครบถ้วน...")
        print("=" * 60)
        
        results_data = {}
        
        # 1. Word Count Distribution
        print("📊 1. Creating Word Count Distribution...")
        word_chart = create_word_count_distribution_chart(self.voice_records)
        if word_chart:
            results_data['word_distribution'] = word_chart
        
        # 2. Machine Learning Classification
        print("🤖 2. Running ML Classification...")
        results_df = self.run_ml_classification()
        if results_df is not None:
            results_data['ml_results'] = results_df
        
        # 3. Comprehensive Dashboard
        if results_df is not None:
            print("📊 3. Creating Comprehensive Dashboard...")
            dashboard_path = create_comprehensive_dashboard(results_df)
            if dashboard_path:
                results_data['dashboard'] = dashboard_path
        
        # 4. Generate Reports
        print("📋 4. Generating Analysis Reports...")
        
        # Basic summary
        basic_summary = generate_basic_summary(self.voice_records)
        basic_report_path = save_analysis_report(basic_summary, "basic")
        
        # ML report if available
        if results_df is not None:
            ml_report = generate_ml_analysis_report(results_df)
            ml_report_path = save_analysis_report(ml_report, "ml_analysis")
            results_data['ml_report'] = ml_report_path
        
        # Project summary
        project_summary = create_project_summary(self.voice_records, results_df)
        project_report_path = save_analysis_report(project_summary, "project_summary")
        results_data['project_summary'] = project_report_path
        
        print("\n✅ การวิเคราะห์ข้อมูลเสร็จสิ้นแบบครบถ้วน!")
        print(f"📁 ผลลัพธ์บันทึกใน: {FILE_CONFIG['output_dir']}")
        
        # Summary of results
        print(f"\n📊 สรุปผลการวิเคราะห์:")
        for key, value in results_data.items():
            if value:
                print(f"   ✅ {key}: {value if isinstance(value, str) else 'Completed'}")
        
        return results_data
    
    def generate_basic_summary_report(self):
        """Generate and display basic summary"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับสร้างรายงาน")
            return
        
        print("📊 กำลังสร้างรายงานสรุปพื้นฐาน...")
        summary = generate_basic_summary(self.voice_records)
        
        print("\n" + "="*60)
        print(summary)
        print("="*60)
        
        # Save report
        report_path = save_analysis_report(summary, "basic_summary")
        if report_path:
            print(f"📁 รายงานบันทึกไว้ที่: {report_path}")
    
    def search_recordings(self):
        """Search recordings interface"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลให้ค้นหา")
            return
        
        keyword = input("🔍 ป้อนคำค้น: ").strip()
        if not keyword:
            print("❌ ไม่ได้ระบุคำค้น")
            return
        
        results = search_voice_records(self.voice_records, keyword)
        
        if results:
            print(f"\n📊 ผลการค้นหา '{keyword}': {len(results)} รายการ")
            print("=" * 50)
            
            for i, record in enumerate(results, 1):
                print(f"\n{i}. ID: {record.get('id', 'N/A')} | คำ: {record.get('word_count', 0)}")
                print(f"     {record['text'][:70]}...")
                print()
        else:
            print(f"❌ ไม่พบการบันทึกที่มี '{keyword}'")
    
    def export_data(self):
        """Export data to CSV"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลให้ Export")
            return
        
        print("📊 กำลัง Export ข้อมูลเป็น CSV...")
        csv_path = export_to_csv(self.voice_records)
        
        if csv_path:
            print(f"✅ Export สำเร็จ: {csv_path}")
        else:
            print("❌ Export ล้มเหลว")
    
    def show_main_menu(self):
        """Display main application menu"""
        print(f"""
{'='*60}
🎙️ THAI VOICE RECORDER WITH ML ANALYTICS
{'='*60}
👤 User: {self.user_login} | 📊 Records: {len(self.voice_records)}
📅 {self.current_datetime} | 🔖 {self.version}

📋 MENU OPTIONS:
1️⃣  บันทึกเสียงแบบต่อเนื่อง (Continuous Recording)
2️⃣  ดูการบันทึกทั้งหมด (View All Recordings)
3️⃣  สร้างกราฟการกระจายคำ (Word Count Distribution)
4️⃣  รันการจำแนกด้วย ML (ML Classification)
5️⃣  วิเคราะห์ข้อมูลแบบครบถ้วน (Complete Analysis)
6️⃣  สร้างรายงานสรุป (Generate Summary Report)
7️⃣  ค้นหาการบันทึก (Search Recordings)
8️⃣  Export เป็น CSV (Export to CSV)
9️⃣  ออกจากโปรแกรม (Exit)
{'='*60}""")
    
    def run_interactive_mode(self):
        """Run main interactive interface"""
        print("🚀 เข้าสู่โหมดปฏิสัมพันธ์")
        
        while True:
            try:
                self.show_main_menu()
                choice = input("\n👉 เลือกตัวเลือก (1-9): ").strip()
                
                menu_actions = {
                    '1': self.record_voice_continuously,
                    '2': self.view_all_recordings,
                    '3': self.create_word_count_distribution,
                    '4': self.run_ml_classification,
                    '5': self.run_complete_analysis,
                    '6': self.generate_basic_summary_report,
                    '7': self.search_recordings,
                    '8': self.export_data,
                    '9': lambda: self._exit_application()
                }
                
                if choice in menu_actions:
                    if choice == '9':
                        break
                    menu_actions[choice]()
                else:
                    print("❌ ตัวเลือกไม่ถูกต้อง กรุณาเลือก 1-9")
                
                input("\n⏸️  กด Enter เพื่อดำเนินการต่อ...")
                
            except KeyboardInterrupt:
                print("\n\n🛑 หยุดการทำงานโดยผู้ใช้")
                break
            except Exception as e:
                print(f"\n❌ เกิดข้อผิดพลาด: {e}")
    
    def _exit_application(self):
        """Exit application with summary"""
        print(f"""
🎯 สรุปการใช้งาน:
📊 จำนวนการบันทึกทั้งหมด: {len(self.voice_records)}
👤 ผู้ใช้: {self.user_login}
📅 Current Date and Time (UTC): 2025-09-02 06:47:37
🔖 Version: {self.version}

✅ ขอบคุณที่ใช้ Thai Voice Recorder with ML Analytics!
""")

def main():
    """Main application entry point"""
    try:
        app = ThaiVoiceRecorderML()
        app.run_interactive_mode()
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    main()