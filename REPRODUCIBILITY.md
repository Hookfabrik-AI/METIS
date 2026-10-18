# Reproduzierbarkeit

## 1. Evidenzintegrität (offline, ohne PyTorch)

```bash
python3 scripts/verify_evidence.py
python3 scripts/summarize_qwen.py
python3 -m unittest discover -s tests -v
```

Verifiziert wird ausschließlich der Inhalt dieses Pakets gegen sein `evidence/provenance.json` und das P2-Datensatzmanifest. Der Archivhash ist ein Provenienzhinweis auf die originale Eingabe; das Quellarchiv ist **nicht** zur Prüfung erforderlich. Diese Integritätskontrolle beweist keine korrekte wissenschaftliche Durchführung.

## 2. P2-Code und Daten

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# Auf einer schnellen Maschine optional Dataset-Rekonstruktion in neuem Zielordner:
python3 -I -B research/p2/dataset.py /tmp/metis-regenerated-p2
# Aufwändiges P2-Training (übernimmt NICHT die archivierten Checkpoints):
METIS_PYTHON="$PWD/.venv/bin/python" bash scripts/train_p2.sh
```

Hinweis: Die historische P2-Evaluation (`research/p2/evaluate.py`) erwartet zusätzlich P1-Quelldateien/-Gewichte. Diese wurden nicht mitgeliefert. Zeit-/Numerikgleichheit der ursprünglichen Trainingsruns wird ohne eingefrorene Hardware, Bibliotheken und Umgebung **nicht** garantiert.

## 3. Qwen

Die 2026-10-17-Experimentquellen sind als `historical/` abgelegt; maschinenlokale Pfade wurden zum Schutz der Privatsphäre ersetzt. Sie enthalten weiterhin Imports der fehlenden privaten `res1_instance`-/`resource_profile`-Runtime; sie sind Referenz- und Auditmaterial, **kein direkt lauffertiger öffentlicher Runner**. Die Archivlogs/Antworten liegen in `evidence/qwen`. Die Offline-Aggregation benötigt keine GPU, Ollama oder Modellgewichte.

Für eine unabhängige E2E-Replikation muss ein eigenständiger offener Runner entwickelt und geprüft werden. Danach Modell-Digests, Umgebung, Aufgaben, Seeds, Laufreihenfolge, RAM-/GPU-Auslastung, Cachezustand, Kandidatengenerierung und sämtliche Kostenterme dokumentieren.

## 4. Ergebnisstatus

- **Rechnerische Reaggregation** der gespeicherten Qwen-Evidenz: maschinell prüfbar.
- **SHA-256-Konsistenz** der P2-Datensätze und Quellen: maschinell prüfbar.
- **Historische neuronale Experimente:** nur archiviert, nicht neu ausgeführt.
- **Kausale Zuschreibung/Generalisierung:** offen.

## 5. P3: noch kein reproduzierbares Artefakt

Der Stand P3 ist gegenwärtig ausschließlich als berichtete Fortschrittsnotiz in `docs/p3-status.md` enthalten. Die vorhandenen Integritätsbefehle prüfen **nicht** P3; sie dürfen nicht als Bestätigung von P3-C2–C6 angegeben werden. Für die geplante Aufnahme: [P3_INGESTION.md](P3_INGESTION.md).
