import streamlit as st
import pandas as pd
import requests

# Define all DASS-42 questions
question_map_full = {
    "Q1A": "I found myself getting upset by quite trivial things.",
    "Q2A": "I was aware of dryness of my mouth.",
    "Q3A": "I couldn't seem to experience any positive feeling at all.",
    "Q4A": "I experienced breathing difficulty.",
    "Q5A": "I just couldn't seem to get going.",
    "Q6A": "I tended to over-react to situations.",
    "Q7A": "I had a feeling of shakiness.",
    "Q8A": "I found it difficult to relax.",
    "Q9A": "I found myself in situations that made me so anxious I was most relieved when they ended.",
    "Q10A": "I felt that I had nothing to look forward to.",
    "Q11A": "I found myself getting upset rather easily.",
    "Q12A": "I felt that I was using a lot of nervous energy.",
    "Q13A": "I felt sad and depressed.",
    "Q14A": "I found myself getting impatient when I was delayed.",
    "Q15A": "I had a feeling of faintness.",
    "Q16A": "I felt that I had lost interest in just about everything.",
    "Q17A": "I felt I wasn't worth much as a person.",
    "Q18A": "I felt that I was rather touchy.",
    "Q19A": "I perspired noticeably in the absence of high temperatures.",
    "Q20A": "I felt scared without any good reason.",
    "Q21A": "I felt that life wasn't worthwhile.",
    "Q22A": "I found it hard to wind down.",
    "Q23A": "I had difficulty in swallowing.",
    "Q24A": "I couldn't seem to get any enjoyment out of the things I did.",
    "Q25A": "I was aware of the action of my heart in the absence of physical exertion.",
    "Q26A": "I felt down-hearted and blue.",
    "Q27A": "I found that I was very irritable.",
    "Q28A": "I felt I was close to panic.",
    "Q29A": "I found it hard to calm down after something upset me.",
    "Q30A": "I feared that I would be 'thrown' by some trivial but unfamiliar task.",
    "Q31A": "I was unable to become enthusiastic about anything.",
    "Q32A": "I found it difficult to tolerate interruptions to what I was doing.",
    "Q33A": "I was in a state of nervous tension.",
    "Q34A": "I felt I was pretty worthless.",
    "Q35A": "I was intolerant of anything that kept me from getting on with what I was doing.",
    "Q36A": "I felt terrified.",
    "Q37A": "I could see nothing in the future to be hopeful about.",
    "Q38A": "I felt that life was meaningless.",
    "Q39A": "I found myself getting agitated.",
    "Q40A": "I was worried about situations in which I might panic.",
    "Q41A": "I experienced trembling.",
    "Q42A": "I found it difficult to work up the initiative to do things."
}

# DASS-21 subset
question_map_short = {
    k: v for k, v in question_map_full.items() if k in [
        "Q1A", "Q2A", "Q3A", "Q6A", "Q7A", "Q8A", "Q11A",
        "Q12A", "Q13A", "Q14A", "Q18A", "Q20A", "Q23A", "Q25A",
        "Q26A", "Q28A", "Q30A", "Q33A", "Q34A", "Q36A", "Q41A"
    ]
}

interpretation = {
    "depression": {
        "normal": "No or minimal symptoms of depression.",
        "mild": "Mild depressive symptoms, may resolve on their own.",
        "moderate": "Moderate level of depression, consider talking to someone or self-care activities.",
        "severe": "Severe symptoms, professional help is strongly recommended.",
        "extremely severe": "Very severe symptoms, immediate mental health support is advised."
    },
    "anxiety": {
        "normal": "No or minimal symptoms of anxiety.",
        "mild": "Mild anxiety, manageable with lifestyle adjustment.",
        "moderate": "Moderate anxiety level, could benefit from mental health strategies.",
        "severe": "Severe anxiety, consider consulting a professional.",
        "extremely severe": "Very high anxiety level, professional support is recommended."
    },
    "stress": {
        "normal": "No or minimal stress symptoms.",
        "mild": "Mild stress, may be situational.",
        "moderate": "Moderate stress, consider stress management techniques.",
        "severe": "High stress, could affect daily functioning.",
        "extremely severe": "Extreme stress, seek professional advice."
    }
}

# Wrap submission for API to subtract 1 from all form inputs
def adjusted_form_data(form_data):
    return {k: max(v - 1, 0) for k, v in form_data.items()}

