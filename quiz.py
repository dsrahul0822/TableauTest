import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ---- Setup page ----
st.set_page_config(page_title="The Scholar Quiz", layout="wide")

# ---- Logo ----
st.markdown("""
    <div style='position: absolute; top: 10px; left: 10px;'>
        <img src="https://raw.githubusercontent.com/dsrahul0822/TableauTest/main/The-Scholar.png" style="height:100px;">
    </div>
""", unsafe_allow_html=True)


st.title("🧠 The Scholar - MCQ Quiz App")

# ---- Learner Info ----
name = st.text_input("Enter your name")
batch = st.selectbox("Select your batch", ["DS14", "DS13", "DS12", "DS11"])

if not name:
    st.warning("Please enter your name to begin the quiz.")
    st.stop()

# ---- Load Questions ----
with open("questions.json", "r") as f:
    questions = json.load(f)

# ---- Form to handle quiz ----
with st.form("quiz_form"):
    st.subheader("📋 Multiple Choice Questions")
    user_answers = {}
    for i, q in enumerate(questions):
        st.write(f"**Q{i+1}: {q['question']}**")
        user_answers[i] = st.radio("Choose an option:", q["options"], key=f"q{i}")
        st.markdown("---")
    submitted = st.form_submit_button("Submit Quiz")

# ---- Process Submission ----
if submitted:
    score = 0
    result_details = []
    for i, q in enumerate(questions):
        user_ans = user_answers.get(i)
        correct_ans = q["answer"]
        is_correct = user_ans == correct_ans
        result_details.append({
            "question": q["question"],
            "selected": user_ans,
            "correct": correct_ans,
            "is_correct": is_correct
        })
        if is_correct:
            score += 1

    st.success(f"🎉 {name}, you scored {score} out of {len(questions)}!")

    # ---- Display question-wise result ----
    for i, res in enumerate(result_details, start=1):
        st.markdown(f"**Q{i}: {res['question']}**")
        st.write(f"✅ Correct Answer: {res['correct']}")
        if res['is_correct']:
            st.markdown(f"<span style='color:green'>✔ You selected: {res['selected']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'>✘ You selected: {res['selected']}</span>", unsafe_allow_html=True)
        st.markdown("---")

    # ---- Save result to Google Sheet ----
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    sheet = client.open("MCQ_Quiz_Results").sheet1

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [now, name, batch, score, len(questions)]
    sheet.append_row(row)

    st.success("✅ Your responses have been recorded successfully!")
