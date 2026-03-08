import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy.fft import rfft, rfftfreq
from gtts import gTTS
import matplotlib.pyplot as plt
import os
import tempfile
import subprocess
import google.generativeai as genai

# ==========================================
# 1. إعدادات الواجهة (UI Configuration)
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Neuro-Engineering", layout="wide", page_icon="🧠")
st.title("🧠 نظام Hypno-Vibe Pro - العيادة الذكية")
st.markdown("---")

# ==========================================
# 2. الدوال الهندسية (Core Functions)
# ==========================================
def generate_binaural_beat(base_freq, beat_freq, duration, sample_rate=44100):
    """توليد الترددات العلاجية"""
    t = np.linspace(0, duration, sample_rate * duration)
    left = np.sin(2 * np.pi * base_freq * t)
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    audio_data = np.vstack((left, right)).T
    audio_data = (audio_data * 32767).astype(np.int16)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_wav.name, sample_rate, audio_data)
    return temp_wav.name

def generate_nature_noise(duration, sample_rate=44100):
    """توليد ضجيج طبيعي (Brown Noise) كخلفية لتمويه الترددات"""
    # الضجيج البني يشبه صوت الشلال أو الرياح العميقة وممتاز للمخ
    white_noise = np.random.randn(duration * sample_rate)
    brown_noise = np.cumsum(white_noise)
    brown_noise = brown_noise / np.max(np.abs(brown_noise)) # تطبيع (Normalization)
    audio_data = (brown_noise * 15000).astype(np.int16) # خفض الصوت نسبياً
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_wav.name, sample_rate, audio_data)
    return temp_wav.name

def generate_tts(text, lang='ar'):
    """توليد الصوت البشري"""
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=text, lang=lang)
    tts.save(temp_mp3.name)
    return temp_mp3.name

def mix_audio_advanced(binaural_wav, voice_mp3, ambient_wav, output_file):
    """دمج المسارات الثلاثة: التردد + الإيحاء + التمويه الطبيعي"""
    cmd = [
        'ffmpeg', '-y',
        '-i', binaural_wav,
        '-i', voice_mp3,
        '-i', ambient_wav,
        '-filter_complex',
        # التردد (0.4) | الإيحاء (1.5 + تأخير 3 ثواني) | التمويه (0.3)
        '[0:a]volume=0.4[bin];'
        '[1:a]adelay=3000|3000,volume=1.5[v];'
        '[2:a]volume=0.3[amb];'
        '[bin][amb]amix=inputs=2[bg];'
        '[bg][v]amix=inputs=2:duration=first',
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def generate_ai_script(api_key, name, state, goal):
    """دالة الاتصال بالذكاء الاصطناعي لكتابة السكريبت"""
    if not api_key:
        return "الرجاء إدخال مفتاح API الخاص بك لتوليد السكريبت الذكي."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        أنت دكتور ومعالج بالتنويم الإيحائي. اكتب سكريبت صوتي قصير (حوالي 100 كلمة) باللغة العربية الفصحى المبسطة أو اللهجة التونسية الخفيفة.
        اسم العميل: {name}
        حالته الحالية: {state}
        الهدف من الجلسة: {goal}
        اجعل الكلام هادئاً، يبعث على الأمان، ويبدأ بطلب أخذ نفس عميق والاسترخاء.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"حدث خطأ في الاتصال بالذكاء الاصطناعي: {e}"

# ==========================================
# 3. إدارة حالة التطبيق (Session State)
# ==========================================
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""

# ==========================================
# 4. واجهة العيادة الذكية (Smart Clinic)
# ==========================================
st.sidebar.title("إعدادات النظام ⚙️")
api_key = st.sidebar.text_input("مفتاح Gemini API (للتوليد التلقائي):", type="password")
st.sidebar.info("احصل على مفتاح مجاني من Google AI Studio.")

st.header("📋 استمارة التشخيص الذكي (AI Diagnosis)")

col_form, col_freq = st.columns(2)

with col_form:
    st.subheader("1. تشخيص الحالة")
    client_name = st.text_input("اسم العميل:", "ضيف")
    current_state = st.selectbox("بماذا يشعر العميل الآن؟", 
                                 ["توتر وضغط عمل شديد", 
                                  "تشتت ذهني وعدم تركيز", 
                                  "برود وضعف في الطاقة الفطرية", 
                                  "أرق وصعوبة في النوم",
                                  "خوف من فقدان السيطرة (توتر داخلي)"])
    session_goal = st.selectbox("الهدف الهندسي من الجلسة:", 
                                ["استرخاء عميق وإعادة ضبط (Factory Reset)", 
                                 "تحفيز حسي ويقظة (Sensory Boost)", 
                                 "الاستسلام وفك القيود العصبية (Letting Go)", 
                                 "تأريض وسكينة (Grounding)"])
    
    if st.button("🤖 توليد السكريبت العلاجي (AI)"):
        with st.spinner("الذكاء الاصطناعي يحلل الحالة ويكتب السكريبت..."):
            script = generate_ai_script(api_key, client_name, current_state, session_goal)
            st.session_state.generated_script = script

with col_freq:
    st.subheader("2. الضبط الهندسي الدقيق (Manual Override)")
    st.info("💡 يمكنك تعديل الترددات يدوياً بناءً على رؤيتك الهندسية.")
    base_freq = st.slider("التردد الأساسي (Base Freq - Hz)", min_value=100.0, max_value=600.0, value=210.42, step=0.1)
    beat_freq = st.slider("النبضة العصبية (Beat Freq - Hz)", min_value=1.0, max_value=40.0, value=8.0, step=0.1)
    duration = st.slider("مدة الجلسة (ثواني) للتجربة:", 20, 180, 45)

st.markdown("---")
st.subheader("3. المراجعة والتوليد النهائي (Final Rendering)")

edited_script = st.text_area("السكريبت الإيحائي (يمكنك التعديل عليه قبل التسجيل):", 
                             value=st.session_state.generated_script, height=150)

if st.button("🎧 دمج (التردد + السكريبت + التمويه الطبيعي)"):
    if not edited_script.strip():
        st.error("السكريبت فارغ! قم بتوليده أولاً أو اكتبه يدوياً.")
    else:
        with st.spinner("جاري بناء الطبقات الصوتية (Binaural + Noise + AI Voice)..."):
            # 1. توليد الترددات
            wav_path = generate_binaural_beat(base_freq, beat_freq, duration)
            # 2. توليد التمويه (الشلال/الطبيعة)
            ambient_path = generate_nature_noise(duration)
            # 3. توليد الصوت
            tts_path = generate_tts(edited_script)
            
            output_file = f"Smart_Session_{client_name}.mp3"
            
            # 4. الدمج الثلاثي
            mix_audio_advanced(wav_path, tts_path, ambient_path, output_file)
            
            st.success("✅ تمت هندسة الجلسة الطبية بنجاح!")
            st.audio(output_file)
