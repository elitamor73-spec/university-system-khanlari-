import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI()

# مسیر templates (سازگار با پلتفرم Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# تنظیمات دیتابیس
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# مدل دانشجو
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    student_id = Column(String, unique=True, nullable=False)
    major = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# تابع اتصال به دیتابیس
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------
# ۱. صفحه اصلی
# -----------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )

# -----------------------
# ۲. صفحه ورود (login.html)
# -----------------------
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

# -----------------------
# ۳. بررسی عملیات ورود
# -----------------------
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        return RedirectResponse(url="/admin", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

# -----------------------
# ۴. پنل مدیریت
# -----------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={}
    )

# -----------------------
# ۵. افزودن دانشجو
# -----------------------
@app.post("/add_student")
async def add_student(
    name: str = Form(...),
    student_id: str = Form(...),
    major: str = Form(...),
    db: Session = Depends(get_db)
):
    new_student = Student(name=name, student_id=student_id, major=major)
    db.add(new_student)
    db.commit()
    return RedirectResponse(url="/students", status_code=303)

# -----------------------
# ۶. مشاهده لیست دانشجویان
# -----------------------
@app.get("/students", response_class=HTMLResponse)
async def view_students(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={"students": students}
    )

# -----------------------
# ۷. صفحه مدیریت حذف
# -----------------------
@app.get("/delete_students", response_class=HTMLResponse)
async def delete_students_page(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse(
        request=request,
        name="delete_students.html",
        context={"students": students}
    )

# -----------------------
# ۸. عملیات حذف دانشجو
# -----------------------
@app.get("/delete/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return RedirectResponse(url="/delete_students", status_code=303)
    
