import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AI Writing Assistant", page_icon="📝", layout="centered")

# Initialize Gemini API using Streamlit Secrets safely
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ GEMINI_API_KEY is missing from your Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# Helper function to call Gemini
def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-3.8-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI response: {e}"

# App UI Header
st.title("📝 AI Writing Assistant")
st.markdown("Please follow the steps below carefully.")

# Initialize Session State variables to manage the flow
if "step" not in st.session_state:
    st.session_state.step = 1
if "essay_text" not in st.session_state:
    st.session_state.essay_text = ""
if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = ""
if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""

# --- STEP 1: Upload & Initial AI Feedback ---
if st.session_state.step == 1:
    st.header("Step 1: Upload Your Opinion Essay")
    
    participant_id = st.text_input("Student #:", value=st.session_state.participant_id)
    
    upload_option = st.radio("How would you like to provide your essay?", ["Upload File (Txt/Docx)", "Copy & Paste Text"])
    
    essay_content = ""
    if upload_option == "Upload File (Txt/Docx)":
        uploaded_file = st.file_uploader("Upload/Copy your opinion essay here[cite: 10]:", type=["txt", "docx"])
        if uploaded_file is not None:
            try:
                essay_content = uploaded_file.read().decode("utf-8")
            except:
                essay_content = str(uploaded_file.read())
    else:
        essay_content = st.text_area("Upload/Copy your opinion essay here[cite: 10]:")
        
    if st.button("Generate AI Feedback & Rewrite"):
        if not participant_id.strip():
            st.warning("Please enter your Student # before proceeding.")
        elif not essay_content.strip():
            st.warning("Please provide your essay before generating feedback.")
        else:
            st.session_state.participant_id = participant_id
            st.session_state.essay_text = essay_content
            
            with st.spinner("The ChatGPT automatically gives personalized feedback and rewrites the essay[cite: 10]..."):
                prompt = f"""
                ai_prompt = f"""
ai_prompt = f"""
You are an English language writing assistant. Please review the following student essay draft:

"{original_essay}"

Provide your response in two clear parts:
1. Feedback: Give brief, concise feedback (2-3 short bullet points focusing on grammar, vocabulary, or mechanics). Do NOT mention coherence or cohesion.
2. Rewrite: Provide a revised version of the essay that maintains a similar word count to the original draft.
"""                
         Essay:
                {essay_content}
                """
                st.session_state.ai_feedback = get_ai_response(prompt)
                st.session_state.step = 2
                st.rerun()

# --- STEP 2: Review & Sequential Evaluation Questions (Q1 - Q5) ---
elif st.session_state.step == 2:
    st.header("Step 2: Evaluate AI Feedback & Rewrite")
    
    st.info("Read the feedback carefully, compare the rewrite with your original writing and answer the following questions[cite: 10]:")
    
    st.subheader("Your Original Essay:")
    st.write(st.session_state.essay_text)
    
    st.subheader("AI Feedback & Rewrite:")
    st.markdown(st.session_state.ai_feedback)
    
    st.markdown("---")
    st.subheader("Evaluation Questions")
    
    # Question 1
    q1_main = st.radio("Question 1: Does the AI's suggestion make your writing clearer and stronger[cite: 10]?", ["Yes", "No"])
    st.write("Why? Choose all applicable[cite: 10]:")
    q1_sub1 = st.text_input("1. grammar (simpler, more advanced)[cite: 10]")
    q1_sub2 = st.text_input("2. vocabulary (simpler, more advanced)[cite: 10]")
    q1_sub3 = st.text_input("3. attitude (relevant/ irrelevant)[cite: 10]")
    q1_sub4 = st.text_input("4. ideas (similar to mine/ different from mine)[cite: 10]")
    q1_sub5 = st.text_input("5. organization (improved/ the same/ less improved)[cite: 10]")
    q1_sub6 = st.text_input("6. spelling and punctuation (improved/ the same)[cite: 10]")
    
    # Question 2
    q2 = st.text_area("Question 2: Which of the AI suggestions would you keep? Explain your decision[cite: 10].")
    
    # Question 3
    q3 = st.text_area("Question 3: Which of the AI suggestions would you modify (change)? Explain your decision[cite: 10].")
    
    # Question 4
    q4 = st.text_area("Question 4: What changes to your writing will you make based on the AI's feedback[cite: 10]?")
    
    # Question 5
    q5 = st.text_area("Question 5: Does the AI feedback keep your ideas/ attitudes the way you did or did it refine them[cite: 10]?")
    
    if st.button("Proceed to Final Revision"):
        st.session_state.step = 3
        st.rerun()

# --- STEP 3: Final Revision & Experience Rating ---
elif st.session_state.step == 3:
    st.header("Step 3: Final Revision & Experience Rating")
    
    st.markdown("Now, take a moment to compare the AI rewrite with your original draft. Decide what to change, adapt, add, remove, or keep. Then revise your essay and submit your final version. Upload the revised essay[cite: 10]:")
    
    revised_essay = st.text_area("Box for the revised essay[cite: 10]:")
    
    st.markdown("---")
    experience_rating = st.slider("Last question about your experience with the chatbot: From 1 to 5 when 1 is the worst and 5 is the best, my experience was[cite: 10]:", 1, 5, 5)
    experience_comment = st.text_area("If you like to say why, you are most welcome to do so[cite: 10]:")
    
    if st.button("Submit Final Study Response"):
        if not revised_essay.strip():
            st.warning("Please provide your revised essay before submitting.")
        else:
            st.success("🎉 Thank you so much![cite: 10]. Your study response has been submitted successfully.")
            st.balloons()
            
            if st.button("Start New Participant Submission"):
                st.session_state.step = 1
                st.session_state.essay_text = ""
                st.session_state.ai_feedback = ""
                st.rerun()
