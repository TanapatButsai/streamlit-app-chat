import streamlit as st
import requests
import os

# HuggingFace API config
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

# Chat function (Zephyr)
def chat_with_gpt(prompt, history=[]):
    full_prompt = ""
    for sender, msg in history:
        role = "User" if sender == "user" else "Assistant"
        full_prompt += f"{role}: {msg}\n"
    full_prompt += f"User: {prompt}\nAssistant:"

    payload = {
        "inputs": full_prompt,
        "parameters": {"temperature": 0.7, "max_new_tokens": 200}
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].split("Assistant:")[-1].strip()
        elif "error" in result:
            raise Exception(result["error"])
        else:
            raise Exception("Unknown format: " + str(result))
    except Exception as e:
        raise Exception(f"❌ Raw response:\n{response.text}\n\nParsed error: {e}")

# DASS Questions
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

def adjusted_form_data(form_data):
    return {k: max(v - 1, 0) for k, v in form_data.items()}

# Session setup
st.set_page_config(page_title="VONIX - GPT + DASS", layout="centered")
st.markdown("### 🧠 VONIX Mental Wellness Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append((
        "assistant",
        "👋 Hi! I’m **Nix**, your mental wellness assistant.\n\nYou can type `1` to start a short checkup, `2` for a full checkup, or ask me anything!"
    ))
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "completed" not in st.session_state:
    st.session_state.completed = False

# User input
user_input = st.chat_input("Type 1 for short test, 2 for full test, or chat with me!")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    
    # === MODE: CHAT GPT ===
    if st.session_state.mode == "chat":
        if user_input.strip() == "1":
            st.session_state.mode = "dass_short"
            st.session_state.chat_history.append(("assistant", "Starting short version (21 questions). Answer 1–4."))
        elif user_input.strip() == "2":
            st.session_state.mode = "dass_full"
            st.session_state.chat_history.append(("assistant", "Starting full version (42 questions). Answer 1–4."))
        else:
            try:
                reply = chat_with_gpt(user_input, st.session_state.chat_history)
                st.session_state.chat_history.append(("assistant", reply))
            except Exception as e:
                st.session_state.chat_history.append(("assistant", str(e)))

    # === MODE: DASS ===
    elif st.session_state.mode in ["dass_short", "dass_full"] and not st.session_state.completed:
        qmap = question_map_short if st.session_state.mode == "dass_short" else question_map_full
        q_keys = list(qmap.keys())
        idx = st.session_state.question_index

        if user_input.strip() in ["1", "2", "3", "4"] and q_keys[idx] not in st.session_state.form_data:
            st.session_state.form_data[q_keys[idx]] = int(user_input.strip())
            st.session_state.question_index += 1

            if st.session_state.question_index < len(q_keys):
                next_q = qmap[q_keys[st.session_state.question_index]]
                st.session_state.chat_history.append(("assistant", f"{st.session_state.question_index+1}. {next_q} (1–4)"))
            else:
                try:
                    response = requests.post("https://vonix-dass-chatbot.onrender.com/predict", json=adjusted_form_data(st.session_state.form_data))
                    result = response.json()
                    if result["status"] == "success":
                        st.session_state.chat_history.append(("assistant", f"**Assessment Result**\n- Depression: {result['result']['depression']}\n- Anxiety: {result['result']['anxiety']}\n- Stress: {result['result']['stress']}"))
                    else:
                        st.session_state.chat_history.append(("assistant", f"Error: {result['message']}"))
                except Exception as e:
                    st.session_state.chat_history.append(("assistant", f"Could not connect to backend: {e}"))
                st.session_state.chat_history.append(("assistant", "You can now ask me anything again or type `1`/`2` to start a new assessment."))
                st.session_state.completed = False
                st.session_state.mode = "chat"
                st.session_state.form_data = {}
                st.session_state.question_index = -1
                st.session_state.mode_set = False

        else:
            st.session_state.chat_history.append(("assistant", "Please answer with a number from 1 to 4."))

# Display history
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)
        