#!/usr/bin/env python3
"""
Generator Ofert na Kompensatory Mocy Biernej
Sundek Energia 2025

Uzycie:
    python generator.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Sciezka do plikow
BASE_DIR = Path(__file__).parent
CENNIK_PATH = BASE_DIR / "cennik.json"
OUTPUT_DIR = BASE_DIR / "oferty"


def load_cennik():
    """Wczytaj cennik z pliku JSON"""
    with open(CENNIK_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def oblicz_koszty(cennik: dict, metry_przewodu: int = 5) -> dict:
    """
    Oblicz calkowite koszty instalacji kompensatora.

    Returns:
        Slownik z kosztami i cena dla klienta
    """
    mat = cennik['koszty_materialow']
    praca = cennik['koszty_pracy']
    komp = cennik['kompensatory']['sinexcel_15kvar']  # Na razie tylko ten model

    # Koszty materialow
    koszt_przekladnikow = mat['przekladnik_50_5A']['koszt_jednostkowy'] * mat['przekladnik_50_5A']['ilosc']
    koszt_zabezpieczenia = mat['zabezpieczenie_3f']['koszt_jednostkowy'] * mat['zabezpieczenie_3f']['ilosc']
    koszt_przewodu = mat['przewod_6x2_5_za_mb']['koszt_jednostkowy'] * metry_przewodu

    # Suma kosztow
    koszt_kompensatora = komp['koszt_zakupu']
    koszt_materialow = koszt_przekladnikow + koszt_zabezpieczenia + koszt_przewodu
    koszt_pracy = praca['montaz_i_konfiguracja']['koszt']

    koszt_calkowity = koszt_kompensatora + koszt_materialow + koszt_pracy

    # Cena dla klienta (z marza)
    marza = cennik['marza_procent'] / 100
    cena_netto = round(koszt_calkowity * (1 + marza), 0)
    cena_brutto = round(cena_netto * 1.23, 0)

    return {
        "kompensator": komp,
        "koszty": {
            "kompensator": koszt_kompensatora,
            "materialy": koszt_materialow,
            "praca": koszt_pracy,
            "razem": koszt_calkowity
        },
        "cena_klient": {
            "netto": cena_netto,
            "brutto": cena_brutto
        },
        "marza_procent": cennik['marza_procent']
    }


def oblicz_oszczednosci(energia_bierna_kwh: float, okres_mc: int) -> dict:
    """Oblicz szacunkowe oszczednosci po instalacji kompensatora."""
    stawka_kary = 0.30  # PLN/kvarh - srednia

    kary_w_okresie = energia_bierna_kwh * stawka_kary
    kary_miesieczne = kary_w_okresie / okres_mc
    kary_roczne = kary_miesieczne * 12

    return {
        "kary_miesieczne": round(kary_miesieczne, 0),
        "kary_roczne": round(kary_roczne, 0),
        "oszczednosc_5_lat": round(kary_roczne * 5, 0)
    }


def oblicz_roi(cena_brutto: float, oszczednosc_roczna: float) -> float:
    """Oblicz zwrot z inwestycji w latach"""
    if oszczednosc_roczna <= 0:
        return 99
    return round(cena_brutto / oszczednosc_roczna, 1)


def generuj_numer_oferty() -> str:
    """Generuj unikalny numer oferty"""
    now = datetime.now()
    return f"OF/{now.year}/{now.month:02d}/{now.strftime('%d%H%M%S')}"


def generuj_oferte_html(dane: dict) -> str:
    """Generuj oferte w formacie HTML - TYLKO SUMA, bez rozbicia cen"""

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oferta {dane['numer_oferty']} - Kompensator mocy biernej</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .oferta {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            padding: 30px;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 5px; }}
        .header .subtitle {{ opacity: 0.9; font-size: 14px; }}
        .meta {{
            display: flex;
            justify-content: space-between;
            padding: 20px 30px;
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }}
        .meta-item {{ text-align: center; }}
        .meta-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; }}
        .meta-value {{ font-size: 16px; font-weight: 600; color: #1e293b; }}
        .section {{
            padding: 25px 30px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .section:last-child {{ border-bottom: none; }}
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 15px;
        }}
        .klient-info {{
            background: #f1f5f9;
            padding: 15px;
            border-radius: 8px;
        }}
        .klient-info p {{ margin: 5px 0; }}

        .cena-box {{
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
        }}
        .cena-tytul {{ font-size: 18px; margin-bottom: 10px; opacity: 0.9; }}
        .cena-wartosc {{ font-size: 48px; font-weight: 700; }}
        .cena-wartosc small {{ font-size: 20px; opacity: 0.8; }}
        .cena-netto {{ font-size: 14px; margin-top: 10px; opacity: 0.8; }}

        .zakres {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .zakres h4 {{ margin-bottom: 10px; color: #374151; }}
        .zakres ul {{ margin-left: 20px; }}
        .zakres li {{ margin: 8px 0; color: #4b5563; }}

        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
        .stat-box {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #2563eb; }}
        .stat-label {{ font-size: 12px; color: #64748b; margin-top: 5px; }}
        .oszczednosci {{ background: #ecfdf5; border: 1px solid #6ee7b7; }}
        .oszczednosci .stat-value {{ color: #059669; }}

        .roi-highlight {{
            background: #fef3c7;
            border: 2px solid #f59e0b;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-top: 20px;
        }}
        .roi-value {{ font-size: 32px; font-weight: 700; color: #d97706; }}

        .valid-info {{
            background: #fef9c3;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            font-size: 14px;
            color: #854d0e;
        }}
        .footer {{
            background: #1e293b;
            color: white;
            padding: 25px 30px;
            text-align: center;
        }}
        .footer a {{ color: #60a5fa; text-decoration: none; }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .oferta {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="oferta">
        <div class="header">
            <h1>OFERTA - KOMPENSACJA MOCY BIERNEJ</h1>
            <p class="subtitle">{dane['firma']['nazwa']} | {dane['numer_oferty']}</p>
        </div>

        <div class="meta">
            <div class="meta-item">
                <div class="meta-label">Numer oferty</div>
                <div class="meta-value">{dane['numer_oferty']}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Data wystawienia</div>
                <div class="meta-value">{dane['data_wystawienia']}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Wazna do</div>
                <div class="meta-value">{dane['data_waznosci']}</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">DANE KLIENTA</div>
            <div class="klient-info">
                <p><strong>{dane['klient']['nazwa']}</strong></p>
                <p>{dane['klient']['adres']}</p>
                {f"<p>NIP: {dane['klient']['nip']}</p>" if dane['klient'].get('nip') else ""}
                {f"<p>Tel: {dane['klient']['telefon']}</p>" if dane['klient'].get('telefon') else ""}
            </div>
        </div>

        <div class="section">
            <div class="section-title">OFERTA CENOWA</div>

            <div class="cena-box">
                <div class="cena-tytul">Kompensator mocy biernej {dane['kompensator']['moc_kvar']} kvar<br>z montazem i uruchomieniem</div>
                <div class="cena-wartosc">{dane['cena']['brutto']:,.0f} <small>PLN brutto</small></div>
                <div class="cena-netto">({dane['cena']['netto']:,.0f} PLN netto + 23% VAT)</div>
            </div>

            <div class="zakres">
                <h4>Zakres uslugi obejmuje:</h4>
                <ul>
                    <li>Kompensator aktywny {dane['kompensator']['model']}</li>
                    <li>Przekladniki pradowe (3 szt.)</li>
                    <li>Zabezpieczenie 3-fazowe</li>
                    <li>Przewody i okablowanie</li>
                    <li>Montaz i podlaczenie do instalacji</li>
                    <li>Konfiguracja i uruchomienie</li>
                    <li>Instruktaz obslugi</li>
                </ul>
            </div>
        </div>

        <div class="section">
            <div class="section-title">DANE Z FAKTURY KLIENTA</div>
            <div class="grid">
                <div class="stat-box">
                    <div class="stat-value">{dane['analiza']['energia_bierna']} kWh</div>
                    <div class="stat-label">Energia bierna z faktury</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{dane['analiza']['okres_mc']} mc</div>
                    <div class="stat-label">Okres rozliczeniowy</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">KALKULACJA OSZCZEDNOSCI</div>
            <div class="grid">
                <div class="stat-box oszczednosci">
                    <div class="stat-value">~{dane['oszczednosci']['kary_miesieczne']:,.0f} PLN</div>
                    <div class="stat-label">Oszczednosc miesiecznie</div>
                </div>
                <div class="stat-box oszczednosci">
                    <div class="stat-value">~{dane['oszczednosci']['kary_roczne']:,.0f} PLN</div>
                    <div class="stat-label">Oszczednosc rocznie</div>
                </div>
            </div>
            <div class="roi-highlight">
                <div>Szacowany zwrot inwestycji</div>
                <div class="roi-value">{dane['roi']} lat</div>
                <div style="font-size: 14px; margin-top: 5px; opacity: 0.8;">
                    Oszczednosc w ciagu 5 lat: <strong>~{dane['oszczednosci']['oszczednosc_5_lat']:,.0f} PLN</strong>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="valid-info">
                Oferta wazna do: <strong>{dane['data_waznosci']}</strong>
            </div>
        </div>

        <div class="footer">
            <p><strong>{dane['firma']['nazwa']}</strong></p>
            <p>{dane['firma']['adres']}</p>
            <p>Tel: {dane['firma']['telefon']} | Email: <a href="mailto:{dane['firma']['email']}">{dane['firma']['email']}</a></p>
            <p><a href="{dane['firma']['www']}">{dane['firma']['www']}</a></p>
        </div>
    </div>
</body>
</html>"""

    return html


