import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from pytz import timezone


# ---- Setup ----
st.set_page_config(page_title="The Scholar Quiz", layout="wide")

st.title("🧠 The Scholar - MCQ Quiz App")

# ---- Input Form ----
if "started" not in st.session_state:
    st.session_state.started = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.started:
    name = st.text_input("Enter your name")
    batch = st.selectbox("Select your batch", ["", "DS14", "DS13", "DS12", "DS11"])
    if st.button("Go to Test"):
        if not name or batch == "":
            st.warning("Please enter your name and select a batch to proceed.")
        else:
            st.session_state.started = True
            st.session_state.name = name
            st.session_state.batch = batch

# ---- Quiz Form ----
if st.session_state.started and not st.session_state.submitted:
    with open("questions.json", "r") as f:
        questions = json.load(f)

    with st.form("quiz_form"):
        st.subheader("📋 Multiple Choice Questions")
        answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            answers[i] = st.radio("Choose an option:", q["options"], key=f"q{i}")
            st.markdown("---")
        if st.form_submit_button("Submit Quiz"):
            st.session_state.submitted = True
            st.session_state.answers = answers

# ---- Results ----
if st.session_state.submitted:
    with open("questions.json", "r") as f:
        questions = json.load(f)

    score = 0
    result_details = []
    for i, q in enumerate(questions):
        user_ans = st.session_state.answers[i]
        correct = q["answer"]
        correct_flag = user_ans == correct
        if correct_flag:
            score += 1
        result_details.append({
            "question": q["question"],
            "selected": user_ans,
            "correct": correct,
            "is_correct": correct_flag
        })

    st.success(f"🎉 {st.session_state.name}, you scored {score} out of {len(questions)}!")

    for i, res in enumerate(result_details, start=1):
        st.markdown(f"**Q{i}: {res['question']}**")
        st.markdown(f"✅ Correct Answer: {res['correct']}")
        if res['is_correct']:
            st.markdown(f"<span style='color:green'>✔ You selected: {res['selected']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'>✘ You selected: {res['selected']}</span>", unsafe_allow_html=True)
        st.markdown("---")

    # ---- Save to Google Sheets ----
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    sheet = client.open("MCQ_Quiz_Results").sheet1


    india = timezone('Asia/Kolkata')
    timestamp = datetime.datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, st.session_state.name, st.session_state.batch, score, len(questions)]
    sheet.append_row(row)

    st.success("✅ Your responses have been recorded successfully!")
