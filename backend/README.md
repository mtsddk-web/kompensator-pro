# KompensatorPRO - Backend API

Backend z OCR (GPT-4 Vision) do analizy faktur i doboru kompensatorów mocy biernej.

## 🚀 Szybki start

### 1. Zainstaluj zależności

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ustaw klucz API OpenAI

Skopiuj `.env.example` do `.env`:

```bash
cp .env.example .env
```

Edytuj `.env` i wpisz swój klucz API:

```
OPENAI_API_KEY=sk-proj-twoj-klucz-api-tutaj
```

**Gdzie wziąć klucz API?**
1. Zarejestruj się na https://platform.openai.com/
2. Przejdź do API Keys: https://platform.openai.com/api-keys
3. Kliknij "Create new secret key"
4. Skopiuj klucz i wklej do `.env`

### 3. Uruchom serwer

```bash
# Z aktywowanym venv
python3 -m uvicorn app.main:app --reload --port 8000
```

Serwer będzie dostępny na: **http://localhost:8000**

## 📡 API Endpoints

### GET `/`
Health check - sprawdź czy API działa

### POST `/api/calculate`
Ręczne obliczenie kompensatora

**Body (JSON):**
```json
{
  "energia_bierna": 612,
  "okres_mc": 2,
  "tg_phi": 0.68,
  "ma_pv": true
}
```

### POST `/api/analyze-invoices`
Analiza faktur przez OCR

**Body (multipart/form-data):**
- `files`: Lista plików (JPG, PNG, PDF)
- `ma_pv`: boolean (czy ma fotowoltaikę)

### GET `/api/compensators`
Lista dostępnych kompensatorów w bazie

### GET `/api/health`
Status serwisu (czy OCR działa, itp.)

## 🧪 Test API

```bash
# Test health check
curl http://localhost:8000/

# Test manual calculation
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"energia_bierna": 612, "okres_mc": 2, "tg_phi": 0.68, "ma_pv": true}'

# Test OCR (z plikiem)
curl -X POST http://localhost:8000/api/analyze-invoices \
  -F "files=@faktura.jpg" \
  -F "ma_pv=true"
```

## 💰 Koszty API

**OpenAI GPT-4o Vision:**
- Input: $2.50 / 1M tokens
- Output: $10.00 / 1M tokens

**Szacunkowy koszt na fakturę:** ~$0.05-0.10 (0.20-0.40 PLN)

## 📁 Struktura

```
backend/
├── app/
│   ├── main.py              # FastAPI app + endpoints
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── ocr_service.py   # OCR przez GPT-4 Vision
│       └── calculator.py    # Algorytm doboru
├── uploads/                 # Przesłane faktury (temporary)
├── requirements.txt
└── .env                    # Klucz API (nie commituj!)
```

## 🔒 Bezpieczeństwo

- Nie commituj pliku `.env` do Git!
- Klucz API powinien być tajny
- Pliki faktur są automatycznie usuwane po przetworzeniu (opcjonalne)

## 📝 Notatki

- Backend wspiera wielokrotny upload faktur (1-10 plików)
- Agreguje dane z wielu miesięcy
- Automatycznie rozpoznaje dostawców energii
- Oblicza współczynnik tgφ jeśli nie ma na fakturze
