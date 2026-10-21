"""Import only qwen3:8b into the private Linux cache; never modify the source."""
import json
import re
import shutil
from pathlib import Path


source = Path("/import-models")
destination = Path("/models")
relative_manifest = Path("manifests/registry.ollama.ai/library/qwen3/8b")
manifest = source / relative_manifest
if manifest.is_file():
    data = json.loads(manifest.read_text(encoding="utf-8"))
    blobs = destination / "blobs"
    blobs.mkdir(parents=True, exist_ok=True)
    for descriptor in [data["config"], *data["layers"]]:
        digest = descriptor["digest"]
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError("Unexpected model blob digest")
        name = digest.replace(":", "-", 1)
        original, target = source / "blobs" / name, blobs / name
        if target.is_file() and target.stat().st_size == descriptor["size"]:
            continue
        if original.stat().st_size != descriptor["size"]:
            raise ValueError(f"Unexpected source model size: {name}")
        print(f"Importing qwen3:8b blob ({descriptor['size']:,} bytes)", flush=True)
        temporary = target.with_suffix(".importing")
        shutil.copyfile(original, temporary)
        temporary.replace(target)
    target_manifest = destination / relative_manifest
    target_manifest.parent.mkdir(parents=True, exist_ok=True)
    target_manifest.write_bytes(manifest.read_bytes())
    print("qwen3:8b is available in the Linux model cache.", flush=True)
else:
    print("No qwen3:8b cache to import; use ollama pull qwen3:8b after startup.", flush=True)
