import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- Setup Google Sheets ------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds_dict = dict(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open("MCQ_Quiz_Results").sheet1  # Replace with your sheet name

# ---------------- Load Questions ------------------
with open("questions.json", "r") as f:
    questions = json.load(f)

# ---------------- UI ------------------
st.markdown(
    """
    <div style='display: flex; align-items: center;'>
        <img src='https://i.ibb.co/jRCkDGR/logo.png' style='height: 60px; margin-right: auto;' />
    </div>
    """,
    unsafe_allow_html=True
)

st.title("📝 Data Analytics Quiz")
st.markdown("---")

# ---------------- Learner Info ------------------
name = st.text_input("Enter your name:")
batch = st.selectbox("Select your batch:", ["DS13", "DS14", "DS15"])

# ---------------- Quiz ------------------
if name and batch:
    st.markdown("### Quiz Questions")
    user_answers = {}
    score = 0

    for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        options = q['options']
        selected = st.radio("Choose an option:", options, key=f"q{i}", index=0)
        user_answers[q['question']] = selected

        correct = q['answer']
        if selected == correct:
            score += 1
            st.success(f"✅ Your answer: {selected}")
        else:
            st.error(f"❌ Your answer: {selected}")
            st.info(f"✅ Correct answer: {correct}")
        st.markdown("---")

    # ---------------- Final Score ------------------
    st.subheader(f"🏁 Final Score: {score} / {len(questions)}")

    if st.button("📤 Submit and Save Result"):
        sheet.append_row([name, batch, score])
        st.success("✅ Result submitted to Google Sheet!")

else:
    st.warning("Please enter your name and select a batch to begin.")
