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
st.set_page_config(page_title="Hypno-Vibe Pro | Sexual Neuro-Clinic", layout="wide", page_icon="🧬")

# تعريف المراحل لكل حالة (Phase 1: Induction, Phase 2: Stimulation, Phase 3: Anchoring)
SEXUAL_PROTOCOL = {
    "علاج البرود وتحفيز الرغبة (نساء)": {
        "p1": {"base": 210.42, "beat": 6.0, "label": "تهيئة عصبية (Theta)"},
        "p2": {"base": 210.42, "beat": 12.0, "label": "تحفيز حسي (Alpha)"},
        "p3": {"base": 432.0, "beat": 8.0, "label": "تثبيت الفطرة"},
    },
    "تأخير القذف والتحكم (رجال)": {
        "p1": {"base": 144.72, "beat": 7.83, "label": "تأريض (Schumann)"},
        "p2": {"base": 144.72, "beat": 4.0, "label": "تثبيط التوتر (Delta/Theta)"},
        "p3": {"base": 144.72, "beat": 7.83, "label": "إعادة توازن"},
    },
    "تقوية الانتصاب والأداء (رجال)": {
        "p1": {"base": 144.72, "beat": 10.0, "label": "تركيز ذهني"},
        "p2": {"base": 144.72, "beat": 40.0, "label": "تدفق حيوي (Gamma)"},
        "p3": {"base": 144.72, "beat": 15.0, "label": "تثبيت الأداء"},
    }
}

# ==========================================
# 2. المحرك الصوتي المرحلي
# ==========================================

def generate_phased_binaural(protocol, total_duration):
    """توليد ملف واحد يحتوي على 3 مراحل ترددية متتالية"""
    sr = 44100
    phase_duration = total_duration // 3
    full_audio = []
    
    for p in ['p1', 'p2', 'p3']:
        base = protocol[p]['base']
        beat = protocol[p]['beat']
        t = np.linspace(0, phase_duration, int(sr * phase_duration))
        left = np.sin(2 * np.pi * base * t)
        right = np.sin(2 * np.pi * (base + beat) * t)
        
        # إضافة Crossfade بسيط بين المراحل
        audio_segment = np.vstack((left, right)).T
        full_audio.append(audio_segment)
    
    combined = np.concatenate(full_audio, axis=0)
    combined = (combined * 32767).astype(np.int16)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(tmp.name, sr, combined)
    return tmp.name

# ==========================================
# 3. واجهة العيادة التخصصية
# ==========================================
st.title("🩺 عيادة الهندسة الجنسية العصبية | Hypno-Vibe Pro")
st.markdown("---")

with st.sidebar:
    st.header("🔐 التحكم السريري")
    api_key = st.text_input("Gemini API Key", type="password")
    voice_source = st.radio("مصدر الصوت البشري:", ["ذكاء اصطناعي", "تسجيل شخصي"])
    if voice_source == "تسجيل شخصي":
        user_audio = st.file_uploader("ارفع تسجيلك الصوتي للجلسة", type=["mp3", "wav"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 بروتوكول الجلسة")
    client_name = st.text_input("اسم العميل:", "عبد القادر")
    selected_case = st.selectbox("التشخيص الجنسي:", list(SEXUAL_PROTOCOL.keys()))
    script_content = st.text_area("السكريبت الإيحائي (يدوي أو مولد):", height=200)
    
    if st.button("🤖 توليد سكريبت تخصصي بالـ AI"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"اكتب سكريبت تنويم إيحائي تخصصي لعلاج {selected_case} لـ {client_name}. ركز على الجوانب النفسية والفسيولوجية."
                res = model.generate_content(prompt)
                script_content = res.text
                st.session_state.script = script_content
                st.rerun()
            except: st.error("فشل الاتصال بالذكاء الاصطناعي.")

with col2:
    st.subheader("📉 التسلسل الترددي للجلسة")
    case_data = SEXUAL_PROTOCOL[selected_case]
    for p in ['p1', 'p2', 'p3']:
        st.write(f"**المرحلة {p[-1]}:** {case_data[p]['label']} ({case_data[p]['base']}Hz + {case_data[p]['beat']}Hz)")
    
    duration = st.slider("مدة الجلسة الكلية (ثواني):", 60, 900, 180)

if st.button("🚀 إنتاج الجلسة المرحلية"):
    with st.spinner("جاري دمج المراحل الترددية وصوت العيادة..."):
        # 1. توليد الترددات المرحلية
        bin_path = generate_phased_binaural(case_data, duration)
        
        # 2. معالجة الصوت البشري
        if voice_source == "ذكاء اصطناعي":
            tts = gTTS(text=script_content, lang='ar')
            v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(v_tmp.name)
            v_path = v_tmp.name
        else:
            if user_audio:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as uv:
                    uv.write(user_audio.getvalue())
                    v_path = uv.name
            else: st.stop()

        # 3. الإنتاج النهائي
        out_name = f"Pro_Sexual_Session_{client_name}.mp3"
        cmd = [
            'ffmpeg', '-y', '-i', bin_path, '-i', v_path,
            '-filter_complex', '[0:a]volume=0.3[b];[1:a]adelay=5000|5000,volume=2.0[v];[b][v]amix=inputs=2:duration=first',
            out_name
        ]
        subprocess.run(cmd, capture_output=True)
        
        st.audio(out_name)
        st.success("✅ تم إنتاج الجلسة بنظام الترددات المتغيرة.")
