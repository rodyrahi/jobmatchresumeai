import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

def generate_ats_friendly_resume(resume_text, jd_text , reference_resume=os.path.join("static", "reference_resumes", "reference_resume.tex"), use_reference=True):
    # Set up your Gemini API key
    # use_reference = True
    # Ensure the GEMINI_API_KEY is set in the environment
    api_key = os.getenv("GEMINI_API_KEY")  # Get API key from environment variable

    # Define the prompt for Gemini

    with open(reference_resume, "r", encoding="utf-8") as ref_file:
        reference_format = ref_file.read()

    
    if use_reference:
        
        prompt = f"""
        Given the following job description (jd_text) and resume (resume_text), create an ATS-friendly resume in LaTeX format. avoid code errors and ensure the output is a valid LaTeX document.
        Ensure the formatting is optimized for ATS systems, aligns with the job description, and matches the formatting style of the provided reference LaTeX file and try to fill one page. 
        Provide the output as a JSON key named "latex" with the LaTeX code as its value. Ensure that all sentences in the output are complete and grammatically correct.

         Instructions:
            - margin should be 0.5 inch on all sides.
        
        
        Reference LaTeX Format:
        {reference_format}

        Job Description:
        {jd_text}

        Resume:
        {resume_text}

        Output the resume in LaTeX format:
        """
    else:
        prompt = f"""
            You are a professional resume writer and LaTeX expert. Given the following job description (`jd_text`) and my current resume (`resume_text`), generate a one-page, ATS-optimized resume in LaTeX format.

            Instructions:
            - Format the resume using clean, minimal LaTeX styling, suitable for ATS parsing.
            - add horizontal lines below sections headings only. 
            - make sure all links are present in the resume.
            - Reduce skills elobration if it exceeds one page.
            - Write dates and locations on the right side of each section.
            - margin should be 0.5 inch on all sides.
            - also keep spacing very minimal between sections.
            - Tailor the content to align closely with the job description, incorporating relevant keywords and skills.
            - Ensure the document is syntactically correct LaTeX with no compilation errors.
            - Optimize the layout for clarity and impact, using clear sections like Education, Experience, Skills, and Projects.
            - Avoid using icons, graphics, or non-standard fonts that might disrupt ATS readability.
            - Use bullet points for accomplishments and quantifiable results wherever applicable.
            - Output only the LaTeX code as a JSON object in the format: -- "latex": "PASTE_LATEX_HERE" 

            Here are the inputs:

            Job Description:
            {jd_text}

            Resume:
            {resume_text}

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