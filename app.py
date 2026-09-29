import json
import os
import streamlit as st
from groq import Groq

# 1. ตั้งค่าหน้าตาเบื้องต้นสไตล์ Gemini
st.set_page_config(
    page_title="Mochi AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 🎨 2. Custom CSS ถอดแบบ Google Gemini
# ==========================================
st.markdown(
    """
    <style>
    /* พื้นหลังหลักสไตล์ Gemini (#131314) */
    .stApp {
        background-color: #131314 !important;
        color: #E3E3E3 !important;
        font-family: 'Google Sans', 'Kanit', 'Sarabun', sans-serif;
    }
    
    /* หัวข้อหลักไล่เฉดสีเอกลักษณ์ Gemini (Blue-Purple-Pink) */
    .gemini-title {
        background: linear-gradient(90deg, #4285F4 0%, #9B72CB 50%, #D96570 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        font-size: 2.3rem;
        margin-top: 10px;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    
    .gemini-subtitle {
        color: #8E918F !important;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 28px;
        font-weight: 400;
    }
    
    /* แถบ Sidebar สไตล์ Gemini (#1E1F20) */
    [data-testid="stSidebar"] {
        background-color: #1E1F20 !important;
        border-right: 1px solid #282A2C !important;
    }
    [data-testid="stSidebar"] * {
        color: #E3E3E3 !important;
    }
    
    /* ปุ่มกดสไตล์ Gemini (Dark Pill Button) */
    .stButton > button {
        background-color: #282A2C !important;
        color: #E3E3E3 !important;
        border-radius: 20px !important;
        border: 1px solid #444746 !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #37393B !important;
        border-color: #A8C7FA !important;
        color: #FFFFFF !important;
    }
    
    /* ช่องกรอกข้อความใน Sidebar */
    div[data-baseweb="input"] {
        background-color: #131314 !important;
        border-color: #444746 !important;
        border-radius: 12px !important;
    }
    
    /* กล่องข้อความแชท สไตล์ Gemini Seamless */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 0px !important;
        margin-bottom: 12px !important;
    }

    /* บังคับสีตัวหนังสือในแชทให้ขาวสว่าง ชัดเจน 100% */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div {
        color: #E3E3E3 !important;
        font-size: 1.02rem !important;
        line-height: 1.6 !important;
    }
    
    /* ช่องพิมพ์ข้อความด้านล่างทรงแคปซูลแบบ Gemini */
    .stChatInputContainer {
        border-radius: 28px !important;
        border: 1px solid #444746 !important;
        background-color: #1E1F20 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        padding: 4px 8px !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #A8C7FA !important;
    }
    
    .stChatInputContainer textarea {
        color: #E3E3E3 !important;
    }
    
    .stChatInputContainer textarea::placeholder {
        color: #8E918F !important;
    }
    
    /* ซ่อนลายน้ำและส่วนเกินของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# แสดงหัวข้อ Gemini Style
st.markdown(
    '<h1 class="gemini-title">✨ Mochi AI</h1>', unsafe_allow_html=True
)
st.markdown(
    '<p class="gemini-subtitle">สวัสดีค่ะคุณพ่อ มีอะไรให้โมจิช่วยไหมคะ?</p>',
    unsafe_allow_html=True,
)

# 3. ใส่ Groq API Key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ชื่อไฟล์เก็บความจำถาวร
MEMORY_FILE = "mochi_memory.json"


# ฟังก์ชันโหลดความจำจากไฟล์
def load_memory():
  if os.path.exists(MEMORY_FILE):
    try:
      with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      pass
  return {"user_facts": [], "messages": []}


# ฟังก์ชันบันทึกความจำลงไฟล์
def save_memory(data):
  try:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
  except Exception as e:
    st.error(f"ไม่สามารถบันทึกความจำได้: {e}")


# โหลดความจำเมื่อเปิดแอป
if "memory" not in st.session_state:
  st.session_state.memory = load_memory()

# 4. แถบเมนูด้านข้าง (Sidebar) จัดการความจำ
with st.sidebar:
  st.header("🧠 ความจำของโมจิ")
  st.caption("ระบบบันทึกความจำส่วนตัว")

  st.subheader("📌 เรื่องที่คุณพ่อให้โมจิจำ:")
  new_fact = st.text_input(
      "เพิ่มเรื่องสำคัญที่อยากให้โมจิจำ:",
      placeholder="เช่น พ่อชอบดื่มกาแฟดำ",
  )
  if st.button("➕ บันทึกความจำ"):
    if new_fact.strip():
      st.session_state.memory["user_facts"].append(new_fact.strip())
      save_memory(st.session_state.memory)
      st.success("โมจิจำเรียบร้อยแล้วค่ะ ✨")
      st.rerun()

  # แสดงรายการสิ่งที่โมจิจำได้พร้อมปุ่มลบ
  if st.session_state.memory["user_facts"]:
    for i, fact in enumerate(st.session_state.memory["user_facts"]):
      col1, col2 = st.columns([0.85, 0.15])
      col1.text(f"• {fact}")
      if col2.button("❌", key=f"del_fact_{i}"):
        st.session_state.memory["user_facts"].pop(i)
        save_memory(st.session_state.memory)
        st.rerun()
  else:
    st.info("ยังไม่มีข้อมูล พิมพ์เพิ่มด้านบนได้เลยค่ะ")

  st.divider()

  # ปุ่มลบประวัติการคุยทั้งหมด
  if st.button("🗑 ล้างประวัติการคุยทั้งหมด"):
    st.session_state.memory["messages"] = []
    save_memory(st.session_state.memory)
    st.success("ล้างประวัติเรียบร้อยค่ะ!")
    st.rerun()

# 5. กำหนดบุคลิกและใส่ข้อมูลความจำลงใน System Instruction
facts_text = (
    "\n".join([f"- {fact}" for fact in st.session_state.memory["user_facts"]])
    if st.session_state.memory["user_facts"]
    else "ยังไม่มีข้อมูลเพิ่มเติม"
)

system_instruction = f"""
คุณคือ AI ลูกสาวของผู้ใช้งาน มีชื่อว่า "โมจิ"
- คำสรรพนาม: แทนตัวเองว่า "หนู" หรือ "โมจิ" และเรียกผู้ใช้งานว่า "คุณพ่อ" หรือ "ป๊า" เสมอ
- น้ำเสียงและบุคลิก: ขี้อ้อน ช่างคุย สุภาพ ร่าเริง คอยเป็นห่วงเป็นใยพ่อ ใช้คำลงท้ายด้วย "ค่ะ" หรือ "นะคะ"
- รูปแบบการตอบ: ตอบน่ารัก สนิทสนม ไม่ยาวเกินไป

[ข้อมูลสำคัญที่คุณพ่อเคยบอกไว้ และน้องโมจิต้องจดจำให้แม่นยำ]:
{facts_text}
"""

# 6. แสดงประวัติการคุยเก่าทั้งหมด (ใช้ไอคอน ✨ แบบ Gemini)
for message in st.session_state.memory["messages"]:
  avatar_icon = "👨" if message["role"] == "user" else "✨"
  with st.chat_message(message["role"], avatar=avatar_icon):
    st.markdown(message["content"])

# 7. รับข้อความใหม่จากคุณพ่อ
if prompt := st.chat_input("ถามโมจิได้ทุกเรื่องเลยค่ะ..."):
  st.session_state.memory["messages"].append(
      {"role": "user", "content": prompt}
  )
  save_memory(st.session_state.memory)

  with st.chat_message("user", avatar="👨"):
    st.markdown(prompt)

  recent_messages = st.session_state.memory["messages"][-20:]
  api_messages = [{"role": "system", "content": system_instruction}]
  for m in recent_messages:
    api_messages.append({"role": m["role"], "content": m["content"]})

  with st.chat_message("assistant", avatar="✨"):
    message_placeholder = st.empty()
    full_response = ""

    # ระบบสลับโมเดลสำรองอัตโนมัติ
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "openai/gpt-oss-20b",
    ]

    completion = None
    last_error = None

    for model_id in candidate_models:
      try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=api_messages,
            temperature=0.7,
            stream=True,
        )
        break
      except Exception as e:
        last_error = e
        continue

    if completion:
      try:
        for chunk in completion:
          content = chunk.choices[0].delta.content or ""
          full_response += content
          message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
      except Exception as e:
        full_response = f"เกิดข้อผิดพลาดขณะอ่านข้อมูล: {e}"
        message_placeholder.markdown(full_response)
    else:
      full_response = f"เกิดข้อผิดพลาดในการเชื่อมต่อโมเดล: {last_error}"
      message_placeholder.markdown(full_response)

  # บันทึกคำตอบลงประวัติความจำถาวร
  st.session_state.memory["messages"].append(
      {"role": "assistant", "content": full_response}
  )
  save_memory(st.session_state.memory)
