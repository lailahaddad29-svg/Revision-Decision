import streamlit as st
import google.generativeai as genai
import requests

# Configure Gemini API using Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")

# Helper function to call Gemini with instructions
def get_ai_response(original_essay):
    try:
        ai_prompt = f"""
        You are an English language writing assistant. Please review the following student essay draft:

        "{original_essay}"

        Provide your response in two clear parts:
        1. Feedback: Give brief, concise, readable feedback in bullet points. Start with positive points and move to points that need improvements. Do NOT mention coherence or cohesion.
        2. Rewrite: Provide a revised version of the essay that maintains a similar word count to the original draft.
        """
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(ai_prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI response: {e}"

# App Title
st.title("AI Writing Assistant")

# Step 1: Student Number and Essay Input
student_id = st.text_input("Student #: *")

upload_option = st.radio("Choose how to input your essay:", ["Paste text", "Upload file"])

original_essay = ""
if upload_option == "Paste text":
    original_essay = st.text_area("Upload/Copy your opinion essay here (between 50 and 200 words): *")
else:
    uploaded_file = st.file_uploader("Upload your essay document (TXT or DOCX) *: ", type=["txt", "docx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            original_essay = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            import docx
            doc = docx.Document(uploaded_file)
            original_essay = "\n".join([para.text for para in doc.paragraphs])

# Word count validation for original essay (50 - 200 words)
original_word_count = len(original_essay.split()) if original_essay else 0

# Button appears directly under the essay input section
if original_essay:
    if original_word_count < 50 or original_word_count > 200:
        st.warning(f"Your essay has {original_word_count} words. Please ensure it is between 50 and 200 words before generating feedback.")
    else:
        if st.button("Generate AI Feedback & Rewrite"):
            with st.spinner("Generating personalized feedback and rewrite..."):
                st.session_state["ai_output"] = get_ai_response(original_essay)

# Display AI Feedback & Rewrite if generated
if "ai_output" in st.session_state:
    st.markdown("### AI Feedback & Rewrite:")
    st.write(st.session_state["ai_output"])
    
    st.markdown("---")
    st.markdown("### Post-Evaluation Questions")
    
    # Question 1
    q1 = st.radio(
        "Question 1: Does the AI's suggestion make your writing clearer and stronger? *", 
        ["Yes", "No", "Maybe"]
    )
    
    st.markdown("**Why? Choose all applicable and specify:**")
    
    # Clickable choices for sub-options
    q1_1_check = st.checkbox("1. grammar")
    q1_1_choice = st.radio("Grammar direction:", ["simpler", "more advanced"], horizontal=True) if q1_1_check else None
    
    q1_2_check = st.checkbox("2. vocabulary")
    q1_2_choice = st.radio("Vocabulary direction:", ["simpler", "more advanced"], horizontal=True) if q1_2_check else None
    
    q1_3_check = st.checkbox("3. attitude")
    q1_3_choice = st.radio("Attitude type:", ["similar to mine", "different from mine"], horizontal=True) if q1_3_check else None
    
    q1_4_check = st.checkbox("4. ideas")
    q1_4_choice = st.radio("Ideas comparison:", ["similar to mine", "different from mine"], horizontal=True) if q1_4_check else None
    
    q1_5_check = st.checkbox("5. organization")
    q1_5_choice = st.radio("Organization effect:", ["improved", "the same", "less improved"], horizontal=True) if q1_5_check else None
    
    q1_6_check = st.checkbox("6. spelling and punctuation")
    q1_6_choice = st.radio("Spelling and punctuation effect:", ["improved", "the same"], horizontal=True) if q1_6_check else None
    
    # Question 2
    q2 = st.text_area("Question 2: Which of the AI suggestions would you keep (from either the feedback or the rewrite)? * (You can copy-paste from the feedback. You may answer in your first language—Arabic or Hebrew—if you prefer). Explain your decision if you'd like.")
    
    # Question 3
    q3 = st.text_area("Question 3: Which of the suggestions would you reject (from either the feedback or the rewrite)? * (You can copy-paste from the feedback. You may answer in your first language—Arabic or Hebrew—if you prefer). Explain your decision if you'd like.")
    
    # Question 4
    q4 = st.text_area("Question 4: What changes to your writing will you make based on the AI's feedback? * (You can copy-paste from the feedback. You may answer in your first language—Arabic or Hebrew—if you prefer).")
    
    # Question 5
    q5 = st.text_area("Question 5: Does the AI feedback keep your ideas/ attitudes the way you did or did it refine them? * (You can copy-paste from the feedback. You may answer in your first language—Arabic or Hebrew—if you prefer).")
    
    st.markdown("---")
    st.markdown("Now, take a moment to reread the feedback, compare the AI rewrite with your original draft. Decide what to change, adapt, add, remove, or keep. Then revise your essay and submit your final version.")
    
    # Final revised essay text area with updated word count constraint (50 - 200 words)
    revised_essay = st.text_area("Write/paste your revised essay here (between 50 and 200 words): *")
    revised_word_count = len(revised_essay.split()) if revised_essay else 0
    
    if revised_essay and (revised_word_count < 50 or revised_word_count > 200):
        st.warning(f"Your revised essay has {revised_word_count} words. Please ensure it is between 50 and 200 words.")

    st.markdown("---")
    experience_rating = st.slider("From 1 to 5 when 1 is the worst and 5 is the best, my experience was:", 1, 5, 3)
    experience_comment = st.text_input("If you’d like to say why, you’re most welcome to do so (you may use Arabic or Hebrew); otherwise, feel free to submit (Optional):")
    
    if st.button("Submit Final Version"):
        # Validate mandatory fields
        missing_fields = []
        if not student_id.strip():
            missing_fields.append("Student #")
        if not original_essay.strip():
            missing_fields.append("Original Essay")
        elif original_word_count < 50 or original_word_count > 200:
            missing_fields.append("Original Essay word count (must be 50-200 words)")
        if "ai_output" not in st.session_state or not st.session_state["ai_output"].strip():
            missing_fields.append("AI Feedback (Please click 'Generate AI Feedback & Rewrite')")
        if not q2.strip():
            missing_fields.append("Question 2")
        if not q3.strip():
            missing_fields.append("Question 3")
        if not q4.strip():
            missing_fields.append("Question 4")
        if not q5.strip():
            missing_fields.append("Question 5")
        if not revised_essay.strip():
            missing_fields.append("Revised Essay")
        elif revised_word_count < 50 or revised_word_count > 200:
            missing_fields.append("Revised Essay word count (must be 50-200 words)")

        if missing_fields:
            st.error(f"Please complete the following required fields before submitting: {', '.join(missing_fields)}")
        else:
            formspree_url = "https://formspree.io/f/mnpnokpq"
            
            payload = {
                "Student_ID": student_id,
                "Original_Essay": original_essay,
                "AI_Output": st.session_state["ai_output"],
                "Q1_Clearer_Stronger": q1,
                "Q1_Grammar": f"{q1_1_check} ({q1_1_choice})",
                "Q1_Vocabulary": f"{q1_2_check} ({q1_2_choice})",
                "Q1_Attitude": f"{q1_3_check} ({q1_3_choice})",
                "Q1_Ideas": f"{q1_4_check} ({q1_4_choice})",
                "Q1_Organization": f"{q1_5_check} ({q1_5_choice})",
                "Q1_Spelling_Punctuation": f"{q1_6_check} ({q1_6_choice})",
                "Q2_Keep": q2,
                "Q3_Reject": q3,
                "Q4_Changes": q4,
                "Q5_Ideas_Refined": q5,
                "Revised_Essay": revised_essay,
                "Experience_Rating": experience_rating,
                "Experience_Comment": experience_comment
            }
            
            try:
                response = requests.post(formspree_url, data=payload)
                if response.status_code == 200:
                    st.success("Thank you so much!")
                    st.balloons()
                else:
                    st.error("There was an error submitting your response. Please try again.")
            except Exception as e:
                st.error(f"Connection error: {e}")
