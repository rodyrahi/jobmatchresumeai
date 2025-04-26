from flask import Flask, request, render_template, jsonify
from PyPDF2 import PdfReader
import subprocess
import os
import tempfile
import time

app = Flask(__name__)

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    resume_text = ""
    for page in reader.pages:
        resume_text += page.extract_text()
    return resume_text

# Function to generate LaTeX resume
def generate_latex_resume(jd_text, resume_text, reference_format):
    prompt = f"""
    Given the following job description (jd_text) and resume (resume_text), create an ATS-friendly resume in LaTeX format. Avoid code errors and ensure the output is a valid LaTeX document.
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
    # Simulate API call to Gemini (replace with actual API call)
    response = {"latex": "Generated LaTeX code here"}  # Replace with actual API response
    return response.get("latex")

# Function to compile LaTeX to PDF
def try_latex_commands(latex_code, output_filename="output.pdf", timeout_seconds=30):
    commands = ["pdflatex", "xelatex", "lualatex"]
    for command in commands:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_path = os.path.join(temp_dir, "temp.tex")
                pdf_path = os.path.join(temp_dir, "temp.pdf")
                with open(tex_path, "w", encoding="utf-8") as tex_file:
                    tex_file.write(latex_code)
                result = subprocess.run(
                    [command, "-interaction=nonstopmode", "-output-directory", temp_dir, tex_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds
                )
                if os.path.exists(pdf_path):
                    os.rename(pdf_path, output_filename)
                    return True
        except Exception as e:
            print(f"Error with {command}: {e}")
    return False

# Load the job description and reference LaTeX format
jd_text = """
Job Title
Data Scientist-Machine Learning
...
"""
with open("reference_resume.tex", "r", encoding="utf-8") as ref_file:
    reference_format = ref_file.read()

@app.route('/')
def index():
    return render_template('index.html')  # Create an HTML form for file upload

@app.route('/generate', methods=['POST'])
def generate():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    pdf_path = os.path.join(tempfile.gettempdir(), file.filename)
    file.save(pdf_path)

    # Extract text from the uploaded PDF
    resume_text = extract_text_from_pdf(pdf_path)

    # Generate LaTeX resume
    latex_code = generate_latex_resume(jd_text, resume_text, reference_format)

    # Compile LaTeX to PDF
    output_pdf = os.path.join(tempfile.gettempdir(), "output.pdf")
    if try_latex_commands(latex_code, output_pdf):
        return jsonify({"message": "PDF generated successfully", "pdf_path": output_pdf})
    else:
        return jsonify({"error": "Failed to generate PDF"}), 500

if __name__ == '__main__':
    app.run(debug=True)
