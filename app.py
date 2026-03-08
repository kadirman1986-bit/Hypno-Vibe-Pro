import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS
import google.generativeai as genai
import matplotlib.pyplot as plt
import time
from datetime import datetime

# ==========================================
# 1. إعدادات النظام والأرشفة
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Bio-Data Center", layout="wide", page_icon="🧠")

# إنشاء مجلد الجلسات إذا لم يكن موجوداً
SESSIONS_DIR = "sessions_archive"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

SESSION_LOGIC = {
    "علاج البرود/التحفيز الأنثوي": {"base": 210.42, "beat": 12.0, "desc": "تردد الزهرة لتحفيز الطاقة الأنثوية."},
    "استعادة الفطرة والذكورة": {"base": 144.72, "beat": 15.0, "desc": "تردد المريخ لتعزيز القوة والتركيز."},
    "الاستسلام وفك القيود (Letting Go)": {"base": 210.42, "beat": 6.0, "desc": "نبضة Theta لفك التشنج والتوتر."},
    "تأريض وسكينة (Grounding/Delay)": {"base": 144.72, "beat": 7.83, "desc": "رنين شومان للهدوء والتحكم."}
}

# ==========================================
# 2. الدوال الهندسية والتحليل البصري
# ==========================================

def plot_visuals(file_path):
    """رسم الموجة والمخطط الطيفي"""
    sr, data = wavfile.read(file_path)
    if len(data.shape) > 1: data = data[:, 0]
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        plt.figure(figsize=(10, 4))
        plt.plot(data[:sr*5], color='#1f77b4', linewidth=0.5)
        plt.title("Waveform (First 5s)")
        plt.axis('off')
        st.pyplot(plt)
        
    with col_v2:
        plt.figure(figsize=(10, 4))
        plt.specgram(data[:sr*10], Fs=sr, cmap="inferno", NFFT=1024)
        plt.title("Spectrogram (Frequency Analysis)")
        plt.ylabel("Frequency [Hz]")
        plt.colorbar(label="Intensity [dB]")
        st.pyplot(plt)

def generate_binaural_beat(base_freq, beat_freq, duration, fade_duration):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    left = np.sin(2 * np.pi * base_freq * t)
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    
    fade_samples = int(fade_duration * sr)
    envelope = np.ones(len(t))
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    audio = (np.vstack((left*envelope, right*envelope)).T * 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(tmp.name, sr, audio)
    return tmp.name

# ==========================================
# 3. واجهة المستخدم (UI)
# ==========================================
st.title("🧠 نظام Hypno-Vibe Pro | إدارة الجلسات والأرشفة")

# --- القائمة الجانبية (الأرشيف) ---
with st.sidebar:
    st.header("📂 أرشيف الجلسات")
    archived_files = sorted(os.listdir(SESSIONS_DIR), reverse=True)
    if archived_files:
        selected_file = st.selectbox("اختر جلسة سابقة:", archived_files)
        file_path = os.path.join(SESSIONS_DIR, selected_file)
        with open(file_path, "rb") as f:
            st.download_button(f"📥 تحميل {selected_file.split('_')[1]}", f, file_name=selected_file)
        if st.button("🗑️ حذف الجلسة"):
            os.remove(file_path)
            st.rerun()
    else:
        st.write("لا توجد جلسات مؤرشفة بعد.")
    
    st.markdown("---")
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("Gemini API Key", type="password")
    language = st.selectbox("لغة السكريبت:", ["العربية", "Français", "English"])
    uploaded_music = st.file_uploader("🎵 إضافة موسيقى خلفية", type=["mp3", "wav"])
    music_vol = st.slider("مستوى الموسيقى", 0.0, 1.0, 0.4) if uploaded_music else 0

# --- المنطقة الأساسية ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 بيانات العميل")
    name = st.text_input("اسم العميل:", "عبد القادر")
    goal = st.selectbox("الهدف العلاجي:", list(SESSION_LOGIC.keys()))
    duration = st.slider("المدة (ثواني):", 30, 600, 60)
    fade_len = st.slider("مدة التلاشي (Fade):", 1, 10, 3)

with col2:
    logic = SESSION_LOGIC[goal]
    st.subheader("📊 تحليل الضبط")
    st.info(f"**Base:** {logic['base']} Hz | **Beat:** {logic['beat']} Hz")
    st.write(f"*{logic['desc']}*")

st.markdown("---")
st.subheader("🎚️ التحكم في الطبقات")
c1, c2, c3 = st.columns(3)
with c1: bin_v = st.slider("الترددات", 0.0, 1.0, 0.2)
with c2: voice_v = st.slider("الصوت البشري", 0.5, 3.0, 2.0)
with c3: noise_v = st.slider("صوت الشلال", 0.0, 1.5, 0.8)

if st.button("🚀 إنتاج وأرشفة الجلسة"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 1. الذكاء الاصطناعي
    status_text.text("🤖 جاري توليد السكريبت...")
    lang_map = {"العربية": "Arabic", "Français": "French", "English": "English"}
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        res = model.generate_content(f"Write a professional hypnotic script for {name}. Goal: {goal}. Language: {lang_map[language]}.")
        script = res.text
    except:
        script = f"Session for {name}. Focus: {goal}. Relax and breathe."
    
    progress_bar.progress(30)
    
    # 2. الهندسة الصوتية
    status_text.text("🧬 هندسة الترددات...")
    bin_path = generate_binaural_beat(logic['base'], logic['beat'], duration, fade_len)
    
    tts_lang = {"العربية": "ar", "Français": "fr", "English": "en"}[language]
    tts = gTTS(text=script, lang=tts_lang)
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)
    
    progress_bar.progress(60)
    
    # 3. الرندرة والأرشفة
    status_text.text("🎛️ جاري الإنتاج النهائي وحفظ الملف...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    out_name = f"{timestamp}_{name}_{goal.replace('/', '-')}.mp3"
    final_path = os.path.join(SESSIONS_DIR, out_name)
    
    # دالة الضجيج
    sr = 44100
    white_noise = np.random.uniform(-1, 1, int(sr * duration))
    brown_noise = (np.cumsum(white_noise) / sr * 25000).astype(np.int16)
    n_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(n_tmp.name, sr, brown_noise)

    cmd = [
        'ffmpeg', '-y', '-i', bin_path, '-i', v_tmp.name, '-i', n_tmp.name,
        '-filter_complex', 
        f'[0:a]volume={bin_v}[b];[1:a]adelay=4000|4000,volume={voice_v}[v];[2:a]volume={noise_v}[n];[b][n]amix=inputs=2[bg];[bg][v]amix=inputs=2:duration=first',
        final_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    progress_bar.progress(100)
    status_text.text(f"✅ تم الإنتاج وحفظ الجلسة في الأرشيف باسم: {out_name}")
    
    st.audio(final_path)
    plot_visuals(bin_path)
    st.success("الجلسة الآن متاحة في القائمة الجانبية (الأرشيف) للرجوع إليها مستقبلاً.")
