from config import APP_CONFIG, FILE_CONFIG, AUDIO_CONFIG
from voiceRecord import configure_microphone, record_single_audio, continuous_recording_mode, store_voice_record
from Thai_textProcessing import fix_thai_word_count
from KMean import ml_text_classification, ML_LIBS_AVAILABLE
from dataVisualize import configure_matplotlib, create_word_count_distribution_chart, create_ml_classification_charts, create_comprehensive_dashboard
from dataManagement import load_voice_records, save_voice_records, create_directories, cleanup_voice_records, export_to_csv, search_voice_records
from analysisReport import generate_basic_summary, generate_ml_analysis_report, save_analysis_report, create_project_summary

class ThaiVoiceRecorderML:
    
    def __init__(self):
        # Application info (UPDATED TIMESTAMP)
        self.user_login = "67991023"
        self.current_datetime = "2025-08-28 07:06:16"
        self.version = "ml-focused-1.0"
        
        # Initialize components
        self.voice_records = []
        self.recognizer = None
        
        # Setup
        self._initialize_application()
    
    def _initialize_application(self):
        """Initialize the application"""
        print(f"🚀 Initializing Thai Voice Recorder with ML Analytics...")
        print(f"👤 User: {self.user_login}")
        print(f"📅 Current Time: {self.current_datetime}")
        print(f"🔖 Version: {self.version}")
        
        # Create directories
        create_directories()
        
        # Configure visualization
        configure_matplotlib()
        
        # Configure microphone
        self.recognizer = configure_microphone()
        
        # Load existing data
        self.voice_records = load_voice_records()
        self.voice_records = cleanup_voice_records(self.voice_records)
        
        # Check capabilities
        self._check_capabilities()
        
        print("✅ Application initialized successfully!")
    
    def _check_capabilities(self):
        """Check available capabilities"""
        print("\n🔍 Checking system capabilities:")
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
        
        # Store all recorded texts
        new_records_count = 0
        for text in recorded_texts:
            if text.strip():
                record = store_voice_record(text, len(self.voice_records) + new_records_count + 1)
                record['word_count'] = fix_thai_word_count(text)
                self.voice_records.append(record)
                new_records_count += 1
        
        # Save data
        if new_records_count > 0:
            save_voice_records(self.voice_records)
            print(f"💾 Saved {new_records_count} new recordings")
        
        # Offer immediate analysis
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
{'=' * 50}
""")
        
        # Show last 10 records with enhanced info
        display_records = self.voice_records[-10:]
        
        for i, record in enumerate(display_records, 1):
            print(f"""
