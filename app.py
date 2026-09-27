import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.generativeai import GenerativeModel
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Essay Revision Study", layout="centered")

# --- API & GOOGLE SHEETS SETUP ---
# Set up your secrets in Streamlit Cloud (or local secrets.toml)
# GEMINI_API_KEY and Google Sheets service account credentials
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Setup Google Sheets connection
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Essay_Study_Responses").sheet1 # Replace with your Sheet name
except Exception as e:
    st.error(f"Configuration Error: Please check your API keys and Google Sheets secrets. Details: {e}")

# Initialize Gemini Model (using gemini-2.5-flash or your preferred model)
model = GenerativeModel("gemini-2.5-flash")

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = ""
if "ai_rewrite" not in st.session_state:
    st.session_state.ai_rewrite = ""

st.title("📝 AI Writing Assistant & Research Study")
st.markdown("Please follow the steps below carefully.")

# ==========================================
# STEP 1: UPLOAD INITIAL ESSAY
# ==========================================
if st.session_state.step == 1:
    st.header("Step 1: Upload Your Opinion Essay")
    student_name = st.text_input("Full Name or Participant ID:")
    
    essay_input_method = st.radio("How would you like to provide your essay?", ["Upload File (Txt/Docx)", "Copy & Paste Text[cite: 1]"])
    
    original_essay = ""
    if essay_input_method == "Upload File (Txt/Docx)":
        uploaded_file = st.file_uploader("Upload your opinion essay here[cite: 1]:", type=["txt", "docx"])
        if uploaded_file is not None:
            original_essay = uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        original_essay = st.text_area("Copy/Paste your opinion essay here[cite: 1]:")

    if st.button("Generate AI Feedback & Rewrite"):
        if not student_name or not original_essay.strip():
            st.warning("Please provide your ID/Name and your essay before proceeding.")
        else:
            st.session_state.student_name = student_name
            st.session_state.original_essay = original_essay
            
            with st.spinner("Analyzing essay and generating feedback..."):
                prompt = f"""
                Act as an expert writing tutor. Analyze the following opinion essay. 
                Provide personalized feedback and a polished rewrite of the essay[cite: 1].
                
                Original Essay:
                {original_essay}
                """
                response = model.generate_content(prompt)
                st.session_state.ai_feedback_response = response.text
                st.session_state.step = 2
                st.rerun()

# ==========================================
# STEP 2: REVIEW FEEDBACK & ANSWER QUESTIONS
# ==========================================
elif st.session_state.step == 2:
    st.header("Step 2: Review Feedback & Answer Questions")
    st.markdown("Read the feedback carefully, compare the rewrite with your original writing, and answer the following questions[cite: 1]:")
    
    with st.expander("View AI Feedback & Rewrite[cite: 1]", expanded=True):
        st.markdown(st.session_state.ai_feedback_response)

    st.markdown("---")
    
    with st.form("questions_form"):
        st.subheader("Question 1[cite: 1]")
        q1_yn = st.radio("Does the AI's suggestion make your writing clearer and stronger[cite: 1]?", ["Yes[cite: 1]", "No[cite: 1]"])
        
        st.markdown("**Why? Choose all applicable[cite: 1]:**")
        q1_grammar = st.checkbox("1. grammar (simpler, more advanced)[cite: 1]")
        q1_vocab = st.checkbox("2. vocabulary (simpler, more advanced)[cite: 1]")
        q1_attitude = st.checkbox("3. attitude (relevant/ irrelevant)[cite: 1]")
        q1_ideas = st.checkbox("4. ideas (similar to mine/ different from mine)[cite: 1]")
        q1_org = st.checkbox("5. organization (improved/ the same/ less improved)[cite: 1]")
        q1_spell = st.checkbox("6. spelling and punctuation (improved/ the same)[cite: 1]")

        st.subheader("Question 2[cite: 1]")
        q2 = st.text_area("Which of the AI suggestions would you keep? Explain your decision[cite: 1]:")

        st.subheader("Question 3[cite: 1]")
        q3 = st.text_area("Which of the AI suggestions would you modify (change)? Explain your decision[cite: 1]:")

        st.subheader("Question 4[cite: 1]")
        q4 = st.text_area("What changes to your writing will you make based on the AI's feedback[cite: 1]?")

        st.subheader("Question 5[cite: 1]")
        q5 = st.text_area("Does the AI feedback keep your ideas/ attitudes the way you did or did it refine them[cite: 1]?")

        submitted_q = st.form_submit_button("Next: Final Revision")
        if submitted_q:
            st.session_state.q1 = f"{q1_yn} | Grammar:{q1_grammar}, Vocab:{q1_vocab}, Attitude:{q1_attitude}, Ideas:{q1_ideas}, Org:{q1_org}, Spelling:{q1_spell}"
            st.session_state.q2 = q2
            st.session_state.q3 = q3
            st.session_state.q4 = q4
            st.session_state.q5 = q5
            st.session_state.step = 3
            st.rerun()

# ==========================================
# STEP 3: REVISE AND SUBMIT FINAL VERSION
# ==========================================
elif st.session_state.step == 3:
    st.header("Step 3: Revise and Submit Final Version")
    st.markdown("Now, take a moment to compare the AI rewrite with your original draft. Decide what to change/adapt/add/remove/keep, revise and submit the final version[cite: 1].")
    
    revised_essay = st.text_area("Upload/Paste the revised essay here[cite: 1]:")
    
    st.markdown("### Final Feedback on Experience")
    experience_rating = st.slider("From 1 to 5 when 1 is the worst and 5 is the best, my experience was[cite: 1]:", 1, 5, 3)
    experience_comment = st.text_area("If you like to say why, you are most welcome to do so[cite: 1]:")

    if st.button("Submit Final Version"):
        if not revised_essay.strip():
            st.warning("Please provide your revised essay before final submission.")
        else:
            with st.spinner("Saving your responses to the research database..."):
                # Compile data row
                row_data = [
                    st.session_state.get("student_name", ""),
                    st.session_state.get("original_essay", ""),
                    st.session_state.get("ai_feedback_response", ""),
                    st.session_state.get("q1", ""),
                    st.session_state.get("q2", ""),
                    st.session_state.get("q3", ""),
                    st.session_state.get("q4", ""),
                    st.session_state.get("q5", ""),
                    revised_essay,
                    str(experience_rating),
                    experience_comment
                ]
                
                # Append row to Google Sheet
                sheet.append_row(row_data)
                
            st.success("Thank you so much! Your submission has been successfully recorded[cite: 1].")
            st.balloons()
            # Reset state optionally
            if st.button("Start New Session"):
                st.session_state.clear()
                st.rerun()
