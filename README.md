# ふくづくりくらぶ Webサイト

株式会社RSFが運営するオリジナルTシャツサービス「ふくづくりくらぶ」のサイト一式。
静的HTML／CSS／JS。ビルドはPython標準ライブラリのみで動く。

## 構成

```
index.html          トップページ（プレビュー版：noindex入り）
tokushoho.html      特定商取引法に基づく表記
privacy.html        プライバシーポリシー
404.html            404ページ
site.webmanifest    Web App Manifest
build.py            公開用ビルド（dist/ を生成）
assets/
  style.css         全ページ共通スタイル
  script.js         ナビゲーション開閉のみ
  hero-people.webp  FV画像（1600x809）
  hero-people.jpg   FV画像フォールバック
  ogp.jpg           OGP画像（1200x630）
  favicon.svg / icon-192.png / icon-512.png
.github/workflows/deploy.yml   Pagesへの自動ビルド＆デプロイ
```

## GitHubへの上げ方

1. リポジトリを作成してこのフォルダの中身をpush（ブランチ名は `main`）
2. リポジトリの Settings > Pages > Source を **GitHub Actions** に変更
3. pushすると deploy.yml が走り、`dist/` の内容が公開される

公開URLはワークフローが自動で決める。

- 既定：`https://<owner>.github.io/<repo>/`
- カスタムドメイン：Settings > Secrets and variables > Actions > Variables に
  `SITE_BASE_URL`（例 `https://fukuzukuri.example.com/`）を登録すると、そちらが優先される

Pagesの Source を「Deploy from a branch」にすると **ビルドが走らずnoindexのまま公開される**。
必ず GitHub Actions を選ぶこと。

## ローカルでの確認

`index.html` をそのままブラウザで開けば見た目は確認できる。
ソースには誤公開防止の `noindex,nofollow` が入っている（ビルド時に自動で外れる）。

公開後と同じ状態を手元で確認したい場合：

```bash
python build.py --base-url https://wg-ryo-a.github.io/fukuzukuri-club/
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

ワークフローには、noindexの残留・canonical・og:image・構造化データの有無を検査する
ステップが入っている。どれか欠けるとデプロイは失敗する。

---

## 公開前に確認が必要なもの

### 1. LINEアカウント（未解決・最優先）

現在のリンク先は `https://line.me/R/ti/p/%40116fanfi`。
この `@116fanfi` は他事業で使っているアカウントIDと同一。
ふくづくりくらぶ専用アカウントを取るなら、`build.py --line-url` で差し替えるか、
HTML内の5箇所を直接置換すること。

流用したままだと、Tシャツの相談と他事業の問い合わせが同じトークに混在し、
友だち追加経路の分析も切り分けられない。

なおURL形式は、LINE Developersの仕様に従い `@` をパーセントエンコード（`%40`）済み。
未エンコードでも動作はするが非推奨とされているため。
管理画面が発行する `lin.ee` の短縮URLでも可。

### 2. 電話番号

`03-6233-8242` を特商法表記・フッター・構造化データに記載している。
現行の受電回線かどうかは未検証。

### 3. 画像の中身

`hero-people.jpg` と `ogp.jpg` は目視確認が未了。
焼き込み文字の残りや生成画像特有の破綻がないか確認すること。

---

## 未確定のため、あえて書いていない事業データ

事実を作らず「注文確定前に個別提示」としている項目：

- ボディの商品名・メーカー・オンス数
- サイズ表、カラー一覧
- 最大印刷寸法
- 通常納期の目安
- 実物の作例写真（現状はFV画像を商品仕様セクションでも流用している）

作例写真と、せめてサイズ展開・カラー数は、確定次第入れたほうがいい。
商品仕様セクションは6項目中4項目が「要相談」で、閲覧者の疑問が解けていない。
