# Week 2 verified agent questionnaire

Name / team: Vom Studierenden einzutragen.

Repository URL or source ZIP: framework-agent-lab-source.zip.

Local model tag and preflight result: qwen3:8b; LIVE PROBE PASSED unter Windows
(14. Oktober) und unter WSL2/Docker (20. Oktober), jeweils lokal.

Answer each in two to five clear sentences and refer to your four-minute video.
Scripted diagnostics support development; completion requires a live repair.

Die Antworten beschreiben den tatsächlich erreichten Stand. Das persönliche
Video ist noch nicht aufgenommen; die Zeitangaben unten beziehen sich auf den
vorbereiteten Ablauf in `video-guide.md`, nicht auf ein bereits vorhandenes Video.

1. Which part of the Week 1 loop did LangGraph replace? Explain the nodes,
   message updates, routes, and what the 32-step limit guarantees.

   Answer: LangGraph ersetzt die manuell gesteuerte Modell-/Tool-Schleife durch
   die Knoten `model`, `tools` und `verify` mit gemeinsamem `AgentState`.
   Der Modellknoten stellt die Systemanweisung vor die Historie und gibt nur die
   neue validierte `AIMessage` zurück; `MessagesState` hängt sie an, während der
   Toolknoten über die Call-ID verknüpfte Beobachtungen ergänzt.
   Native Aufrufe führen zu Tools und zurück zum Modell, eine finale Antwort zur
   Verifikation und danach zu END.
   Die Grenze von 32 Graphschritten beendet zu lange Schleifen als unvollständig,
   garantiert aber weder 32 Toolaufrufe noch eine bestimmte Laufzeit oder eine
   richtige Reparatur (Videoabschnitt 0:00–0:40).

2. Which boundaries do the supplied tools enforce regardless of the model's
   request? Explain both denials and why a fixed test command still needs review.

   Answer: Die Python-Tools begrenzen unabhängig vom Modell relative sichtbare
   Pfade auf den Service, verweigern Traversal, versteckte Komponenten und
   symbolische Links und erlauben nur eindeutige Ersetzungen in Pricing mit
   maximal 12.000 Bytes.
   Der demonstrierte Leseaufruf für `../HANDOUT.md` wurde wegen Traversal und die
   Ersetzung von `Decimal` durch `float` wegen mehrfach vorkommendem Alttext
   abgewiesen; ein Hashvergleich bestätigte unverändertes Pricing.
   `run_tests` erlaubt nur den vorgegebenen unittest-Befehl mit 30 Sekunden
   Timeout und verlangt exakt `yes`, nachdem der Mensch den Diff geprüft hat.
   Diese Freigabe ist nötig, weil Tests veränderten Python-Code mit den Rechten
   des Benutzers importieren; die Tools sind keine Betriebssystem-Sandbox
   (Videoabschnitte 1:00–2:35 und 3:15–4:00).

3. How does your verification node distinguish a final response from verified
   completion? Explain failed/denied tests and an edit after a passing test.
   Identify one incomplete result you demonstrated.

   Answer: Der Verifikationsknoten verlangt eine gültige, nichtleere finale
   `AIMessage` ohne Toolaufrufe sowie eine zum nativen `run_tests`-Aufruf
   verknüpfte Beobachtung mit `exit_code=0` nach der letzten erfolgreichen Änderung.
   Eine erfolgreiche Pricing-Änderung löscht frühere Testerfolge, und jeder
   spätere fehlgeschlagene, verweigerte oder fehlerhafte Test löscht den aktuellen
   Erfolg ebenfalls; JSON-artiger Nachrichtentext ist kein Toolbeleg.
   Der bestandene Smoke-Check endet ausdrücklich `incomplete`, weil Lesen allein
   keinen bestandenen Test liefert; der Workflow-Check demonstriert zusätzlich
   die verweigerte Freigabe und veraltete Tests nach einer weiteren Änderung.
   Ein Modellschluss wie „fertig“ kann diese Regeln nicht überstimmen
   (Videoabschnitte 0:00–0:40 und 3:15–4:00).

4. What evidence shows that the live model read, edited, and tested the service?
   State the model tag, your regression's expected business result and baseline
   failure, the final test result, and protected files you checked. What remains
   unverified?

   Answer: Im verifizierten Windows-Lauf vom 14. Oktober hat `qwen3:8b`
   Regeln, Akzeptanztests und Pricing über native `read_file`-Aufrufe gelesen,
   anschließend `edit_pricing` mit Call-ID `75f58f25-3e95-4b49-83d1-e50c794f434b`
   ausgewählt und die verknüpfte Beobachtung `Updated orders/pricing.py once`
   erhalten; nach persönlicher Freigabe lieferte sein `run_tests`-Aufruf mit
   Call-ID `1a2310ba-891f-4300-a52c-cacadff76694` die verknüpfte Beobachtung
   `exit_code=0` mit zehn bestandenen Tests und der Graph endete `VERIFIED`
   mit CLI-Exitcode 0.
   Der unabhängig vom Reparaturmodell geschriebene Grenzfall erwartet bei einer
   Position von 99,995 EUR nach HALF_UP-Rundung einen Subtotal und Gesamtpreis von
   100,00 EUR sowie kostenlosen Versand; die Baseline scheitert mit 99,995 EUR
   Subtotal, 5 EUR Versand und 105,00 EUR Gesamtpreis.
   Die unabhängige Prüfung besteht auch unter WSL mit allen neun ursprünglichen
   Akzeptanztests plus dieser Regression; der geprüfte Diff für Validation,
   Service, Storage, Akzeptanztests und Dokumentation ist leer und der
   Service-Status enthält nur Pricing sowie den neuen Studententest.
   Noch unbestätigt sind der finale Erfolg des neuen WSL-Modellreparaturlaufs
   und das persönliche Video/Partnerreview;
   außerdem beweisen endliche Tests weder alle Eingaben noch eine OS-Sandbox
   (Videoabschnitte 0:40–1:00 und 2:35–4:00).
