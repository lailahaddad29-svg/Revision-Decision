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

# App Title (Without "& research study")
st.title("Who should make the final revision decision? Flowchart for the Chatbot")

# Step 1: Student Number and Essay Input
student_id = st.text_input("Student # / ID:")
original_essay = st.text_area("Upload/Copy your opinion essay here:")

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
    
    # Question 1
    q1 = st.radio(
        "Question 1: Does the AI's suggestion make your writing clearer and stronger?", 
        ["Select...", "Yes", "Key"] # Adjust as needed per flowchart
    )
    st.write("Why? Choose all applicable:")
    q1_1 = st.checkbox("1. grammar (simpler, more advanced)")
    q1_2 = st.checkbox("2. vocabulary (simpler, more advanced)")
    q1_3 = st.checkbox("3. attitude (relevant / irrelevant)")
    q1_4 = st.checkbox("4. ideas (similar to mine / different from mine)")
    q1_5 = st.checkbox("5. organization (improved / the same / less improved)")
    q1_6 = st.checkbox("6. spelling and punctuation (improved / the same)")
    
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
    
    revised_essay = st.text_area("Upload / paste your revised essay here:")
    
    st.markdown("---")
    experience_rating = st.slider("From 1 to 5 when 1 is the worst and 5 is the best, my experience was:", 1, 5, 3)
    experience_comment = st.text_input("If you’d like to say why, you’re most welcome to do so; otherwise, feel free to submit:")
    
    if st.button("Submit Final Version"):
        st.success("Thank you so much!")
