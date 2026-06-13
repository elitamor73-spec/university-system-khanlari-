
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

students_db = []
ADMIN_PASSWORD = "1111"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/add-student", response_class=HTMLResponse)
def add_student_page(request: Request, message: str = ""):
    return templates.TemplateResponse("add_student.html", {"request": request, "message": message})

@app.post("/add-student")
def add_student(firstname: str = Form(...), lastname: str = Form(...), national_id: str = Form(...), password: str = Form(...)):
    for s in students_db:
        if s["national_id"] == national_id:
            return RedirectResponse(url="/add-student?message=این کد ملی قبلاً ثبت شده است", status_code=303)
    students_db.append({
        "id": len(students_db)+1,
        "firstname": firstname,
        "lastname": lastname,
        "national_id": national_id,
        "password": password
    })
    return RedirectResponse(url="/add-student?message=دانشجو با موفقیت اضافه شد", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, message: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.post("/login")
def login(national_id: str = Form(...), password: str = Form(...)):
    for s in students_db:
        if s["national_id"] == national_id and s["password"] == password:
            return RedirectResponse(url="/login?message=ورود موفق بود", status_code=303)
    return RedirectResponse(url="/login?message=شما عضو نیستید", status_code=303)

@app.get("/students", response_class=HTMLResponse)
def students_list(request: Request):
    return templates.TemplateResponse("students.html", {"request": request, "students": students_db})

@app.get("/admin-delete", response_class=HTMLResponse)
def admin_page(request: Request, message: str = ""):
    return templates.TemplateResponse("admin.html", {"request": request, "students": students_db, "message": message})

@app.post("/admin-login")
def admin_login(password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        return RedirectResponse(url="/admin-delete?message=authorized", status_code=303)
    return RedirectResponse(url="/admin-delete?message=رمز اشتباه است", status_code=303)

@app.get("/delete/{student_id}")
def delete_student(student_id: int):
    global students_db
    students_db = [s for s in students_db if s["id"] != student_id]
    return RedirectResponse(url="/admin-delete?message=دانشجو حذف شد", status_code=303)