def zapisz_oferte(html: str, numer_oferty: str, nazwa_klienta: str) -> Path:
    """Zapisz oferte do pliku"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    safe_nazwa = "".join(c if c.isalnum() or c in ' -_' else '' for c in nazwa_klienta)
    safe_numer = numer_oferty.replace('/', '-')

    filename = f"oferta_{safe_numer}_{safe_nazwa}.html"
    filepath = OUTPUT_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath


def main():
    """Glowna funkcja - interaktywny generator ofert"""

    print("\n" + "="*60)
    print("  GENERATOR OFERT - KOMPENSATOR MOCY BIERNEJ")
    print("  Sundek Energia 2025")
    print("="*60 + "\n")

    # Wczytaj cennik
    cennik = load_cennik()
    print(f"Cennik zaladowany (wersja: {cennik['version']})\n")

    # DANE KLIENTA
    print("-" * 40)
    print("1. DANE KLIENTA")
    print("-" * 40)

    klient_nazwa = input("Nazwa klienta/firmy: ").strip()
    if not klient_nazwa:
        klient_nazwa = "Klient"

    klient_adres = input("Adres: ").strip()
    klient_nip = input("NIP (opcjonalnie, Enter = pomiń): ").strip()
    klient_telefon = input("Telefon (opcjonalnie, Enter = pomiń): ").strip()

    # DANE Z FAKTURY
    print("\n" + "-" * 40)
    print("2. DANE Z FAKTURY (do kalkulacji oszczednosci)")
    print("-" * 40)

    try:
        energia_bierna = float(input("Energia bierna z faktury [kWh]: ").replace(',', '.'))
    except ValueError:
        energia_bierna = 500
        print(f"   (uzyto wartosci: {energia_bierna})")

    try:
        okres_mc = int(input("Okres rozliczeniowy [miesiecy, 1-4]: "))
        okres_mc = max(1, min(4, okres_mc))
    except ValueError:
        okres_mc = 2
        print(f"   (uzyto wartosci: {okres_mc})")

    # METRY PRZEWODU
    print("\n" + "-" * 40)
    print("3. PARAMETRY INSTALACJI")
    print("-" * 40)

    try:
        metry_przewodu = int(input("Metry przewodu do przekladnikow [domyslnie 5]: ") or "5")
    except ValueError:
        metry_przewodu = 5

    # OBLICZENIA
    print("\n" + "-" * 40)
    print("4. KALKULACJA")
    print("-" * 40)

    koszty = oblicz_koszty(cennik, metry_przewodu)
    oszczednosci = oblicz_oszczednosci(energia_bierna, okres_mc)
    roi = oblicz_roi(koszty['cena_klient']['brutto'], oszczednosci['kary_roczne'])

    print(f"\n   --- KOSZTY (wewnetrzne, NIE pokazywac klientowi!) ---")
    print(f"   Kompensator:  {koszty['koszty']['kompensator']:>8} PLN")
    print(f"   Materialy:    {koszty['koszty']['materialy']:>8} PLN")
    print(f"   Praca:        {koszty['koszty']['praca']:>8} PLN")
    print(f"   --------------------------------")
    print(f"   KOSZT RAZEM:  {koszty['koszty']['razem']:>8} PLN")
    print(f"   + marza {koszty['marza_procent']}%")

    print(f"\n   --- CENA DLA KLIENTA ---")
    print(f"   NETTO:  {koszty['cena_klient']['netto']:>10,.0f} PLN")
    print(f"   BRUTTO: {koszty['cena_klient']['brutto']:>10,.0f} PLN")

    print(f"\n   Oszczednosc roczna klienta: ~{oszczednosci['kary_roczne']:,.0f} PLN")
    print(f"   ROI: {roi} lat")

    # GENEROWANIE OFERTY
    print("\n" + "-" * 40)
    print("5. GENEROWANIE OFERTY")
    print("-" * 40)

    numer_oferty = generuj_numer_oferty()
    data_wystawienia = datetime.now().strftime("%Y-%m-%d")
    data_waznosci = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    dane_oferty = {
        "numer_oferty": numer_oferty,
        "data_wystawienia": data_wystawienia,
        "data_waznosci": data_waznosci,
        "klient": {
            "nazwa": klient_nazwa,
            "adres": klient_adres,
            "nip": klient_nip,
            "telefon": klient_telefon
        },
        "analiza": {
            "energia_bierna": energia_bierna,
            "okres_mc": okres_mc
        },
        "kompensator": koszty['kompensator'],
        "cena": koszty['cena_klient'],
        "oszczednosci": oszczednosci,
        "roi": roi,
        "firma": cennik['firma']
    }

    # Generuj HTML
    html = generuj_oferte_html(dane_oferty)
    filepath = zapisz_oferte(html, numer_oferty, klient_nazwa)

    print(f"\n   Oferta zapisana: {filepath}")

    # Otworz w przegladarce?
    otworz = input("\n   Otworzyc w przegladarce? [t/n]: ").lower()
    if otworz in ['t', 'tak', 'y', 'yes', '1', '']:
        import webbrowser
        webbrowser.open(f"file://{filepath.absolute()}")

    print("\n" + "="*60)
    print("   GOTOWE!")
    print("="*60 + "\n")

    return dane_oferty


if __name__ == "__main__":
    main()
