from PyPDF2 import PdfReader
import subprocess
import os
import tempfile
import time
from pathlib import Path
import uuid


def extract_text_from_pdf(pdf_file):

    reader = PdfReader(pdf_file)

    # Extract text from each page
    resume_text = ""
    for page in reader.pages:
        resume_text += page.extract_text()

    return resume_text


def try_latex_commands(latex_code, timeout_seconds=30):
    
    commands = ["pdflatex", "xelatex", "lualatex"]
    folder_name = f"{uuid.uuid4().int % 1000}"
    static_tmpdir = os.path.join(os.getcwd(), "static", "tmp", folder_name)  
    os.mkdir(path=static_tmpdir, exist_ok=True)
    tex_path = static_tmpdir / f"resume.tex"
    pdf_path = static_tmpdir / f"resume.pdf"

    tex_path.write_text(latex_code, encoding="utf-8")

    for command in commands:
        try:
            result = subprocess.run(
                [command, "-interaction=nonstopmode", "-output-directory", str(static_tmpdir), str(tex_path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds
            )
            if pdf_path.exists():
                print(pdf_path)
                # time.sleep(50)
                return pdf_path, static_tmpdir
            
        except Exception as e:
            print(f"Error using {command}: {e}")

    raise RuntimeError("All LaTeX commands failed. Cannot compile PDF.")