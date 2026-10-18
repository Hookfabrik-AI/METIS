# Freigabegate · MÉTIS (nicht automatisch erfüllt)

**Zweck:** Prüfkriterien für eine geplante Veröffentlichung oder wissenschaftliche Versionsfreigabe. Sicherheits-, Lizenz- und Evidenzfreigaben sind getrennt zu beurteilen.

- [ ] Sicherheitsprüfung aller Repo-Dateien inkl. Git-History; keine privaten Schlüssel, Tokens, privaten Laufzeitdaten oder nicht freigegebenen Codeabhängigkeiten.
- [ ] Lizenzentscheidung für Quellcode, Modelldaten/Gewichte und Datensätze; Rechts- und Herkunftsprüfung.
- [ ] Echte P3-Artefakte erst nach separatem Security-/Herkunftsgate übernehmen, P3-Claims dann unabhängig neu aggregieren.
- [ ] Versionierte, unabhängig ausführbare Forschungstests mit fixierten Inputs/Weights/Modelldigests/Umgebungen.
- [ ] Wiederholte gepaarte Studien und ausreichend Stichproben; Unsicherheit und Effektstärken dokumentiert.
- [ ] Regeln, Zufall, Min-Conflicts, neutraler Hinweis und MÉTIS-Hinweise unter vergleichbaren Bedingungen.
- [ ] Korrektheit, Fehlverankerung, OOD-Generalisierung, Kosten, Ressourcenbudget und Grenzen geprüft.
- [ ] Fehlende P1-Artefakte entweder reproduzierbar beigefügt oder Claims darauf reduziert.
- [ ] Unabhängiger Reviewer bestätigt Evidenz und Dokumentationsgenauigkeit.
- [ ] **Human Acceptance** für konkrete öffentliche Artefakte/Claims/Rechte.

Auch bei öffentlich sichtbarem Repository gilt: keine Aussage „MÉTIS beschleunigt große Modelle allgemein“ ohne entsprechende Evidenz. Eine Open-Source-Freigabe entsteht nicht allein aus GitHub-Sichtbarkeit. Unbelegte Behauptungen gehören als Hypothesen in `docs/roadmap.md`.
