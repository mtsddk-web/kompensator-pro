import base64
import os
from typing import List, Dict, Optional
from openai import OpenAI
from PIL import Image
import io

class OCRService:
    """Serwis do rozpoznawania faktur za pomocą GPT-4 Vision"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def encode_image_to_base64(self, image_path: str) -> str:
        """Konwertuje obraz do base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_invoice(self, image_path: str) -> Dict:
        """
        Analizuje pojedynczą fakturę za energię

        Returns:
            Dict z danymi: energia_bierna_kwh, tg_phi, okres_mc, etc.
        """

        # Encode image
        base64_image = self.encode_image_to_base64(image_path)

        # Prompt dla GPT-4 Vision
        prompt = """
        Jesteś ekspertem od analizy faktur za energię elektryczną w Polsce.

        Przeanalizuj tę fakturę i wyciągnij następujące informacje:

        1. **Energia bierna indukcyjna** (w kWh) - szukaj: "energia bierna indukcyjna", "energia reaktywna", "reactive energy"
        2. **Współczynnik tgφ** (tangent phi) - szukaj: "tg φ", "tgfi", "tan φ"
        3. **Okres rozliczeniowy** - ile miesięcy obejmuje faktura (zwykle 1-4 miesiące)
        4. **Energia czynna pobrana** (w kWh) - opcjonalnie
        5. **Dostawca energii** - Tauron, PGE, Energa, Enea, etc.

        WAŻNE:
        - Jeśli faktura jest za kilka miesięcy (np. 2 miesiące), wpisz liczbę miesięcy
        - Jeśli nie ma tgφ na fakturze, możesz go obliczyć: tgφ = energia_bierna / energia_czynna
        - Jeśli jest "energia bierna pojemnościowa", IGNORUJ ją - potrzebujemy tylko INDUKCYJNEJ

        Zwróć dane w formacie JSON:
        {
            "energia_bierna_kwh": <float>,
            "tg_phi": <float lub null>,
            "okres_mc": <int>,
            "energia_czynna_kwh": <float lub null>,
            "dostawca": "<string lub null>",
            "data_faktury": "<string lub null>",
            "success": true,
            "error": null
        }

        Jeśli nie możesz odczytać danych, zwróć:
        {
            "success": false,
            "error": "Opis problemu"
        }
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # lub "gpt-4-vision-preview"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1  # Niska temperatura = bardziej deterministyczne
            )

            # Wyciągnij JSON z odpowiedzi
            result_text = response.choices[0].message.content
            print(f"📄 GPT-4 Response: {result_text[:500]}...")  # Log first 500 chars

            # Parse JSON (GPT-4 powinien zwrócić czysty JSON)
            import json
            result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))

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
