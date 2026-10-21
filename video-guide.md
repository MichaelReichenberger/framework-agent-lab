# Ablauf für das persönliche Vier-Minuten-Video

Status: Aufnahme ausstehend. Dieser Leitfaden ist kein Video und kein Beleg für
einen Live-Lauf. Die Implementierung und der zusätzliche Regressionstest wurden
mit Codex erstellt; erläutere die Zusammenarbeit und deinen eigenen Beitrag
ehrlich. Trage deinen Namen im Fragebogen ein und führe das Partnerreview selbst
durch. Nimm das Video erst auf, wenn Live-Reparatur und Abschlussprüfung belegt
sind.

Die technische Prüfung ist jetzt abgeschlossen: `qwen3:8b` hat Pricing im
Live-Lauf geändert, der persönlich freigegebene Testaufruf bestand mit zehn
Tests und der Graph endete `VERIFIED` (Exitcode 0). Auch die unabhängige
Zehn-Test-Prüfung besteht, und der Diff der geschützten Dateien ist leer.

| Zeit | Bild und Erläuterung |
| --- | --- |
| 0:00–0:40 | `starter/agent.py`: Zustandsgraph, nur native Toolaufrufe, angehängte Nachrichten, explizites `verify`, 32-Schritt-Grenze. Erkläre, warum eine Modellbehauptung keinen Erfolg belegt. |
| 0:40–1:00 | Geschäftliche Herleitung des eigenen Tests: 99,995 EUR wird vor der Versandentscheidung auf 100,00 EUR gerundet. Zeige den tatsächlichen Baseline-Fehler und die unveränderten Akzeptanztests. |
| 1:00–2:35 | Live-Ausgabe mit Modelltag `qwen3:8b`: Lesen der Regeln, Tests und Pricing; native Call-ID und dazugehörige Beobachtung; vom Modell ausgewählte Ersetzung. Zeige den Diff vor der persönlichen `yes`-Freigabe und anschließend die Testbeobachtung sowie das Verifikationsergebnis. |
| 2:35–3:15 | Unabhängig zehn Service-Tests ausführen; Service-Diff mit ausschließlich Pricing und neuem Studententest sowie leerer Diff der geschützten Dateien zeigen. |
| 3:15–4:00 | Traversal und mehrdeutige Ersetzung als verweigerte Aufrufe zeigen. Ein `incomplete`-Ergebnis aus Smoke/Workflow erklären, einschließlich veralteter Tests nach einem Edit. Grenzen: endliche Tests; die Anwendungstools ersetzen keine OS-Sandbox und Testcode kann auf eingebundene Projektdateien zugreifen. |

Verwende für einen erneuten Live-Reparaturlauf eine frische Kopie der Baseline.
Setze die erfolgreiche Service-Reparatur nicht zurück. Im lokalen Checkout
exportiert `git archive HEAD` aus dem Verzeichnis `target-service` den
aufgezeichneten ursprünglichen Service; kopiere außerdem
`tests/test_student.py` in die frische Kopie, bevor du den Agenten startest.
Halte Laufzeitdateien und Kopien außerhalb von `target-service`.
Die Abgabe-ZIP enthält die reparierten Quellen, nicht diese Git-Metadaten.

Für die Aufnahme unter WSL gilt [WSL.md](WSL.md): Python und Ollama laufen
gemeinsam im Linux-Container. Das WSL-Limit wurde nach Freigabe auf 8 GB RAM/
4 GB Swap angehoben. Beide Graph-Diagnosen, elf Verifikationstests, zehn
Service-Tests und der Modell-Preflight bestehen dort. Für den neuen
Live-Reparaturlauf ist `.wsl-runs/2026-10-19/service` vorbereitet; verwende nur
das tatsächlich erreichte Verifikationsergebnis dieser Kopie als WSL-Beleg.

Für das Review müssen sich die nativen Requests und Observations an denselben
IDs zuordnen lassen. Ein Screenshot von „fertig“, ein Preflight oder ein
geskriptetes Fixture ist kein Ersatz für den beobachteten Live-Edit.
Falls Inferenz länger dauert, kennzeichne eventuelle Auslassungen klar und
behalte den tatsächlichen Request, die Beobachtung, den Diff und die Freigabe
sichtbar. Behaupte keine Ergebnisse, die du nicht demonstrieren kannst.
