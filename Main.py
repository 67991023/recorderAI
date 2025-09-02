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
        self.version = "ml-focused-1.1"
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
        print("\n🔍 Checking system capabilities...")
        
        capabilities = []
        if self.recognizer:
            capabilities.append("✅ Voice Recording")
        
        if ML_LIBS_AVAILABLE:
            capabilities.append("✅ ML Classification")
        else:
            capabilities.append("⚠️ ML Classification (limited)")
        
        capabilities.extend(["✅ Data Visualization", "✅ Report Generation", "✅ Data Export/Import"])
        
        print("📋 Available features:")
        for cap in capabilities:
            print(f"   {cap}")
    
    def record_voice_continuously(self):
        """Start continuous voice recording mode"""
        if not self.recognizer:
            print("❌ Voice recorder not available")
            return
        
        print("\n🎙️ Starting continuous voice recording...")
        recorded_texts = continuous_recording_mode(self.recognizer)
        
        if recorded_texts:
            print(f"\n📝 Processing {len(recorded_texts)} recordings...")
            
            for i, text in enumerate(recorded_texts):
                record_id = len(self.voice_records) + 1
                voice_record = store_voice_record(text, record_id)
                voice_record['word_count'] = fix_thai_word_count(text)
                self.voice_records.append(voice_record)
            
            if save_voice_records(self.voice_records):
                print(f"✅ Successfully saved {len(recorded_texts)} new recordings")
            else:
                print("❌ Failed to save recordings")
        else:
            print("ℹ️ No recordings captured")
    
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
{'=' * 50}
""")
        
        display_records = self.voice_records[-10:]
        
        for i, record in enumerate(display_records, 1):
            print(f"""
