#!/usr/bin/env python3
"""新しいCTF writeupを対話的に作成するスクリプト。

問題を解き始めるときに実行すると、メタデータを対話入力して
  docs/<ctf>/<category>/<slug>.md
を雛形から生成し、画像用の images/ ディレクトリと mkdocs.yml の nav も整える。

使い方:
    python scripts/new_writeup.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# scripts/ の1つ上がリポジトリルート
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

# カテゴリ: 入力キー -> (ディレクトリ名, 表示名/タグ名)
CATEGORIES = {
    "1": ("web", "Web"),
    "2": ("crypto", "Crypto"),
    "3": ("pwn", "Pwn"),
    "4": ("rev", "Reversing"),
    "5": ("forensics", "Forensics"),
    "6": ("misc", "Misc"),
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]

# nav のインデント（mkdocs.yml の既存スタイルに合わせる）
CTF_INDENT = "  "        # 2
CAT_INDENT = "      "    # 6
ITEM_INDENT = "          "  # 10


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"{prompt}{suffix}: ").strip()
        if val:
            return val
        if default is not None:
            return default
        print("  入力してください。")


def ask_choice(prompt: str, options: dict[str, tuple[str, str]]) -> tuple[str, str]:
    print(prompt)
    for key, (_, label) in options.items():
        print(f"  {key}) {label}")
    while True:
        val = input("番号を選択: ").strip()
        if val in options:
            return options[val]
        print("  一覧から番号を選んでください。")


def slugify(name: str) -> str:
    """問題名を kebab-case のファイル名/URL向けslugに変換。"""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)  # 英数字以外はハイフンに
    s = s.strip("-")
    return s or "untitled"


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def insert_into_nav(ctf_display: str, category_display: str, title: str, relpath: str) -> bool:
    """mkdocs.yml の nav に 1エントリを差し込む。成功で True。"""
    if not MKDOCS.exists():
        return False
    lines = MKDOCS.read_text(encoding="utf-8").splitlines()

    # nav: の位置と、nav ブロックの終端を求める
    try:
        nav_idx = next(i for i, ln in enumerate(lines) if ln.rstrip() == "nav:")
    except StopIteration:
        return False
    nav_end = len(lines)
    for i in range(nav_idx + 1, len(lines)):
        ln = lines[i]
        if ln.strip() and indent_of(ln) == 0:  # 次のトップレベルキー
            nav_end = i
            break

    entry = f"{ITEM_INDENT}- {title}: {relpath}"
    cat_header = f"{CAT_INDENT}- {category_display}:"
    ctf_header = f"{CTF_INDENT}- {ctf_display}:"

    def find(header: str, start: int, end: int) -> int | None:
        target = header.strip()
        for i in range(start, end):
            if lines[i].strip() == target and indent_of(lines[i]) == indent_of(header):
                return i
        return None

    ctf_i = find(ctf_header, nav_idx + 1, nav_end)
    if ctf_i is None:
        # CTF ごと新設して nav 末尾に追加
        block = [ctf_header, cat_header, entry]
        lines[nav_end:nav_end] = block
        MKDOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True

    # CTF ブロックの終端（インデント<=2 で次の項目、または nav 終端）
    ctf_end = nav_end
    for i in range(ctf_i + 1, nav_end):
        if lines[i].strip() and indent_of(lines[i]) <= CTF_INDENT.__len__():
            ctf_end = i
            break

    cat_i = find(cat_header, ctf_i + 1, ctf_end)
    if cat_i is None:
        # カテゴリを新設して CTF ブロック末尾へ
        block = [cat_header, entry]
        lines[ctf_end:ctf_end] = block
        MKDOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True

    # カテゴリブロックの終端（インデント<=6 で次の項目）
    cat_end = ctf_end
    for i in range(cat_i + 1, ctf_end):
        if lines[i].strip() and indent_of(lines[i]) <= CAT_INDENT.__len__():
            cat_end = i
            break
    lines[cat_end:cat_end] = [entry]
    MKDOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def build_markdown(meta: dict) -> str:
    tag_lines = "\n".join(f"  - {t}" for t in meta["tags"])
    return f"""---
