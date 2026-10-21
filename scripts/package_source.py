"""Package lab source, excluding personal configuration and runtime artifacts."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    files = [root / name for name in (
        ".gitignore", ".dockerignore", "Dockerfile.wsl", "compose.wsl.yaml",
        "HANDOUT.md", "README.md", "WSL.md", "video-guide.md", "task.txt", "task-shipping.txt",
        "requirements.txt", "requirements-lock.txt",
    )]
    for directory in ("starter", "checks", "scripts", "target-service"):
        for path in (root / directory).rglob("*"):
            parts = path.relative_to(root).parts
            if (path.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in parts)
                    and path.suffix in {".py", ".sh", ".md", ".txt"}):
                files.append(path)
    files.append(root / "target-service/.gitignore")
    archive = root / "framework-agent-lab-source.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as output:
        for path in sorted(files):
            output.write(path, "framework-agent-lab/" + path.relative_to(root).as_posix())
    with ZipFile(archive) as output:
        assert output.testzip() is None
        for path in files:
            assert output.read("framework-agent-lab/" + path.relative_to(root).as_posix()) == path.read_bytes()
    print(f"Packaged {len(files)} source files: {archive.name}")
    print("Questionnaire supplied separately; models, environments, local settings and demo runs excluded.")


if __name__ == "__main__":
    main()
