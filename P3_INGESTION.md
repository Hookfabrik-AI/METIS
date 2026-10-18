# P3-Aufnahme ins MÉTIS-Forschungsrepository

**Der aktuell vorliegende P3-Fortschrittsbericht ist nicht dasselbe wie ein P3-Release.** Für einen belegten P3-Stand werden folgende Dateien benötigt — aus dem aktiven Entwicklungsprojekt **nur nach separater Auswahl und Sicherheitsprüfung**.

## Aufnahmecheckliste

- [ ] Commit/Source-Snapshot der P3-Implementierung, einschließlich Code-Diff zur archivierten P2-Modellarchitektur; keine absoluten Privatpfade
- [ ] Training-Configs, Hyperparameter, Seeds, Versionsnummern und Beschreibung der Änderungen an Daten und numerischen Konstanten
- [ ] P3-Datensplits und maschinenlesbare SHA-256-Manifeste; Generator-Quellen, Train/Dev/Test-Trennung und Dokumentation der Filterkorrektur
- [ ] P3-Checkpoints (nur geprüfte, freigegebene Gewichte); genaue Zuordnung Modell ↔ Seed ↔ Run ↔ Test
- [ ] Maschinenlesbare Testberichte zu C2–C6, einschließlich individueller Aufgabenresultate für gepaarte Vergleiche und Definition von FB@4 und L−1
- [ ] Statistische Tests zu C4 (Berechnung, Baseline/Regel, N, zufällige Seeds, Effektgrößen) sowie vollständige Kostenrechnung inkl. Verifikator und Vorwärtsläufen
- [ ] K4/K5-Fehlerfälle, Min-Conflicts-Protokoll und vereinheitlichte Baselines
- [ ] Unabhängig ausführbare Reaggregationsskripte und ein Verifikationsbericht
- [ ] Secret-, Lizenz-, Datenschutz- und Herkunftsprüfung des konkreten Upload-Pakets
- [ ] Reviewer-Freigabe und ausdrückliche Human Acceptance vor öffentlichem Release

## Vorgeschlagene Zielpfade nach erfolgreicher Prüfung

```text
research/p3/                versionierte P3-Implementierung und Konfigurationen
datasets/p3/                freigegebene Splits samt Hashmanifest
models/p3/                  freigegebene Modellgewichte mit Modellkarten
evidence/p3/                Rohresultate, Auswertung, Seeds, Provenienz
scripts/                    separate P3-Integritäts- und Reaggregationsbefehle
```

Diese Verzeichnisse werden **nicht mit Platzhalter-Rohdaten aufgefüllt**. Bis zur Aufnahme der echten Artefakte verbleiben P3-Zahlen als gemeldete Resultate in `docs/p3-status.md`.
