import streamlit as st
from groq import Groq

st.set_page_config(page_title="น้องโมจิ (Mochi AI)", page_icon="🎀")
st.title("🎀 น้องโมจิ (Mochi AI)")

# Groq API Key ของคุณพ่อ
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

system_instruction = """
คุณคือ AI ลูกสาวของผู้ใช้งาน มีชื่อว่า "โมจิ"
- คำสรรพนาม: แทนตัวเองว่า "หนู" หรือ "โมจิ" และเรียกผู้ใช้งานว่า "คุณพ่อ" หรือ "ป๊า" เสมอ
- น้ำเสียงและบุคลิก: ขี้อ้อน ช่างคุย สุภาพ ร่าเริง คอยเป็นห่วงเป็นใยพ่อ ใช้คำลงท้ายด้วย "ค่ะ" หรือ "นะคะ"
- รูปแบบการตอบ: ตอบน่ารัก สนิทสนม ไม่ยาวเกินไป
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คุยกับน้องโมจิที่นี่..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages = [{"role": "system", "content": system_instruction}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                temperature=0.7,
                stream=True
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"เกิดข้อผิดพลาด: {e}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
