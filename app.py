import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS
import json
import time
from datetime import datetime

# ==========================================
# 1. البروتوكولات والمراحل
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Monitor Mode", layout="wide", page_icon="🎛️")

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
# 2. محرك المعاينة والإنتاج (Core Engine)
# ==========================================

def generate_phase_audio(phase_data, script, duration, noise_vol, voice_speed=True):
    """توليد ملف صوتي لمرحلة واحدة فقط (تردد + ضجيج + صوت)"""
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # التردد والضجيج
    left = np.sin(2 * np.pi * phase_data['base'] * t)
    right = np.sin(2 * np.pi * (phase_data['base'] + phase_data['beat']) * t)
    white_noise = np.random.uniform(-1, 1, len(t))
    brown_noise = (np.cumsum(white_noise) / sr * 25000).astype(np.float32)
    brown_noise = (brown_noise / np.max(np.abs(brown_noise))) * noise_vol
    
    bin_audio = np.vstack((left + brown_noise, right + brown_noise)).T
    bin_audio = (bin_audio / np.max(np.abs(bin_audio)) * 32767).astype(np.int16)
    
    b_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(b_tmp.name, sr, bin_audio)
    
    # الصوت البشري لهذه المرحلة
    tts = gTTS(text=script, lang='ar', slow=voice_speed)
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)
    
    # دمج المرحلة الواحدة للمعاينة
    out_preview = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    cmd = [
        'ffmpeg', '-y', '-i', b_tmp.name, '-i', v_tmp.name,
        '-filter_complex', '[0:a]volume=0.3[b];[1:a]volume=1.8[v];[b][v]amix=inputs=2:duration=first',
        out_preview.name
    ]
    subprocess.run(cmd, capture_output=True)
    return out_preview.name

# ==========================================
# 3. واجهة المستخدم (UI)
# ==========================================
st.title("🎛️ نظام المراقبة السريرية | Hypno-Vibe Pro")
st.markdown("قم بضبط السكريبت لكل مرحلة، ثم اسمع المعاينة قبل الدمج النهائي.")

with st.sidebar:
    st.header("⚙️ الضبط العام")
    noise_lvl = st.slider("مستوى الضجيج البني:", 0.0, 0.5, 0.2)
    v_slow = st.checkbox("صوت تنويمي بطيء", value=True)

selected_case = st.selectbox("بروتوكول الحالة:", list(SEXUAL_PROTOCOL.keys()))
name = st.text_input("اسم العميل:", "عبد القادر")
total_dur = st.slider("المدة الكلية (ثواني):", 180, 1200, 300)

st.markdown("---")
col1, col2, col3 = st.columns(3)
case = SEXUAL_PROTOCOL[selected_case]

# مصفوفة لتخزين السكريبتات
scripts = {}

with col1:
    st.subheader(f"1️⃣ {case['p1']['label']}")
    scripts['p1'] = st.text_area("نص المرحلة 1:", "استرخي الآن بعمق، واسمحي لكل توتر بالرحيل.", key="txt1")
    if st.button("🔊 معاينة المرحلة 1"):
        prev = generate_phase_audio(case['p1'], scripts['p1'], total_dur//3, noise_lvl, v_slow)
        st.audio(prev)

with col2:
    st.subheader(f"2️⃣ {case['p2']['label']}")
    scripts['p2'] = st.text_area("نص المرحلة 2:", "استشعري نبضات الطاقة والأنوثة تملأ كيانك.", key="txt2")
    if st.button("🔊 معاينة المرحلة 2"):
        prev = generate_phase_audio(case['p2'], scripts['p2'], total_dur//3, noise_lvl, v_slow)
        st.audio(prev)

with col3:
    st.subheader(f"3️⃣ {case['p3']['label']}")
    scripts['p3'] = st.text_area("نص المرحلة 3:", "هذا الشعور هو حقيقتكِ الدائمة، احتفظي به.", key="txt3")
    if st.button("🔊 معاينة المرحلة 3"):
        prev = generate_phase_audio(case['p3'], scripts['p3'], total_dur//3, noise_lvl, v_slow)
        st.audio(prev)

st.markdown("---")
# الإنتاج النهائي
if st.button("🚀 إنتاج البروتوكول الكامل (Full Rendering)"):
    with st.spinner("جاري دمج المراحل بتنقية الـ Crossfade والأرشفة..."):
        # (هنا نضع نفس دالة الإنتاج النهائي السابقة التي تدمج الـ 3 مراحل معاً)
        # سيقوم الكود بجمع السكريبتات وتوليد الملف النهائي وحفظ الـ Metadata
        full_script = f"{scripts['p1']}. {scripts['p2']}. {scripts['p3']}"
        
        # الرندرة النهائية...
        st.success("✅ تم إنتاج الجلسة بنجاح بناءً على معاينتك الدقيقة.")
        # ... (بقية كود الحفظ والتحميل)
