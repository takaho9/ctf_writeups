# CTF Writeups

解いたCTF問題のwriteup集。セキュリティ学習の記録＆ポートフォリオ。
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) で静的サイト化し GitHub Pages で公開しています。

公開URL: https://takaho9.github.io/ctf_writeups/

## 構成

```
docs/                     # 公開されるコンテンツ
  index.md                # トップページ（問題一覧）
  notes/                  # 調べたことのメモ・チートシート
  tags.md                 # タグ別一覧（自動生成）
  <ctf>/<category>/
    <challenge>.md        # writeup 本体
    images/               # 画像（記事と同ディレクトリ）
scripts/                  # 作成補助スクリプト
template.md               # 新規writeupのテンプレ
mkdocs.yml                # サイト設定
```

## 新しく書く

```bash
python scripts/new_writeup.py   # 問題のwriteup（メタデータを対話入力）
python scripts/new_note.py      # 調べたことのメモ（全項目Enterでスキップ可）
```

どちらも雛形の生成・`mkdocs.yml` の `nav` 追記まで自動で行う。
手動で作る場合は `template.md` をコピーして配置し、`nav` に追記する。

## ローカルプレビュー

```bash
pip install --user -r requirements.txt
python -m mkdocs serve      # http://127.0.0.1:8000
```

## 公開

`main` に push すると `.github/workflows/deploy.yml` が走り、ビルド結果が `gh-pages` ブランチへ自動デプロイされる。

初回のみ GitHub リポジトリの **Settings → Pages → Source** を `gh-pages` ブランチに設定する（これで公開URLに反映される）。

## 注意

開催中CTFの解答公開はルール違反になることが多いため、公開対象は **終了済み or 常設練習問題** に限る。
