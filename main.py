# main.py
from fastapi import FastAPI, Request, HTTPException
# This is the crucial part for connecting to your frontend
from fastapi.middleware.cors import CORSMiddleware 

from fastapi.staticfiles import StaticFiles  # <-- IMPORT THIS
from fastapi.responses import FileResponse, JSONResponse

from pathlib import Path
import uuid

from fastapi import File, UploadFile
from fastapi.responses import RedirectResponse
import shutil
import json
import traceback

# import module python untuk read and check excel
import read_excel_ckr, read_excel_bgr, read_excel_krw
import check_excel_ckr, check_excel_bgr, check_excel_krw


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

# Dictionary untuk menyimpan hasil processing sementara
# Ini lebih reliable daripada file di /tmp untuk serverless
processing_results = {}

# --- NEW FILE UPLOAD ENDPOINT. ---
#
# This MUST come BEFORE your page routes
#
@app.post("/upload/{nama_cabang}")
async def upload_cikarang_file(nama_cabang: str, file: UploadFile = File(...)):
    
    # This is where you decide what to do with the file.
    # Let's save it to a folder named 'uploads'
    
    # (Make sure you create an 'uploads' folder in your project)
    # Note: On Vercel, this is temporary. For permanent storage,
    # you'd upload to a service like Amazon S3 or Google Cloud Storage.
    
    upload_folder = Path("/tmp")
    
    original_file_path = upload_folder / file.filename
    
    ###############################
    result_id = str(uuid.uuid4())

    try:
        valid_cabang = ["cikarang", "bogor", "karawang"]

        if nama_cabang not in valid_cabang:
            raise HTTPException(status_code=400, detail=f"Invalid cabang: {nama_cabang}")
        
        # Validasi file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
        
        # Save the file to disk
        print(f"Processing file: {file.filename} for cabang: {nama_cabang}")

        # Save the file to disk
        with open(original_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"Original file saved to: {original_file_path}")
        
        #################################
        # Process berdasarkan cabang dengan error handling
        df_office = None
        df_driver = None
        final_refrence_json_string = None

        try:
            if nama_cabang == "cikarang":
                # memanggil fungsi untuk read (output: df_office, df_driver)
                df_office, df_driver = read_excel_ckr.read_excel(original_file_path)

                # memanggil fungsi untuk check dan generate JSON
                final_refrence_json_string = check_excel_ckr.check_excel(df_office, df_driver)

            elif nama_cabang == "bogor":
                # memanggil fungsi untuk read (output: df_office, df_driver)
                df_office, df_driver = read_excel_bgr.read_excel(original_file_path)

                # memanggil fungsi untuk check dan generate JSON
                final_refrence_json_string = check_excel_bgr.check_excel(df_office, df_driver)

            elif nama_cabang == "karawang":
                # memanggil fungsi untuk read (output: df_office, df_driver)
                df_office, df_driver = read_excel_krw.read_excel(original_file_path)

                # memanggil fungsi untuk check dan generate JSON
                final_refrence_json_string = check_excel_krw.check_excel(df_office, df_driver)

        except Exception as processing_error:
            print(f"Error during processing: {str(processing_error)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing Excel file: {str(processing_error)}"
            )
        
        # Validasi hasil
        if not final_refrence_json_string:
            raise HTTPException(
                status_code=500, 
                detail="Processing returned empty result"
            )
        
        # Validasi JSON
        try:
            json_data = json.loads(final_refrence_json_string)
            if not isinstance(json_data, dict) or 'office' not in json_data or 'driver' not in json_data:
                raise ValueError("Invalid JSON structure")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Invalid JSON generated: {str(e)}"
            )
        
        # Simpan hasil di memory (lebih reliable untuk serverless)
        processing_results[result_id] = {
            "data": json_data,
            "cabang": nama_cabang,
            "filename": file.filename
        }

        # 1. Create a new, unique filename for our JSON
        json_filename = f"{uuid.uuid4()}_result.json"
        json_file_path = upload_folder / json_filename
        
        # 2. Save the JSON string to that file
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(final_refrence_json_string)
        # -----------------------------

        print(f"Processing complete. Result ID: {result_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        await file.close()
        # Hapus file original untuk save space
        try:
            if original_file_path.exists():
                original_file_path.unlink()
        except:
            pass
    
    # Redirect dengan result_id
    return RedirectResponse(
        url=f"/report_viewer?file={result_id}&nm_cabang={nama_cabang}", 
        status_code=303
    )

# --- NEW FILE SERVING ENDPOINT ---
# This route's job is to securely serve files from the /tmp directory.
# The browser will call this from the viewer.html's javascript.
@app.get("/get-uploaded-file/{filename}")
async def get_uploaded_file(filename: str):
    
    # Coba ambil dari memory terlebih dahulu
    if filename in processing_results:
        print(f"Serving from memory: {filename}")
        return JSONResponse(content=processing_results[filename]["data"])

    # Fallback ke file di /tmp
    file_path = Path("/tmp") / f"{filename}_result.json"
    
    if not file_path.exists():
        print(f"File not found: {filename}")
        raise HTTPException(
            status_code=404, 
            detail="File not found or has expired. Please upload again."
        )
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Serving from file: {filename}")
        return JSONResponse(content=data)
    except Exception as e:
        print(f"Error reading file {filename}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading result file: {str(e)}"
        )


# --- SERVE FRONTEND ---

@app.get("/")
async def serve_home():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/cabang")
async def serve_cabang():
    return FileResponse(BASE_DIR / "static" / "cabang.html")

@app.get("/cabang/{nama_cabang}")
async def serve_cabang_page(nama_cabang: str):
    return FileResponse(BASE_DIR / "static" / f"{nama_cabang}.html")

@app.get("/report_viewer")
async def serve_viewer_page(request: Request):
    return FileResponse(BASE_DIR / "static" / "page_report.html")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}