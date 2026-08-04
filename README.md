# ふくづくりくらぶ Webサイト

株式会社RSFが運営するオリジナルTシャツサービス「ふくづくりくらぶ」のサイト一式。
静的HTML／CSS／JS。ビルドはPython標準ライブラリのみで動く。

## リポジトリ直下の構成

このREADMEと同じ階層に以下が並んでいること。
`.github` がリポジトリ直下にないと、ワークフローが認識されない。

```
.github/workflows/deploy.yml   Pagesへの自動ビルド＆デプロイ
index.html                     トップページ（noindex入りのソース）
tokushoho.html                 特定商取引法に基づく表記
privacy.html                   プライバシーポリシー
404.html                       404ページ
site.webmanifest
build.py                       公開用ビルド（dist/ を生成）
.gitignore
assets/
  style.css  script.js
  hero-people.webp / hero-people.jpg   FV画像 1600x809
  ogp.jpg                              OGP画像 1200x630
  favicon.svg  icon-192.png  icon-512.png
```

## 公開手順

1. リポジトリ直下にこのフォルダの中身を置いて push（ブランチは `main`）
2. Settings > Pages > Source を **GitHub Actions** に変更
3. Actions タブで `Deploy to GitHub Pages` が緑になるのを待つ

Source が「Deploy from a branch」のままだとビルドが走らず、
noindex が付いたソースがそのまま公開される。canonical、OGP画像、
構造化データ、sitemap.xml も生成されない。必ず GitHub Actions を選ぶこと。

### 公開URL

ワークフローが自動で決める。

- 既定：`https://<owner>.github.io/<repo>/`
- カスタムドメイン：Settings > Secrets and variables > Actions > Variables に
  `SITE_BASE_URL`（末尾スラッシュ付き。例 `https://fukuzukuri.example.com/`）を登録

リポジトリ名がそのまま公開URLになるので、SNSやLINEに貼る前に名前を確定させること。
リネームすれば次の push で新URLを拾い直す。

## ローカル確認

`index.html` をそのままブラウザで開けば見た目は確認できる。
ソースには誤公開防止の `noindex,nofollow` が入っている（ビルド時に自動で外れる）。

公開後と同じ状態を確認したい場合：

```bash
python build.py --base-url https://wg-ryo-a.github.io/huku/
cd dist && python -m http.server 8000
```

## build.py がやること

- `noindex,nofollow` を除去
- `canonical` / `og:url` / `og:image` / `og:site_name` を絶対URLで挿入
- 構造化データ（Organization / WebSite / Product / FAQPage）を挿入
  FAQは `index.html` の `<details>` から自動抽出するので、本文を直せば構造化データも追随する
- `sitemap.xml` / `robots.txt` / `.nojekyll` を生成
- `--line-url` を渡すとLINE友だち追加URLを全ページ一括置換

```bash
python build.py --base-url https://example.com/ --line-url https://lin.ee/xxxxxxx
```

ワークフローには noindex の残留・canonical・og:image・構造化データの有無を検査する
ステップが入っている。どれか欠けるとデプロイは失敗する。

## 編集時の注意

FVを差し替えるなど大きく作り直したときに、以下が巻き戻りやすい。
過去に一度全部戻ったことがあるので、`git diff` で確認すること。

- LINE URLの `%40` エンコード（`@` のままでも動くがLINE側の推奨外）
- 画像の `width` / `height` と CSS の `aspect-ratio`（実ファイルは 1600x809）
- ヘッダーの `white-space: nowrap` と 380px未満タイア
- `section[id], main[id]` の `scroll-margin-top`
- 注文フローの8カラムグリッド
- 特商法の「サイト名・屋号」行

---

## 公開前に確認が必要なもの

### 1. LINEアカウント（未解決・最優先）

現在のリンク先は `https://line.me/R/ti/p/%40116fanfi`。
この `@116fanfi` は他事業で使っているアカウントIDと同一。
専用アカウントを取ったら `build.py --line-url` で差し替えるか、
`index.html` 内の6箇所を直接置換すること。

流用したままだと、Tシャツの相談と他事業の問い合わせが同じトークに混在し、
友だち追加経路の分析も切り分けられない。

### 2. 電話番号

`03-6233-8242` を特商法表記・フッター・構造化データに記載している。
現行の受電回線かどうかは未検証。

### 3. 画像の中身

`hero-people.jpg` と `ogp.jpg` は目視確認が未了。

---

## 未確定のため、あえて書いていない事業データ

- ボディの商品名・メーカー・オンス数
- サイズ表、カラー一覧
- 最大印刷寸法
- 通常納期の目安
- 実物の作例写真（現状はFV画像を商品仕様セクションでも流用している）

作例写真と、サイズ展開・カラー数は確定次第入れる。
商品仕様セクションは6項目中4項目が「要相談」で、閲覧者の疑問が解けていない。
