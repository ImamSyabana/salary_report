# main.py
from fastapi import FastAPI
# This is the crucial part for connecting to your frontend
from fastapi.middleware.cors import CORSMiddleware 

from fastapi.staticfiles import StaticFiles  # <-- IMPORT THIS
from fastapi.responses import FileResponse

from pathlib import Path

app = FastAPI()

# --- Define the base directory ---
# This creates a reliable, absolute path to the 'static' folder
# no matter where Vercel runs the code.
BASE_DIR = Path(__file__).resolve().parent

# --- THIS IS THE CRITICAL PART ---
# Set up CORS to allow your frontend to make requests
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
     # Add the URL your frontend is running on
    "*",# You can also use "*" to allow all origins, but it's less secure
    # "http://localhost:5500" is a common one for live servers

    # --- ADD YOUR VERCEL URLS ---
    "https://salary-report.vercel.app/", 
    # You can also add Vercel's preview URLs
    # "https://*.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Which origins are allowed
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
# -----------------------------------

@app.get("/api/data")
def get_data():
    # This is the data your frontend will receive
    return {"message": "Hello from the FastAPI backend!"}


# --- SERVE FRONTEND ---
# This new code serves your static files (HTML, CSS, JS)

# 1. Mount the 'static' directory
# This tells FastAPI that any URL starting with /
# should look for files in the 'static' directory
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 2. A "catch-all" endpoint for the root
# This tells FastAPI to serve 'index.html' for the root URL
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')