📌 รายการที่ {record['id']} (ล่าสุด #{i})
📅 วันที่: {record.get('date', 'N/A')} ⏰ เวลา: {record.get('time', 'N/A')}
📊 จำนวนคำ: {record.get('word_count', 0)} คำ | ตัวอักษร: {record.get('character_count', 0)} ตัว
📝 เนื้อหา: {record['text'][:80]}{'...' if len(record['text']) > 80 else ''}
{'-' * 60}""")
        
        if len(self.voice_records) >= 1:
            word_counts = [r.get('word_count', 0) for r in self.voice_records]
            avg_words = sum(word_counts) / len(word_counts)
            
            print(f"""
📊 สถิติสรุป:
• ค่าเฉลี่ยคำต่อรายการ: {avg_words:.1f}
• การบันทึกที่ยาวที่สุด: {max(word_counts)} คำ
• การบันทึกที่สั้นที่สุด: {min(word_counts)} คำ
• พร้อมสำหรับการวิเคราะห์ ML
""")
    
    def create_word_count_distribution(self):
        """Generate word count distribution chart"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับสร้างกราฟ")
            return
        
        print("📊 Creating word count distribution chart...")
        chart_path = create_word_count_distribution_chart(self.voice_records)
        
        if chart_path:
            print(f"✅ Chart saved: {chart_path}")
        else:
            print("❌ Failed to create chart")
    
    def run_ml_classification(self):
        """Run machine learning classification"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับการวิเคราะห์ ML")
            return None
        
        if not ML_LIBS_AVAILABLE:
            print("❌ ML libraries not available")
            return None
        
        print("🤖 Running ML classification...")
        results_df = ml_text_classification(self.voice_records)
        
        if not results_df.empty:
            print("✅ ML classification completed")
            return results_df
        else:
            print("❌ ML classification failed")
            return None
    
    def run_complete_analysis(self):
        """Run comprehensive analysis with ML features"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับวิเคราะห์")
            return
        
        print("\n🔬 เริ่มการวิเคราะห์ข้อมูลแบบครบถ้วน...")
        print("=" * 60)
        
        results_data = {}
        
        # Word Count Distribution
        print("📊 1. Creating Word Count Distribution...")
        word_chart = create_word_count_distribution_chart(self.voice_records)
        if word_chart:
            results_data['word_distribution'] = word_chart
        
        # Machine Learning Classification
        print("🤖 2. Running ML Classification...")
        results_df = self.run_ml_classification()
        if results_df is not None:
            results_data['ml_results'] = results_df
        
        # Comprehensive Dashboard
        if results_df is not None:
            print("📈 3. Creating Comprehensive Dashboard...")
            dashboard_path = create_comprehensive_dashboard(results_df)
            if dashboard_path:
                results_data['dashboard'] = dashboard_path
            
            # ML Classification Charts
            print("📊 4. Creating ML Classification Charts...")
            ml_chart = create_ml_classification_charts(results_df)
            if ml_chart:
                results_data['ml_charts'] = ml_chart
            
            # ML Analysis Report
            print("📄 5. Generating ML Analysis Report...")
            ml_report = generate_ml_analysis_report(results_df)
            ml_report_path = save_analysis_report(ml_report, "ml_analysis")
            if ml_report_path:
                results_data['ml_report'] = ml_report_path
        
        # Basic Summary Report
        print("📝 6. Generating Basic Summary Report...")
        basic_summary = generate_basic_summary(self.voice_records)
        basic_report_path = save_analysis_report(basic_summary, "basic")
        if basic_report_path:
            results_data['basic_report'] = basic_report_path
        
        # Project Summary
        print("🎓 7. Creating Project Summary...")
        project_summary = create_project_summary(self.voice_records, results_df)
        project_path = save_analysis_report(project_summary, "project_summary")
        if project_path:
            results_data['project_summary'] = project_path
        
        print("\n✅ การวิเคราะห์เสร็จสิ้น!")
        print("=" * 60)
        print("📁 ไฟล์ที่สร้าง:")
        for key, path in results_data.items():
            print(f"   • {key}: {path}")
    
    def generate_basic_summary_report(self):
        """Generate and display basic summary"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับสร้างรายงาน")
            return
        
        print("📊 Generating basic summary report...")
        summary = generate_basic_summary(self.voice_records)
        
        print("\n" + "="*60)
        print(summary)
        print("="*60)
        
        save_path = save_analysis_report(summary, "basic_summary")
        if save_path:
            print(f"💾 Report saved to: {save_path}")
    
    def search_recordings(self):
        """Search recordings interface"""
        if not self.voice_records:
            print("❌ ไม่มีการบันทึกเสียงให้ค้นหา")
            return
        
        keyword = input("🔍 ป้อนคำที่ต้องการค้นหา: ").strip()
        if not keyword:
            print("❌ กรุณาป้อนคำค้นหา")
            return
        
        results = search_voice_records(self.voice_records, keyword)
        
        if results:
            print(f"\n🔍 พบ {len(results)} รายการที่มี '{keyword}':")
            for record in results:
                print(f"\n📌 ID: {record['id']}")
                print(f"📅 วันที่: {record.get('date', 'N/A')}")
                print(f"     {record['text'][:70]}...")
                print()
        else:
            print(f"❌ ไม่พบการบันทึกที่มี '{keyword}'")
    
    def export_data(self):
        """Export data to CSV"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลให้ส่งออก")
            return
        
        print("📤 Exporting data to CSV...")
        csv_path = export_to_csv(self.voice_records)
        
        if csv_path:
            print(f"✅ Data exported successfully: {csv_path}")
        else:
            print("❌ Failed to export data")
    
    def show_main_menu(self):
        """Display main application menu"""
        print(f"""
{'='*70}
🎙️  THAI VOICE RECORDER WITH ML ANALYTICS
{'='*70}
👤 User: {self.user_login} | 📅 {self.current_datetime}
📊 Records: {len(self.voice_records)} | 🤖 ML: {'Available' if ML_LIBS_AVAILABLE else 'Limited'}

1️⃣  📝 Continuous Voice Recording
2️⃣  👁️  View All Recordings  
3️⃣  📊 Create Word Count Distribution
4️⃣  🤖 Run ML Classification
5️⃣  🔬 Run Complete Analysis
6️⃣  📄 Generate Basic Summary Report
7️⃣  🔍 Search Recordings
8️⃣  📤 Export Data to CSV
9️⃣  🚪 Exit

{'='*70}""")
    
    def run_interactive_mode(self):
        """Run main interactive interface"""
        print("🚀 Starting Thai Voice Recorder with ML Analytics")
        
        while True:
            try:
                self.show_main_menu()
                choice = input("👉 Select an option (1-9): ").strip()
                
                if choice == '1':
                    self.record_voice_continuously()
                elif choice == '2':
                    self.view_all_recordings()
                elif choice == '3':
                    self.create_word_count_distribution()
                elif choice == '4':
                    self.run_ml_classification()
                elif choice == '5':
                    self.run_complete_analysis()
                elif choice == '6':
                    self.generate_basic_summary_report()
                elif choice == '7':
                    self.search_recordings()
                elif choice == '8':
                    self.export_data()
                elif choice == '9':
                    print("👋 Thank you for using Thai Voice Recorder!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-9.")
                
                input("\n⏸️  Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("⏸️  Press Enter to continue...")

def main():
    """Main application entry point"""
    try:
        app = ThaiVoiceRecorderML()
        app.run_interactive_mode()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Please check your system configuration and try again.")

if __name__ == "__main__":
    main()