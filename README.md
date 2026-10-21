# Verifizierter lokaler Coding-Agent mit LangGraph

Ein lokales Ollama-Modell (`qwen3:8b`) liest Geschäftsregeln und Tests eines
Bestellservices, repariert dessen Preisberechnung und fordert eine persönliche
Freigabe für die Tests an. LangGraph steuert `model -> tools -> model` und führt
eine finale Modellantwort durch `verify` zu `END`. Verifizierter Erfolg benötigt
aktuelle bestandene Tests; eine Modellbehauptung genügt nicht. Die vollständige
Aufgabenstellung steht in [HANDOUT.md](HANDOUT.md).

**`target-service` enthält bereits die reparierte Version.** Die Anleitung zeigt
deren Prüfung und anschließend eine neue Live-Reparatur auf einer separaten
fehlerhaften Kopie. Sie funktioniert aus einem frischen Klon ohne persönliche
`.env.wsl`, lokale Demo-Skripte oder zusätzliche Git-Tags.

## 1. Voraussetzungen

- WSL2 mit Ubuntu und Git im Ubuntu-Terminal.
- Docker Desktop mit WSL2-Backend und aktivierter Ubuntu-Integration unter
  Settings -> Resources -> WSL Integration.
- Eine für Docker/WSL eingerichtete NVIDIA-GPU: `compose.wsl.yaml` verwendet
  `gpus: all`. Eine reine CPU-Konfiguration ist hier nicht enthalten.
- Etwa 16 GB Arbeitsspeicher und Platz für Container und das ungefähr 5,2 GB
  große Modell; Internetzugang für den ersten Build und Modelldownload.

Docker Desktop starten. **Alle folgenden Befehle im Ubuntu-Terminal ausführen.**
Python 3.12, die Pakete aus `requirements-lock.txt` und Ollama werden gemeinsam
im Linux-Container bereitgestellt. Dafür ist keine zusätzliche Python- oder
Ollama-Installation auf dem Host erforderlich.

```bash
docker version
docker compose version
git --version
```

`docker version` muss auch den Server erreichen. Wird `docker` in Ubuntu nicht
gefunden, zuerst die WSL-Integration in Docker Desktop aktivieren.

## 2. Klonen und Container starten

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/MichaelReichenberger/framework-agent-lab.git
cd framework-agent-lab

mkdir -p .wsl-models
bash scripts/wsl.sh up -d --build --wait --wait-timeout 300
bash scripts/wsl.sh exec lab python --version
bash scripts/wsl.sh exec lab python -m pip check
```

Bei einem privaten Repository sind GitHub-Zugriffsberechtigung und eine passende
Git-Anmeldung erforderlich. Erwartet werden Python **3.12** und
`No broken requirements found.` Der erste Build kann einige Minuten dauern.

Das Projekt ist im Container unter `/workspace` eingebunden. Agent und Ollama
verwenden dort `http://127.0.0.1:11434`; ein Host-Port wird nicht freigegeben.
`.wsl-models` ist eine optionale Importquelle. Ohne Cache wird das Modell im
nächsten Schritt direkt ins projektbezogene Linux-Volume geladen.

## 3. Modell laden und Preflight bestehen

```bash
bash scripts/wsl.sh exec lab ollama pull qwen3:8b
bash scripts/wsl.sh exec lab ollama list
bash scripts/wsl.sh exec lab python checks/probe_model.py --model qwen3:8b
```

Erwartet wird **`LIVE PROBE PASSED`**: nativer `get_lab_status`-Aufruf,
verknüpfte Tool-Beobachtung und finale Modellantwort. Der Preflight verändert
keine Dateien und beweist noch keine Reparatur. Den Live-Agenten erst nach
bestandenem Preflight starten.

Modellkonfiguration: lokal, Temperatur 0, Reasoning deaktiviert, 16.384
Kontexttokens, 2.048 Ausgabetokens und 120 Sekunden HTTP-Timeout.

## 4. Graph-Diagnosen und reparierten Service prüfen

```bash
bash scripts/wsl.sh exec lab python checks/smoke.py --agent starter/agent.py --root target-service
bash scripts/wsl.sh exec lab python checks/workflow.py --agent starter/agent.py
bash scripts/wsl.sh exec lab python -m unittest discover -s checks -p test_verification.py -v
bash scripts/wsl.sh exec -w /workspace/target-service lab python -m unittest discover -s tests -v
```

| Prüfung | Erwartetes Ergebnis |
| --- | --- |
| Smoke | `SMOKE PASSED`; ungetestete Arbeit endet korrekt `incomplete` |
| Workflow | `WORKFLOW PASSED`; Edit, Freigabe/Verweigerung, Testfehler, veraltete Tests und Schrittlimit |
| Verifikation und Antwortvalidierung | 11 Tests, `OK` |
| Bereits reparierter Service | 9 Akzeptanztests plus 1 Regressionstest, `OK` |

