import streamlit as st
import numpy as np
from scipy.io import wavfile
from gtts import gTTS
import os
import tempfile
import subprocess
import google.generativeai as genai

# ==========================================
# 1. إعدادات النظام وقاعدة البيانات
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Bio-Logic", layout="wide", page_icon="🧘‍♂️")

# قاعدة بيانات الترددات (تتحكم بها الخوارزمية آلياً)
SESSION_LOGIC = {
    "استرخاء وإعادة ضبط (Factory Reset)": {"base": 432.0, "beat": 10.0, "desc": "تردد الشفاء الكوني مع نبضة Alpha."},
    "تحفيز حسي (Sensory Boost)": {"base": 40.0, "beat": 40.0, "desc": "تردد Gamma للنشوة واليقظة الحسية القصوى."},
    "الاستسلام وفك القيود (Letting Go)": {"base": 210.42, "beat": 6.0, "desc": "تردد فينوس مع نبضة Theta لفك التشنج النفسي."},
    "تأريض وسكينة (Grounding/Delay)": {"base": 144.72, "beat": 7.83, "desc": "تردد المريخ مع رنين شومان للتحكم في الانفعال."},
    "علاج البرود/التحفيز الأنثوي": {"base": 210.42, "beat": 12.0, "desc": "تردد الأنوثة لتحفيز تدفق الطاقة الحيوية."},
    "استعادة الفطرة والذكورة": {"base": 144.72, "beat": 15.0, "desc": "تردد القوة والتركيز الذكوري الفطري."}
}

# ==========================================
# 2. الدوال الهندسية المطورة
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

def generate_nature_noise(duration, sample_rate=44100):
    white_noise = np.random.randn(duration * sample_rate)
    brown_noise = np.cumsum(white_noise)
    brown_noise = brown_noise / np.max(np.abs(brown_noise))
    audio_data = (brown_noise * 12000).astype(np.int16)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_wav.name, sample_rate, audio_data)
    return temp_wav.name

def generate_human_tts(text, lang='ar'):
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    # جعل الصوت أبطأ قليلاً ليبدو بشرياً وعلاجياً أكثر
    tts = gTTS(text=text, lang=lang, slow=False) 
    tts.save(temp_mp3.name)
    return temp_mp3.name

def mix_audio_final(binaural_wav, voice_mp3, ambient_wav, output_file):
    # خوارزمية دمج احترافية توازن بين الطبقات الثلاث
    cmd = [
        'ffmpeg', '-y',
        '-i', binaural_wav,
        '-i', voice_mp3,
        '-i', ambient_wav,
        '-filter_complex',
        '[0:a]volume=0.3[bin];' # التردد خافت ليعمل تحت الوعي
        '[1:a]adelay=4000|4000,volume=1.8[v];' # صوت بشري واضح ومرتفع
        '[2:a]volume=0.25[amb];' # صوت طبيعي ناعم
        '[bin][amb]amix=inputs=2[bg];'
        '[bg][v]amix=inputs=2:duration=first',
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ==========================================
# 3. واجهة المستخدم الذكية
# ==========================================
st.title("🧠 عيادة Hypno-Vibe: نظام التوازن الفطري")
st.sidebar.header("إعدادات الاتصال")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

# الاستمارة
st.subheader("📋 تشخيص الحالة (التحليل الحيوي)")
c1, c2 = st.columns(2)

with c1:
    name = st.text_input("اسم العميل:", "عبد القادر")
    goal = st.selectbox("الهدف من الجلسة:", list(SESSION_LOGIC.keys()))
    duration = st.slider("مدة الجلسة (ثواني):", 30, 300, 60)

with c2:
    status_info = SESSION_LOGIC[goal]
    st.info(f"⚙️ **الضبط التلقائي للتردد:**\n- التردد الأساسي: {status_info['base']} Hz\n- نبضة الدماغ: {status_info['beat']} Hz\n- الهدف: {status_info['desc']}")

# توليد السكريبت
if st.button("🤖 توليد سكريبت علاجي مخصص"):
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"اكتب سكريبت تنويم إيحائي احترافي وقصير لـ {name}. الهدف: {goal}. الأسلوب: هادئ، مشجع، يركز على التواصل مع الجسد والفطرة السليمة. اللغة: عربية فصحى دافئة."
            response = model.generate_content(prompt)
            st.session_state.script = response.text
        except:
            st.error("فشل الاتصال بالذكاء الاصطناعي. تأكد من مفتاح الـ API.")
    else:
        st.warning("يرجى إدخال مفتاح API في القائمة الجانبية.")

if 'script' in st.session_state:
    final_script = st.text_area("السكريبت المقترح (يمكنك التعديل):", st.session_state.script, height=200)
    
    if st.button("🎧 إنتاج الجلسة النهائية"):
        with st.spinner("جاري دمج الطبقات العصبية بصوت بشري..."):
            wav_path = generate_binaural_beat(status_info['base'], status_info['beat'], duration)
            noise_path = generate_nature_noise(duration)
            voice_path = generate_human_tts(final_script)
            output = f"Final_Session_{name}.mp3"
            
            mix_audio_final(wav_path, voice_path, noise_path, output)
            
            st.success("✅ الجلسة جاهزة. الترددات مخفية خلف التمويه الصوتي.")
            st.audio(output)
