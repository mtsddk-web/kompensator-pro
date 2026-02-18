import base64
import os
from typing import List, Dict, Optional
from anthropic import Anthropic
from PIL import Image
import io
import json
import fitz  # PyMuPDF

class ClaudeOCRService:
    """Serwis do rozpoznawania faktur za pomocą Claude Vision (Anthropic)"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def pdf_to_images(self, pdf_path: str, max_pages: int = 15) -> list:
        """
        Konwertuje wszystkie strony PDF na obrazy PNG
        Returns: Lista PNG bytes dla każdej strony (max 15 stron)
        """
        doc = fitz.open(pdf_path)
        images = []

        # Konwertuj wszystkie strony (max 15)
        num_pages = min(len(doc), max_pages)
        print(f"📄 PDF ma {len(doc)} stron, konwertuję {num_pages} pierwszych...")

        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            # Renderuj stronę jako obraz (wysokiej jakości)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            png_bytes = pix.tobytes("png")
            images.append(png_bytes)

        doc.close()
        return images

    def encode_image_to_base64(self, image_path: str) -> list:
        """
        Konwertuje obraz/PDF do base64 + wykrywa media type
        Automatycznie konwertuje PDF → wiele PNG (wszystkie strony)
        Returns: Lista [(base64_string, media_type), ...]
        """
        # Wykryj typ pliku
        ext = os.path.splitext(image_path)[1].lower()

        # Jeśli PDF, konwertuj wszystkie strony na PNG
        if ext == '.pdf':
            print(f"📄 Konwertuję PDF (wszystkie strony) na obrazy...")
            png_images = self.pdf_to_images(image_path)
            results = []
            for png_bytes in png_images:
                base64_string = base64.standard_b64encode(png_bytes).decode('utf-8')
                results.append((base64_string, 'image/png'))
            return results
        else:
            # Normalny obraz - jedna strona
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(ext, 'image/jpeg')

            with open(image_path, "rb") as image_file:
                base64_string = base64.standard_b64encode(image_file.read()).decode('utf-8')

            return [(base64_string, media_type)]

    def analyze_invoice(self, image_path: str) -> Dict:
        """
        Analizuje pojedynczą fakturę za energię

        Returns:
            Dict z danymi: energia_bierna_kwh, tg_phi, okres_mc, etc.
        """

        # Encode image(s) - może być wiele stron dla PDF
        images = self.encode_image_to_base64(image_path)

        # Prompt dla Claude
        prompt = """Jesteś ekspertem od analizy faktur za energię elektryczną w Polsce.

WAŻNE: Analizujesz WSZYSTKIE STRONY faktury (w tym załączniki). Przejrzyj każdą stronę dokładnie!

Przeanalizuj dokładnie WSZYSTKIE STRONY tej faktury i znajdź:

1. **Energia bierna indukcyjna** (kWh lub kvarh) - NAJWAŻNIEJSZE! Szukaj w:
   - Tabele "Rozliczenie energii biernej indukcyjnej"
   - "Licznik energii biernej indukcyjnej"
   - Sekcja "Dane techniczno-rozliczeniowe"
   - Załączniki do faktury VAT

2. **Współczynnik tgφ** - jeśli brak, oblicz: tgφ = energia_bierna / energia_czynna

3. **Okres rozliczeniowy** (liczba miesięcy)

4. **Energia czynna** (kWh)

5. **Dostawca** (Tauron, PGE, etc.)

KRYTYCZNE:
- Szukaj w ZAŁĄCZNIKACH do faktury - często dane są tam!
- Jeśli widzisz tabelę z "Licznik energii biernej indukcyjnej" - to jest WŁAŚCIWA wartość!
- "Energia bierna pojemnościowa" - IGNORUJ
- Zwróć TYLKO czysty JSON, BEZ żadnych uwag, markdown, ani dodatkowego tekstu!

Format odpowiedzi (TYLKO JSON, nic więcej):
{
    "energia_bierna_kwh": <float>,
    "tg_phi": <float lub null>,
    "okres_mc": <int>,
    "energia_czynna_kwh": <float lub null>,
    "dostawca": "<string>",
    "data_faktury": "<string>",
    "success": true,
    "error": null
}"""

        try:
            # Przygotuj content z wszystkimi stronami
            content = []

            # Dodaj wszystkie obrazy (strony PDF)
            for base64_image, media_type in images:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_image
                    }
                })

            # Dodaj prompt na końcu
            content.append({
                "type": "text",
                "text": prompt
            })

            response = self.client.messages.create(
                model="claude-sonnet-4-5",  # Claude Sonnet 4.5 (najnowszy z vision)
                max_tokens=2048,  # Zwiększone dla dłuższej analizy
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )

            # Wyciągnij tekst z odpowiedzi
            result_text = response.content[0].text
            print(f"📄 Claude Response: {result_text[:500]}...")  # Debug log

            # Parse JSON
            # Usuń markdown jeśli jest
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '')
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '')

            result = json.loads(result_text.strip())

            print(f"✅ Parsed result: {result}")
            return result

        except Exception as e:
            print(f"❌ OCR Error: {str(e)}")
            return {
                "success": False,
                "error": f"Błąd OCR: {str(e)}"
            }

    def analyze_multiple_invoices(self, image_paths: List[str]) -> List[Dict]:
        """
        Analizuje wiele faktur i agreguje wyniki

        Args:
            image_paths: Lista ścieżek do plików faktur

        Returns:
            Lista wyników dla każdej faktury + zagregowane dane
        """
        results = []

        for i, path in enumerate(image_paths, 1):
            print(f"Analizuję fakturę {i}/{len(image_paths)}: {os.path.basename(path)}")
            result = self.analyze_invoice(path)
            result['file_name'] = os.path.basename(path)
            results.append(result)

        return results

    def aggregate_invoice_data(self, results: List[Dict]) -> Dict:
        """
        Agreguje dane z wielu faktur

        Sumuje energię bierną, oblicza średni tgφ, liczy miesiące
        """
        successful = [r for r in results if r.get('success', False)]

        if not successful:
            return {
                "success": False,
                "error": "Nie udało się odczytać żadnej faktury",
                "details": results
            }

        # Suma energii biernej
        total_energia_bierna = sum(r['energia_bierna_kwh'] for r in successful)

        # Suma miesięcy
        total_okres_mc = sum(r.get('okres_mc', 1) for r in successful)

        # Średni tgφ (ważony energią)
        tg_phi_values = [r for r in successful if r.get('tg_phi')]
        if tg_phi_values:
            avg_tg_phi = sum(r['tg_phi'] * r['energia_bierna_kwh'] for r in tg_phi_values) / total_energia_bierna
        else:
            # Oblicz z energii czynnej jeśli dostępna
            energia_czynna = [r for r in successful if r.get('energia_czynna_kwh')]
            if energia_czynna:
                total_czynna = sum(r['energia_czynna_kwh'] for r in energia_czynna)
                avg_tg_phi = total_energia_bierna / total_czynna if total_czynna > 0 else None
            else:
                avg_tg_phi = None

        return {
            "success": True,
            "energia_bierna_kwh": round(total_energia_bierna, 2),
            "okres_mc": total_okres_mc,
            "tg_phi": round(avg_tg_phi, 3) if avg_tg_phi else None,
            "liczba_faktur": len(successful),
            "faktury": successful,
            "failed_invoices": [r for r in results if not r.get('success', False)]
        }
