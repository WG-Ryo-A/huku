# ふくづくりくらぶ Webサイト

株式会社RSFが運営するオリジナルTシャツサービス「ふくづくりくらぶ」の静的サイト。

## 主な実装

- 1枚から・片面1,000円を最上部で訴求
- 実際の制作事例を掲載
- 制作事例のカテゴリ絞り込み
- 片面／両面の料金表示
- 利用シーン、デザイン対応、商品仕様、注文フロー、FAQ
- LINE導線を全ページで統一
- 特定商取引法に基づく表記・プライバシーポリシー
- PC／タブレット／スマートフォン対応
- OGP、構造化データ、sitemap、robots.txtの公開用ビルド

## LINE URL

`https://line.me/R/ti/p/%40116fanfi`

## 構成

```text
.github/workflows/deploy.yml
index.html
privacy.html
tokushoho.html
404.html
site.webmanifest
build.py
assets/
  style.css
  script.js
  works/               制作事例画像（WebP）
  ogp.jpg
  favicon.svg
  icon-192.png
  icon-512.png
```

## 公開用ビルド

ソースHTMLには誤公開防止の `noindex,nofollow` が入っています。
公開時は必ず `build.py` を実行し、生成された `dist/` を公開してください。

```bash
python build.py --base-url https://example.com/
```

公開URLを指定すると以下を自動生成・反映します。

- noindexの除去
- canonical
- og:url / og:image
- Organization / WebSite / Product / FAQPage の構造化データ
- sitemap.xml
- robots.txt

## 注文条件

- 最低注文枚数：1枚
- 片面フルカラー：1枚1,000円（税込）
- 両面フルカラー：1枚1,500円（税込）
- 送料：全国一律1,000円（税込）
- 支払方法：銀行振込、クレジットカード、PayPay
- 支払時期：前払い
- 修正：2往復まで無料

## 未確定のためサイトで個別案内としている項目

- ボディの商品名・メーカー・オンス数
- サイズ表、カラー一覧
- 最大印刷寸法
- 通常納期の固定日数
- 3往復目以降の修正料金
