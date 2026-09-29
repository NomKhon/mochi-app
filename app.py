import json
import os
import streamlit as st
from groq import Groq

# 1. ตั้งค่าหน้าตาแชท
st.set_page_config(
    page_title="น้องโมจิ (Mochi AI)", page_icon="🎀", layout="centered"
)
st.title("🎀 น้องโมจิ (Mochi AI)")

# 2. ใส่ Groq API Key ของคุณพ่อ
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

# 3. แถบเมนูด้านข้าง (Sidebar) จัดการความจำ
with st.sidebar:
  st.header("🧠 สมองและความจำของน้องโมจิ")
  st.caption("ระบบบันทึกความจำถาวร (Persistent Memory)")

  # ช่องเพิ่มข้อมูลที่อยากให้น้องโมจิจดจำ
  st.subheader("📌 สิ่งที่โมจิจดจำไว้:")
  new_fact = st.text_input(
      "เพิ่มข้อมูลที่คุณพ่ออยากให้โมจิจำ:",
      placeholder="เช่น พ่อชอบดื่มกาแฟดำไม่ใส่น้ำตาล",
  )
  if st.button("➕ ให้โมจิจดจำ"):
    if new_fact.strip():
      st.session_state.memory["user_facts"].append(new_fact.strip())
      save_memory(st.session_state.memory)
      st.success("น้องโมจิจำเรียบร้อยแล้วค่ะ! 🎀")
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
    st.info("ยังไม่มีข้อมูลความจำพิเศษ พิมพ์เพิ่มด้านบนได้เลยค่ะ")

  st.divider()

  # ปุ่มลบประวัติการคุยทั้งหมด
  if st.button("🗑️ ลบประวัติการคุยทั้งหมด"):
    st.session_state.memory["messages"] = []
    save_memory(st.session_state.memory)
    st.success("ลบประวัติการคุยเรียบร้อยค่ะ!")
    st.rerun()

# 4. กำหนดบุคลิกและใส่ข้อมูลความจำลงใน System Instruction
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

# 5. แสดงประวัติการคุยเก่าทั้งหมด
for message in st.session_state.memory["messages"]:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# 6. รับข้อความใหม่จากคุณพ่อ
if prompt := st.chat_input("พิมพ์คุยกับน้องโมจิที่นี่..."):
  # บันทึกข้อความของคุณพ่อลงในประวัติความจำ
  st.session_state.memory["messages"].append(
      {"role": "user", "content": prompt}
  )
  save_memory(st.session_state.memory)

  with st.chat_message("user"):
    st.markdown(prompt)

  # ดึงประวัติการคุยย้อนหลังไปส่งให้ Groq
  recent_messages = st.session_state.memory["messages"][-20:]
  api_messages = [{"role": "system", "content": system_instruction}]
  for m in recent_messages:
    api_messages.append({"role": m["role"], "content": m["content"]})

  with st.chat_message("assistant"):
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

  # บันทึกคำตอบของน้องโมจิลงประวัติความจำถาวร
  st.session_state.memory["messages"].append(
      {"role": "assistant", "content": full_response}
  )
  save_memory(st.session_state.memory)
