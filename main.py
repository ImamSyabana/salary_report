# main.py
from fastapi import FastAPI, Request
# This is the crucial part for connecting to your frontend
from fastapi.middleware.cors import CORSMiddleware 

from fastapi.staticfiles import StaticFiles  # <-- IMPORT THIS
from fastapi.responses import FileResponse

from pathlib import Path
import uuid

from fastapi import File, UploadFile
from fastapi.responses import RedirectResponse
import shutil

# import module python untuk read and check excel
import read_excel_ckr
import check_excel_ckr


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
    # You can also use "*" to allow all origins, but it's less secure
    # "http://localhost:5500" is a common one for live servers

    # --- ADD YOUR VERCEL URLS ---
    "https://salary-report.vercel.app", 
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

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# --- NEW FILE UPLOAD ENDPOINT. ---
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
    
    upload_folder = Path("/tmp")
    
    original_file_path = upload_folder / file.filename
    
    try:
        # Save the file to disk
        with open(original_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"Original file saved to: {original_file_path}")
        
        # memanggil fungsi untuk read (output: df_office, df_driver)
        df_office, df_driver = read_excel_ckr.read_excel(original_file_path)

        # memanggil fungsi untuk check dan generate JSON
        final_refrence_json_string = check_excel_ckr.check_excel(df_office, df_driver)

        if not final_refrence_json_string:
            return {"message": "Error processing the Excel file."}
        

        # 1. Create a new, unique filename for our JSON
        json_filename = f"{uuid.uuid4()}_result.json"
        json_file_path = upload_folder / json_filename
        
        # 2. Save the JSON string to that file
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(final_refrence_json_string)
        # -----------------------------

    except Exception as e:
        print(f"Error: {e}")
        return {"message": f"There was an error: {e}"}
        
    finally:
        await file.close() # Always close the file
    
    # --- IMPORTANT ---
    
    # Instead of redirecting back to /cikarang,
    # we redirect to the /viewer page and pass the filename
    # as a query parameter in the URL.
    return RedirectResponse(url=f"/cikarang_report?file={json_filename}", status_code=303)


# --- NEW FILE SERVING ENDPOINT ---
# This route's job is to securely serve files from the /tmp directory.
# The browser will call this from the viewer.html's javascript.
@app.get("/get-uploaded-file/{filename}")
async def get_uploaded_file(filename: str):
    
    file_path = Path("/tmp") / filename
    
    # Security check: make sure the file exists
    if not file_path.exists():
        return {"error": "File not found or has expired."}, 404
    
    # Send the file's raw contents back
    return FileResponse(file_path)


# --- SERVE FRONTEND ---

# 2. A "catch-all" endpoint for the root
# This tells FastAPI to serve 'index.html' for the root URL
@app.get("/")
async def serve_home():
    return FileResponse(BASE_DIR / "static" / "index.html")

# route untuk pilih antara tiga cabang 
@app.get("/cabang")
async def serve_cabang():
    return FileResponse(BASE_DIR / "static" / "cabang.html" )

# This route serves your ABOUT page
@app.get("/cabang/cikarang")
async def serve_cikarang():
    # FileResponse sends back an HTML file
    return FileResponse(BASE_DIR / "static" / "cikarang.html")

# --- NEW VIEWER PAGE ROUTE ---
# This route serves the viewer.html page itself.
@app.get("/cikarang_report")
async def serve_viewer_page(request: Request): # <-- Accept the request object
    
    # Check if the 'file' parameter is NOT in the URL
    if "file" not in request.query_params:
        # If it's missing, redirect the user back to the upload page
        return RedirectResponse(url="/cabang/cikarang", status_code=307)
        
    # If the 'file' parameter exists, serve the report page as usual
    return FileResponse(BASE_DIR / "static" / "cikarang_report.html")