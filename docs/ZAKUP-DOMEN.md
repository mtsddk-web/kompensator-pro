# 🌐 INSTRUKCJA ZAKUPU DOMEN

## 📋 Lista domen do zakupu

1. **kompensatorpro.pl** (główna aplikacja)
2. **jakikompensator.pl** (landing page / redirect)
3. **dobor-kompensatora.pl** (landing page SEO / redirect)

---

## 💰 Koszt

- **Pojedyncza domena .pl:** ~50 PLN/rok
- **TOTAL:** ~150 PLN/rok (3 domeny)

---

## 🛒 GDZIE KUPIĆ - TOP 3 REKOMENDACJE

### **OPCJA 1: home.pl** ⭐ **POLECAM!**

```
Strona: https://home.pl/domeny/
Cena: 49.99 PLN/rok
```

**Krok po kroku:**
1. Wejdź na https://home.pl/domeny/
2. Wpisz: `kompensatorpro.pl` → Szukaj
3. Jeśli wolna → Dodaj do koszyka
4. Powtórz dla: `jakikompensator.pl` i `dobor-kompensatora.pl`
5. Koszyk → Zamówienie → Płatność
6. **WAŻNE:** Przy rejestracji:
   - Odznacz "automatyczne odnowienie" (możesz włączyć później)
   - Wybierz DNS: "Własne serwery DNS" (podamy później)

**Zalety:**
- ✅ Polski support (telefon, czat)
- ✅ Tanie domeny
- ✅ Łatwy panel

---

### **OPCJA 2: OVH.pl**

```
Strona: https://www.ovhcloud.com/pl/domains/
Cena: 39.99 PLN/rok (promocja)
```

**Krok po kroku:**
1. Wejdź na https://www.ovhcloud.com/pl/domains/
2. Wyszukaj domeny
3. Dodaj do koszyka
4. Rejestracja/Logowanie
5. Płatność

**Zalety:**
- ✅ Najtańsze
- ✅ Darmowy WHOIS privacy
- ⚠️ Panel trochę skomplikowany

---

### **OPCJA 3: Cloudflare Registrar**

```
Strona: https://www.cloudflare.com/products/registrar/
Cena: ~45 PLN/rok (cena hurtowa)
```

**UWAGA:** Wymaga założenia konta Cloudflare

**Zalety:**
- ✅ Cena hurtowa (bez marży)
- ✅ Automatyczne DNSSEC
- ✅ Bezpłatny CDN

---

## ⚙️ KONFIGURACJA DNS (po zakupie)

### **Dla Vercel (rekomendowane):**

Po zakupie domen, w panelu zarządzania domeną ustaw:

```
TYP    NAZWA                      WARTOŚĆ
────────────────────────────────────────────────────────
A      kompensatorpro.pl          76.76.21.21
CNAME  www                        cname.vercel-dns.com
```

**LUB skorzystaj z nameservers Vercel:**
```
ns1.vercel-dns.com
ns2.vercel-dns.com
```

---

## 🔀 PRZEKIEROWANIA (dla 2 pomocniczych domen)

### **Metoda 1: W panelu domeny**

W panelu home.pl / OVH:
- Przekierowanie 301:
  - `jakikompensator.pl` → `https://kompensatorpro.pl`
  - `dobor-kompensatora.pl` → `https://kompensatorpro.pl`

### **Metoda 2: W Vercel (lepsze!)**

1. Dodaj wszystkie 3 domeny do projektu Vercel
2. W pliku `vercel.json`:

```json
{
  "redirects": [
    {
      "source": "/(.*)",
      "destination": "https://kompensatorpro.pl/$1",
      "permanent": true,
      "host": "jakikompensator.pl"
    },
    {
      "source": "/(.*)",
      "destination": "https://kompensatorpro.pl/$1",
      "permanent": true,
      "host": "dobor-kompensatora.pl"
    }
  ]
}
```

---

## ✅ CHECKLIST

Po zakupie domen:

- [ ] Kupiono kompensatorpro.pl
- [ ] Kupiono jakikompensator.pl
- [ ] Kupiono dobor-kompensatora.pl
- [ ] Ustawiono DNS na Vercel
- [ ] Skonfigurowano przekierowania 301
- [ ] Sprawdzono działanie (otwórz w przeglądarce)

---

## 🆘 PROBLEMY?

### **Domena zajęta?**

Jeśli któraś z domen jest zajęta:
1. Sprawdź WHOIS: https://dns.pl/whois
2. Alternatywy:
   - `kompensator-pro.pl` (z myślnikiem)
   - `kompensatorypro.pl` (liczba mnoga)
   - `mocbierna.pl` (inna nazwa)

### **DNS nie działa?**

- Poczekaj 24-48h (propagacja DNS)
- Sprawdź: https://www.whatsmydns.net/

---

## 📞 KONTAKT DO SUPPORTU

- **home.pl:** 12 297 88 00
- **OVH:** 71 750 02 00
- **Cloudflare:** support przez dashboard

---

**Powodzenia! Po zakupie domen wracamy do setupu aplikacji! 🚀**
