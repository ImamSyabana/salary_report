# main.py
from fastapi import FastAPI
# This is the crucial part for connecting to your frontend
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

# --- THIS IS THE CRITICAL PART ---
# Set up CORS to allow your frontend to make requests
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
     # Add the URL your frontend is running on
    "*"# You can also use "*" to allow all origins, but it's less secure
    # "http://localhost:5500" is a common one for live servers
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