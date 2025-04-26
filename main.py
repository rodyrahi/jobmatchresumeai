from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from process_pdf import extract_text_from_pdf , try_latex_commands
from genai_func import generate_ats_friendly_resume 

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})






@app.post("/send_resume")
async def send_resume(request: Request):
    form_data = await request.form()
    file = form_data["resumeFile"]
    resume_text = extract_text_from_pdf(file.file)
    response_letex = generate_ats_friendly_resume(resume_text , form_data["jobDescription"])
    
    pdf_content = try_latex_commands(response_letex)
    # with open("static/resume.pdf", "wb") as f:
    #     f.write(pdf_content)    
    
    return templates.TemplateResponse("show_latex.html", { "request": request ,"pdf_content": "static/temp.pdf"})





@app.get("/test", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("show_latex.html", {"request": request})



@app.get("/delete_onload")
async def delete_temp_pdf():
    import os
    try:
        os.remove("static/temp.pdf")
        return {"message": "Temporary PDF deleted successfully"}
    except FileNotFoundError:
        return {"message": "No temporary PDF found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    
    
    
    
    