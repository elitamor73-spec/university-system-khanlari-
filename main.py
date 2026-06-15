import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

# مسیر templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# دیتابیس
SQLALCHEMY_DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    student_id = Column(String, unique=True)
    major = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# صفحه اصلی
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html", context={})

# صفحه ورود
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})

# بررسی ورود
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        return RedirectResponse(url="/admin", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

# پنل مدیریت
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html", context={})

# افزودن دانشجو
@app.post("/add_student")
async def add_student(name: str = Form(...), student_id: str = Form(...), major: str = Form(...), db: Session = Depends(get_db)):
    new_student = Student(name=name, student_id=student_id, major=major)
    db.add(new_student)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# مشاهده دانشجویان
@app.get("/students", response_class=HTMLResponse)
async def view_students(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse(request=request, name="students.html", context={"students": students})

# صفحه حذف دانشجویان
@app.get("/delete_students", response_class=HTMLResponse)
async def delete_students_page(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse(request=request, name="delete_students.html", context={"students": students})

# حذف دانشجو
@app.get("/delete/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return RedirectResponse(url="/delete_students", status_code=303)
    
