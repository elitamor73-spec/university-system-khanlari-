import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    student_id = Column(String, unique=True, nullable=False)
    major = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# صفحه اصلی
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ورود دانشجو
@app.get("/login", response_class=HTMLResponse)
async def student_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def student_login(username: str = Form(...), password: str = Form(...)):
    if username == "student" and password == "1234":
        return RedirectResponse(url="/students", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

# ورود ادمین (فقط با رمز عبور)
@app.get("/admin_login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin_login")
async def admin_login(password: str = Form(...)):
    if password == "1234":  # رمز عبور ادمین
        return RedirectResponse(url="/delete_students", status_code=303)
    return RedirectResponse(url="/admin_login", status_code=303)

# لیست دانشجویان
@app.get("/students", response_class=HTMLResponse)
async def view_students(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

# صفحه حذف دانشجویان
@app.get("/delete_students", response_class=HTMLResponse)
async def delete_page(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse("delete_students.html", {"request": request, "students": students})

# عملیات حذف
@app.get("/delete/{student_id}")
async def delete_action(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return RedirectResponse(url="/delete_students", status_code=303)
    
