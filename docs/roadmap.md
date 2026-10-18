**P3-Fortschritt:** [Gemeldeter Stand und Limitierungen](p3-status.md) · [Aufnahme echter P3-Artefakte](../P3_INGESTION.md). Dies ist keine bestätigte P3-Evidenz.

# Forschungsfahrplan (Vorschlag, nicht bereits durchgeführt)

1. **Evidenz einfrieren:** Repro-Umgebung mit genauen Python/PyTorch/Ollama- und Qwen-Modell-Digests; Hardware-/Speicher-/Cacheprotokoll; feste Aufgaben-IDs und gesicherter Quellhash.
2. **Qwen-Runner entkoppeln:** Abhängigkeit von der privaten MOIRAI-Instanz-Runtime entfernen, ohne das ursprüngliche Experiment nachträglich umzudeuten; Änderungen unabhängig prüfen.
3. **Neue gepaarte Kontrollstudie:** Qwen allein, neutrales Textfragment, zufälliger Kandidat, deterministischer Regelkandidat, Min-Conflicts-Kandidat, MÉTIS-Kandidat und (optional) ablatierte MÉTIS-Features; identisches Hint-Format/Tokenbudget und randomisierte Armreihenfolge.
4. **Schwierigkeits- und OOD-Test:** mehr unterschiedliche Familien, härtere und unbekannte Constraints, klare Trennung zwischen Distribution und echten neuen Aufgabentypen.
5. **Risiko & Kalibrierung:** testbare Konfidenzkalibrierung, Gate/Abstention, Missinformation-Sensitivität, Verankerung und Qualitätsverlust.
6. **Vollständige Kostenbilanz:** Modell-, Verifikations-, Tokenisierungs-, Cache-, Prompt- und Speicher-Overhead in End-to-End-Walltime; reproduzierte Trials unter begrenztem CPU-/GPU-/RAM-Budget.
7. **Abnahme:** unabhängige Quellcode- und Datenprüfung, reproduzierbare Ablation, dokumentierter negativer Befund und menschliche Freigabe vor Veröffentlichung.
