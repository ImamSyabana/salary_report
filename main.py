# main.py
from fastapi import FastAPI
# This is the crucial part for connecting to your frontend
from fastapi.middleware.cors import CORSMiddleware 

from fastapi.staticfiles import StaticFiles  # <-- IMPORT THIS
from fastapi.responses import FileResponse

from pathlib import Path

from fastapi import File, UploadFile
from fastapi.responses import RedirectResponse
import shutil

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

# --- NEW FILE UPLOAD ENDPOINT ---
#
# This MUST come BEFORE your page routes
#
@app.post("/upload/cikarang")
async def upload_cikarang_file(file: UploadFile = File(...)):
    
    # This is where you decide what to do with the file.
    # Let's save it to a folder named 'uploads'
    
    # (Make sure you create an 'uploads' folder in your project)
    # Note: On Vercel, this is temporary. For permanent storage,
    # you'd upload to a service like Amazon S3 or Google Cloud Storage.
    
    upload_folder = BASE_DIR / "uploads"
    upload_folder.mkdir(exist_ok=True) # Create the folder if it doesn't exist
    
    file_path = upload_folder / file.filename
    
    try:
        # Save the file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"Successfully uploaded file: {file.filename}")
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return {"message": f"There was an error: {e}"}
        
    finally:
        await file.close() # Always close the file
    
    # --- IMPORTANT ---
    # After saving, send the user back to the Cikarang page
    # This is much cleaner than showing them a JSON response.
    return RedirectResponse(url="/cikarang", status_code=303)

# --- SERVE FRONTEND ---

# 2. A "catch-all" endpoint for the root
# This tells FastAPI to serve 'index.html' for the root URL
@app.get("/")
async def serve_home():
    return FileResponse(BASE_DIR / "static" / "index.html")

# This route serves your ABOUT page
@app.get("/cikarang")
async def serve_about():
    # FileResponse sends back an HTML file
    return FileResponse(BASE_DIR / "static" / "cikarang.html")