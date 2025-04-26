from PyPDF2 import PdfReader
import subprocess
import os
import tempfile
import time


def extract_text_from_pdf(pdf_file):

    reader = PdfReader(pdf_file)

    # Extract text from each page
    resume_text = ""
    for page in reader.pages:
        resume_text += page.extract_text()

    return resume_text


def try_latex_commands(latex_code, timeout_seconds=30):
    """
    Try multiple LaTeX commands to generate a PDF from LaTeX code and save it to the /static directory.
    
    Args:
        latex_code (str): The LaTeX code to convert.
        timeout_seconds (int): Maximum time to wait for each command.
    Returns:
        bytes: PDF content if successful, None if all commands fail.
    """
    commands = ["pdflatex", "pdtex", "xelatex", "lualatex"]
    static_dir = os.path.join(os.getcwd(), "static")  # Ensures absolute path
    os.makedirs(static_dir, exist_ok=True)  # Make sure static/ exists

    tex_path = os.path.join(static_dir, "temp.tex")
    pdf_path = os.path.join(static_dir, "temp.pdf")

    start_time = time.time()

    for command in commands:
        try:
            print(f"Trying command: {command}")

            # Write LaTeX code to temp.tex
            with open(tex_path, "w", encoding="utf-8") as tex_file:
                tex_file.write(latex_code)

            # Run LaTeX compiler
            result = subprocess.run(
                [command, "-interaction=nonstopmode", "-output-directory", static_dir, tex_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds
            )

            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                elapsed_time = time.time() - start_time
                print(f"PDF successfully created using {command} in {elapsed_time:.2f} seconds")
                return pdf_content
            else:
                print(f"PDF was not created using {command}.")
                print(result.stderr)

        except subprocess.TimeoutExpired:
            print(f"Error: {command} timed out after {timeout_seconds} seconds.")
        except subprocess.CalledProcessError as e:
            print(f"Error running {command}: {e}")
        except Exception as e:
            print(f"Unexpected error with {command}: {str(e)}")

    print("All LaTeX commands failed.")
    return None
