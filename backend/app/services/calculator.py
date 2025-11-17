from typing import Dict, List, Tuple
from app.models.schemas import CompensatorRecommendation, CalculationResult

class CompensatorCalculator:
    """Kalkulator do doboru kompensatorów mocy biernej"""

    # Baza danych kompensatorów LOPI LKD
    COMPENSATORS_DB = [
        {"model": "LOPI LKD 5 PRO", "moc_kvar": 5, "cena": 9000, "typ": "dynamiczny"},
        {"model": "LOPI LKD 10 PRO", "moc_kvar": 10, "cena": 9500, "typ": "dynamiczny"},
        {"model": "LOPI LKD 15 PRO", "moc_kvar": 15, "cena": 11000, "typ": "dynamiczny"},
        {"model": "LOPI LKD 20 PRO", "moc_kvar": 20, "cena": 12000, "typ": "dynamiczny"},
        {"model": "LOPI LKD 25 PRO", "moc_kvar": 25, "cena": 14000, "typ": "dynamiczny"},
        {"model": "LOPI LKD 30 PRO", "moc_kvar": 30, "cena": 16000, "typ": "dynamiczny"},
        {"model": "LOPI LKD 40 PRO", "moc_kvar": 40, "cena": 20000, "typ": "dynamiczny"},
        {"model": "LOPI LKD 50 PRO", "moc_kvar": 50, "cena": 25000, "typ": "dynamiczny"},
    ]

    def calculate_compensator(
        self,
        energia_bierna_kwh: float,
        okres_mc: int,
        tg_phi: float,
        ma_pv: bool = False,
        moc_czynna_kw: float = None
    ) -> CalculationResult:
        """
        Oblicza wymaganą moc kompensatora

        Args:
            energia_bierna_kwh: Energia bierna w kWh
            okres_mc: Okres rozliczeniowy w miesiącach
            tg_phi: Współczynnik mocy (tangent phi)
            ma_pv: Czy instalacja ma fotowoltaikę
            moc_czynna_kw: Moc czynna (opcjonalna, do dokładniejszych obliczeń)

        Returns:
            CalculationResult z rekomendacją
        """

        # 1. Oblicz średnią moc bierną
        srednia_kvar = energia_bierna_kwh / (okres_mc * 720)  # 720h = 30 dni × 24h

        # 2. Oblicz szczytową moc bierną
        # Mnożnik zależy od typu instalacji
        if ma_pv:
            mnoznik = 10  # Instalacje PV mają większe wahania
        else:
            mnoznik = 6   # Typowe przemysłowe

        szczyt_kvar = srednia_kvar * mnoznik

        # 3. Obliczenie alternatywne (jeśli mamy moc czynną)
        qc_wzor = None
        if moc_czynna_kw:
            # QC = P × (tgφ₁ - tgφ₂)
            tg_phi_docelowy = 0.35  # Bezpieczny margines poniżej 0.4
            qc_wzor = moc_czynna_kw * (tg_phi - tg_phi_docelowy)
        else:
            # Szacuj moc czynną z energii biernej i tgφ
            if tg_phi and tg_phi > 0:
                szacowana_energia_czynna = energia_bierna_kwh / tg_phi
                szacowana_moc_czynna = szacowana_energia_czynna / (okres_mc * 720)
                qc_wzor = szacowana_moc_czynna * (tg_phi - 0.35)

        # Wybierz większą wartość
        moc_wymagana = max(szczyt_kvar, qc_wzor if qc_wzor else 0)

        # 4. Dodaj zapasy
        if ma_pv:
            moc_wymagana *= 1.3  # +30% dla instalacji PV

        moc_wymagana *= 1.2  # +20% rezerwa rozwoju

        # 5. Zaokrąglij do standardowej mocy
        moc_kvar = self._round_to_standard_power(moc_wymagana)

        # 6. Wybierz typ kompensatora
        typ = "dynamiczny" if ma_pv else "klasyczny"

        # 7. Znajdź rekomendowany model
        recommended = self._find_compensator(moc_kvar, typ)

        # 8. Oblicz ROI
        kary_pln = self._calculate_penalties(energia_bierna_kwh, okres_mc)
        oszczednosc_mc = kary_pln
        oszczednosc_rok = oszczednosc_mc * 12
        roi_lata = round(recommended["cena"] / oszczednosc_rok, 1) if oszczednosc_rok > 0 else 999

        # 9. Przygotuj wynik
        return CalculationResult(
            moc_kvar=moc_kvar,
            typ=typ,
            rekomendacja=CompensatorRecommendation(
                moc_kvar=moc_kvar,
                typ=typ,
                model=recommended["model"],
                cena_szacunkowa=recommended["cena"]
            ),
            roi_lata=roi_lata,
            kary_pln=round(kary_pln),
            oszczednosc_mc=round(oszczednosc_mc),
            oszczednosc_rok=round(oszczednosc_rok),
            dane={
                "energia_bierna": energia_bierna_kwh,
                "tg_phi": tg_phi,
                "ma_pv": ma_pv,
                "okres_mc": okres_mc
            },
            obliczenia={
                "srednia_kvar": round(srednia_kvar, 2),
                "szczyt_kvar": round(szczyt_kvar, 2),
                "qc_wzor": round(qc_wzor, 2) if qc_wzor else None,
                "mnoznik": mnoznik,
                "zapas_pv": "30%" if ma_pv else "0%",
                "zapas_rozwoj": "20%"
            }
        )

    def _round_to_standard_power(self, moc_wymagana: float) -> int:
        """Zaokrągla do najbliższej standardowej mocy"""
        standard_powers = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]

        for power in standard_powers:
            if power >= moc_wymagana:
                return power

        return 100  # Max dla małych instalacji

    def _find_compensator(self, moc_kvar: int, typ: str) -> Dict:
        """Znajduje odpowiedni kompensator w bazie"""
        # Szukaj w bazie
        for comp in self.COMPENSATORS_DB:
            if comp["moc_kvar"] == moc_kvar:
                return comp

        # Fallback - zwróć najbliższy większy
        for comp in self.COMPENSATORS_DB:
            if comp["moc_kvar"] >= moc_kvar:
                return comp

        # Jeśli nic nie pasuje, zwróć największy
        return self.COMPENSATORS_DB[-1]

    def _calculate_penalties(self, energia_bierna_kwh: float, okres_mc: int) -> float:
        """
        Oblicza szacunkowe kary za energię bierną

        Stawka od 2025: ~2.28 PLN/kvarh (wzrost 45%)
        """
        # Współczynnik kary (różni się u dostawców, przyjmujemy średnią)
        stawka_kvarh = 2.28  # PLN za kvarh od 2025

        # Miesięczna kara
        kara_total = energia_bierna_kwh * stawka_kvarh
        kara_miesieczna = kara_total / okres_mc

        return kara_miesieczna

    def calculate_from_multiple_invoices(
        self,
        faktury: List[Dict],
        ma_pv: bool = False
    ) -> CalculationResult:
        """
        Oblicza na podstawie wielu faktur

        Agreguje dane i wykonuje obliczenia
        """
        # Suma energii biernej
        total_energia_bierna = sum(f.get("energia_bierna_kwh", 0) for f in faktury)

        # Suma miesięcy
        total_okres_mc = sum(f.get("okres_mc", 1) for f in faktury)

        # Średni tgφ ważony energią
        tg_phi_values = [(f.get("tg_phi", 0), f.get("energia_bierna_kwh", 0)) for f in faktury if f.get("tg_phi")]

        if tg_phi_values:
            avg_tg_phi = sum(tg * eb for tg, eb in tg_phi_values) / total_energia_bierna
        else:
            avg_tg_phi = 0.5  # Fallback

        # Wywołaj standardowe obliczenia
        result = self.calculate_compensator(
            energia_bierna_kwh=total_energia_bierna,
            okres_mc=total_okres_mc,
            tg_phi=avg_tg_phi,
            ma_pv=ma_pv
        )

        # Dodaj informację o źródle
        result.zrodlo_danych = "ocr"
        result.faktury_przeanalizowane = len(faktury)

        return result
