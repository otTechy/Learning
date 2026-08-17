import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf_utils import extract_text_from_pdf
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
import uuid

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Llama 3.1 model (ensure you have the model file in the correct path)
LLAMA_MODEL_PATH = "llama-3.1-8b-instruct.Q4_K_M.gguf"  # Update with your model file
llm = None
if os.path.exists(LLAMA_MODEL_PATH):
    llm = LlamaCpp(model_path=LLAMA_MODEL_PATH, n_ctx=2048, n_threads=4)

@app.post("/extract")
async def extract_pdf(
    file: UploadFile = File(...),
    output_format: str = Form("json")
):
    # Save uploaded PDF
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    # Extract text
    text = extract_text_from_pdf(file_path)
    # Use Llama to process text
    if llm:
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""
You are an AI PDF data extraction agent. Given the following PDF text, extract the key data points and return them in {output_format} format.\n\nPDF Text:\n{text}\n\nExtracted Data:
"""
        )
        result = llm(prompt.format(text=text[:2000], output_format=output_format))
    else:
        result = {"error": "Llama model not loaded. Please add the model file."}
    return JSONResponse(content={"result": result})
