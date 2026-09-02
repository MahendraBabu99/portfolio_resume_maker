from pydantic import BaseModel
from fastapi import FastAPI, UploadFile , File
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from db.createdb import insert_users, select, bucket_pdf
from portfolio_code.code_gen import complete
from dotenv import load_dotenv
import os
from pypdf import PdfReader
from supabase import create_client
import requests
from io import BytesIO

load_dotenv()

anon = os.getenv("SUPABASE_API")
url  = os.getenv("SUPABASE_URL")

supabase = create_client(url, anon)

#creating a fastapi object
app = FastAPI()

#adding middleware routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserData(BaseModel):
    name : str
    role : str
    
@app.post('/users')
def users_insert(user: UserData):
    return insert_users(
        supabase,
        user.name,
        user.role
    )
    
@app.get('/userdata')
def user_data():
    return select(supabase)

class Pdf(BaseModel):
    filename : str
    
@app.post('/resume')
async def getpdf(user_id:int,file: UploadFile = File(...)):
    return bucket_pdf(supabase, user_id,file)

@app.post('/portfolio')
def port_folio(id:int):
    return complete(supabase,id,requests, PdfReader, BytesIO)