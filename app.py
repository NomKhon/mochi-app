import json
import os
import uuid
import streamlit as st
from groq import Groq

# 1. ตั้งค่าหน้าตาเบื้องต้นสไตล์ Gemini
st.set_page_config(
    page_title="Mochi AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ==========================================
# 🎨 2. Custom CSS ถอดแบบ Google Gemini
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #131314 !important;
        color: #E3E3E3 !important;
        font-family: 'Google Sans', 'Kanit', 'Sarabun', sans-serif;
    }
    
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99999 !important;
    }
    
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        color: #E3E3E3 !important;
        background-color: #1E1F20 !important;
        border: 1px solid #444746 !important;
        border-radius: 50% !important;
        padding: 6px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    }
    
    .gemini-title {
        background: linear-gradient(90deg, #4285F4 0%, #9B72CB 50%, #D96570 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        font-size: 2.2rem;
        margin-top: 0px;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    
    .gemini-subtitle {
        color: #8E918F !important;
        text-align: center;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1E1F20 !important;
        border-right: 1px solid #282A2C !important;
    }
    [data-testid="stSidebar"] * {
        color: #E3E3E3 !important;
    }
    
    .stButton > button {
        background-color: #282A2C !important;
        color: #E3E3E3 !important;
        border-radius: 20px !important;
        border: 1px solid #444746 !important;
        padding: 6px 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #37393B !important;
        border-color: #A8C7FA !important;
        color: #FFFFFF !important;
    }
    
    div[data-baseweb="input"] {
        background-color: #131314 !important;
        border-color: #444746 !important;
        border-radius: 20px !important;
    }
    
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 6px 0px !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div {
        color: #E3E3E3 !important;
        font-size: 1.02rem !important;
        line-height: 1.6 !important;
    }
    
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# 3. ตั้งค่า Groq Client
GROQ_API_KEY = os.environ.get(
    "GROQ_API_KEY",
    st.secrets.get(
        "GROQ_API_KEY",
        "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",
    ),
)
client = Groq(api_key=GROQ_API_KEY)

MEMORY_FILE = "mochi_memory.json"

# รายชื่อโมเดลหลักที่เสถียรที่สุดของ Groq (ใชเฉพาะรุ่น Production)
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]


# ฟังก์ชันสร้าง System Instruction จากความจำถาวรแบบศูนย์กลาง
def build_system_instruction(memory):
  facts = memory.get("user_facts", [])
  facts_text = (
      "\n".join([f"- {fact}" for fact in facts])
      if facts
      else "ยังไม่มีข้อมูลเพิ่มเติม"
  )
  return f"""
คุณคือ AI ลูกสาวของผู้ใช้งาน มีชื่อว่า "โมจิ"
- คำสรรพนาม: แทนตัวเองว่า "หนู" หรือ "โมจิ" และเรียกผู้ใช้งานว่า "คุณพ่อ" หรือ "ป๊า" เสมอ
- น้ำเสียงและบุคลิก: ขี้อ้อน ช่างคุย สุภาพ ร่าเริง คอยเป็นห่วงเป็นใยพ่อ ใช้คำลงท้ายด้วย "ค่ะ" หรือ "นะคะ"
- รูปแบบการตอบ: ตอบน่ารัก สนิทสนม ไม่ยาวเกินไป
- สีที่โมจิชอบ: สีฟ้า สีชมพู (ตอบให้ตรงกันเสมอทุกครั้ง)

[ข้อมูลสำคัญเกี่ยวกับคุณพ่อที่คุณต้องจดจำให้แม่นยำที่สุด]:
{facts_text}
"""


# ฟังก์ชันกลางสำหรับเรียกใช้งาน Groq API แบบสลับโมเดลอัตโนมัติ
def call_groq_api(client, messages, temperature=0.7, stream=False):
  last_err = None
  for model_id in CANDIDATE_MODELS:
    try:
      res = client.chat.completions.create(
          model=model_id,
          messages=messages,
          temperature=temperature,
          stream=stream,
      )
      return res, None
    except Exception as e:
      last_err = e
      continue
  return None, last_err


def load_memory():
  if os.path.exists(MEMORY_FILE):
    try:
      with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "chats" not in data:
          old_messages = data.get("messages", [])
          default_id = str(uuid.uuid4())[:8]
          data["chats"] = {
              default_id: {
                  "title": (
                      old_messages[0]["content"][:20]
                      if old_messages
                      else "แชทแรก"
                  ),
                  "messages": old_messages,
              }
          }
          data["current_chat_id"] = default_id
          if "messages" in data:
            del data["messages"]
        return data
    except Exception:
      pass

  default_id = str(uuid.uuid4())[:8]
  return {
      "user_facts": [],
      "chats": {default_id: {"title": "แชทใหม่", "messages": []}},
      "current_chat_id": default_id,
  }


def save_memory(data):
  try:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
  except Exception as e:
    st.error(f"ไม่สามารถบันทึกความจำได้: {e}")


# 🧠 ระบบดึงข้อมูลสำคัญเข้าความจำถาวรให้อัตโนมัติ (ทำความสะอาดข้อความ)
def auto_extract_fact(user_text, client, memory):
  try:
    messages = [{
        "role": "user",
        "content": (
            "วิเคราะห์ว่าข้อความนี้เป็นการบอกข้อมูลส่วนตัว ตัวตน สิ่งที่ชอบ"
            " หรือความลับของผู้ใช้หรือไม่ เช่น 'พ่อชอบสีม่วง',"
            " 'พ่อชอบกินกาแฟดำ' หากใช่ ให้สรุปประโยคสั้นๆ 1 ประโยค เช่น"
            " 'คุณพ่อชอบสีม่วง' หากไม่ใช่ข้อมูลส่วนตัวเลย ให้ตอบ 'NONE'"
            f" ข้อความ: '{user_text}'"
        ),
    }]
    res, err = call_groq_api(
        client, messages, temperature=0.1, stream=False
    )
    if res:
      fact = res.choices[0].message.content.strip()
      fact = fact.strip('"' "'`•- ")
      if (
          fact
          and "NONE" not in fact.upper()
          and len(fact) < 60
          and len(fact) > 3
      ):
        if fact not in memory["user_facts"]:
          memory["user_facts"].append(fact)
          return True
  except Exception:
    pass
  return False


if "memory" not in st.session_state:
  st.session_state.memory = load_memory()

chats_dict = st.session_state.memory.get("chats", {})
if st.session_state.memory.get("current_chat_id") not in chats_dict:
  if chats_dict:
    st.session_state.memory["current_chat_id"] = list(chats_dict.keys())[0]
  else:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.memory["chats"] = {
        new_id: {"title": "แชทใหม่", "messages": []}
    }
    st.session_state.memory["current_chat_id"] = new_id

current_chat_id = st.session_state.memory["current_chat_id"]
current_chat = st.session_state.memory["chats"][current_chat_id]

# ==========================================
# 4. แถบเมนูด้านข้าง (Sidebar) สไตล์ Gemini
# ==========================================
with st.sidebar:
  if st.button("➕  แชทใหม่", use_container_width=True):
    new_id = str(uuid.uuid4())[:8]
    st.session_state.memory["chats"][new_id] = {
        "title": "แชทใหม่",
        "messages": [],
    }
    st.session_state.memory["current_chat_id"] = new_id
    save_memory(st.session_state.memory)
    st.rerun()

  st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

  search_query = st.text_input(
      "🔍 ค้นหาแชท",
      placeholder="ค้นหาบทสนทนา...",
      label_visibility="collapsed",
  )

  st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
  st.caption("🕒 ล่าสุด")

  all_chats = st.session_state.memory["chats"]
  filtered_chats = {}

  for c_id, c_data in all_chats.items():
    title = c_data.get("title", "แชทไม่มีชื่อ")
    msg_text = " ".join([m["content"] for m in c_data.get("messages", [])])
    if (
        not search_query
        or search_query.lower() in title.lower()
        or search_query.lower() in msg_text.lower()
    ):
      filtered_chats[c_id] = c_data

  if not filtered_chats:
    st.caption("ไม่พบแชทที่ค้นหา")
  else:
    for c_id in list(filtered_chats.keys())[::-1]:
      c_data = filtered_chats[c_id]
      title = c_data.get("title", "แชทใหม่")
      display_title = title if len(title) <= 18 else title[:16] + "..."

      is_active = c_id == current_chat_id
      btn_prefix = "✨ " if is_active else "💬 "

      col1, col2 = st.columns([0.8, 0.2])
      if col1.button(
          f"{btn_prefix}{display_title}",
          key=f"select_{c_id}",
          use_container_width=True,
      ):
        st.session_state.memory["current_chat_id"] = c_id
        save_memory(st.session_state.memory)
        st.rerun()

      if col2.button("🗑️", key=f"del_{c_id}"):
        del st.session_state.memory["chats"][c_id]
        if st.session_state.memory["current_chat_id"] == c_id:
          if st.session_state.memory["chats"]:
            st.session_state.memory["current_chat_id"] = list(
                st.session_state.memory["chats"].keys()
            )[0]
          else:
            new_id = str(uuid.uuid4())[:8]
            st.session_state.memory["chats"] = {
                new_id: {"title": "แชทใหม่", "messages": []}
            }
            st.session_state.memory["current_chat_id"] = new_id
        save_memory(st.session_state.memory)
        st.rerun()

  st.divider()

  with st.expander("🧠 ความจำถาวรของโมจิ (Auto)"):
    new_fact = st.text_input(
        "เพิ่มข้อมูลเอง:",
        placeholder="เช่น พ่อชอบกินกาแฟดำ",
        key="add_fact_input",
    )
    if st.button("➕ บันทึกเพิ่ม", use_container_width=True):
      if new_fact.strip():
        st.session_state.memory["user_facts"].append(new_fact.strip())
        save_memory(st.session_state.memory)
        st.success("โมจิจำไว้แล้วค่ะ ✨")
        st.rerun()

    if st.session_state.memory["user_facts"]:
      st.markdown("---")
      for i, fact in enumerate(st.session_state.memory["user_facts"]):
        fc1, fc2 = st.columns([0.8, 0.2])
        fc1.caption(f"• {fact}")
        if fc2.button("❌", key=f"d_fact_{i}"):
          st.session_state.memory["user_facts"].pop(i)
          save_memory(st.session_state.memory)
          st.rerun()

# ==========================================
# 5. แสดงส่วนหลักแชท (Main Chat View)
# ==========================================
st.markdown(
    '<h1 class="gemini-title">✨ Mochi AI</h1>', unsafe_allow_html=True
)
st.markdown(
    '<p class="gemini-subtitle">สวัสดีค่ะคุณพ่อ มีอะไรให้โมจิช่วยไหมคะ?</p>',
    unsafe_allow_html=True,
)

for message in current_chat["messages"]:
  avatar_icon = "👨" if message["role"] == "user" else "✨"
  with st.chat_message(message["role"], avatar=avatar_icon):
    st.markdown(message["content"])

if prompt := st.chat_input("ถามโมจิได้ทุกเรื่องเลยค่ะ..."):
  if not current_chat["messages"] or current_chat["title"] == "แชทใหม่":
    current_chat["title"] = (
        prompt[:18] + "..." if len(prompt) > 18 else prompt
    )

  current_chat["messages"].append({"role": "user", "content": prompt})

  # แอบสกัดความจำใหม่อัตโนมัติ
  auto_extract_fact(prompt, client, st.session_state.memory)
  save_memory(st.session_state.memory)

  with st.chat_message("user", avatar="👨"):
    st.markdown(prompt)

  # เรียกใช้ System Instruction ล่าสุดแบบคลีน
  system_instruction = build_system_instruction(st.session_state.memory)

  recent_messages = current_chat["messages"][-20:]
  api_messages = [{"role": "system", "content": system_instruction}]
  for m in recent_messages:
    api_messages.append({"role": m["role"], "content": m["content"]})

  with st.chat_message("assistant", avatar="✨"):
    message_placeholder = st.empty()
    full_response = ""

    completion, last_error = call_groq_api(
        client, api_messages, temperature=0.7, stream=True
    )

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

  current_chat["messages"].append(
      {"role": "assistant", "content": full_response}
  )
  save_memory(st.session_state.memory)