# Session state setup
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "question_index" not in st.session_state:
    st.session_state.question_index = -1
if "completed" not in st.session_state:
    st.session_state.completed = False
if "mode" not in st.session_state:
    st.session_state.mode = None
if "awaiting_question" not in st.session_state:
    st.session_state.awaiting_question = False
if "awaiting_first_input" not in st.session_state:
    st.session_state.awaiting_first_input = False
if "mode_set" not in st.session_state:
    st.session_state.mode_set = False

# UI
st.set_page_config(page_title="VONIX - AI Health Assistant", layout="centered")
st.title("VONIX AI Health Assistant")

# Chat message start
if st.session_state.question_index == -1:
    st.session_state.chat_history.append(("assistant", "Hi there! Would you like to take the short (21 questions) or full (42 questions) DASS assessment?\n\nPlease type `1` for short or `2` for full."))
    st.session_state.question_index = 0

user_input = st.chat_input("Your answer")

if user_input and not st.session_state.mode_set:
    if user_input.strip() == "1":
        st.session_state.mode = "short"
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", "Great! Let's begin the short version. \n Please answer each question with a number from 1 to 4."))
        # st.session_state.chat_history.append(("assistant", "Please answer each question with a number from 1 to 4."))
        st.session_state.awaiting_question = True
        st.session_state.awaiting_first_input = False
        st.session_state.mode_set = True
    elif user_input.strip() == "2":
        st.session_state.mode = "full"
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", "Great! Let's begin the full version. \n Please answer each question with a number from 1 to 4."))
        # st.session_state.chat_history.append(("assistant", "Please answer each question with a number from 1 to 4."))
        st.session_state.awaiting_question = True
        st.session_state.awaiting_first_input = False
        st.session_state.mode_set = True
    else:
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", "Please type `1` for short (21) or `2` for full (42) assessment."))

question_map = question_map_short if st.session_state.mode == "short" else question_map_full

if st.session_state.awaiting_question:
    q_keys = list(question_map.keys())
    first_q = question_map[q_keys[0]]
    st.session_state.chat_history.append(("assistant", f"1. {first_q} (1-4)"))
    st.session_state.awaiting_question = False
    st.session_state.awaiting_first_input = True

elif st.session_state.mode and not st.session_state.completed and st.session_state.awaiting_first_input:
    q_keys = list(question_map.keys())
    current_key = q_keys[0]
    if user_input and user_input.strip() in ["1", "2", "3", "4"] and current_key not in st.session_state.form_data:
        rating = int(user_input.strip())
        st.session_state.form_data[current_key] = rating
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.question_index = 1
        st.session_state.awaiting_first_input = False
        next_q = question_map[q_keys[1]]
        st.session_state.chat_history.append(("assistant", f"2. {next_q} (1-4)"))

elif st.session_state.mode and not st.session_state.completed:
    q_keys = list(question_map.keys())
    if 0 <= st.session_state.question_index < len(q_keys):
        current_key = q_keys[st.session_state.question_index]
        if user_input and user_input.strip() in ["1", "2", "3", "4"] and current_key not in st.session_state.form_data:
            rating = int(user_input.strip())
            st.session_state.form_data[current_key] = rating
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.question_index += 1

            if st.session_state.question_index < len(q_keys):
                next_q = question_map[q_keys[st.session_state.question_index]]
                st.session_state.chat_history.append(("assistant", f"{st.session_state.question_index+1}. {next_q} (1-4)"))
            else:
                try:
                    response = requests.post("https://vonix-dass-chatbot.onrender.com/predict", json=adjusted_form_data(st.session_state.form_data))
                    result = response.json()
                    if result["status"] == "success":
                        st.session_state.chat_history.append(("assistant", f"Assessment Result:\n- Depression: **{result['result']['depression']}**\n- Anxiety: **{result['result']['anxiety']}**\n- Stress: **{result['result']['stress']}**"))
                    else:
                        st.session_state.chat_history.append(("assistant", f"Error: {result['message']}"))
                except Exception as e:
                    st.session_state.chat_history.append(("assistant", f"Could not connect to backend: {e}"))
                st.session_state.completed = True
        elif user_input and current_key not in st.session_state.form_data:
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", "Please answer with a number between 1 and 4."))
    elif st.session_state.question_index >= len(q_keys):
        st.session_state.completed = True



# Display chat
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)
