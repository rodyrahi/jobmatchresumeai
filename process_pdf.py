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
    folder_name = f"{uuid.uuid4().int % 1000000:06d}"
    static_tmpdir = os.path.join("static" ,"tmp", folder_name)
    os.makedirs(static_tmpdir, exist_ok=True)

    tex_path = os.path.join(static_tmpdir, "resume.tex")
    pdf_path = os.path.join(static_tmpdir, "resume.pdf")

    # Write LaTeX code to file and ensure it's flushed to disk
    with open(tex_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(latex_code)
        tex_file.flush()
        os.fsync(tex_file.fileno())  # Ensure file is written to disk

    if not Path(tex_path).exists():
        raise FileNotFoundError(f"TeX file not found at {tex_path}")

    print(f"Created .tex file at: {tex_path}")
    print(f"Temporary directory: {static_tmpdir}")

    for command in commands:
        try:
            # Small delay to ensure file system is ready
            time.sleep(0.1)
            result = subprocess.run(
                [command, "-interaction=nonstopmode", "-output-directory", static_tmpdir, tex_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds
            )
            print(f"Command {command} output: {result.stdout}")
            print(f"Command {command} errors: {result.stderr}")

            if Path(pdf_path).exists():
                print(f"PDF generated at: {pdf_path}")
                return pdf_path, static_tmpdir
            else:
                print(f"PDF not found after running {command}")

        except subprocess.TimeoutExpired:
            print(f"Timeout running {command}")
        except Exception as e:
            print(f"Error using {command}: {e}")

    raise RuntimeError("All LaTeX commands failed. Cannot compile PDF.")