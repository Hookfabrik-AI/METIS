# MÉTIS — Research Repository

**HOOKFABRIK · Independent AI Research · 18. Oktober 2026**

**Evidenzstatus:** P2 ist durch archivierten Quellcode, Datensätze, Modellgewichte und Auswertungen dokumentiert. Für P3 liegt ein Ergebnisbericht vor; zugehörige Checkpoints und Rohdaten sind bislang nicht enthalten. Die historischen Trainings- und Qwen-Versuche wurden für dieses Repository nicht erneut ausgeführt.

[**Forschungsbuch lesen**](docs/index.html) · [Methodik](docs/methods.md) · [Ergebnisse](docs/findings.md) · [Reproduzierbarkeit](REPRODUCIBILITY.md)

## Forschungsgegenstand

MÉTIS ist ein kleines, selbst trainiertes Transformer-Modell mit **679.571 trainierbaren Parametern** in der archivierten P2-Standardkonfiguration, spezialisiert auf strukturierte Constraint-Aufgaben. Im P2-Piloten wurde eine Bindung von Variable, Koeffizient/Vorzeichen und Slotposition innerhalb der Constraint-Repräsentation eingeführt. In einem weiteren Experiment wurde untersucht, ob das Modell auf schwacher, ausgelasteter Hardware einem größeren lokalen Sprachmodell (Qwen) nützliche Lösungskandidaten liefern kann.

Die **offene Kernfrage** ist nicht nur, ob ein Hint Qwen schneller macht, sondern ob **der gelernte Inhalt von MÉTIS** einen messbaren Vorteil gegenüber gleich präsentierten, einfachen alternativen Kandidaten liefert — bei vergleichbarer Korrektheit und unter Einschluss aller Laufzeitkosten.

## Forschungsstände

| Stand | Evidenzstatus | Verfügbare Artefakte |
|---|---|---|
| **P2** | Historische Evidenz archiviert; Integrität prüfbar | Quellcode, Datensplits, sieben Gewichte, Evaluationsdateien |
| **P3** | **Berichtet, nicht unabhängig geprüft** | Ergebnisbericht vom 18.10.2026; **keine P3-Rohdaten oder Gewichte** |
| **Qwen-Vierarm** | Aus archivierten Runs nachaggregiert | Historischer Versuch mit **P2**, **nicht P3** |

Für P3 wurden bei unveränderter Modellarchitektur laut Bericht C2–C6 bestanden, darunter C4. Zahlen, Grenzen und Widersprüche stehen unter [P3-Status](docs/p3-status.md). Der Aufnahmeplan für echte P3-Artefakte steht in [P3_INGESTION.md](P3_INGESTION.md). **P3-Aussagen sind noch keine durch dieses Repo reproduzierten Befunde.**

## Momentaufnahme aus den vorliegenden Rohdaten

Das spätere Vierarm-Experiment verwendet zwölf strukturierte Aufgaben. Für diese Repositorium-Auswertung gilt: T01 aus run_04, T02–T05 aus run_03, T06–T09 aus run_04, T10–T12 aus run_05. **Das sind fortgesetzte/erneute Teilruns und keine unabhängig replizierte, vorab definierte einzige Messserie.** Ein Wiederholungsversuch von T01 aus run_03 bleibt als Originaldatensatz separat erhalten.

| Verfahren | korrekt / Aufgaben | Qwen-Ausgabe-Tokens (Summe) | Qwen-Antwortzeit (Summe, s) |
|---|---:|---:|---:|
| A: Qwen ohne Kandidat | 11/12 | 40.559 | 2.045,3 |
| B: Qwen + MÉTIS-Kandidat | 10/12 | 36.241 | 1.892,8 |
| C: Qwen + Zufallskandidat | 10/12 | 52.074 | 2.819,2 |
| D: Qwen + Min-Conflicts (256 Prüfungen) | 11/12 | 24.910 | 1.367,5 |

MÉTIS lag hier gegenüber A bei **10,6 % weniger Qwen-Ausgabe-Tokens**, bei einer geringeren Erfolgsquote. Die einfache Min-Conflicts-Baseline schnitt besser ab. Das belegt **keinen kausalen generellen Beschleunigungseffekt durch ein neuronales Modell**; Fallzahl, Mehrfachversuche, Promptunterschiede, Laufzeitstreuung und fehlende Kontrollbedingungen begrenzen die Aussagekraft. Die angegebene Antwortzeit ist **nicht** die vollständige End-to-End-Laufzeit aller Varianten.

Der ältere Zweibedingungsversuch (run_01/02) zeigte eine größere Ersparnis bei den normalen Aufgaben, verwendete aber unterschiedliche Hint-Inhalte und enthält keinen isolierten Methodenvergleich. Siehe [Befunde](docs/findings.md), [Modellarchitektur](docs/architecture.md), [Methodik](docs/methods.md) und [Grenzen](docs/limitations.md).

## Aufbau

```text
research/p2/             historische P2-Trainings-, Modell- und Auswertungsskripte
research/qwen/historical/ historische, pfadbereinigte Qwen-Experimentquellen
models/p2/               sieben ausgewählte P2-best.pt-Gewichte (3 Seeds, A/B + seed0/C)
datasets/p2/             originale generierte P2-Datensplits + SHA-256-Manifest
evidence/p2/             gespeicherte P2-Evaluationen und individuelle Ergebnisse
evidence/qwen/           die relevanten Qwen-Aufgaben, Antworten, Ergebnisse und Summaries
evidence/index.json      maschinenlesbare Forschungskennzahlen + Geltungsbereich
evidence/provenance.json Quelle, Hashes, dokumentierte Bereinigungen
scripts/                 unabhängige Integritäts- und Auswertungswerkzeuge
docs/                    Forschungsnotizen, P3-Status, Hypothesen, Grenzen, Freigaberegeln
tests/                   offline ausführbare Unit-Tests für die Evidenz
```

## Schnell prüfen (kein LLM, kein Model-Load notwendig)

```bash
python3 scripts/verify_evidence.py
python3 scripts/summarize_qwen.py
python3 -m unittest discover -s tests -v
```

**Forschung reproduzieren:** Siehe [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Die Datengenerierung und P2-Trainingskette liegen bei; eine vollständige historische P2-C5/C6-Reproduktion verlangt zusätzlich P1-Modelle/-Daten, die im Repository nicht enthalten sind. Die Qwen-Skripte benötigen die nicht enthaltene externe `res1_instance`-/`resource_profile`-Runtime und eine eingefrorene Ollama-Modellversion. Die Quellen sind **keine sofort lauffertige unabhängige Qwen-Benchmarkumgebung**.

## Provenienz und Nutzung

Historische Qwen-Skripte wurden von maschinenspezifischen absoluten Pfaden bereinigt. Original- und abgeleitete SHA-256-Prüfsummen dokumentiert [evidence/provenance.json](evidence/provenance.json). Weitere Einschränkungen sind unter [Bekannte Grenzen](docs/limitations.md) aufgeführt.

Eine Lizenz für Code, Datensätze und Modellgewichte ist bislang nicht festgelegt. Vor Nachnutzung sind die Nutzungsrechte zu klären. Die Kriterien für eine formale Forschungsfreigabe stehen unter [RELEASE_GATE.md](RELEASE_GATE.md).
