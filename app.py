import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy.fft import rfft, rfftfreq
from gtts import gTTS
from pydub import AudioSegment
import matplotlib.pyplot as plt
import os
import tempfile

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
    """توليد ترددات Binaural Beats"""
    t = np.linspace(0, duration, sample_rate * duration)
    # الأذن اليسرى (التردد الأساسي)
    left = np.sin(2 * np.pi * base_freq * t)
    # الأذن اليمنى (التردد الأساسي + فارق النبضة)
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    
    # تحويل إلى 16-bit PCM
    audio_data = np.vstack((left, right)).T
    audio_data = (audio_data * 32767).astype(np.int16)
    
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_wav.name, sample_rate, audio_data)
    return temp_wav.name

def generate_tts(text, lang='ar'):
    """توليد السكريبت الصوتي AI"""
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=text, lang=lang)
    tts.save(temp_mp3.name)
    return temp_mp3.name

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
        with st.spinner("جاري المعالجة الهندسية..."):
            # تحديد الترددات
            freq_map = {
                "الاسترخاء العميق (Alpha 10Hz)": {"base": 200, "beat": 10},
                "التركيز والنشاط (Beta 15Hz)": {"base": 200, "beat": 15},
                "تطهير الترددات (Detox 432Hz)": {"base": 432, "beat": 8},
                "رنين الأرض (Schumann 7.83Hz)": {"base": 144.72, "beat": 7.83}
            }
            config = freq_map[session_type]
            
            # توليد الملفات
            wav_path = generate_binaural_beat(config["base"], config["beat"], duration)
            tts_path = generate_tts(custom_script)
            
            # الدمج
            bg_audio = AudioSegment.from_wav(wav_path)
            voice = AudioSegment.from_mp3(tts_path)
            # خفض صوت الترددات ليكون في الخلفية
            bg_audio = bg_audio - 10 
            final_audio = bg_audio.overlay(voice, position=2000)
            
            output_file = f"Session_{client_name}.mp3"
            final_audio.export(output_file, format="mp3")
            
            st.success(f"✅ تمت هندسة الجلسة بنجاح: التردد الأساسي {config['base']}Hz | النبضة {config['beat']}Hz")
            st.audio(output_file)

# ==========================================
# الوحدة الثانية: بروتوكول الزوجين
# ==========================================
elif module == "2️⃣ بروتوكول الزوجين (Sync)":
    st.header("💞 بروتوكول المزامنة البيولوجية (Couples Sync)")
    st.markdown("هذا النظام يقوم بتوليد ملفين منفصلين يعملان بالتوازي. **الزوج** يستمع لترددات التهدئة (تأخير الاستجابة)، و**الزوجة** تستمع لترددات التحفيز وإزالة التوتر.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👨 مسار الزوج (Down-clocking)")
        male_freq = st.selectbox("تردد التهدئة:", ["Schumann (7.83Hz)", "Deep Theta (5Hz)"])
    
    with col2:
        st.subheader("👩 مسار الزوجة (Letting Go)")
        female_freq = st.selectbox("تردد التحفيز/الاسترخاء:", ["Venus Frequency (210.42Hz)", "Alpha Focus (12Hz)"])
        
    st.warning("⚠️ في النسخة القادمة، سيتم بث هذين المسارين عبر شبكة Wi-Fi لسماعتين مختلفتين (Multi-room Audio).")

# ==========================================
# الوحدة الثالثة: الدرع الواقي (FFT Scanner)
# ==========================================
elif module == "3️⃣ الدرع الواقي (FFT Scanner)":
    st.header("🛡️ رادار الترددات الخفية (Neuro-Shield)")
    st.markdown("قم برفع ملف صوتي (WAV) لتحليله رياضياً واكتشاف ما إذا كان يحتوي على ترددات تحت سمعية (Infrasound) مخفية.")
    
    uploaded_file = st.file_uploader("رفع ملف صوتي (WAV فقط)", type=['wav'])
    
    if uploaded_file is not None:
        with st.spinner("جاري تحليل الطيف الصوتي (FFT)..."):
            # قراءة الملف
            sample_rate, data = wavfile.read(uploaded_file)
            
            # تحويل ستيريو إلى مونو إذا لزم الأمر
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            # أخذ عينة (أول 5 ثواني لتسريع المعالجة)
            N = sample_rate * 5
            data_sample = data[:N]
            
            # تطبيق تحويل فورييه (FFT)
            yf = rfft(data_sample)
            xf = rfftfreq(N, 1 / sample_rate)
            
            # التركيز على الترددات المنخفضة جداً (0 إلى 50 هرتز) لكشف التلاعب
            mask = xf <= 50
            
            # رسم المخطط
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(xf[mask], np.abs(yf[mask]), color='red')
            ax.set_title("تحليل الترددات المنخفضة جداً (Infrasound Spectrum)")
            ax.set_xlabel("التردد (Hz)")
            ax.set_ylabel("الشدة (Amplitude)")
            ax.grid(True)
            
            st.pyplot(fig)
            
            # نظام الإنذار المبكر
            peak_freq = xf[mask][np.argmax(np.abs(yf[mask]))]
            if peak_freq < 20 and peak_freq > 1:
                st.error(f"🚨 تحذير: تم اكتشاف ذروة ترددية قوية عند {peak_freq:.2f} Hz. قد يحتوي هذا الملف على رسائل خفية (Subliminal).")
            else:
                st.success("✅ الملف نظيف: لا توجد ترددات تحت سمعية موجهة.")
