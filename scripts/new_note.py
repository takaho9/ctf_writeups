#!/usr/bin/env python3
"""調べたことを雑にメモするノートを対話的に作成するスクリプト。

問題用の writeup とは別に、再利用できる知識・調査メモを
  docs/notes/<slug>.md
として生成し、mkdocs.yml の Notes セクションに nav を追記する。

すべての項目は Enter でスキップ可能（雑に取れるように）。
  - タイトル未入力 -> 日時（例 2026-07-10 15:30）をタイトルにする
  - タグ未入力     -> Notes のみ

使い方:
    python scripts/new_note.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# scripts/ の1つ上がリポジトリルート
ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "docs" / "notes"
MKDOCS = ROOT / "mkdocs.yml"

# Notes セクションのインデント（mkdocs.yml の既存スタイルに合わせる）
SECTION_INDENT = "  "     # 2  ("  - Notes:")
ITEM_INDENT = "      "    # 6  ("      - <title>: notes/xxx.md")


def slugify(name: str) -> str:
    """タイトルを kebab-case のファイル名向けslugに変換。英数字が無ければ空文字。"""
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def yaml_scalar(value: str) -> str:
    """nav タイトル用に、必要なら YAML でクオートする。"""
    if value == "" or re.search(r'[:#\[\]{}&*!|>\'"%@`,]', value) or value[0] in " -?":
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return value


def insert_into_notes_nav(title: str, relpath: str) -> bool:
    """mkdocs.yml の Notes セクション末尾に 1エントリを差し込む。成功で True。"""
    if not MKDOCS.exists():
        return False
    lines = MKDOCS.read_text(encoding="utf-8").splitlines()

    # "  - Notes:" を探す
    notes_i = None
    for i, ln in enumerate(lines):
        if ln.strip() == "- Notes:" and indent_of(ln) == len(SECTION_INDENT):
            notes_i = i
            break
    if notes_i is None:
        return False

    # Notes ブロックの終端（インデント<=2 の次の項目、または EOF）
    block_end = len(lines)
    for i in range(notes_i + 1, len(lines)):
        if lines[i].strip() and indent_of(lines[i]) <= len(SECTION_INDENT):
            block_end = i
            break

    entry = f"{ITEM_INDENT}- {yaml_scalar(title)}: {relpath}"
    lines[block_end:block_end] = [entry]
    MKDOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def build_markdown(title: str, tags: list[str], stamp: str) -> str:
    tag_lines = "\n".join(f"  - {t}" for t in tags)
    return f"""---
tags:
{tag_lines}
---

# {title}

<small>{stamp}</small>

"""


def main() -> int:
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d %H:%M")

    print("=== 新しいノートを作成（Enterで各項目スキップ可）===\n")

    title = input("タイトル (空Enter=日時): ").strip()
    if not title:
        title = stamp

    tags_in = input("タグ (カンマ区切り, 空Enter=Notes のみ): ").strip()
    extra = [t.strip() for t in re.split(r"[,\s]+", tags_in) if t.strip()]
    seen: set[str] = set()
    tags: list[str] = []
    for t in ["Notes", *extra]:
        if t.lower() not in seen:
            seen.add(t.lower())
            tags.append(t)

    # slug: タイトルから作る。英数字が無い（日本語のみ等）や日時タイトルなら日時ベース。
    slug = slugify(title)
    if not slug:
        slug = now.strftime("%Y-%m-%d-%H%M")

    md_path = NOTES_DIR / f"{slug}.md"
    # 衝突したら連番を付与
    if md_path.exists():
        n = 2
        while (NOTES_DIR / f"{slug}-{n}.md").exists():
            n += 1
        slug = f"{slug}-{n}"
        md_path = NOTES_DIR / f"{slug}.md"

    relpath = f"notes/{slug}.md"

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(build_markdown(title, tags, stamp), encoding="utf-8")
    print(f"\n[作成] docs/{relpath}")
    print(f"       タイトル: {title} / タグ: {', '.join(tags)}")

    if insert_into_notes_nav(title, relpath):
        print("[更新] mkdocs.yml の Notes に nav を追加")
    else:
        print("[注意] nav を自動更新できませんでした。mkdocs.yml の Notes 下に手動で追記してください:")
        print(f"        {ITEM_INDENT}- {yaml_scalar(title)}: {relpath}")

    # VSCode で開く（空Enter=開く）
    ans = input("\nVSCode で開きますか? [Y/n]: ").strip().lower()
    if ans not in ("n", "no"):
        try:
            subprocess.run(["code", str(md_path)], check=False)
        except FileNotFoundError:
            print("  'code' コマンドが見つかりません。手動で開いてください。")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n中止しました。")
        sys.exit(130)
