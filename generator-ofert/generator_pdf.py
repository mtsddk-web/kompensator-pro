#!/usr/bin/env python3
"""
Generator PDF dla ofert kompensatorow
Wymaga: pip install weasyprint

Alternatywnie mozna uzyc przegladarki:
- Otworz plik HTML
- Drukuj (Ctrl+P)
- Zapisz jako PDF
"""

import sys
from pathlib import Path

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WeasyPrint nie jest zainstalowany.")
    print("Zainstaluj: pip install weasyprint")
    print("Lub uzyj przegladarki do zapisu PDF.\n")


def html_to_pdf(html_path: Path, pdf_path: Path = None) -> Path:
    """
    Konwertuj plik HTML na PDF.

    Args:
        html_path: Sciezka do pliku HTML
        pdf_path: Sciezka wyjsciowa PDF (opcjonalnie)

    Returns:
        Sciezka do wygenerowanego PDF
    """
    if not WEASYPRINT_AVAILABLE:
        print("WeasyPrint niedostepny - uzyj przegladarki do zapisu PDF")
        return None

    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {html_path}")

    if pdf_path is None:
        pdf_path = html_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path)

    # Generuj PDF
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))

    return pdf_path


def konwertuj_wszystkie_oferty(oferty_dir: Path = None):
    """Konwertuj wszystkie oferty HTML w folderze na PDF"""

    if oferty_dir is None:
        oferty_dir = Path(__file__).parent / "oferty"

    if not oferty_dir.exists():
        print(f"Folder nie istnieje: {oferty_dir}")
        return

    html_files = list(oferty_dir.glob("*.html"))
    if not html_files:
        print("Brak plikow HTML do konwersji")
        return

    print(f"Znaleziono {len(html_files)} plikow HTML\n")

    for html_file in html_files:
        pdf_file = html_file.with_suffix('.pdf')
        if pdf_file.exists():
            print(f"[SKIP] {html_file.name} -> juz istnieje PDF")
            continue

        try:
            result = html_to_pdf(html_file, pdf_file)
            if result:
                print(f"[OK] {html_file.name} -> {pdf_file.name}")
        except Exception as e:
            print(f"[ERROR] {html_file.name}: {e}")


def main():
    """Glowna funkcja"""
    if len(sys.argv) > 1:
        # Konwertuj konkretny plik
        html_path = Path(sys.argv[1])
        pdf_path = html_to_pdf(html_path)
        if pdf_path:
            print(f"PDF zapisany: {pdf_path}")
    else:
        # Konwertuj wszystkie
        konwertuj_wszystkie_oferty()


if __name__ == "__main__":
    main()
