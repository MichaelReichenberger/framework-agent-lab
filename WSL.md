# Ausführung mit WSL2 und Docker Desktop

Alle folgenden Befehle laufen im **Ubuntu-Terminal von WSL**, im Projektordner:

```bash
cd /mnt/c/Users/micha/Downloads/framework-agent-lab/framework-agent-lab
bash scripts/wsl.sh up -d --build
bash scripts/wsl.sh exec lab python --version
bash scripts/wsl.sh exec lab python -m pip check
bash scripts/wsl.sh exec lab ollama list
bash scripts/wsl.sh exec lab python checks/probe_model.py --model qwen3:8b
```

Docker Desktop muss laufen und seine WSL-Integration für Ubuntu muss aktiviert
sein. Die Konfiguration verwendet die NVIDIA-GPU. Python 3.12, die Pakete aus
`requirements-lock.txt` und Ollama befinden sich **gemeinsam im Linux-Container**
`lab`; der Agent erreicht diesen Ollama-Prozess über `127.0.0.1:11434` im selben
Container. Der Windows-Ollama-Server wird dafür nicht verwendet, und es wird
kein Host-Port veröffentlicht. Ubuntu selbst benötigt weder ein systemweit
installiertes Python 3.12 noch einen eigenen Ollama-Dienst.

Die lokale, nicht zur Abgabe gehörende Datei `.env.wsl` bindet den vorhandenen
Windows-Cache `/mnt/c/Users/micha/.ollama/models` nur lesend unter `/import-models`
ein. Beim ersten Start kopiert `scripts/import_model_cache.py` nur die für
`qwen3:8b` benötigten Dateien in das projektbezogene Linux-Volume `model-cache`.
Weitere Starts überspringen vollständig kopierte Blobs. Ollama liest Gewichte
und schreibt Metadaten danach unter `/models` im Linux-Volume, ohne den
Windows-Cache zu ändern. Das Modell muss nicht erneut heruntergeladen werden.
Der erste Versuch mit direkt eingebundenen Windows-Gewichten lief beim Laden
in einen Preflight-Timeout; deshalb wird der Linux-Cache verwendet.
Auf einem anderen Rechner kannst du `.env.wsl` weglassen: Compose verwendet
`.wsl-models` dann als leere Importquelle. Lade das Modell mit
`bash scripts/wsl.sh exec lab ollama pull qwen3:8b` direkt in das Linux-Volume.
Eine Windows-Virtualenv unter `.venv` wird im Container nicht benutzt; dessen
Linux-Python und Pakete liegen unter `/opt/venv`.

Prüfungen:

```bash
bash scripts/wsl.sh exec lab python checks/smoke.py --agent starter/agent.py --root target-service
bash scripts/wsl.sh exec lab python checks/workflow.py --agent starter/agent.py
bash scripts/wsl.sh exec lab python -m unittest discover -s checks -p test_verification.py -v
bash scripts/wsl.sh exec -w /workspace/target-service lab python -m unittest discover -s tests -v
```

Interaktiver Agentenlauf auf dem bereits reparierten Service:

```bash
bash scripts/wsl.sh exec lab python starter/agent.py \
  --root target-service --model qwen3:8b --task "$(cat task.txt)"
```

Vor der Eingabe von `yes` den konkreten Pricing-Diff prüfen. Für eine erneute
Reparaturdemonstration eine frische Kopie der aufgezeichneten Baseline verwenden,
den Studententest vor dem Modelllauf hinzufügen und seinen Baseline-Fehler
zeigen. Den erfolgreichen ursprünglichen Service nicht zurücksetzen.

Containerstatus und Abschalten:

```bash
bash scripts/wsl.sh ps
bash scripts/wsl.sh logs --tail=40 lab
bash scripts/wsl.sh stop
```

Die Projektdateien werden nach `/workspace` eingebunden. Der Docker-Socket wird
nicht eingebunden. Die Anwendungstools behalten ihre vorgegebenen Grenzen;
ausgeführter Python-Code hat Zugriff auf die eingebundenen Projektdateien.

Grundlagen: [Ollama mit NVIDIA-GPU in Docker](https://docs.ollama.com/docker),
[uv und Python in Docker](https://docs.astral.sh/uv/guides/integration/docker/).

Prüfstand vom 20. Oktober: Der Linux-Image-Build mit Python 3.12.15 und
`pip check` ist bestanden. Der erste Containerstart scheiterte an der
Metadatenmigration im schreibgeschützten Cache; mit einem beschreibbaren
Linux-Volume gelingt die Metadatenmigration.
Danach reagierten Ubuntu-Befehle mit `WSAETIMEDOUT` und Docker meldete HTTP 500.
Am 20. Oktober wurde nach persönlicher Freigabe die bisherige `.wslconfig` unter
`.wsl-runs/wslconfig.backup-2026-10-20-4d2dd2d9.ini` gesichert und auf maximal
8 GB RAM/4 GB Swap umgestellt. Docker und WSL wurden neu gestartet; Ubuntu
meldet jetzt 7,8 GiB RAM und 4,0 GiB Swap, Docker 28.0.4 und Compose 2.34.0 sind
über die Ubuntu-Integration wieder erreichbar. Beide Graph-Diagnosen, elf
Verifikationstests und die zehn Tests des reparierten Services bestehen unter
Linux. Die frische Baseline zeigt fünf Fehler unter neun Akzeptanztests und
einen fehlschlagenden Studententest; beide unerlaubten Tool-Aufrufe werden ohne
Pricing-Änderung abgewiesen. Der wiederholte Preflight besteht mit
`LIVE PROBE PASSED`. Das endgültige Image ist auf Ollama **0.35.1** gepinnt,
entsprechend der installierten Windows-Version, und verwendet Python 3.12.15,
den lokalen Linux-Cache sowie den vorgeschriebenen 16.384-Token-Kontext.
Preflight, beide Graph-Diagnosen, elf Verifikationstests und alle zehn Tests des
reparierten Services bestehen auch mit diesem endgültigen Image.

Die vorangegangenen qwen3-Reparaturversuche mit Ollama 0.40.6 blieben fehlerhaft
und wurden beendet; das erlaubte Alternativmodell qwen2.5:7b bestand seinen
Preflight, lieferte nach dem Lesen aber eine leere Antwort und endete korrekt
`INCOMPLETE`. Ein neuer vollständiger Reparaturlauf vom Baseline-Fehler bis
`VERIFIED` ist unter Ollama 0.35.1 noch nicht durchgeführt. Es läuft aktuell
kein Reparaturagent. Die bisherigen verifizierten Live-Reparaturergebnisse vom
14. Oktober stammen aus der Windows-Ausführung.

Für die noch ausstehende frische WSL-Reparatur ist die Baseline einschließlich
des zuvor fehlgeschlagenen Studententests am bereits freigegebenen Pfad
vorbereitet:

```bash
bash scripts/wsl.sh exec lab python starter/agent.py \
  --root .wsl-runs/2026-10-19/service --model qwen3:8b --task "$(cat task.txt)"
```

Die fehlgeschlagenen qwen3-Änderungen bleiben separat unter
`.wsl-runs/2026-10-20-qwen3-incomplete-service` erhalten. Die Demo-Kopien und
Laufzeitprotokolle werden nicht in die Quellcode-ZIP aufgenommen.
