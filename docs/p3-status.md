# MÉTIS P3 — vorläufiger Fortschrittsbericht

**Stand:** 18.10.2026 · **Nachweisstatus:** vom Projektteam gemeldet, **nicht unabhängig anhand von P3-Rohdaten/Checkpoints verifiziert**.

Dies ist ein **Forschungsfortschrittsbericht**, keine unabhängig replizierte P3-Studie. P3-Trainings- und Auswertungsartefakte sind in diesem Repository **nicht enthalten**. P2-Artefakte dürfen nicht als P3-Artefakte interpretiert werden.

## Gemeldete Änderungen gegenüber P2

- **Modellarchitektur:** laut Projektmeldung unverändert; P3 wurde erneut/weiter trainiert. Der exakte Trainings- und Daten-Unterschied kann ohne P3-Code/Configs noch nicht auditiert werden.
- **C2/C3:** weiterhin bestanden.
- **C4 (gelernte Steuerung gegen Regel):** P2 nicht bestanden (`p = 0,906`); P3 bestanden (gemeldete Differenz `+0,015`, `p < 0,001`). Der Vorteil entsteht laut Bericht durch gesparte Prüfungen; P3 benötigt mehr Vorwärtsläufe. Ohne Prüfkosten ist die Policy schlechter.
- **C5 K4, gepaarte Aufgaben P3−P2:** L−1 `+6` bis `+10` Prozentpunkte; FB@4 `+8` bis `+19` Prozentpunkte.
- **C6 K1, P3−P2:** L−1 `+6` bis `+12` Prozentpunkte; FB@4 `+9` bis `+13` Prozentpunkte.
- **FB@4 über die Klassen:** gemeldet etwa `0,80–0,82`; als P2-Referenz nennt der Bericht etwa `0,75` **auf dessen eigenem Testset**, deshalb **kein direkter gepaarter Vergleich** allein aus diesen Zahlen.
- **C4-Entscheidungszählung:** 835-mal „reparieren“ vs. 209-mal „neu lösen“ (nicht unabhängig reaggregiert).

## Einschränkungen / negative Befunde

- **K4 bleibt schwach:** gemeldetes FB@4 `0,44–0,51`, unter Min-Conflicts bei 256 Prüfungen (`0,61`).
- **Feedback statt Neu-Sampling:** Vorteil laut Bericht bei nur ca. 2–3,5 Prozentpunkten.
- **K5 uneinheitlich:** auf schweren Aufgaben laut Bericht für Seed 1 schlechter als P2.
- **Keine isolierte Ablation:** zusätzliche Daten und numerische Konstanten wurden zusammen geändert. Der Anteil jedes Hebels ist unklar.
- **Trainingsbudget:** gegen Ende stiegen Lernkurven noch an. Das sagt etwas über den beobachteten Trainingsverlauf, beweist aber nicht, dass längeres Training hilft.
- **Datenqualität:** ein zunächst zu strenger Filter hätte die Testsets verzerrt. Der Lauf wurde laut Projektmeldung **vor dem Training** angehalten und nach Korrektur neu begonnen.
- **Umgebung:** berichtet wurde Training auf ungefähr halber CPU bei niedriger Priorität. Hardware-/Laufzeit-Logs fehlen hier.

## Quellenstatus und Anspruchsniveau

Quelle: Projektbericht vom 18.10.2026. Zahlen wurden aus einer Ergebnisdarstellung **übertragen**, nicht aus maschinenlesbaren P3-Rohdaten neu berechnet. Keine detaillierte Aussage zu Signifikanzmethoden, Stichprobenumfang, exakten C2/C3-Schwellen, Runs und Konfidenzintervallen möglich, solange deren Auswerteartefakte fehlen.

**Nicht behaupten:** dass C4 hier repliziert sei, P3 bereits unabhängig reproduziert wäre, allgemeine Problemlösekompetenz bewiesen sei oder das Qwen-Vierarmexperiment P3 verwendet hätte (dort wurde P2 verwendet).

## Anschluss

Erforderliche P3-Rohartefakte und die Akzeptanzprüfung stehen in [P3_INGESTION.md](../P3_INGESTION.md). Erst nach Hash-/Code-/Daten-/Auswertungsprüfung kann aus diesem berichteten Fortschritt ein verifizierter Repositorium-Befund werden.