Smoke und Workflow verwenden geskriptete Modelle. Automatische Freigaben im
Workflow gelten nur für dessen harmlose temporäre Testdateien. Diese Diagnosen
ersetzen den echten Modelllauf aus Schritt 7 nicht.

## 5. Frische Baseline für die Live-Reparatur vorbereiten

Im selben Ubuntu-Terminal im Repository-Hauptordner bleiben. Für jeden Versuch
wird ein neuer Ordner erstellt. Der Export enthält die eingecheckten
Service-Dateien, zunächst ohne Studententest:

```bash
mkdir -p .wsl-runs
demo_run=$(mktemp -d .wsl-runs/live-XXXXXX)
demo_root="$demo_run/service"
mkdir "$demo_root"
git archive HEAD target-service | tar -x --strip-components=1 \
  --exclude='target-service/tests/test_student.py' -C "$demo_root"
printf '%s\n' "$demo_root" > .wsl-runs/current-demo.txt
```

Nur in dieser Kopie wird jetzt die originale fehlerhafte Pricing-Version
wiederhergestellt. Das bereitet den Ausgangszustand vor; die spätere Reparatur
muss das Modell selbst über `edit_pricing` auswählen und ausführen.

```bash
cat > "$demo_root/orders/pricing.py" <<'PY'
"""Pricing calculation. Support has reported incorrect customer totals."""
from decimal import Decimal
from .validation import validate_order


def quote(lines, discount=Decimal("0")):
    validate_order(lines, discount)
    subtotal = sum((line["unit_price"] * line["quantity"] for line in lines), Decimal("0"))
    shipping = Decimal("0") if subtotal >= Decimal("100") else Decimal("5")
    total = ((subtotal + shipping) * (1 - discount)).quantize(Decimal("0.01"))
    return {"subtotal": subtotal, "shipping": shipping, "total": total}
PY

git -C "$demo_root" init --initial-branch=main
git -C "$demo_root" add .
git -C "$demo_root" -c user.name="Lab Student" -c user.email="student@example.invalid" \
  commit -m "Record original pricing baseline"

bash scripts/wsl.sh exec -w "/workspace/$demo_root" lab \
  python -m unittest discover -s tests -p test_acceptance.py -v
```

Erwartet: **9 Tests, 5 Fehler, 4 bestanden, Exitcode 1**. Die Baseline-Fehler sind
beabsichtigt. Danach die folgenden Befehle separat ausführen:

```bash
cp target-service/tests/test_student.py "$demo_root/tests/test_student.py"
bash scripts/wsl.sh exec -w "/workspace/$demo_root" lab \
  python -m unittest discover -s tests -p test_student.py -v
```

Erwartet: **1 fehlgeschlagener Regressionstest, Exitcode 1**. Bei 99,995 EUR muss
die Position vor der Versandentscheidung auf 100,00 EUR gerundet werden:
Subtotal und Gesamtpreis 100,00 EUR, Versand 0,00 EUR. Die Baseline liefert
Subtotal 99,995 EUR, Versand 5 EUR und Gesamtpreis 105,00 EUR.
Der Regressionstest ist damit vor der Modellreparatur vorhanden und geprüft.
Für die eigene Laborabgabe ist gemäß Handout ein selbst hergeleiteter Test nötig;
der hier enthaltene Test wurde mit Codex-Unterstützung erstellt.

## 6. Zwei Tool-Verweigerungen demonstrieren

Dieser Check verwendet den bereits reparierten Service und bestätigt per
Hashvergleich, dass beide verweigerten Anfragen Pricing unverändert lassen:

```bash
bash scripts/wsl.sh exec -T lab python - <<'PY'
from hashlib import sha256
from pathlib import Path
from starter.agent import build_tools

pricing = Path("target-service/orders/pricing.py")
before = sha256(pricing.read_bytes()).hexdigest()
tools = {tool.name: tool for tool in build_tools(Path("target-service"))}
print(tools["read_file"].invoke({"path": "../HANDOUT.md"}))
print(tools["edit_pricing"].invoke({"old": "Decimal", "new": "float"}))
assert sha256(pricing.read_bytes()).hexdigest() == before
print("Pricing unverändert.")
PY
```

Beide Antworten beginnen mit `ERROR`: Der erste Pfad verlässt den Arbeitsbereich;
im zweiten Aufruf kommt der alte Text mehrfach vor und ist daher nicht eindeutig.

## 7. Live-Agenten starten und Tests persönlich freigeben

Im ersten Terminal im Repository-Hauptordner:

```bash
demo_root=$(cat .wsl-runs/current-demo.txt)
bash scripts/wsl.sh exec lab python starter/agent.py \
  --root "$demo_root" --model qwen3:8b --task "$(cat task.txt)"
```

