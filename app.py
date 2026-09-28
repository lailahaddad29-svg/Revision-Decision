import streamlit as st
import google.generativeai as genai

# Configure Gemini API using Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")

# Helper function to call Gemini with the updated instructions
def get_ai_response(original_essay):
    try:
        ai_prompt = f"""
        You are an English language writing assistant. Please review the following student essay draft:

        "{original_essay}"

        Provide your response in two clear parts:
        1. Feedback: Give brief, concise, readable feedback in bullet points. Start with positive points and move to points that need improvements. Do NOT mention coherence or cohesion.
        2. Rewrite: Provide a revised version of the essay that maintains a similar word count to the original draft.
        """
        model = genai.GenerativeModel("gemini-3.8-flash")
        response = model.generate_content(ai_prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI response: {e}"

# App Title
st.title("AI writing assistant")

# Step 1: Student Number and Essay Input (with File Upload option)
student_id = st.text_input("Student # / ID:")

upload_option = st.radio("Choose how to input your essay:", ["Paste text", "Upload file"])

original_essay = ""
if upload_option == "Paste text":
    original_essay = st.text_area("Upload/Copy your opinion essay here:")
else:
    uploaded_file = st.file_uploader("Upload your essay document (TXT or DOCX):", type=["txt", "docx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            original_essay = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            import docx
            doc = docx.Document(uploaded_file)
            original_essay = "\n".join([para.text for para in doc.paragraphs])

if student_id and original_essay:
    if st.button("Generate AI Feedback & Rewrite"):
        with st.spinner("Generating personalized feedback and rewrite..."):
            ai_output = get_ai_response(original_essay)
            st.session_state["ai_output"] = ai_output

# Display AI Feedback & Rewrite if generated
if "ai_output" in st.session_state:
    st.markdown("### AI Feedback & Rewrite:")
    st.write(st.session_state["ai_output"])
    
    st.markdown("---")
    st.markdown("### Post-Evaluation Questions")
    
    # Question 1 with Yes / No / Maybe
    q1 = st.radio(
        "Question 1: Does the AI's suggestion make your writing clearer and stronger?", 
        ["Select...", "Yes", "No", "Maybe"]
    )
    
    st.markdown("**Why? Choose all applicable and specify:**")
    
    # Clickable choices for sub-options
    q1_1_check = st.checkbox("1. grammar")
    q1_1_choice = st.radio("Grammar direction:", ["simpler", "more advanced"], horizontal=True) if q1_1_check else None
    
    q1_2_check = st.checkbox("2. vocabulary")
    q1_2_choice = st.radio("Vocabulary direction:", ["simpler", "more advanced"], horizontal=True) if q1_2_check else None
    
    q1_3_check = st.checkbox("3. attitude")
    q1_3_choice = st.radio("Attitude type:", ["relevant", "irrelevant"], horizontal=True) if q1_3_check else None
    
    q1_4_check = st.checkbox("4. ideas")
    q1_4_choice = st.radio("Ideas comparison:", ["similar to mine", "different from mine"], horizontal=True) if q1_4_check else None
    
    q1_5_check = st.checkbox("5. organization")
    q1_5_choice = st.radio("Organization effect:", ["improved", "the same", "less improved"], horizontal=True) if q1_5_check else None
    
    q1_6_check = st.checkbox("6. spelling and punctuation")
    q1_6_choice = st.radio("Spelling and punctuation effect:", ["improved", "the same"], horizontal=True) if q1_6_check else None
    
    # Question 2
    q2 = st.text_area("Question 2: Which of the AI suggestions would you keep? Explain your decision.")
    
    # Question 3
    q3 = st.text_area("Question 3: Which of the AI suggestions would you reject? Explain your decision.")
    
    # Question 4
    q4 = st.text_area("Question 4: What changes to your writing will you make based on the AI's feedback?")
    
    # Question 5
    q5 = st.text_area("Question 5: Does the AI feedback keep your ideas/ attitudes the way you did or did it refine them?")
    
    st.markdown("---")
    st.markdown("Now, take a moment to reread the feedback, compare the AI rewrite with your original draft. Decide what to change, adapt, add, remove, or keep. Then revise your essay and submit your final version.")
    
    # Final revised essay text area only (upload removed)
    revised_essay = st.text_area("Write/paste your revised essay here:")
    
    st.markdown("---")
    experience_rating = st.slider("From 1 to 5 when 1 is the worst and 5 is the best, my experience was:", 1, 5, 3)
    experience_comment = st.text_input("If you’d like to say why, you’re most welcome to do so; otherwise, feel free to submit:")
    
    if st.button("Submit Final Version"):
        st.success("Thank you so much!")
