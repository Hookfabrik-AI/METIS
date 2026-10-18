# HOOKFABRIK · Forschungsnotiz
## MÉTIS P2 × Qwen — Neuronale Lösungsvorschläge als Unterstützung eines Sprachmodells

**Status:** Experiment abgeschlossen; unabhängige Prüfung `VERIFIED_WITH_NOTES`  
**Einordnung:** Eigenständiger Forschungsschritt nach MÉTIS P2; *P3* ist lediglich ein möglicher Arbeitstitel, keine neue Modellversion.  
**Evidenzgrundlage dieser Notiz:** Vom Projekt übermittelter Abschlussbericht einschließlich Zusammenfassung des unabhängigen Codex-Reviews. Die Rohdaten und Quelldateien wurden für diese Notiz nicht selbst eingesehen.

### 1. Forschungsfrage

Kann ein kleines, auf strukturierte Constraint-Aufgaben trainiertes CPU-Modell (MÉTIS P2) ein größeres lokales Sprachmodell (`qwen3.5:latest`) dabei unterstützen, Aufgaben mit weniger Generierungsaufwand und ohne Qualitätsverlust zu lösen?

Eine zweite, engere Frage ist, ob *die gelernten MÉTIS-Vorschläge selbst* einen Vorteil bringen – oder bereits irgendein vorgegebener Kandidat die Generierung verkürzt.

### 2. Versuchsaufbau

- **MÉTIS:** Unveränderter P2-Checkpoint; experimenteller Adapter erzeugt eigene Lösungskandidaten, die zwei wahrscheinlichsten Werte je Variable und eine modellierte Selbsteinschätzung. Ein Reparaturvorschlag ist vorgesehen, wurde im ausgewerteten Lauf aber nicht ausgelöst.
- **Qwen:** `qwen3.5:latest`, Thinking deaktiviert, Temperatur 0.
- **Eingabe:** Zwölf neue, bereits formal als Bedingungen dargestellte Aufgaben; die Übersetzung aus natürlicher Alltagssprache wurde **nicht** untersucht.
- **Vergleich:** Qwen ohne Hinweis gegenüber Qwen mit dem vollständigen MÉTIS-Hinweispaket.
- **Korrektur:** Bei einer falschen auswertbaren Antwort hätte der Prüfer in beiden Varianten lediglich verletzte Bedingungen zurückgemeldet. Die MÉTIS-Reparatur wurde nicht aktiviert, weil entsprechende auswertbare Fehlantworten ausblieben.
- **Einschränkung:** Kein Vergleich mit Zufallskandidaten, einfachen Regelkandidaten oder einem gleich langen neutralen Hinweis; pro Aufgabe und Bedingung nur ein Lauf.

### 3. Beobachtete Ergebnisse

| Messgröße | Qwen allein | Qwen + MÉTIS-Hinweis |
|---|---:|---:|
| Normale Aufgaben korrekt | 8/8 | 8/8 |
| Schwere Aufgaben korrekt | 3/4 | 2/4 |
| Insgesamt korrekt | **11/12** | **10/12** |
| Ausgabe-Tokens, normal | 26.277 | 8.595 |
| Ausgabe-Tokens, schwer | 22.668 | 21.012 |
| Ausgabe-Tokens, gesamt | **48.945** | **29.607** |
| Gemessene Qwen-Laufzeit, gesamt | **2.388 s** | **1.580 s** |

Rechnerisch wurden über alle zwölf Aufgaben **19.338 Ausgabe-Tokens bzw. 39,5 %** weniger erzeugt. Die aggregierte gemessene Qwen-Zeit lag **808 s bzw. 33,8 %** niedriger. Bei den acht normalen Aufgaben betrug die Tokenersparnis etwa **67,3 %**; bei den vier schweren Aufgaben lediglich **7,3 %**.

Diese Unterschiede sind **Beobachtungen unter zwei Promptbedingungen**, kein belegter kausaler Effekt des trainierten MÉTIS.

### 4. Konkrete Beobachtungen und Fehlermuster

- In den acht normalen Aufgaben gab MÉTIS fünfmal direkt einen richtigen Kandidaten aus. Qwen prüfte die Bedingungen und konnte solche Kandidaten übernehmen.
- In den übrigen normalen Aufgaben entdeckte Qwen falsche Vorschläge und übernahm sie nicht blind.
- In **allen vier schweren Aufgaben** war der MÉTIS-Vorschlag falsch.
- **T11 (Logik):** Qwen allein löste die Aufgabe, mit MÉTIS-Hinweis nicht. Im Verlauf verwarf Qwen einen potenziell richtigen Ansatz unter Verweis auf die hochkonfidente MÉTIS-Präferenz (`x4 = 1`, 97 %). Die **Verankerung ist belegt**, aber **nicht als alleinige Fehlerursache**, weil Qwen zusätzlich eigene Logikfehler machte und der verworfene Ansatz nicht die einzige gültige Lösung war.
- **T09:** Beide Bedingungen scheiterten. Antworttexte eines abgebrochenen, *nicht ausgewerteten* Laufteils sind nicht archiviert.
- **T10/T12:** Beide Bedingungen lösten die Aufgaben trotz falscher MÉTIS-Vorschläge; mit Hinweis war die Bearbeitung etwas schneller.