Das Modell soll Regeln, Akzeptanztests und Pricing lesen, Pricing über
`edit_pricing` ändern und `run_tests` anfordern. Das Terminal zeigt native
Anfragen und Tool-Ergebnisse. `task.txt` ist die Aufgabenanweisung;
`SYSTEM_INSTRUCTION` in `starter/agent.py` gibt zusätzlich die fachliche
Berechnungsreihenfolge vor. Der vollständige Modellinput wird nicht separat
protokolliert. Eine Modellantwort kann während der Berechnung eine Weile dauern.

Bei `Approve this command only? Type yes:` den Prozess warten lassen.
**Vor der Freigabe** ein zweites Ubuntu-Terminal öffnen und dort ausführen:

```bash
cd ~/projects/framework-agent-lab
demo_root=$(cat .wsl-runs/current-demo.txt)
git -C "$demo_root" diff -- orders/pricing.py
git -C "$demo_root" status --short
```

Nach Prüfung im ersten Terminal exakt **`yes`** eingeben. Genehmigt wird nur der
angezeigte feste unittest-Befehl im Demo-Verzeichnis. Er importiert veränderten
Python-Code mit den Containerrechten; die Tool-Grenzen sind keine OS-Sandbox.

Ein erfolgreicher Lauf zeigt eine `run_tests`-Beobachtung mit `exit_code=0`,
10 bestandenen Tests und anschließend **`VERIFIED`**. `verify` verlangt eine
gültige nichtleere finale Antwort und aktuelle verknüpfte Testbelege. Spätere
erfolgreiche Edits oder erfolglose/verweigerte Tests entwerten frühere Testerfolge.
Das Limit von 32 Graphschritten begrenzt die Schleife, nicht ihre Laufzeit.

Agent-Exitcodes: **0** verifiziert, **2** unvollständig/Fehler, **130** unterbrochen.
Bei `INCOMPLETE` Grund und Diff prüfen; keine manuelle Pricing-Reparatur als
erfolgreichen Modelllauf ausgeben. Für eine Wiederholung Schritt 5 mit einer
neuen Kopie beginnen.

## 8. Diff und Tests unabhängig prüfen

Nach Ende des Agenten, im Repository-Hauptordner:

```bash
demo_root=$(cat .wsl-runs/current-demo.txt)
git -C "$demo_root" status --short
git -C "$demo_root" diff -- orders/pricing.py
git -C "$demo_root" diff --exit-code HEAD -- \
  orders/validation.py orders/service.py orders/storage.py tests/test_acceptance.py docs
cmp target-service/tests/test_student.py "$demo_root/tests/test_student.py"
bash scripts/wsl.sh exec -w "/workspace/$demo_root" lab \
  python -m unittest discover -s tests -v
```

Erwartet: Nur `orders/pricing.py` als geändert und `tests/test_student.py` als neu;
der geschützte Diff und `cmp` bleiben ohne Ausgabe mit Exitcode 0. Auch der
separate Testlauf muss **alle 10 Tests** bestehen. Keine Akzeptanztests oder
Geschäftsregeln abschwächen, um Erfolg zu erreichen.

## Nachgewiesener WSL-Lauf und Abgabe

Am 20. Oktober 2026 bestand ein vollständiger Live-Lauf unter WSL2/Docker mit
Python 3.12.15, Ollama 0.35.1 und `qwen3:8b`: Baseline mit fünf Akzeptanzfehlern
und fehlschlagender Regression, bestandener Preflight, native Leseaufrufe,
ein modellgewählter Pricing-Edit und persönlich freigegebener Testaufruf.
Der Agent endete `VERIFIED` mit Exitcode 0 und zehn bestandenen Tests; auch
der unabhängige Testlauf bestand alle zehn Tests, geschützte Dateien unverändert.
Beide Graph-Diagnosen und die elf zusätzlichen Verifikationstests bestanden.
Dies dokumentiert einen beobachteten Lauf; ein neuer Modelllauf kann anders enden.

Die Implementierung und der Regressionstest entstanden mit Codex-Unterstützung.
Finite Tests beweisen keine Korrektheit für alle Eingaben. Zur Abgabe gehören
Quellcode, der ausgefüllte [Fragebogen](questionnaire.md) und ein persönliches
Vier-Minuten-Video. Das Handout verlangt außerdem ein Partnerreview; Hinweise
zur Aufnahme stehen in [video-guide.md](video-guide.md). Persönliche
Konfiguration, Modelle, Caches und Demo-Verzeichnisse bleiben per `.gitignore`
außerhalb des Repositorys.

Containerstatus, Diagnose und Beenden:

```bash
bash scripts/wsl.sh ps
bash scripts/wsl.sh logs --tail=40 lab
bash scripts/wsl.sh stop
```

Wenn nur die Modelldateien fehlen, Schritt 3 wiederholen. Bei einem
Containerstartfehler zuerst die Logs und die Docker-/GPU-Verfügbarkeit prüfen.
