from pydantic import BaseModel, Field
from typing import Optional, List

class InvoiceData(BaseModel):
    """Dane wyciągnięte z faktury"""
    energia_bierna_kwh: float = Field(..., description="Energia bierna indukcyjna w kWh")
    okres_mc: int = Field(..., description="Liczba miesięcy w okresie rozliczeniowym")
    tg_phi: Optional[float] = Field(None, description="Współczynnik tgφ")
    energia_czynna_kwh: Optional[float] = Field(None, description="Energia czynna")
    dostawca: Optional[str] = Field(None, description="Dostawca energii (Tauron/PGE/etc)")
    data_faktury: Optional[str] = Field(None, description="Data faktury")

class CalculationRequest(BaseModel):
    """Request do ręcznego obliczenia"""
    energia_bierna: float
    okres_mc: int = 1
    tg_phi: float
    ma_pv: bool = False

class CompensatorRecommendation(BaseModel):
    """Rekomendacja kompensatora"""
    moc_kvar: int = Field(..., description="Moc kompensatora w kvar")
    typ: str = Field(..., description="Typ: dynamiczny lub klasyczny")
    model: str = Field(..., description="Konkretny model np. LOPI LKD 10 PRO")
    cena_szacunkowa: int = Field(..., description="Szacunkowa cena w PLN")

class CalculationResult(BaseModel):
    """Wynik obliczeń"""
    moc_kvar: int
    typ: str
    rekomendacja: CompensatorRecommendation
    roi_lata: float
    kary_pln: int
    oszczednosc_mc: int
    oszczednosc_rok: int
    dane: dict
    obliczenia: dict
    zrodlo_danych: str = Field(default="manual", description="manual lub ocr")
    faktury_przeanalizowane: int = Field(default=1, description="Liczba przeanalizowanych faktur")