### 5. Unabhängige Prüfung durch Codex

**Urteil: `VERIFIED_WITH_NOTES`.** Nach dem übermittelten Prüfbericht:

- **Integrität:** Alle zwölf MÉTIS-Vorschläge wurden aus dem gespeicherten Checkpoint reproduziert; es handelt sich um echte Modellausgaben.
- **Zeitmessung:** Berichtete Summen und Zeiten stimmen; die Messung deckt sich mit Ollama bis auf höchstens 0,05 s Abweichung.
- **Berichtsgenauigkeit:** Sechs geforderte Präzisierungen wurden eingearbeitet.
- **Ursächlichkeit:** **Nicht bestätigt.** Der Test vergleicht vollständige Promptpakete, nicht isoliert die Qualität von MÉTIS gegenüber generischen Kandidaten.

### 6. Grenzen der Evidenz

1. Qwens beobachtete Generierungsrate schwankte zwischen etwa **18 und 31 Tokens/s**; die Ursache blieb offen.
2. Prompts mit MÉTIS waren etwa **doppelt so lang** wie die Prompts ohne Hinweis.
3. Ollama verwendete zum Teil zwischengespeicherte Eingaben wieder. Das kann die Laufzeit beeinflussen; **die Tokenzahlen sind daher die robustere Messgröße**.
4. Zwei Ollama-Teilzeiten (Modellladen und Prompt-Einlesen) wurden nicht in `results.json` persistiert; Rekonstruktion wäre nur über Logs möglich.
5. Die MÉTIS-Rechenzeit wurde für die **vier schweren Aufgaben mit insgesamt 0,28 s** gemessen. Für Lauf 1 ist kein überlieferter Messwert verfügbar; **keine Hochrechnung**.
6. Zwölf Aufgaben mit je einem Durchlauf erlauben keine robuste Verallgemeinerung; kein Zufalls-/Regel-/Neutralhinweis als Kontrollbedingung.
7. Die Aufgaben lagen bereits formalisiert vor; natürliche Sprache, allgemeines Reasoning, MOIRAI, NOUMORA sowie 14B- oder Frontier-Modelle wurden hier nicht getestet.

### 7. Forschungsbefund

**Nachgewiesen:** Ein kleines trainiertes CPU-Modell kann echte Kandidaten für ein größeres LLM bereitstellen; Qwen nutzt diese Kandidaten sichtbar. In diesem konkreten Versuch erzeugte Qwen mit dem vollständigen MÉTIS-Hinweis bei normalen Aufgaben erheblich weniger Tokens. Bei schweren Aufgaben brachte das Hinweispaket wenig Ersparnis und fiel hinsichtlich Lösungsquote zurück.

**Nicht nachgewiesen:** Dass die **trainierten Inhalte** von MÉTIS (statt allgemein eines vorgegebenen Kandidaten bzw. eines geänderten Promptformats) die Einsparung verursachten; dass der Ansatz die allgemeine Problemlösefähigkeit steigert; dass eine entsprechende Beschleunigung auf Qwen 14B, Claude oder Codex übertragbar ist.

**Neue Forschungsfrage:** Wie lassen sich hilfreiche spezialisierte Vorschläge so kennzeichnen, prüfen und gewichten, dass ein LLM weniger suchen muss, ohne richtige eigene Lösungsansätze wegen überkonfidenter falscher Hinweise zu verwerfen?

### 8. Einordnung und Dokumentationsverweise

Dies ist ein **Funktions- und Beobachtungsnachweis mit gemischtem Ergebnis**, noch kein kausal isolierter Effizienznachweis von MÉTIS. Es gibt keinen Anlass, das Ergebnis entweder als gescheitert oder als allgemeine Tokenoptimierung zu verkaufen.

Lokal vom Projekt genannte Referenzen (Pfadangaben, keine hier neu verifizierten Dateien):

- `NOUMORA_THINKING_20261016/10_METIS_QWEN_E2E_ERGEBNIS.md` – überarbeiteter Ergebnisbericht.
- `reviews/CODEX_METIS_QWEN_E2E_R1.md` – unabhängiger Prüfbericht.
- `<LOCAL_QWEN_RUN_01>/` – archivierte Rohdaten, Prompts und Antworten.

**Publikationsregel:** Bei Veröffentlichung die vollständigen Berichte und reproduzierbaren Artefakte verlinken; diese Notiz ersetzt sie nicht. Keine weitergehenden Effizienz- oder Kausalitätsansprüche aus den obigen Zahlen ableiten.
