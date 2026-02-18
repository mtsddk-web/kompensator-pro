import { useState } from 'react'
import './App.css'

function App() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [manualData, setManualData] = useState({
    energia_bierna: '',
    okres_mc: 1,
    tg_phi: '',
    ma_pv: false
  })

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setFiles(prev => [...prev, ...newFiles])
      setError(null)
    }
  }

  const removeFile = (indexToRemove) => {
    setFiles(prev => prev.filter((_, index) => index !== indexToRemove))
  }

  const handleUploadAll = async () => {
    if (files.length === 0) {
      setError('Dodaj przynajmniej jedną fakturę!')
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    formData.append('ma_pv', manualData.ma_pv ? 'true' : 'false')

    try {
      const response = await fetch('http://localhost:8000/api/analyze-invoices', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        // Wyświetl szczegółowy błąd z backendu
        const errorMsg = errorData.detail || JSON.stringify(errorData) || 'Błąd podczas analizy'
        throw new Error(errorMsg)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Błąd podczas analizy faktur')
    } finally {
      setLoading(false)
    }
  }

  const handleManualCalculate = async () => {
    if (!manualData.energia_bierna || !manualData.tg_phi) {
      setError('Wypełnij wszystkie pola!')
      return
    }

    setLoading(true)
    setError(null)

    // Symulacja obliczen - później podłączymy prawdziwy backend
    setTimeout(() => {
      const energia_bierna = parseFloat(manualData.energia_bierna)
      const okres_mc = parseInt(manualData.okres_mc)
      const tg_phi = parseFloat(manualData.tg_phi)
      const ma_pv = manualData.ma_pv

      // Proste obliczenia (wersja uproszczona)
      const srednia_kvar = energia_bierna / (okres_mc * 720)
      const mnoznik = ma_pv ? 10 : 6
      const szczyt_kvar = srednia_kvar * mnoznik

      // Zapasy
      let moc_wymagana = szczyt_kvar * (ma_pv ? 1.3 : 1) * 1.2

      // Zaokrąglij do standardowej mocy
      const moce_std = [5, 10, 15, 20, 25, 30, 40, 50]
      const moc_kvar = moce_std.find(m => m >= moc_wymagana) || 50

      const kary_pln = energia_bierna * 0.3 // Szacunkowe
      const oszczednosc_mc = kary_pln
      const oszczednosc_rok = oszczednosc_mc * 12
      const cena_urzadzenia = moc_kvar * 500 // Szacunkowa cena
      const roi_lata = (cena_urzadzenia / oszczednosc_rok).toFixed(1)

      setResult({
        moc_kvar,
        typ: ma_pv ? 'dynamiczny' : 'klasyczny',
        rekomendacja: {
          model: `LOPI LKD ${moc_kvar} PRO`,
          cena: cena_urzadzenia
        },
        roi_lata,
        kary_pln: Math.round(kary_pln),
        oszczednosc_mc: Math.round(oszczednosc_mc),
        oszczednosc_rok: Math.round(oszczednosc_rok),
        dane: {
          energia_bierna,
          tg_phi,
          ma_pv
        },
        obliczenia: {
          srednia_kvar: srednia_kvar.toFixed(2),
          szczyt_kvar: szczyt_kvar.toFixed(2),
          qc_wzor: (moc_wymagana / 1.2 / (ma_pv ? 1.3 : 1)).toFixed(2)
        }
      })
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            ⚡ <span className="text-indigo-600">Kompensator</span>PRO
          </h1>
          <p className="text-gray-600 mt-1">
            Profesjonalny dobór kompensatora mocy biernej w 30 sekund
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12">
        {!result ? (
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                📄 Wrzuć faktury
              </h2>
              <p className="text-gray-600 mb-6">
                Automatyczna analiza przez AI (OCR)
              </p>

              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <div className="text-6xl mb-4">📸</div>
                <p className="text-gray-700 font-medium mb-2">Dodaj faktury (kilka miesięcy)</p>
                <p className="text-gray-500 text-sm mb-4">JPG, PNG, PDF - maksymalnie 10 plików</p>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept="image/*,application/pdf"
                  className="hidden"
                  id="file-upload"
                  multiple
                />
                <label
                  htmlFor="file-upload"
                  className="inline-block bg-indigo-600 text-white py-2 px-6 rounded-lg cursor-pointer hover:bg-indigo-700 transition-colors"
                >
                  + Dodaj faktury
                </label>

                {/* Lista uploadowanych plików */}
                {files.length > 0 && (
                  <div className="mt-6 space-y-2">
                    <p className="text-sm font-medium text-gray-700 text-left">
                      Dodane faktury ({files.length}):
                    </p>
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between bg-gray-50 p-3 rounded-lg text-left"
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <span className="text-2xl">📄</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="ml-2 text-red-600 hover:text-red-800 font-medium text-sm"
                        >
                          Usuń
                        </button>
                      </div>
                    ))}

                    {/* Checkbox PV */}
                    <div className="flex items-center mt-4 mb-2 text-left">
                      <input
                        type="checkbox"
                        id="ma_pv_upload"
                        checked={manualData.ma_pv}
                        onChange={(e) => setManualData({...manualData, ma_pv: e.target.checked})}
                        className="w-4 h-4 text-indigo-600 rounded"
                      />
                      <label htmlFor="ma_pv_upload" className="ml-2 text-sm text-gray-700">
                        Posiadam instalację fotowoltaiczną (PV)
                      </label>
                    </div>

                    <button
                      onClick={handleUploadAll}
                      disabled={loading}
                      className="w-full mt-2 bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
                    >
                      {loading ? 'Analizuję...' : `Analizuj ${files.length} ${files.length === 1 ? 'fakturę' : 'faktury'} →`}
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                ⚙️ Wprowadź dane ręcznie
              </h2>
              <p className="text-gray-600 mb-6">
                Jeśli znasz dane z faktury
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Energia bierna indukcyjna (kWh)
                  </label>
                  <input
                    type="number"
                    value={manualData.energia_bierna}
                    onChange={(e) => setManualData({...manualData, energia_bierna: e.target.value})}
                    placeholder="np. 612"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Okres rozliczeniowy
                  </label>
                  <select
                    value={manualData.okres_mc}
                    onChange={(e) => setManualData({...manualData, okres_mc: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="1">1 miesiąc</option>
                    <option value="2">2 miesiące</option>
                    <option value="3">3 miesiące</option>
                    <option value="4">4 miesiące</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    tgφ (współczynnik mocy)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={manualData.tg_phi}
                    onChange={(e) => setManualData({...manualData, tg_phi: e.target.value})}
                    placeholder="np. 0.57"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="ma_pv"
                    checked={manualData.ma_pv}
                    onChange={(e) => setManualData({...manualData, ma_pv: e.target.checked})}
                    className="w-4 h-4 text-indigo-600 rounded"
                  />
                  <label htmlFor="ma_pv" className="ml-2 text-sm text-gray-700">
                    Posiadam instalację fotowoltaiczną (PV)
                  </label>
                </div>

                <button
                  onClick={handleManualCalculate}
                  disabled={loading}
                  className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
                >
                  {loading ? 'Obliczam...' : 'Oblicz kompensator →'}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  ✅ Wyniki analizy
                </h2>
                <p className="text-gray-600">
                  Rekomendacja kompensatora dla Twojej instalacji
                </p>
              </div>
              <button
                onClick={() => {
                  setResult(null)
                  setFiles([])
                  setManualData({ energia_bierna: '', okres_mc: 1, tg_phi: '', ma_pv: false })
                }}
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                ← Nowa analiza
              </button>
            </div>

            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-6 text-white mb-8">
              <h3 className="text-2xl font-bold mb-2">
                {result.rekomendacja.model}
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <p className="text-indigo-200 text-sm">Moc</p>
                  <p className="text-2xl font-bold">{result.moc_kvar} kvar</p>
                </div>
                <div>
                  <p className="text-indigo-200 text-sm">Typ</p>
                  <p className="text-xl font-semibold capitalize">{result.typ}</p>
                </div>
                <div>
                  <p className="text-indigo-200 text-sm">Cena (szac.)</p>
                  <p className="text-2xl font-bold">{result.rekomendacja.cena} PLN</p>
                </div>
                <div>
                  <p className="text-indigo-200 text-sm">ROI</p>
                  <p className="text-2xl font-bold">{result.roi_lata} lat</p>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="border border-gray-200 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">📊 Dane z faktury</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Energia bierna:</span>
                    <span className="font-medium">{result.dane.energia_bierna} kWh</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">tgφ obecne:</span>
                    <span className="font-medium">{result.dane.tg_phi}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Kary miesięcznie:</span>
                    <span className="font-medium text-red-600">{result.kary_pln} PLN</span>
                  </div>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">💰 Oszczędności</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Oszczędność/mc:</span>
                    <span className="font-medium text-green-600">~{result.oszczednosc_mc} PLN</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Oszczędność/rok:</span>
                    <span className="font-medium text-green-600">~{result.oszczednosc_rok} PLN</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Zwrot inwestycji:</span>
                    <span className="font-medium">{result.roi_lata} lat</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
              <h4 className="font-semibold text-gray-900 mb-3">🔍 Jak to policzyliśmy?</h4>
              <div className="text-sm text-gray-700 space-y-2">
                <p>
                  <strong>1. Średnia moc bierna:</strong> {result.obliczenia.srednia_kvar} kvar
                </p>
                <p>
                  <strong>2. Szczyt:</strong> {result.obliczenia.szczyt_kvar} kvar
                  (średnia × {result.dane.ma_pv ? '10 (instalacja PV)' : '6'})
                </p>
                <p>
                  <strong>3. Zapasy:</strong> +{result.dane.ma_pv ? '30% (PV) + ' : ''}20% (rozwój) = <strong>{result.moc_kvar} kvar</strong>
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <button className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700">
                📄 Pobierz raport PDF
              </button>
              <button className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-300">
                📧 Wyślij na email
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-800 font-bold mb-2">❌ Błąd</p>
            <p className="text-red-700 text-sm whitespace-pre-wrap font-mono">{error}</p>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600 text-sm">
          <p>© 2025 KompensatorPRO | Powered by <a href="https://sundek-energia.pl" className="text-indigo-600 hover:underline">Sundek Energia</a></p>
        </div>
      </footer>
    </div>
  )
}

export default App
