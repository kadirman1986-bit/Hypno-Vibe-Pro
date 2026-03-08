import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy.fft import rfft, rfftfreq
from gtts import gTTS
import matplotlib.pyplot as plt
import os
import tempfile
import subprocess # المكتبة الأساسية البديلة

# ==========================================
# 1. إعدادات الواجهة (UI Configuration)
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Neuro-Engineering", layout="wide", page_icon="🧠")
st.title("🧠 نظام Hypno-Vibe Pro - مختبر الهندسة العصبية")
st.markdown("---")

# ==========================================
# 2. الدوال الهندسية (Core Functions)
# ==========================================
def generate_binaural_beat(base_freq, beat_freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, sample_rate * duration)
    left = np.sin(2 * np.pi * base_freq * t)
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    audio_data = np.vstack((left, right)).T
    audio_data = (audio_data * 32767).astype(np.int16)
    
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_wav.name, sample_rate, audio_data)
    return temp_wav.name

def generate_tts(text, lang='ar'):
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=text, lang=lang)
    tts.save(temp_mp3.name)
    return temp_mp3.name

def mix_audio_ffmpeg(bg_wav, voice_mp3, output_file):
    """دمج الصوتيات باستخدام خادم Linux مباشرة بدلا من مكتبات بايثون"""
    # نخفض صوت التردد (0.3) وندمج معه السكريبت الصوتي
    cmd = [
        'ffmpeg', '-y',
        '-i', bg_wav,
        '-i', voice_mp3,
        '-filter_complex',
        '[0:a]volume=0.3[bg];[1:a]adelay=2000|2000[v];[bg][v]amix=inputs=2:duration=first',
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ==========================================
# 3. القائمة الجانبية (Sidebar Navigation)
# ==========================================
st.sidebar.title("وحدات التحكم 🎛️")
module = st.sidebar.radio("اختر النظام:", 
                          ["1️⃣ مولد الجلسات الفردية", 
                           "2️⃣ بروتوكول الزوجين (Sync)", 
                           "3️⃣ الدرع الواقي (FFT Scanner)"])

# ==========================================
# الوحدة الأولى: مولد الجلسات
# ==========================================
if module == "1️⃣ مولد الجلسات الفردية":
    st.header("🎧 توليد جلسة هندسة عصبية")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("اسم العميل (اختياري):", "Guest")
        session_type = st.selectbox("نوع الجلسة المستهدفة:", 
                                    ["الاسترخاء العميق (Alpha 10Hz)", 
                                     "التركيز والنشاط (Beta 15Hz)", 
                                     "تطهير الترددات (Detox 432Hz)", 
                                     "رنين الأرض (Schumann 7.83Hz)"])
        duration = st.slider("المدة (بالثواني) للتجربة:", 10, 120, 30)
    
    with col2:
        st.info("💡 **السكريبت الإيحائي:** سيتم دمجه مع الترددات آلياً.")
        custom_script = st.text_area("اكتب سكريبت الجلسة هنا:", 
                                     "استرخ تماماً. أنت الآن في مكان آمن، وتستعيد توازنك الطبيعي.")
    
    if st.button("🚀 بدء توليد الجلسة"):
        with st.spinner("جاري المعالجة الهندسية عبر خوادم Streamlit..."):
            freq_map = {
                "الاسترخاء العميق (Alpha 10Hz)": {"base": 200, "beat": 10},
                "التركيز والنشاط (Beta 15Hz)": {"base": 200, "beat": 15},
                "تطهير الترددات (Detox 432Hz)": {"base": 432, "beat": 8},
                "رنين الأرض (Schumann 7.83Hz)": {"base": 144.72, "beat": 7.83}
            }
            config = freq_map[session_type]
            
            wav_path = generate_binaural_beat(config["base"], config["beat"], duration)
            tts_path = generate_tts(custom_script)
            output_file = f"Session_{client_name}.mp3"
            
            # الدمج عبر دالتنا الجديدة
            mix_audio_ffmpeg(wav_path, tts_path, output_file)
            
            st.success(f"✅ تمت هندسة الجلسة بنجاح: التردد الأساسي {config['base']}Hz | النبضة {config['beat']}Hz")
            st.audio(output_file)

# الوحدة الثانية والثالثة تبقى كما هي في الكود السابق...
