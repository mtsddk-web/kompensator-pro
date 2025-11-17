# ⚡ KompensatorPRO

> Profesjonalna aplikacja webowa do automatycznego doboru kompensatorów mocy biernej

## 🎯 Opis projektu

KompensatorPRO to narzędzie SaaS dla elektryków i firm instalacyjnych, które automatycznie analizuje faktury za energię elektryczną i rekomenduje optymalny kompensator mocy biernej.

### Główne funkcje (MVP):
- ⚙️ Ręczne wprowadzanie danych z faktury ✅ **GOTOWE**
- 📊 Precyzyjne obliczenia mocy kompensatora ✅ **GOTOWE**
- 💡 Rekomendacje konkretnych modeli (LOPI LKD) ✅ **GOTOWE**
- 💰 Kalkulator ROI i oszczędności ✅ **GOTOWE**
- 📸 Upload faktur (zdjęcie/PDF) 🔄 **W PRZYGOTOWANIU**
- 🤖 Automatyczne rozpoznawanie OCR (GPT-4 Vision) 🔄 **W PRZYGOTOWANIU**
- 📄 Generator profesjonalnych raportów PDF 🔄 **W PRZYGOTOWANIU**

## 🏗️ Architektura

```
kompensator-pro/
├── frontend/          # React + Vite + TailwindCSS ✅
├── backend/           # Python FastAPI (w przygotowaniu)
├── database/          # PostgreSQL schemas (w przygotowaniu)
└── docs/              # Dokumentacja ✅
```

## 🚀 Szybki Start

### Wymagania
- Node.js 18+
- npm lub yarn

### Frontend (działa już teraz!)

```bash
cd frontend
npm install
npm run dev
```

Aplikacja będzie dostępna na: **http://localhost:5173**

### Test aplikacji

1. Otwórz http://localhost:5173
2. Kliknij "Wprowadź dane ręcznie"
3. Wpisz dane testowe:
   - Energia bierna: `612`
   - Okres: `2 miesiące`
   - tgφ: `0.57`
   - ☑️ Zaznacz "Posiadam PV"
4. Kliknij "Oblicz kompensator"

**Zobacz magię! 🎉**

## 🚀 Tech Stack

### Frontend
- **Framework:** React 18 + Vite
- **Styling:** TailwindCSS
- **Upload:** react-dropzone
- **PDF:** jsPDF / react-pdf
- **State:** Zustand
- **HTTP:** Axios

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **OCR:** OpenAI GPT-4 Vision API
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy
- **Auth:** JWT tokens
- **Storage:** AWS S3 / Cloudflare R2

### DevOps
- **Frontend hosting:** Vercel
- **Backend hosting:** Railway / Render
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry

## 💰 Business Model

### Plany cenowe:
- **Free:** 3 obliczenia/miesiąc
- **Pro:** 49 PLN/mc - nielimitowane obliczenia
- **Business:** 149 PLN/mc - multi-user + white-label

### Płatności:
- Stripe (subskrypcje)
- Przelewy24 (jednorazowe)

## 📋 Roadmap

### Faza 1: MVP (3 tygodnie)
- [x] Setup projektu
- [ ] Frontend: Landing + Upload
- [ ] Backend: API + Obliczenia
- [ ] OCR: Podstawowe rozpoznawanie
- [ ] Baza produktów: LOPI, Savlo
- [ ] Generator PDF
- [ ] Płatności: Stripe

### Faza 2: Beta (4 tygodnie)
- [ ] Testy z elektrykami
- [ ] Rozpoznawanie wszystkich dostawców energii
- [ ] Historia obliczeń
- [ ] Baza klientów

### Faza 3: Launch
- [ ] Marketing
- [ ] SEO
- [ ] Partnerstwa z hurtowniami

## 🛠️ Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Setup

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📊 Algorytm obliczeń

```python
def calculate_compensator(
    energia_bierna_kwh: float,
    okres_mc: int,
    tg_phi_obecny: float,
    moc_czynna_kw: float,
    ma_pv: bool = False
) -> dict:
    """
    Oblicza wymaganą moc kompensatora

    Returns:
        {
            'moc_kvar': float,
            'typ': 'dynamiczny' | 'klasyczny',
            'rekomendacje': [produkt1, produkt2, ...],
            'roi_lata': float
        }
    """
    # Średnia moc bierna
    srednia_kvar = energia_bierna_kwh / (okres_mc * 720)

    # Szczyt (mnożnik zależy od typu instalacji)
    mnoznik = 10 if ma_pv else 6
    szczyt_kvar = srednia_kvar * mnoznik

    # Obliczenie ze wzoru QC = P × (tgφ₁ - tgφ₂)
    tg_phi_docelowy = 0.35
    qc_wzor = moc_czynna_kw * (tg_phi_obecny - tg_phi_docelowy)

    # Wybierz większą wartość
    moc_wymagana = max(szczyt_kvar, qc_wzor)

    # Zapasy
    if ma_pv:
        moc_wymagana *= 1.3  # +30% dla PV
    moc_wymagana *= 1.2  # +20% rezerwa

    # Zaokrąglij do standardowej mocy
    moce_std = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    moc_kvar = min([m for m in moce_std if m >= moc_wymagana], default=100)

    return {
        'moc_kvar': moc_kvar,
        'typ': 'dynamiczny' if ma_pv else 'klasyczny',
        # ... więcej danych
    }
```

## 📝 License

Proprietary - © 2025 Sundek Energia

## 👨‍💻 Author

**Sundek Energia**
- Website: https://sundek-energia.pl
- Email: kontakt@sundek-energia.pl

---

**Built with ❤️ in Poland 🇵🇱**
