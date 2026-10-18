# Bekannte Grenzen und offene Reproduktionslücken

1. **Keine unabhängige Wiederholung durchgeführt:** Die Rohdaten wurden geprüft/neu zusammengefasst, die neuronalen bzw. Qwen-Runs aber nicht erneut gestartet.
2. **Nicht isoliert repliziert:** Die 12-Aufgaben-Stichprobe ist klein; der Vierarm-Aggregatwert nutzt run_03, run_04 und run_05. T01 wurde mehrfach ausgeführt; die Auswertungsregel ist explizit und ändert keine Rohdaten.
3. **Nicht vollständig portabler Qwen-Runner:** Historische Qwen-Quellen importieren `res1_instance` und `resource_profile` aus einer nicht enthaltenen, privaten MOIRAI-Runtime. Die lokalen Pfade wurden als sichtbare Platzhalter ersetzt. Keine Veröffentlichung privater Runtime-Komponenten und kein Vortäuschen eines funktionierenden Ersatzes.
4. **Modelldigest unvollständig:** `qwen3.5:latest` ist versionsveränderlich. Hardwarezustände und Teile des Ollama-Model-Load-/Prompt-Overheads sind nicht kontinuierlich als einheitliche vollständige E2E-Kosten erfasst.
5. **P1 fehlt:** Das P2-Evaluationsprogramm verlangt P1-Quelldateien und Checkpoints für Vergleiche C5/C6; diese lagen nicht im übergebenen Archiv. Die P2-Ergebnisse sind archiviert, aber für alle Teilfragen noch nicht eigenständig reproduziert.
6. **Gewichte:** Sieben von vielen Trainings-Checkpoints wurden bewusst ausgewählt. Es handelt sich um ungeprüfte `.pt`-Artefakte aus dem Archiv; lade diese nur aus vertrauenswürdigen Quellen, bevorzugt mit `torch.load(..., weights_only=True)`.
7. **Keine Aussagen über frei formulierte Probleme:** Aufgabe/Constraints wurden dem LLM bereits formalisiert übergeben. Übertragbarkeit auf Alltagssprache, neue Domänen, größere LLMs und Mehragentensysteme nicht belegt.
8. **Erfolgsquote:** Der frühere Qwen-Hinweis konnte Ankerfehler begünstigen; in der Vierarm-Stichprobe erreichte MÉTIS mit 10/12 gegenüber 11/12 ohne Hinweis eine geringere Lösungsquote.
9. **Keine Lizenz gewählt:** Die wissenschaftliche Veröffentlichung und Nachnutzung müssen vorher ausdrücklich freigegeben werden.

10. **P3 nur als Meldung:** Für den 18.10.2026-Bericht fehlen weiterhin P3-Checkpoints, Konfigurationen, Rohresultate und replizierbare Auswertungen. Siehe `docs/p3-status.md`.
