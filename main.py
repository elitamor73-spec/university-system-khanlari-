import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI()

# تنظیم مسیر تمپلیت‌ها
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# دیتابیس
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    student_id = Column(String)
    major = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# مسیرها
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin_login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin_login")
async def admin_login(password: str = Form(...)):
    if password == "1234":
        return RedirectResponse(url="/delete_students", status_code=303)
    return RedirectResponse(url="/admin_login", status_code=303)

@app.get("/students", response_class=HTMLResponse)
async def list_students(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

@app.get("/delete_students", response_class=HTMLResponse)
async def delete_students_page(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse("delete_students.html", {"request": request, "students": students})

@app.get("/delete/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return RedirectResponse(url="/delete_students", status_code=303)
    