tags:
{tag_lines}
---

# {meta['name']}

## 問題
- **プラットフォーム / CTF**: {meta['ctf']}
- **カテゴリ**: {meta['category']}
- **難易度**: {meta['difficulty']}
- **リンク**: {meta['link']}
- **説明**: {meta['description']}

## 使った技術・脆弱性
<!-- 使った脆弱性・手法を箇条書きで -->

## 解答までの道筋
1.
2.
3.

## 決め手 / つまずいた点
<!-- 思考プロセスを言語化 -->

## 学んだこと

## 参考
-
"""


def main() -> int:
    print("=== 新しい writeup を作成 ===\n")

    name = ask("問題名")
    ctf = ask("プラットフォーム / CTF", default="picoCTF")
    cat_dir, cat_display = ask_choice("\nカテゴリを選択:", CATEGORIES)

    print("\n難易度を選択:")
    for i, d in enumerate(DIFFICULTIES, 1):
        print(f"  {i}) {d}")
    di = input("番号を選択 [1]: ").strip() or "1"
    difficulty = DIFFICULTIES[int(di) - 1] if di.isdigit() and 1 <= int(di) <= len(DIFFICULTIES) else "Easy"

    link = ask("リンク (URL)", default="")
    description = ask("説明 (1行)", default="")

    # タグ: カテゴリ名とCTF名を既定に、追加分をカンマ/空白区切りで受け取る
    default_tags = [cat_display, ctf]
    extra = input(f"追加タグ (カンマ区切り, 既定: {', '.join(default_tags)}): ").strip()
    extra_tags = [t.strip() for t in re.split(r"[,\s]+", extra) if t.strip()]
    # 重複を除きつつ順序維持: カテゴリ, 追加タグ..., CTF
    seen: set[str] = set()
    tags: list[str] = []
    for t in [cat_display, *extra_tags, ctf]:
        if t.lower() not in seen:
            seen.add(t.lower())
            tags.append(t)

    ctf_dir = slugify(ctf)
    slug = slugify(name)
    target_dir = DOCS / ctf_dir / cat_dir
    md_path = target_dir / f"{slug}.md"
    relpath = f"{ctf_dir}/{cat_dir}/{slug}.md"

    if md_path.exists():
        print(f"\n[中止] 既に存在します: {md_path.relative_to(ROOT)}")
        return 1

    meta = {
        "name": name,
        "ctf": ctf,
        "category": cat_display,
        "difficulty": difficulty,
        "link": link,
        "description": description,
        "tags": tags,
    }

    # 確認
    print("\n--- 生成内容 ---")
    print(f"  ファイル : docs/{relpath}")
    print(f"  問題名   : {name}")
    print(f"  CTF      : {ctf}")
    print(f"  カテゴリ : {cat_display}")
    print(f"  難易度   : {difficulty}")
    print(f"  タグ     : {', '.join(tags)}")
    if input("\nこの内容で作成しますか? [Y/n]: ").strip().lower() in ("n", "no"):
        print("中止しました。")
        return 1

    # 生成
    (target_dir / "images").mkdir(parents=True, exist_ok=True)
    md_path.write_text(build_markdown(meta), encoding="utf-8")
    print(f"\n[作成] docs/{relpath}")
    print(f"[作成] docs/{ctf_dir}/{cat_dir}/images/  (スクショ置き場)")

    if insert_into_nav(ctf, cat_display, name, relpath):
        print("[更新] mkdocs.yml の nav にエントリを追加")
    else:
        print("[注意] nav を自動更新できませんでした。mkdocs.yml に手動で追記してください:")
        print(f'        {ITEM_INDENT}- {name}: {relpath}')

    # VSCode で開く
    if input("\nVSCode で今すぐ開きますか? [y/N]: ").strip().lower() in ("y", "yes"):
        try:
            subprocess.run(["code", str(md_path)], check=False)
        except FileNotFoundError:
            print("  'code' コマンドが見つかりません（VSCodeのPATH連携が未設定）。手動で開いてください。")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n中止しました。")
        sys.exit(130)
