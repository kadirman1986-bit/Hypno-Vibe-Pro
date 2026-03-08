import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS
import google.generativeai as genai
import time
from datetime import datetime

# ==========================================
# 1. مصفوفة الهندسة الجنسية (Phased Logic)
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Phased Clinic", layout="wide", page_icon="🧬")

# تعريف المراحل لكل حالة
SEXUAL_PROTOCOL = {
    "علاج البرود وتحفيز الرغبة (نساء)": {
        "p1": {"base": 210.42, "beat": 6.0, "label": "تهيئة عصبية", "default": "استرخي تماماً، اسمحي لجسدك بالهدوء."},
        "p2": {"base": 210.42, "beat": 12.0, "label": "تحفيز حسي", "default": "استشعري الحرارة والطاقة تتدفق في كيانك الآن."},
        "p3": {"base": 432.0, "beat": 8.0, "label": "تثبيت الفطرة", "default": "أنتِ الآن في انسجام تام مع فطرتك وقوتك."},
    },
    "تأخير القذف والتحكم (رجال)": {
        "p1": {"base": 144.72, "beat": 7.83, "label": "تأريض وسكينة", "default": "تنفس بعمق، أنت الآن ثابت وهادئ كالأرض."},
        "p2": {"base": 144.72, "beat": 4.0, "label": "تثبيط التوتر", "default": "تحرر من كل ضغط، سيطر على هدوئك الداخلي."},
        "p3": {"base": 144.72, "beat": 7.83, "label": "إعادة توازن", "default": "أنت الآن تملك زمام التحكم والاتزان الكامل."},
    }
}

# ==========================================
# 2. الدوال الهندسية
# ==========================================

def get_script(api_key, name, phase_label, phase_goal):
    """حاول استخدام AI، وإذا فشل استخدم سكريبت الطوارئ"""
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"اكتب جملة تنويم إيحائي واحدة قصيرة جداً لـ {name}. الهدف: {phase_label} لـ {phase_goal}."
            return model.generate_content(prompt).text
        except: pass
    return None

def mix_phased_audio(phases_data, output_name):
    # دمج الملفات عبر FFmpeg (سيتم تنفيذها في زر الإنتاج)
    pass

# ==========================================
# 3. الواجهة
# ==========================================
st.title("🩺 عيادة الهندسة الجنسية المرحلية | Hypno-Vibe")

with st.sidebar:
    st.header("🔑 إعدادات النظام")
    api_key = st.text_input("Gemini API Key (اختياري)", type="password")
    st.info("إذا لم يعمل المفتاح، سيستخدم النظام سكريبتات الطوارئ.")

selected_case = st.selectbox("التشخيص الجنسي المخصص:", list(SEXUAL_PROTOCOL.keys()))
name = st.text_input("اسم العميل:", "عبد القادر")
duration = st.slider("المدة الكلية للجلسة (ثواني):", 60, 900, 180)

st.markdown("---")
st.subheader("📝 هندسة السكريبتات لكل مرحلة")

col1, col2, col3 = st.columns(3)
case_data = SEXUAL_PROTOCOL[selected_case]

# مربعات إدخال السكريبت لكل مرحلة
with col1:
    st.write(f"**المرحلة 1: {case_data['p1']['label']}**")
    s1 = st.text_area("سكريبت المرحلة 1:", case_data['p1']['default'], key="s1")
with col2:
    st.write(f"**المرحلة 2: {case_data['p2']['label']}**")
    s2 = st.text_area("سكريبت المرحلة 2:", case_data['p2']['default'], key="s2")
with col3:
    st.write(f"**المرحلة 3: {case_data['p3']['label']}**")
    s3 = st.text_area("سكريبت المرحلة 3:", case_data['p3']['default'], key="s3")

if st.button("🚀 إنتاج الجلسة المرحلية المتكاملة"):
    with st.spinner("جاري بناء الطبقات الثلاث والدمج..."):
        sr = 44100
        p_dur = duration // 3
        
        # توليد الصوت البشري للمراحل الثلاث ودمجهم
        full_voice_text = f"{s1}. (صمت قصير). {s2}. (صمت قصير). {s3}"
        tts = gTTS(text=full_voice_text, lang='ar')
        v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(v_tmp.name)
        
        # توليد الترددات المتغيرة
        full_audio = []
        for p in ['p1', 'p2', 'p3']:
            t = np.linspace(0, p_dur, int(sr * p_dur))
            left = np.sin(2 * np.pi * case_data[p]['base'] * t)
            right = np.sin(2 * np.pi * (case_data[p]['base'] + case_data[p]['beat']) * t)
            full_audio.append(np.vstack((left, right)).T)
        
        bin_combined = (np.concatenate(full_audio, axis=0) * 32767).astype(np.int16)
        bin_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        wavfile.write(bin_path, sr, bin_combined)

        # الإنتاج النهائي
        out_name = f"Phased_Session_{name}.mp3"
        cmd = [
            'ffmpeg', '-y', '-i', bin_path, '-i', v_tmp.name,
            '-filter_complex', '[0:a]volume=0.3[b];[1:a]volume=2.0[v];[b][v]amix=inputs=2:duration=first',
            out_name
        ]
        subprocess.run(cmd)
        
        st.audio(out_name)
        st.success("✅ تم إنتاج الجلسة. المراحل تتغير تلقائياً مع السكريبت المخصص.")