📌 รายการที่ {record['id']} (ล่าสุด #{i})
📅 วันที่: {record.get('date', 'N/A')} ⏰ เวลา: {record.get('time', 'N/A')}
📊 จำนวนคำ: {record.get('word_count', 0)} คำ | ตัวอักษร: {record.get('character_count', 0)} ตัว
📝 เนื้อหา: {record['text'][:80]}{'...' if len(record['text']) > 80 else ''}
{'-' * 60}""")
        
        # Quick statistics
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
        
        print("📊 กำลังสร้างกราฟ Word Count Distribution...")
        chart_path = create_word_count_distribution_chart(self.voice_records)
        
        if chart_path:
            print(f"✅ กราฟบันทึกแล้วที่: {chart_path}")
        else:
            print("❌ ไม่สามารถสร้างกราฟได้")
    
    def run_ml_classification(self):
        """Run machine learning classification"""
        if not ML_LIBS_AVAILABLE:
            print("❌ Machine Learning libraries ไม่พร้อมใช้งาน")
            print("กรุณาติดตั้ง: pip install scikit-learn")
            return
        
        if len(self.voice_records) < 2:
            print("❌ ต้องมีข้อมูลอย่างน้อย 2 รายการสำหรับ ML")
            return
        
        print("🤖 กำลังทำ Machine Learning Classification...")
        results_df = ml_text_classification(self.voice_records)
        
        if not results_df.empty:
            # Create ML visualization
            chart_path = create_ml_classification_charts(results_df)
            
            if chart_path:
                print(f"✅ ML analysis charts saved: {chart_path}")
            
            return results_df
        else:
            print("❌ ไม่สามารถทำ ML classification ได้")
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
            print("❌ ไม่มีข้อมูลสำหรับสร้างสรุป")
            return
        
        print("📊 กำลังสร้างสรุปการวิเคราะห์...")
        summary = generate_basic_summary(self.voice_records)
        
        # Display summary
        print(summary)
        
        # Save summary
        report_path = save_analysis_report(summary, "basic_summary")
        if report_path:
            print(f"\n📄 สรุปบันทึกไว้ที่: {report_path}")
    
    def search_recordings(self):
        """Search recordings interface"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับค้นหา")
            return
        
        keyword = input("🔍 ใส่คำค้นหา: ").strip()
        if not keyword:
            print("❌ กรุณาใส่คำค้นหา")
            return
        
        results = search_voice_records(self.voice_records, keyword)
        
        if results:
            print(f"\n🎯 พบ {len(results)} รายการที่มี '{keyword}':")
            print("-" * 50)
            
            for i, record in enumerate(results[-5:], 1):  # Show last 5 results
                print(f"{i:2d}. [{record.get('date', 'N/A')} {record.get('time', 'N/A')}] ({record.get('word_count', 0)} คำ)")
                print(f"     {record['text'][:70]}...")
                print()
        else:
            print(f"❌ ไม่พบการบันทึกที่มี '{keyword}'")
    
    def export_data(self):
        """Export data to CSV"""
        if not self.voice_records:
            print("❌ ไม่มีข้อมูลสำหรับ export")
            return
        
        export_path = export_to_csv(self.voice_records)
        if export_path:
            print(f"📤 ข้อมูล export แล้วที่: {export_path}")
        else:
            print("❌ ไม่สามารถ export ข้อมูลได้")
    
    def show_main_menu(self):
        """Display main application menu"""
        print(f"\n{'🎙️ Thai Voice Recorder with ML Analytics' :^70}")
        print(f"{'👤 User: ' + self.user_login + ' | 📅 ' + self.current_datetime :^70}")
        print(f"{'🔬 Features: ML Classification + Word Distribution + Visualization' :^70}")
        print("=" * 70)
        
        print("📋 ตัวเลือกหลัก:")
        print("1. 🔄 บันทึกเสียงต่อเนื่อง")
        print("2. 👁️  ดูการบันทึกทั้งหมด")
        print("3. 📊 สร้างกราฟ Word Count Distribution")
        print("4. 🤖 ทำ Machine Learning Classification")
        print("5. 🔬 วิเคราะห์ข้อมูลแบบครบถ้วน (ML + Visualization)")
        print("6. 📋 สร้างสรุปการวิเคราะห์")
        print("7. 🔍 ค้นหาการบันทึก")
        print("8. 📤 Export ข้อมูล (CSV)")
        print("0. 🚪 ออกจากโปรแกรม")
    
    def run_interactive_mode(self):
        """Run main interactive interface"""
        print(f"🚀 เริ่มใช้งาน Thai Voice Recorder with ML Analytics!")
        print(f"📊 ข้อมูลปัจจุบัน: {len(self.voice_records)} การบันทึก")
        print(f"🎯 พร้อมสำหรับการวิเคราะห์ด้วย Machine Learning")
        
        while True:
            self.show_main_menu()
            choice = input(f"\n🔢 เลือกหมายเลข (0-8): ").strip()
            
            try:
                if choice == "1":
                    self.record_voice_continuously()
                    
                elif choice == "2":
                    self.view_all_recordings()
                    
                elif choice == "3":
                    self.create_word_count_distribution()
                    
                elif choice == "4":
                    self.run_ml_classification()
                    
                elif choice == "5":
                    self.run_complete_analysis()
                    
                elif choice == "6":
                    self.generate_basic_summary_report()
                    
                elif choice == "7":
                    self.search_recordings()
                    
                elif choice == "8":
                    self.export_data()
                    
                elif choice == "0":
                    print(f"\n👋 ขอบคุณที่ใช้ Thai Voice Recorder with ML Analytics!")
                    print(f"📊 รวมการบันทึก: {len(self.voice_records)} รายการ")
                    print(f"💾 ข้อมูลบันทึกไว้ที่: {FILE_CONFIG['data_file']}")
                    print(f"📁 ผลการวิเคราะห์: {FILE_CONFIG['output_dir']}")
                    print(f"👤 ผู้ใช้: {self.user_login}")
                    print(f"🕒 เซสชันสิ้นสุด: {self.current_datetime}")
                    print(f"🔖 เวอร์ชัน: {self.version}")
                    print(f"✨ ขอบคุณที่ใช้บริการ!")
                    break
                    
                else:
                    print("❌ เลือกหมายเลขไม่ถูกต้อง (0-8)")
                
            except KeyboardInterrupt:
                print("\n\n⚠️ โปรแกรมถูกหยุดโดยผู้ใช้")
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
            
            input("\n📱 กด Enter เพื่อดำเนินการต่อ...")

def main():
    """Main application entry point"""
    try:
        print("🚀 Starting Thai Voice Recorder with ML Analytics...")
        print(f"👤 Current User Login: 67991023")
        print(f"📅 Current Date and Time (UTC): 2025-08-28 07:06:16")
        print(f"🔬 Features: Voice Recording + ML Classification + Word Distribution + Visualization")
        print("=" * 80)
        
        # Create and run application
        app = ThaiVoiceRecorderML()
        app.run_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ โปรแกรมถูกหยุดโดยผู้ใช้")
        print("👋 ขอบคุณที่ใช้บริการ!")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        print("🔧 กรุณาตรวจสอบการติดตั้ง dependencies")
        
    finally:
        print("🏁 โปรแกรมสิ้นสุด - Thai Voice Analytics Project")

if __name__ == "__main__":
    main()