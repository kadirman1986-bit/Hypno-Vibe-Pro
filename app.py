import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS
import json
from datetime import datetime

# ==========================================
# 1. البروتوكولات والمراحل
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Phased Audio", layout="wide", page_icon="🎛️")

SEXUAL_PROTOCOL = {
    "علاج البرود وتحفيز الرغبة (نساء)": {
        "p1": {"base": 210.42, "beat": 6.0, "label": "تهيئة عصبية"},
        "p2": {"base": 210.42, "beat": 12.0, "label": "تحفيز حسي"},
        "p3": {"base": 432.0, "beat": 8.0, "label": "تثبيت الفطرة"},
    },
    "تأخير القذف والتحكم (رجال)": {
        "p1": {"base": 144.72, "beat": 7.83, "label": "تأريض وسكينة"},
        "p2": {"base": 144.72, "beat": 4.0, "label": "تثبيط التوتر"},
        "p3": {"base": 144.72, "beat": 7.83, "label": "إعادة توازن"},
    }
}

# ==========================================
# 2. الدوال الهندسية (Core Engine)
# ==========================================

def generate_brown_noise(duration, sr=44100, noise_vol=0.5):
    """توليد صوت شلال (Brown Noise) مسموع وقوي"""
    samples = int(duration * sr)
    white_noise = np.random.uniform(-1, 1, samples)
    # التكامل لتحويل الضجيج الأبيض إلى بني (صوت شلال)
    brown_noise = np.cumsum(white_noise)
    # تطبيع الصوت ورفعه ليكون مسموعاً بوضوح
    brown_noise = (brown_noise / np.max(np.abs(brown_noise))) * noise_vol
    return brown_noise

def generate_phase_audio(phase_data, script, duration, noise_vol, voice_speed=True):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # 1. الترددات (Binaural Beats)
    left = np.sin(2 * np.pi * phase_data['base'] * t)
    right = np.sin(2 * np.pi * (phase_data['base'] + phase_data['beat']) * t)
    
    # 2. صوت الشلال (Brown Noise) المطور
    brown_noise = generate_brown_noise(duration, sr, noise_vol)
    
    # دمج الترددات مع الشلال
    left_mix = (left * 0.5) + brown_noise
    right_mix = (right * 0.5) + brown_noise
    
    # تحويل لـ 16-bit PCM
    mixed = np.vstack((left_mix, right_mix)).T
    mixed = (mixed / np.max(np.abs(mixed)) * 32767).astype(np.int16)
    
    b_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(b_tmp.name, sr, mixed)
    
    # 3. الصوت البشري
    tts = gTTS(text=script, lang='ar', slow=voice_speed)
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)
    
    # الدمج عبر FFmpeg
    out_preview = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    cmd = [
        'ffmpeg', '-y', '-i', b_tmp.name, '-i', v_tmp.name,
        '-filter_complex', '[0:a]volume=1.0[b];[1:a]volume=2.0[v];[b][v]amix=inputs=2:duration=first',
        out_preview.name
    ]
    subprocess.run(cmd, capture_output=True)
    return out_preview.name

# ==========================================
# 3. واجهة المستخدم (UI)
# ==========================================
st.title("🎛️ نظام Hypno-Vibe Pro: التحكم السريري الكامل")
st.info("تم إصلاح نظام 'صوت الشلال' ليكون مسموعاً وفعالاً في تمويه الترددات.")

with st.sidebar:
    st.header("⚙️ الضبط السمعي")
    noise_lvl = st.slider("مستوى صوت الشلال (التمويه):", 0.1, 1.0, 0.6)
    v_slow = st.checkbox("صوت تنويمي بطيء", value=True)

selected_case = st.selectbox("بروتوكول الحالة:", list(SEXUAL_PROTOCOL.keys()))
name = st.text_input("اسم العميل:", "عبد القادر")
total_dur = st.slider("المدة الكلية (ثواني):", 180, 1200, 300)

st.markdown("---")
col1, col2, col3 = st.columns(3)
case = SEXUAL_PROTOCOL[selected_case]
scripts = {}

# إعداد المراحل
for i, p_key in enumerate(['p1', 'p2', 'p3'], 1):
    with [col1, col2, col3][i-1]:
        st.subheader(f"{i}️⃣ {case[p_key]['label']}")
        scripts[p_key] = st.text_area(f"نص المرحلة {i}:", f"نص تجريبي للمرحلة {i}...")
        if st.button(f"🔊 معاينة المرحلة {i}"):
            with st.spinner(f"جاري إنتاج معاينة المرحلة {i}..."):
                prev = generate_phase_audio(case[p_key], scripts[p_key], total_dur//3, noise_lvl, v_slow)
                st.audio(prev)

st.markdown("---")

if st.button("🚀 إنتاج الجلسة الكاملة (Full Phased Rendering)"):
    with st.spinner("جاري دمج المراحل الثلاث مع صوت الشلال والأرشفة..."):
        sr = 44100
        p_dur = total_dur // 3
        
        # 1. بناء الترددات المرحلية مع شلال مستمر
        full_audio_list = []
        for p_key in ['p1', 'p2', 'p3']:
            p_data = case[p_key]
            t = np.linspace(0, p_dur, int(sr * p_dur))
            left = (np.sin(2 * np.pi * p_data['base'] * t) * 0.5) + generate_brown_noise(p_dur, sr, noise_lvl)
            right = (np.sin(2 * np.pi * (p_data['base'] + p_data['beat']) * t) * 0.5) + generate_brown_noise(p_dur, sr, noise_lvl)
            full_audio_list.append(np.vstack((left, right)).T)
        
        combined_audio = np.concatenate(full_audio_list, axis=0)
        combined_audio = (combined_audio / np.max(np.abs(combined_audio)) * 32767).astype(np.int16)
        
        bin_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        wavfile.write(bin_path, sr, combined_audio)
        
        # 2. بناء سكريبت الصوت الكامل
        full_script = f"{scripts['p1']}. {scripts['p2']}. {scripts['p3']}"
        tts = gTTS(text=full_script, lang='ar', slow=v_slow)
        v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(v_tmp.name)
        
        # 3. الدمج النهائي
        out_name = f"Final_{name}_{selected_case[:5]}.mp3"
        cmd = [
            'ffmpeg', '-y', '-i', bin_path, '-i', v_tmp.name,
            '-filter_complex', '[0:a]volume=1.0[b];[1:a]adelay=4000|4000,volume=2.0[v];[b][v]amix=inputs=2:duration=first',
            out_name
        ]
        subprocess.run(cmd)
        
        st.audio(out_name)
        st.success("✅ تم إنتاج الجلسة بنجاح مع صوت شلال واضح.")
        with open(out_name, "rb") as f:
            st.download_button("📥 تحميل الجلسة النهائية", f, file_name=out_name)
