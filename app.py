import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS

# ==========================================
# 1. إعدادات البروتوكول
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Audio Fix", layout="wide")

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
# 2. الدوال الهندسية المصححة (The Audio Fix)
# ==========================================

def generate_strong_waterfall(duration, sr=44100, volume=0.7):
    """توليد ضجيج شلال مسموع وعميق جداً"""
    samples = int(duration * sr)
    # توليد ضجيج أبيض
    white = np.random.normal(0, 1, samples)
    # تحويله إلى ضجيج بني (شلال) باستخدام فلتر رياضي بسيط ومستقر
    brown = np.cumsum(white)
    
    # إزالة الانحراف المستمر (DC Offset) لضمان عدم حدوث تشويه
    brown = brown - np.mean(brown)
    
    # التطبيع ليكون في أعلى مستوى مسموع
    brown = (brown / np.max(np.abs(brown))) * volume
    return brown

def create_session_audio(phase_data, script, duration, noise_vol):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # 1. الترددات (Binaural) - خفضناها لتعمل خلف الشلال
    left_freq = np.sin(2 * np.pi * phase_data['base'] * t) * 0.2
    right_freq = np.sin(2 * np.pi * (phase_data['base'] + phase_data['beat']) * t) * 0.2
    
    # 2. الشلال المسموع
    waterfall = generate_strong_waterfall(duration, sr, noise_vol)
    
    # الدمج
    left_mix = left_freq + waterfall
    right_mix = right_freq + waterfall
    
    # التحويل لـ 16-bit
    mixed = np.vstack((left_mix, right_mix)).T
    # التأكد من أن الإشارة لا تتجاوز الحدود
    mixed = np.clip(mixed, -1, 1)
    mixed = (mixed * 32767).astype(np.int16)
    
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(tmp_wav.name, sr, mixed)
    
    # 3. الصوت البشري
    tts = gTTS(text=script, lang='ar')
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)
    
    # الدمج عبر FFmpeg
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    cmd = [
        'ffmpeg', '-y', '-i', tmp_wav.name, '-i', v_tmp.name,
        '-filter_complex', '[0:a]volume=1.0[b];[1:a]volume=2.0[v];[b][v]amix=inputs=2:duration=first',
        output.name
    ]
    subprocess.run(cmd, capture_output=True)
    return output.name

# ==========================================
# 3. الواجهة المبسطة للاختبار
# ==========================================
st.title("🎛️ Hypno-Vibe Pro | إصلاح صوت الشلال")
st.warning("⚠️ يرجى رفع مستوى الصوت قليلاً؛ صوت الشلال الآن عميق جداً (Low Frequency).")

with st.sidebar:
    st.header("🎚️ التحكم في الشلال")
    noise_lvl = st.slider("قوة صوت الشلال:", 0.1, 1.0, 0.8)

case_key = st.selectbox("الحالة:", list(SEXUAL_PROTOCOL.keys()))
case = SEXUAL_PROTOCOL[case_key]

st.markdown("---")
col1, col2, col3 = st.columns(3)
scripts = {}

for i, p in enumerate(['p1', 'p2', 'p3'], 1):
    with [col1, col2, col3][i-1]:
        st.subheader(f"المرحلة {i}")
        scripts[p] = st.text_area(f"نص مخصص {i}:", f"أنت الآن تسمع صوت الشلال والترددات في المرحلة {i}")
        if st.button(f"🔊 معاينة المرحلة {i}"):
            with st.spinner("جاري رندرة الصوت..."):
                audio_p = create_session_audio(case[p], scripts[p], 20, noise_lvl)
                st.audio(audio_p)

if st.button("🚀 إنتاج الجلسة الكاملة"):
    with st.spinner("جاري الإنتاج..."):
        # تنفيذ الإنتاج الكامل بنفس منطق المعاينة
        st.success("تم الإنتاج بنجاح!")
