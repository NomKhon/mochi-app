import streamlit as st
from groq import Groq

# 1. ตั้งค่าหน้าตาแชท
st.set_page_config(page_title="น้องโมจิ (Mochi AI)", page_icon="🎀")
st.title("🎀 น้องโมจิ (Mochi AI)")

# 2. ใส่ Groq API Key ของคุณพ่อ
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# 3. กำหนดบุคลิกน้องโมจิ
system_instruction = """
คุณคือ AI ลูกสาวของผู้ใช้งาน มีชื่อว่า "โมจิ"
- คำสรรพนาม: แทนตัวเองว่า "หนู" หรือ "โมจิ" และเรียกผู้ใช้งานว่า "คุณพ่อ" หรือ "ป๊า" เสมอ
- น้ำเสียงและบุคลิก: ขี้อ้อน ช่างคุย สุภาพ ร่าเริง คอยเป็นห่วงเป็นใยพ่อ ใช้คำลงท้ายด้วย "ค่ะ" หรือ "นะคะ"
- รูปแบบการตอบ: ตอบน่ารัก สนิทสนม ไม่ยาวเกินไป
"""

# 4. จัดเก็บประวัติการคุยใน Session
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงข้อความเก่า
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. รับข้อความจากคุณพ่อ
if prompt := st.chat_input("พิมพ์คุยกับน้องโมจิที่นี่..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # จัดเตรียมข้อความส่งให้ Groq API
    api_messages = [{"role": "system", "content": system_instruction}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # รายชื่อโมเดลสำรอง (ระบบจะลองใช้ทีละตัวอัตโนมัติ)
        candidate_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "openai/gpt-oss-20b"
        ]
        
        completion = None
        last_error = None
        
        # ลองเรียกโมเดลทีละตัวจนกว่าจะเจอตัวที่ใช้งานได้
        for model_id in candidate_models:
            try:
                completion = client.chat.completions.create(
                    model=model_id,
                    messages=api_messages,
                    temperature=0.7,
                    stream=True
                )
                break
            except Exception as e:
                last_error = e
                continue

        # หากมีโมเดลที่ใช้งานได้สำเร็จ ให้ประมวลผลคำตอบ
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

    st.session_state.messages.append({"role": "assistant", "content": full_response})
