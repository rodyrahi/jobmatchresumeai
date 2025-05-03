from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import BackgroundTasks
import shutil

from process_pdf import extract_text_from_pdf , try_latex_commands
from genai_func import generate_ats_friendly_resume 

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("new_design_bs4.html", {"request": request})






@app.post("/send_resume")
async def send_resume(request: Request):
    form_data = await request.form()
    file = form_data["resumeFile"]
    resume_text = extract_text_from_pdf(file.file)
    response_letex = generate_ats_friendly_resume(resume_text , form_data["jobDescription"])
    
    pdf_path, folder_path = try_latex_commands(response_letex)
    folder_path = str(folder_path).replace("\\", "/")   
    
    return templates.TemplateResponse("show_latex.html", { "request": request ,"pdf_path": pdf_path , "folder_path": folder_path})





@app.get("/test", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("show_latex.html", {"request": request})

import os


@app.post("/delete_folder")
async def delete_folder(request: Request):
    form_data = await request.form()
    folder = form_data["name"].replace("resume.pdf", "")
    folder = folder.strip("/")  # Remove leading/trailing slashes
    folder_path = os.path.abspath(folder)  # Get absolute path
    
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=False)
            return {"message": f"Successfully deleted folder: {folder_path}"}
        else:
            return {"message": f"Folder not found: {folder_path}"}
    except Exception as e:
        return {"message": f"Error deleting folder: {str(e)}"}




@app.post("/create_resume")
async def create_resume(request: Request):
    form_data = await request.form()
    form_dict = dict(form_data)
    
    response_letex = generate_ats_friendly_resume(form_data, form_data["jobDescription"])
    
    
    pdf_path, folder_path = try_latex_commands(response_letex)
    folder_path = str(folder_path).replace("\\", "/")   
    
    return templates.TemplateResponse("show_latex.html", { "request": request ,"pdf_path": pdf_path , "folder_path": folder_path})

import re


@app.post("/extract_linkedin_jd")
async def extract_linkedin_jd(request: Request):
    try:
        form_data = await request.form()
        linkedin_url = form_data["linkedin_url"]
        
        
    
        match = re.search(r'(https?://(www\.)?linkedin\.com/[^\s]+)', linkedin_url)
        linkedin_url = match.group(1) if match else None

        
        # Import necessary libraries
        import requests
        from bs4 import BeautifulSoup
        
        # Send GET request to LinkedIn URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(linkedin_url, headers=headers)
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find job description section
        # Note: LinkedIn's structure might change, so selectors might need updates
        job_description = soup.find('div', {'class': 'description__text'})
        
        if job_description:
            # Clean and extract text
            jd_text = job_description.get_text(strip=True)
            print(jd_text)
            return jd_text
        else:
            pass
            
    except Exception as e:
        pass





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)    

    
    
    
    
    