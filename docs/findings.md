> **Versionen trennen:** Der neuere P3-Fortschritt ist [nur als Projektmeldung dokumentiert](p3-status.md). Alle in dieser Datei aus Archivdaten dargestellten P2-/Qwen-Befunde bleiben historische P2-Befunde.

# Forschungsbefunde · Evidenz und Einordnung

## P2: trainierter neuraler Constraint-Vorschläger

Die P2-Quelldateien und sieben Datensplits sind anhand der ursprünglichen SHA-256-Dokumentation bzw. des Datensatz-Manifests anhand der archivierten Daten geprüft. P2 ergänzt die Slot-Bindung (Variable, Koeffizient/Vorzeichen, Position). Die historische Auswertung liegt unter `evidence/p2/P2_EVAL.json` und enthält Vergleiche mit untrainiertem Modell, mit/ohne Feedback sowie mit P1. Einige P1-Abhängigkeiten fehlen hier; deshalb sind die auf P1 bezogenen Aussagen in diesem Repo vorerst **archivierte Befunde** und keine vollständig eigenständig reproduzierten Befunde.

Auch die gelernte Strategiewahl war auf dem P2-Testset nicht überzeugend besser als eine einfache Regel: `C4` wurde laut gespeicherter Auswertung **nicht bestätigt** (p = 0,906). Ein nicht signifikanter Befund darf nicht als Erfolgsnachweis interpretiert werden.

## Qwen: früher Zweibedingungsvergleich (run_01 und run_02)

Archivierte Projektnotiz `historical-qwen-note.md`: 12 Aufgaben, 11/12 Qwen allein vs. 10/12 Qwen mit vollem MÉTIS-Hinweispaket; 48.945 vs. 29.607 Output-Tokens und 2.388 vs. 1.580 Sekunden Qwen-Zeit. Die normalen Aufgaben waren in beiden Varianten 8/8 korrekt; bei schwierigen Aufgaben lag MÉTIS-Hinweis schlechter. Der Hinweis enthielt mehr Information als nur einen neutral eingefügten Lösungskandidaten. Das ist **keine** isolierte kausale Evaluation der Modellinhalte.

## Vierarm-Kontrollvergleich (run_03–05)

Alle drei Kandidatenarme B/C/D nutzen laut überliefertem Quellcode denselben Einleitungstext und unterscheiden sich im Kandidatenverfahren. Die Aufgaben liegen strukturiert, nicht in freier Alltagssprache vor. Die Vergleichssummen sind aus `results.json` neu aggregiert; keine neue Qwen-Ausführung.

| Arm | Herkunft des Kandidaten | Gelöst | Output-Tokens | Qwen-Zeit in s | korrekte Kandidaten |
|---|---|---:|---:|---:|---:|
| A | kein Kandidat | 11/12 | 40.559 | 2.045,3 | — |
| B | MÉTIS P2 (greedy) | 10/12 | 36.241 | 1.892,8 | 5/12 |
| C | gleichverteilt zufällig | 10/12 | 52.074 | 2.819,2 | 0/12 |
| D | Min-Conflicts (Budget 256) | 11/12 | 24.910 | 1.367,5 | 7/12 |

**Vorläufige Interpretation:** Bei den überwiegend leichteren Aufgaben helfen MÉTIS-Kandidaten gegenüber ganz ohne Kandidat oft beim Reduzieren der Generierung. Auf schwierigen Aufgaben verlagert sich das Verhältnis; dort sind MÉTIS-Kandidaten sämtlich falsch (siehe archivierte erste Vergleichsstufe), und die Gefahr von Fehlverankerung und Zusatzarbeit ist sichtbar. Die heuristische Baseline D erzielt in dieser Stichprobe die geringste Ausgabe und mindestens dieselbe Lösungsquote wie A. Weder die Güte generischer „Hints“ noch die Leistung von MÉTIS auf neuen offenen Aufgaben ist damit abschließend bestimmt.

**Hinweis zur Zusammensetzung:** T01 wurde in run_03 und run_04 getestet. Für die Tabelle wurde explizit die spätere T01-Aufzeichnung aus run_04 verwendet. Die frühere Aufzeichnung bleibt erhalten, damit kein einzelner Wert unbemerkt verschwindet. Das Zusammenführen von Runs mit unterschiedlichen Speicherzuständen darf nicht als sauber kontrollierte replizierte Studie ausgegeben werden.
