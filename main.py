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
    
    print(form_dict)
    return form_dict





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)    

    
    
    
    
    