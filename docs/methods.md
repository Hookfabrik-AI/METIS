# Methodik

## Forschungsfragen

- Kann ein sehr kleines, trainiertes neuronales Modell formal strukturierte Constraints so repräsentieren, dass es tatsächlich zwischen leicht verwechselbaren Aufgaben unterscheidet?
- Erhöhen P2-Hinweise die Erfolgsquote und/oder reduzieren sie Output-Tokens sowie gesamte reale Ausführungszeit eines größeren LLM?
- Welchen **inkrementellen** Nutzen liefern gelernte Vorschläge gegenüber neutralen Hinweisen, Zufall, heuristischen Kandidaten und einem deterministischen Verifikator?
- Wie lässt sich Fehlverankerung durch einen hochkonfidenten, aber falschen Hinweis vermeiden?

## P2-Protokoll

Vier ursprüngliche Aufgabengruppen: `K1_numbers`, `K2_schedule`, `K3_logic`, `K4_equations`; externe Tests auch mit `K5_coloring`. Synthetische Problemgeneratoren, train/dev/test getrennt; Parameter/Splits/Seeds in `datasets/p2/manifest.json`. `problems.violations` fungiert als deterministischer externer Prüfer. Die Modelleinheiten sehen formale Conditions und ggf. vorherigen Kandidaten/Verletzungsflags, aber keine Solver-Traces oder korrekten Lösungszahlen als Input. Details: `research/p2/model.py`, `cog.py`, `evaluate.py`.

## Qwen-Vierarm

- A: keine Kandidaten.
- B: MÉTIS P2 Greedy-Vorschlag.
- C: uniform zufällige Werte pro Variable (fixierter Seed).
- D: Min-Conflicts mit maximal 256 Verifikatorevaluationen, bester beobachteter Kandidat.
- B/C/D: identische Einleitung „Ein ungeprüfter Lösungsvorschlag (kann falsch sein):“.
- Qwen: im historischen Skript `qwen3.5:latest`, `think=false`, `temperature=0`, `seed=0`, `num_predict=4096`, bis zu drei Attempts und jeweils beschränktes Zeitbudget. `latest` ist **kein unveränderlicher Modell-Digest**.
- Feedback: Bei falscher Ausgabe werden ausschließlich verletzte Bedingungen genannt. Protokollbeschreibungen stehen im historischen (pfadbereinigten) `research/qwen/historical/metis_qwen_4arm.py`.
- Zielmaße: korrekt/12, Ausgabe-Tokens (`eval_count` über alle Versuche) und Summen der `wall_s` je Arm. Verifier-, MÉTIS- und Min-Conflicts-CPU sind separate Kostenterme; prompt processing/model loading/warmup gehören zur kompletten E2E-Bilanz.

## Statistische Aussagegrenze

Nur zwölf Aufgaben, kein gepaartes Mehrfachsampling je Bedingung und uneinheitliche Hardware-/Cachezustände. Die vierarmigen Daten sind aus drei Teilruns mit dokumentierter Dublette kombiniert, nicht aus einem einzig durchgängigen, vorab festgelegten Durchlauf. Kein bestätigter kausaler oder auf neue Verteilungen generalisierbarer Effekt. Kein Claim zu spontaner Reflexion oder allgemeiner Intelligenz.
