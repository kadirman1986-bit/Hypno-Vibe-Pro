import streamlit as st
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import subprocess
from gtts import gTTS
import google.generativeai as genai

# ==========================================
# 1. إعدادات النظام وقاعدة البيانات التقنية
# ==========================================
st.set_page_config(page_title="Hypno-Vibe Pro | Bio-Engineering", layout="wide", page_icon="🧠")

# قاعدة بيانات الترددات (الضبط الآلي بناءً على الحالات التي ناقشناها)
SESSION_LOGIC = {
    "علاج البرود/التحفيز الأنثوي": {"base": 210.42, "beat": 12.0, "desc": "تردد الزهرة لتحفيز الطاقة الأنثوية الحيوية."},
    "استعادة الفطرة والذكورة": {"base": 144.72, "beat": 15.0, "desc": "تردد المريخ لتعزيز القوة والتركيز الفطري."},
    "الاستسلام وفك القيود (Letting Go)": {"base": 210.42, "beat": 6.0, "desc": "نبضة Theta العميقة لإزالة التشنج النفسي والتوتر."},
    "تأريض وسكينة (Grounding/Delay)": {"base": 144.72, "beat": 7.83, "desc": "رنين شومان للهدوء والتحكم في الانفعالات وسرعة الاستجابة."}
}

# سكريبتات الطوارئ الاحترافية (Offline Mode)
OFFLINE_SCRIPTS = {
    "علاج البرود/التحفيز الأنثوي": "تنفسي بعمق.. استرخي تماماً. اسمحي لجسدك باستعادة توازنه الطبيعي وطاقته الحيوية الآن. أنتِ في حالة انسجام تام مع فطرتكِ النقية.",
    "استعادة الفطرة والذكورة": "خذ نفساً عميقاً.. استشعر قوتك الداخلية واتزانك. أنت الآن في حالة سيطرة وهدوء، متصل تماماً بفطرتك وذكورتك السليمة.",
    "الاستسلام وفك القيود (Letting Go)": "تحرر من كل القيود العصبية.. اترك كل الأفكار ترحل. الاستسلام لهذا السلام هو قمة الأمان. جسدك يعرف طريقه تماماً نحو اللذة والسكينة.",
    "تأريض وسكينة (Grounding/Delay)": "أنت الآن ثابت كالجبال.. هادئ كالبحر. نبضاتك متناغمة مع رنين الأرض. السكينة تملأ كيانك وتمنحك سيطرة كاملة على مشاعرك."
}

# ==========================================
# 2. الدوال الهندسية (Core Engines)
# ==========================================

def generate_binaural_beat(base_freq, beat_freq, duration):
    """توليد الترددات العلاجية الخام (Binaural)"""
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    left = np.sin(2 * np.pi * base_freq * t)
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    audio = np.vstack((left, right)).T
    audio = (audio * 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(tmp.name, sr, audio)
    return tmp.name

def get_ai_script(api_key, name, goal):
    """جلب السكريبت من Gemini أو استخدام النسخة الاحتياطية"""
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

def render_final_session(binaural_path, script_text, duration, output_name):
    """دمج الطبقات باستخدام FFmpeg مع إصلاح صوت الشلال (التمويه)"""
    # 1. توليد الصوت البشري (TTS)
    tts = gTTS(text=script_text, lang='ar')
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)
    
    # 2. توليد الضجيج الطبيعي (إصلاح صوت الشلال - Brown Noise)
    sr = 44100
    white_noise = np.random.uniform(-1, 1, int(sr * duration))
    brown_noise = np.cumsum(white_noise)
    # رفع المستوى (Normalize & Boost) ليظهر بوضوح كصوت شلال مريح
    brown_noise = (brown_noise / np.max(np.abs(brown_noise)) * 28000).astype(np.int16) 
    n_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(n_tmp.name, sr, brown_noise)

    # 3. الدمج عبر FFmpeg مع موازنة دقيقة للمستويات
    # [0:a] الترددات | [1:a] الصوت البشري | [2:a] صوت الشلال
    cmd = [
        'ffmpeg', '-y',
        '-i', binaural_path,
        '-i', v_tmp.name,
        '-i', n_tmp.name,
        '-filter_complex',
        '[0:a]volume=0.2[b];'
        '[1:a]adelay=4000|4000,volume=2.0[v];'
        '[2:a]volume=0.9[n];'
        '[b][n]amix=inputs=2[bg];'
        '[bg][v]amix=inputs=2:duration=first',
        output_name
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_name

# ==========================================
# 3. واجهة التطبيق (UI)
# ==========================================
st.title("🧠 عيادة Hypno-Vibe: مختبر الهندسة العصبية الذكي")
st.markdown("---")

with st.sidebar:
    st.header("🔑 إعدادات الوصول")
    api_key = st.text_input("Gemini API Key (اختياري)", type="password")
    st.info("إذا فشل الـ AI، سيعمل النظام بالسكريبتات المخزنة آلياً.")

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

if st.button("🚀 بدء هندسة وإنتاج الجلسة"):
    with st.spinner("جاري دمج الطبقات العصبية وبناء صوت الشلال..."):
        # 1. جلب السكريبت
        final_script = get_ai_script(api_key, name, goal)
        st.write("📝 **السكريبت المستخدم:**")
        st.info(final_script)
        
        # 2. توليد ودمج الملفات
        bin_path = generate_binaural_beat(logic['base'], logic['beat'], duration)
        output_file = f"Session_{name}.mp3"
        
        render_final_session(bin_path, final_script, duration, output_file)
        
        # 3. عرض النتيجة
        st.audio(output_file)
        st.success("✅ الجلسة جاهزة. صوت الشلال يغطي الترددات، والصوت البشري يبدأ بعد 4 ثوانٍ.")
