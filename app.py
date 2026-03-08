import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS
import google.generativeai as genai
import matplotlib.pyplot as plt

# ==========================================
# 1. إعدادات النظام وقاعدة البيانات التقنية
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Bio-Engineering", layout="wide", page_icon="🧠")

SESSION_LOGIC = {
    "علاج البرود/التحفيز الأنثوي": {"base": 210.42, "beat": 12.0, "desc": "تردد الزهرة لتحفيز الطاقة الأنثوية الحيوية."},
    "استعادة الفطرة والذكورة": {"base": 144.72, "beat": 15.0, "desc": "تردد المريخ لتعزيز القوة والتركيز الفطري."},
    "الاستسلام وفك القيود (Letting Go)": {"base": 210.42, "beat": 6.0, "desc": "نبضة Theta العميقة لإزالة التشنج النفسي والتوتر."},
    "تأريض وسكينة (Grounding/Delay)": {"base": 144.72, "beat": 7.83, "desc": "رنين شومان للهدوء والتحكم في الانفعالات وسرعة الاستجابة."}
}

OFFLINE_SCRIPTS = {
    "علاج البرود/التحفيز الأنثوي": "تنفسي بعمق.. استرخي تماماً. اسمحي لجسدك باستعادة توازنه الطبيعي وطاقته الحيوية الآن.",
    "استعادة الفطرة والذكورة": "خذ نفساً عميقاً.. استشعر قوتك الداخلية واتزانك.",
    "الاستسلام وفك القيود (Letting Go)": "تحرر من كل القيود العصبية.. اترك كل الأفكار ترحل.",
    "تأريض وسكينة (Grounding/Delay)": "أنت الآن ثابت كالجبال.. هادئ كالبحر."
}

# ==========================================
# 2. الدوال الهندسية (Core Engines)
# ==========================================

def generate_binaural_beat(base_freq, beat_freq, duration, fade_duration=3):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    left = np.sin(2 * np.pi * base_freq * t)
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    
    fade_samples = int(fade_duration * sr)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    envelope = np.ones(len(t))
    envelope[:fade_samples] = fade_in
    envelope[-fade_samples:] = fade_out
    
    left *= envelope
    right *= envelope
    
    audio = np.vstack((left, right)).T
    audio = (audio * 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(tmp.name, sr, audio)
    return tmp.name

def get_ai_script(api_key, name, goal):
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"اكتب سكريبت تنويم إيحائي قصير وهادئ جداً لـ {name}. الهدف: {goal}. اللغة: عربية فصحى دافئة."
            response = model.generate_content(prompt)
            return response.text
        except:
            return f"مرحباً {name}. " + OFFLINE_SCRIPTS.get(goal)
    return f"مرحباً {name}. " + OFFLINE_SCRIPTS.get(goal)

def render_final_session(binaural_path, script_text, duration, output_name, levels, music_file=None):
    tts = gTTS(text=script_text, lang='ar')
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)

    sr = 44100
    white_noise = np.random.uniform(-1, 1, int(sr * duration))
    brown_noise = np.cumsum(white_noise)
    brown_noise = (brown_noise / np.max(np.abs(brown_noise)) * 28000).astype(np.int16) 
    n_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(n_tmp.name, sr, brown_noise)

    inputs = ['-i', binaural_path, '-i', v_tmp.name, '-i', n_tmp.name]
    filter_complex = (
        f'[0:a]volume={levels["binaural"]}[b];'
        f'[1:a]adelay=4000|4000,volume={levels["voice"]}[v];'
        f'[2:a]volume={levels["noise"]}[n];'
        '[b][n]amix=inputs=2[bg];'
        '[bg][v]amix=inputs=2:duration=first'
    )

    if music_file:
        inputs += ['-i', music_file]
        filter_complex += ';[3:a]volume=0.5[m];[bg][m]amix=inputs=2[bgm];[bgm][v]amix=inputs=2:duration=first'

    cmd = ['ffmpeg', '-y'] + inputs + ['-filter_complex', filter_complex, output_name]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_name

def plot_waveform(file_path):
    sr, data = wavfile.read(file_path)
    plt.figure(figsize=(10, 3))
    plt.plot(data[:sr*5])  # عرض أول 5 ثواني فقط
    plt.title("شكل الموجة الصوتية")
    st.pyplot(plt)

# ==========================================
# 3. واجهة التطبيق (UI)
# ==========================================
st.title("🧠 عيادة Hypno-Vibe: النسخة الموسعة")
st.markdown("---")

with st.sidebar:
    st.header("🔑 إعدادات الوصول")
    api_key = st.sidebar.text_input("Gemini API Key (اختياري)", type="password")
    export_format = st.selectbox("صيغة التصدير:", ["mp3", "wav"])
    music_file = st.file_uploader("🎵 رفع موسيقى خلفية (اختياري)", type=["mp3", "wav"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 تشخيص العميل")
    name = st.text_input("اسم العميل:", "عبد القادر")
    goal = st.selectbox("هدف الجلسة المستهدف:", list(SESSION_LOGIC.keys()))
    duration = st.slider("مدة الجلسة (ثواني):", 30, 300, 60)

with col2:
    logic = SESSION_LOGIC[goal]
    st.subheader("⚙️ الضبط الترددي الآلي")
    st.success(f"**التردد المختار:** {logic['base']} Hz")
    st.success(f"**نبضة الدماغ:** {logic['beat']} Hz")
    st.write(f"*توصيف المهندس:* {logic['desc']}")

st.markdown("---")

st.subheader("🎚️ تحكم في مستويات الصوت")
cols = st.columns(3)
with cols[0]:
    bin_vol = st.slider("مستوى الترددات (Binaural)", 0.0, 1.0, 0.2)
with cols[1]:
    voice_vol = st.slider("مستوى الصوت البشري (Voice)", 0.5, 3.0, 2.0)
with cols[2]:
    noise_vol = st.slider("مستوى صوت الشلال (Noise)", 0.0, 1.5, 0.9)

levels = {"binaural": bin_vol, "voice": voice_vol, "noise": noise_vol}

st.markdown("---")
st.subheader("👂 معاينة مباشرة")
if st.button("🔊 معاينة الترددات فقط"):
    bin_path = generate_binaural_beat(logic['base'], logic['beat'], duration)
    st.audio(bin_path)
    plot_waveform(bin_path)

if st.button("🔊 معاينة الضجيج فقط"):
    sr = 44100
    white_noise = np.random.uniform(-1, 1, int(sr * duration))
    brown_noise = np.cumsum(white_noise)
    brown_noise = (brown_noise / np.max(np.abs(brown_noise)) * 28000).astype(np.int16) 
    n_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(n_tmp.name, sr, brown_noise)
    st.audio(n_tmp.name)
    plot_waveform(n_tmp.name)

st.markdown("---")
if st.button("🚀 بدء هندسة وإنتاج الجلسة"):
    with st.spinner("جاري دمج الطبقات العصبية وبناء صوت الشلال..."):
        final_script = get_ai_script(api_key, name, goal)
        st.write("📝 **السكريبت المستخدم:**")
        st.info(final_script)
        
        bin_path =
