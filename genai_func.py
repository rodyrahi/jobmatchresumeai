import os
from google import genai

def generate_ats_friendly_resume(resume_text, jd_text , reference_resume=os.path.join("static", "reference_resumes", "reference_resume.tex")):
    # Set up your Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")  # Get API key from environment variable

    # Define the prompt for Gemini

    with open(reference_resume, "r", encoding="utf-8") as ref_file:
        reference_format = ref_file.read()

    prompt = f"""
    Given the following job description (jd_text) and resume (resume_text), create an ATS-friendly resume in LaTeX format. avoid code errors and ensure the output is a valid LaTeX document.
    Ensure the formatting is optimized for ATS systems, aligns with the job description, and matches the formatting style of the provided reference LaTeX file and try to fill one page. 
    Provide the output as a JSON key named "latex" with the LaTeX code as its value. Ensure that all sentences in the output are complete and grammatically correct.

    Reference LaTeX Format:
    {reference_format}

    Job Description:
    {jd_text}

    Resume:
    {resume_text}

    Output the resume in LaTeX format:
    """

    client = genai.Client(api_key=api_key)

    # Send the request to Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        }
    )

    response_text = response.text

    response_dict = eval(response_text)  # Convert the string to a dictionary
    response_latex = response_dict.get("latex")  # Extract the LaTeX code
    return response_latex




# make it into a function where input is resume_text and jd_text and output is 