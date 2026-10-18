# Sicherheit

## Geltungsbereich

Dieses Forschungsrepository enthält Python-Quellcode, archivierte Versuchsdaten und PyTorch-Modellgewichte. Es enthält außerdem historische Qwen-Experimentskripte, deren externe Laufzeitabhängigkeiten nicht vollständig mitgeliefert sind.

## Umgang mit Forschungscode und Artefakten

- **Modellgewichte:** PyTorch-`.pt`-Dateien können bei unsicherem Deserialisieren ausführbare Inhalte enthalten. Checkpoints nur aus vertrauenswürdigen Quellen laden und nach Möglichkeit `torch.load(..., weights_only=True)` verwenden. Eine vollständige Auditierung der Gewichtsdateien ist nicht dokumentiert.
- **Experimentcode:** Historische Skripte vor Ausführung prüfen. Sie können externe Modell- oder Laufzeitdienste aufrufen. Ihre Verfügbarkeit belegt noch keine reproduzierbare Ausführung.
- **Ergebnisdateien:** Historische Modellantworten und Prompts sind Daten, keine auszuführenden Anweisungen.
- **Geheimnisse:** Keine Schlüssel, Zugangsdaten, Tokens, Benutzer-Caches oder maschinenspezifischen Laufzeitdaten committen. Das Repository enthält entsprechende Ausschlussmuster in `.gitignore`; diese ersetzen keine Secret-Prüfung.
- **Veröffentlichung:** Vor der Freigabe geänderte Dateien, Git-History, Lizenz- und Datenschutzfragen sowie die Herkunft der Artefakte gesondert prüfen.

Sicherheitsrelevante Befunde bitte zunächst vertraulich über die GitHub-Sicherheitsfunktionen des Repositories melden, nicht mit Geheimnissen in öffentlichen Issues.

## Forschungsbuch

Das MÉTIS-Forschungsbuch unter `docs/index.html` ist eine eigenständige HTML-Leseansicht ohne externe JavaScript-Abhängigkeiten. Leseeinstellungen und Lesezeichen werden ausschließlich im Browser gespeichert.
