import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2 as pdf
import os
import json

# Load environment variables
load_dotenv()

# Configure the Google Generative AI client
genai.configure(api_key=api_key=os.getenv('GOOGLE_API_KEY'))

# Streamlit UI elements
st.title("ATS System")
st.header("Application Tracking System")

# Function to get Google Gemini response
def google_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(input_text)
    # Extract the relevant part of the response
    try:
        response_text = response.candidates[0].content.parts[0].text
        return response_text
    except (IndexError, AttributeError):
        return "Error in extracting the response content"

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to convert JSON response to markdown format
def json_to_markdown(response_text):
    try:
        # Extract JSON part from response text
        json_start_index = response_text.find('{')
        json_end_index = response_text.rfind('}') + 1
        json_str = response_text[json_start_index:json_end_index]
        response_json = json.loads(json_str)

        # Convert JSON to markdown
        markdown_str = (
            f"**JD Match:** {response_json['JD Match']}\n\n"
            f"**Missing Keywords:** {', '.join(response_json['MissingKeywords'])}\n\n"
            f"**Profile Summary:** {response_json['Profile Summary']}\n"
        )
        return markdown_str
    except (json.JSONDecodeError, KeyError) as e:
        return f"Error in decoding the response JSON: {str(e)}"

# Input prompt template
input_prompt_template = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analytics,
big data engineering, Data Science, and ML Engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide
the best assistance for improving the resumes. Assign the percentage Matching based
on JD and the missing keywords with high accuracy.
Resume: {resume_text}
Description: {jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Job description input
jd = st.text_area("Give the Job Description in the below text area")

# Resume file upload
uploaded_file = st.file_uploader("Upload the Resume file here: ", type="pdf", help="Please upload the PDF")

# Submit button
submit = st.button("Submit")

# Handle form submission
if submit:
    if uploaded_file is not None and jd:
        resume_text = input_pdf_text(uploaded_file)
        
        # Construct the input prompt with the resume text and job description
        input_prompt = input_prompt_template.format(resume_text=resume_text, jd=jd)
        
        # Get the response from Google Gemini
        response_text = google_gemini_response(input_prompt)

        # Display the raw response for debugging purposes (can be removed later)
        st.text("Raw response:")
        st.text(response_text)
        
        # Convert the JSON response to markdown format
        markdown_response = json_to_markdown(response_text)
        
        # Display the response
        st.subheader("ATS Evaluation Result")
        st.markdown(markdown_response)
    else:
        st.error("Please provide both a job description and a resume file.")
