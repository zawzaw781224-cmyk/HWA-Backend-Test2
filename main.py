from fastapi import FastAPI , Form , Request
from fastapi.responses import HTMLResponse , RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db,init_db
import sqlite3
from auth import hash_context , verify_password
import uuid
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates  = Jinja2Templates(directory="templates")
sessions = {}
init_db()

app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/",response_class = HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request,
        "login.html",
        {"request" : request}
        )

@app.get("/signup",response_class =HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request,
        "signup.html",
        {"request" : request}
        )

@app.post("/signup")
def signup(request:Request,username:str = Form(...),
           password:str =Form(...)):
    conn = get_db()
    cursor = conn.cursor()
       
    hashed = hash_context(password)
    try: 
        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?,?)",
            (username,hashed)
        )
        conn.commit()
        return RedirectResponse(url="/",status_code = 302)
    except sqlite3.IntegrityError:
        return templates.TemplateResponse(request,"signup.html",{"request":request,"error":"username already exists"})
    finally:
        conn.close()

@app.post("/login")
def login(request:Request,username:str = Form(...),password:str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password FROM users WHERE username = ?", 
        (username,)
    )
    user = cursor.fetchone()
    if not user:
        return templates.TemplateResponse(request,"login.html",{"request":request,"error":"username not found"})
    stored_password = user[0]
    if not verify_password(password,stored_password):
        return templates.TemplateResponse(request,"login.html",
                                      {"request":request,"error":"incorrect password"})
        
    session_id = str(uuid.uuid4())
    sessions[session_id] = username
    response = RedirectResponse(url = "/dashboard",status_code = 302)
    response.set_cookie(key = "session_id",value = session_id, httponly = True)
    return response

@app.get("/dashboard",response_class = HTMLResponse)
def dashboard(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url= "/")
    username = sessions[session_id]
    return templates.TemplateResponse(request,"dashboard.html",
                                      {"request":request,"username":username})

@app.get("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    response = RedirectResponse(url= "/")
    response.delete_cookie("session_id")
    return response
@app.get("/activeUsers")
def active_users():
    return {
        "count":len(sessions),
        "users":list(sessions.values())
    }