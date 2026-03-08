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
# 1. إعدادات النظام
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Custom Voice", layout="wide", page_icon="🎙️")

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
# 2. الدوال الهندسية
# ==========================================

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
st.title("🧠 Hypno-Vibe Pro: التحكم الصوتي الكامل")

with st.sidebar:
    st.header("📂 الأرشيف")
    archived_files = sorted(os.listdir(SESSIONS_DIR), reverse=True)
    if archived_files:
        selected_file = st.selectbox("الجلسات السابقة:", archived_files)
    
    st.markdown("---")
    st.header("⚙️ الإعدادات المتقدمة")
    api_key = st.text_input("Gemini API Key (للسكريبت الآلي)", type="password")
    uploaded_music = st.file_uploader("🎵 موسيقى خلفية", type=["mp3", "wav"])
    music_vol = st.slider("مستوى الموسيقى", 0.0, 1.0, 0.4) if uploaded_music else 0

col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 بيانات العميل والسكريبت")
    name = st.text_input("اسم العميل:", "عبد القادر")
    
    script_mode = st.radio("مصدر السكريبت:", ["توليد ذكاء اصطناعي", "كتابة يدوية"])
    if script_mode == "توليد ذكاء اصطناعي":
        goal = st.selectbox("الهدف:", list(SESSION_LOGIC.keys()))
        final_script = "" # سيولد لاحقاً
    else:
        final_script = st.text_area("اكتب السكريبت الخاص بك هنا:", height=150)
        goal = st.selectbox("التردد المطلوب لهذا السكريبت:", list(SESSION_LOGIC.keys()))

with col2:
    st.subheader("🎙️ مصدر الصوت البشري")
    voice_mode = st.radio("نوع الصوت:", ["صوت النظام (AI Voice)", "تسجيل صوتي شخصي (Upload)"])
    
    if voice_mode == "تسجيل صوتي شخصي (Upload)":
        user_voice = st.file_uploader("ارفع تسجيلك الصوتي (بصوتك):", type=["mp3", "wav", "m4a"])
        if user_voice:
            st.audio(user_voice)
    
    duration = st.slider("المدة الإجمالية للترددات (ثواني):", 30, 600, 60)
    fade_len = st.slider("مدة التلاشي (Fade):", 1, 10, 3)

st.markdown("---")
st.subheader("🎚️ هندسة المسارات")
c1, c2, c3 = st.columns(3)
with c1: bin_v = st.slider("قوة الترددات", 0.0, 1.0, 0.2)
with c2: voice_v = st.slider("قوة صوتك/النظام", 0.5, 3.0, 2.0)
with c3: noise_v = st.slider("قوة الشلال", 0.0, 1.5, 0.8)

if st.button("🚀 إنتاج الجلسة النهائية"):
    progress_bar = st.progress(0)
    
    # 1. معالجة السكريبت
    if script_mode == "توليد ذكاء اصطناعي" and not final_script:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            res = model.generate_content(f"Write a hypnotic script for {name}. Goal: {goal}. Arabic.")
            final_script = res.text
        except:
            final_script = f"استرخ يا {name} واستمع للترددات."
    
    progress_bar.progress(30)
    
    # 2. معالجة الصوت البشري
    if voice_mode == "صوت النظام (AI Voice)":
        tts = gTTS(text=final_script, lang='ar')
        v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(v_tmp.name)
        v_path = v_tmp.name
    else:
        if user_voice:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as uv:
                uv.write(user_voice.getvalue())
                v_path = uv.name
        else:
            st.error("الرجاء رفع تسجيلك الصوتي أولاً!")
            st.stop()
            
    progress_bar.progress(60)
    
    # 3. الدمج النهائي (FFmpeg)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    out_name = f"{timestamp}_{name}_Custom.mp3"
    final_path = os.path.join(SESSIONS_DIR, out_name)
    
    bin_path = generate_binaural_beat(SESSION_LOGIC[goal]['base'], SESSION_LOGIC[goal]['beat'], duration, fade_len)
    
    # توليد الضجيج
    sr = 44100
    white_noise = np.random.uniform(-1, 1, int(sr * duration))
    brown_noise = (np.cumsum(white_noise) / sr * 25000).astype(np.int16)
    n_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(n_tmp.name, sr, brown_noise)

    # بناء أمر FFmpeg
    cmd = [
        'ffmpeg', '-y', '-i', bin_path, '-i', v_path, '-i', n_tmp.name,
        '-filter_complex', 
        f'[0:a]volume={bin_v}[b];[1:a]adelay=3000|3000,volume={voice_v}[v];[2:a]volume={noise_v}[n];[b][n]amix=inputs=2[bg];[bg][v]amix=inputs=2:duration=first',
        final_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    progress_bar.progress(100)
    st.success(f"✅ تم الدمج بنجاح! السكريبت: {final_script[:50]}...")
    st.audio(final_path)
    
    with open(final_path, "rb") as f:
        st.download_button("📥 تحميل الجلسة بصوتك", f, file_name=out_name)
