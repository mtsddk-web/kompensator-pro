# Generator Ofert - Kompensatory Mocy Biernej

Prosty generator ofert na kompensatory mocy biernej dla Sundek Energia.

## Szybki start

```bash
cd /Users/mateuszdudek/Documents/atlas/kompensator-pro/generator-ofert
python3 generator.py
```

## Jak to dziala

1. Wpisujesz dane klienta
2. Wpisujesz dane z faktury (energia bierna, tg phi)
3. Program oblicza wymagana moc kompensatora
4. Dobiera produkt z cennika
5. Generuje oferte HTML

## Pliki

- `generator.py` - glowny skrypt generatora
- `cennik.json` - cennik produktow i uslug (do edycji!)
- `generator_pdf.py` - konwersja HTML -> PDF
- `oferty/` - folder z wygenerowanymi ofertami

## Cennik

Edytuj plik `cennik.json` aby zaktualizowac:
- ceny kompensatorow klasycznych i dynamicznych
- ceny uslug montazu
- dane firmy

## Generowanie PDF

### Opcja 1: WeasyPrint (automatycznie)
```bash
pip install weasyprint
python3 generator_pdf.py oferty/nazwa_oferty.html
```

### Opcja 2: Z przegladarki (reczne)
1. Otworz plik HTML w przegladarce
2. Ctrl+P (lub Cmd+P na Mac)
3. "Zapisz jako PDF"

## Przykladowe uzycie

```
python3 generator.py

1. DANE KLIENTA
Nazwa klienta/firmy: Jan Kowalski Sp. z o.o.
Adres: ul. Przemyslowa 10, 40-000 Katowice
NIP: 123-456-78-90
Telefon: 500 600 700

2. DANE Z FAKTURY
Energia bierna [kWh/kvarh]: 612
Okres rozliczeniowy [miesiecy, 1-4]: 2
Wspolczynnik tg phi: 0.57
Czy klient ma instalacje PV? [t/n]: n

--> Oferta wygenerowana!
```

## Do zrobienia

- [ ] Integracja z React frontendem
- [ ] Automatyczny upload faktur (OCR)
- [ ] Baza danych ofert
- [ ] Wysylka mailem
