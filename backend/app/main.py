from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from dotenv import load_dotenv

from app.services.claude_ocr_service import ClaudeOCRService
from app.services.calculator import CompensatorCalculator
from app.models.schemas import CalculationRequest, CalculationResult

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="KompensatorPRO API",
    description="API do automatycznego doboru kompensatorów mocy biernej (Claude Vision OCR)",
    version="1.1.0"
)

# CORS - pozwól na requesty z frontendu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services - Claude Vision API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("⚠️  WARNING: ANTHROPIC_API_KEY nie jest ustawiony! OCR nie będzie działał.")
    print("⚠️  Ustaw klucz API w pliku .env")

ocr_service = ClaudeOCRService(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
calculator = CompensatorCalculator()

# Upload directory
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "KompensatorPRO API (Claude Vision)",
        "version": "1.2.0",
        "ocr_enabled": ANTHROPIC_API_KEY is not None,
        "ocr_model": "claude-sonnet-4-5"
    }

@app.post("/api/calculate", response_model=CalculationResult)
async def calculate_manual(request: CalculationRequest):
    """
    Ręczne obliczenie kompensatora (bez OCR)

    Endpoint dla użytkowników którzy wprowadzają dane manualnie
    """
    try:
        result = calculator.calculate_compensator(
            energia_bierna_kwh=request.energia_bierna,
            okres_mc=request.okres_mc,
            tg_phi=request.tg_phi,
            ma_pv=request.ma_pv
        )
        result.zrodlo_danych = "manual"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd obliczenia: {str(e)}")

@app.post("/api/analyze-invoices")
async def analyze_invoices(
    files: List[UploadFile] = File(...),
    ma_pv: Optional[bool] = Form(False)
):
    """
    Analiza faktur przez OCR i obliczenie kompensatora

    Args:
        files: Lista plików (zdjęcia/PDF faktur)
        ma_pv: Czy instalacja ma fotowoltaikę

    Returns:
        CalculationResult z rekomendacją
    """

    if not ocr_service:
        raise HTTPException(
            status_code=503,
            detail="OCR nie jest dostępny. Brak klucza API OpenAI."
        )

    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Nie przesłano żadnych plików")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maksymalnie 10 faktur na raz")

    saved_paths = []
    try:
        # 1. Zapisz przesłane pliki
        for file in files:
            # Walidacja typu pliku
            if not file.content_type.startswith(('image/', 'application/pdf')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Nieprawidłowy typ pliku: {file.filename}. Dozwolone: JPG, PNG, PDF"
                )

            # Zapisz plik
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_paths.append(file_path)

        # 2. Przeanalizuj faktury przez OCR
        print(f"📸 Analizuję {len(saved_paths)} faktur przez GPT-4 Vision...")
        ocr_results = ocr_service.analyze_multiple_invoices(saved_paths)

        # 3. Agreguj dane
        aggregated = ocr_service.aggregate_invoice_data(ocr_results)

        if not aggregated.get("success"):
            raise HTTPException(
                status_code=400,
                detail=aggregated.get("error", "Nie udało się odczytać faktur")
            )

        # 4. Oblicz kompensator
        print(f"🔢 Obliczam kompensator...")
        result = calculator.calculate_from_multiple_invoices(
            faktury=aggregated["faktury"],
            ma_pv=ma_pv
        )

        # 5. Dodaj szczegóły OCR do wyniku
        return JSONResponse(content={
            **result.model_dump(),
            "ocr_details": {
                "faktury_sukces": len(aggregated["faktury"]),
                "faktury_blad": len(aggregated.get("failed_invoices", [])),
                "szczegoly": ocr_results
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania: {str(e)}")

    finally:
        # Cleanup - usuń przesłane pliki (opcjonalnie)
        # for path in saved_paths:
        #     if os.path.exists(path):
        #         os.remove(path)
        pass

@app.get("/api/compensators")
async def list_compensators():
    """Zwraca listę dostępnych kompensatorów"""
    return {"compensators": calculator.COMPENSATORS_DB}

@app.get("/api/health")
async def health_check():
    """Sprawdzenie stanu serwisu"""
    return {
        "status": "healthy",
        "ocr_enabled": ocr_service is not None,
        "upload_dir": UPLOAD_DIR,
        "uploads_exist": os.path.exists(UPLOAD_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
