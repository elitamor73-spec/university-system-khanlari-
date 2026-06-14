    from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def home():
    return HTMLResponse(content="<h1>Server is Running!</h1><p>سلام! اگر این صفحه را میبینید یعنی سرور رندر سالم است.</p>")
    
