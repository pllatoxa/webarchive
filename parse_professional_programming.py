#!/usr/bin/env python3
"""
Парсер репозитория professional-programming от charlax.

Скрипт обходит все .md файлы, извлекает элементы списков с Markdown-ссылками
и сохраняет структуру в JSON и CSV.
"""

import argparse
import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
RESOURCE_RE = re.compile(r"^\s*[-*+]\s+\[(.+?)\]\((.+?)\)\s*(?:[-–—]\s*(.*))?$")

DEFAULT_REPO_DIR = "./professional-programming"
DEFAULT_JSON_OUT = "professional_programming_resources.json"
DEFAULT_CSV_OUT = "professional_programming_resources.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse professional-programming markdown resources.")
    parser.add_argument(
        "--repo-dir",
        default=DEFAULT_REPO_DIR,
        help="Путь к корню репозитория professional-programming (по умолчанию: %(default)s)",
    )
    parser.add_argument(
        "--json-out",
        default=DEFAULT_JSON_OUT,
        help="Путь для вывода JSON (по умолчанию: %(default)s)",
    )
    parser.add_argument(
        "--csv-out",
        default=DEFAULT_CSV_OUT,
        help="Путь для вывода CSV (по умолчанию: %(default)s)",
    )
    return parser.parse_args()


def iter_markdown_files(repo_dir: Path) -> Iterable[Path]:
    """Итерирует по .md файлам, пропуская скрытые директории."""
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            if filename.lower().endswith(".md"):
                yield Path(root) / filename


def normalize_heading(text: str) -> str:
    """Очищает заголовок от хвостовых # и пробелов."""
    cleaned = text.strip()
    cleaned = re.sub(r"\s+#*$", "", cleaned)
    return cleaned.strip()


def update_heading_stack(stack: List[str], level: int, heading: str) -> List[str]:
    """Обновляет стек заголовков до нужного уровня."""
    new_stack = stack[: level - 1]
    new_stack.append(heading)
    return new_stack


def extract_resource(line: str) -> Tuple[str, str, str]:
    """Пробует извлечь ресурс из строки списка. Возвращает (title, url, description) или None."""
    match = RESOURCE_RE.match(line)
    if not match:
        return None
    title, url, desc = match.groups()
    desc = desc or ""
    desc = desc.strip().lstrip("-–—").strip()
    return title.strip(), url.strip(), desc


def parse_markdown_file(path: Path, repo_dir: Path, start_id: int) -> Tuple[List[Dict], int]:
    resources: List[Dict] = []
    heading_stack: List[str] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    for line in lines:
        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = normalize_heading(heading_match.group(2))
            heading_stack = update_heading_stack(heading_stack, level, heading_text)
            continue

        resource = extract_resource(line)
        if resource:
            title, url, description = resource
            category_h1 = heading_stack[0] if len(heading_stack) >= 1 else ""
            category_h2 = heading_stack[1] if len(heading_stack) >= 2 else ""
            category_h3 = heading_stack[2] if len(heading_stack) >= 3 else ""
            category_path = " / ".join([h for h in heading_stack if h])
            resources.append(
                {
                    "id": start_id + len(resources),
                    "title": title,
                    "url": url,
                    "description": description,
                    "category_h1": category_h1,
                    "category_h2": category_h2,
                    "category_h3": category_h3,
                    "category_path": category_path,
                    "file_path": str(path.relative_to(repo_dir).as_posix()),
                    "raw_line": line.rstrip("\n"),
                }
            )

    return resources, start_id + len(resources)


def write_json(resources: List[Dict], json_path: Path) -> None:
    json_path.write_text(json.dumps(resources, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(resources: List[Dict], csv_path: Path) -> None:
    fieldnames = [
        "id",
        "title",
        "url",
        "description",
        "category_h1",
        "category_h2",
        "category_h3",
        "category_path",
        "file_path",
        "raw_line",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resources)


def main() -> None:
    args = parse_args()
    repo_dir = Path(args.repo_dir).expanduser().resolve()
    json_out = Path(args.json_out).expanduser().resolve()
    csv_out = Path(args.csv_out).expanduser().resolve()

    if not repo_dir.exists():
        raise SystemExit(f"Repo directory not found: {repo_dir}")

    all_resources: List[Dict] = []
    current_id = 1

    for md_file in sorted(iter_markdown_files(repo_dir)):
        file_resources, current_id = parse_markdown_file(md_file, repo_dir, current_id)
        all_resources.extend(file_resources)

    write_json(all_resources, json_out)
    write_csv(all_resources, csv_out)
    print(f"Parsed {len(all_resources)} resources from {repo_dir}")
    print(f"JSON saved to: {json_out}")
    print(f"CSV saved to: {csv_out}")


if __name__ == "__main__":
    main()
