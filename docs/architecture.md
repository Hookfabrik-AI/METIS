# Modellarchitektur · MÉTIS P2

Der hier archivierte `research/p2/model.py` beschreibt den experimentellen P2-Stand (kein allgemeines Sprachmodell). Seine `Net()`-Standardkonfiguration enthält **679.571 trainierbare Parameter** (aus den Modulparametern der Klasse ermittelt, ohne Checkpoint-Laden).

## Aufbau

- **Modelltyp:** kleiner Transformer-Encoder für symbolische Constraints und Variablen.
- **Breite / Tiefe:** `d=128`, vier Encoder-Layer, vier Attention-Heads, Feedforward-Breite `256`, Dropout `0.0`.
- **Eingaberepräsentation:** ein Klassentoken, maximal 24 Constraint-Tokens und maximal 12 Variable-Tokens; Domänen und Constraints werden als eingebettete Struktur übergeben.
- **P2-spezifischer Eingriff:** Je Constraint-Slot werden Variablen-ID, Koeffizient/Vorzeichen und Slotposition gemeinsam über ein kleines MLP (`bind`) codiert und anschließend akkumuliert. Damit wird die in P1 beobachtete mehrdeutige Bindung dieser Merkmale adressiert.
- **Ausgabe:** pro Variable Logits über einen Wertewortschatz von 16 Symbolen (`0..15`), mit Domänenmaske. Zusätzlich zwei spezialisierte Köpfe (`head_p`, `head_q`) für Selbstbeurteilung und Strategiewahl, die in Stage C trainiert wurden.
- **Feedbackmodi:** frischer Vorschlag, Reparatur mit Verifikatorflags und vorheriger Versuch ohne Flags. Der externe Constraint-Verifikator steht außerhalb des Modells.

## Abgrenzung

Die Architektur verarbeitet formalisierte Aufgabenobjekte, **keine freie natürliche Sprache**. Die behauptete P2-Bindung ist eine konkrete Implementierungsänderung; sie ist kein Nachweis allgemeiner Reasoning-Kompetenz. Vollständige Trainings-/Evaluationsdetails liegen in den Quellskripten und den archivierten Resultaten; die Qwen-Vierarm-Studie verwendete `seed0/C/best.pt`.
