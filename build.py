#!/usr/bin/env python3
"""ふくづくりくらぶ 公開用ビルド。

ソースの index.html / tokushoho.html / privacy.html は noindex 付きのプレビュー版。
このスクリプトが dist/ に公開用ファイルを生成する。

  - noindex,nofollow を除去
  - canonical / og:url / og:image を絶対URLで挿入
  - 構造化データ（Organization / WebSite / Product / FAQPage）を挿入
  - robots.txt / sitemap.xml / .nojekyll を生成
  - 必要なら LINE 友だち追加URLを一括置換

使い方:
  python build.py --base-url https://wg-ryo-a.github.io/fukuzukuri-club/
  python build.py --base-url https://example.com/ --line-url https://lin.ee/xxxxxxx
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
PAGES = ("index.html", "tokushoho.html", "privacy.html")
EXTRA_FILES = ("site.webmanifest", "404.html")

NOINDEX_LINE = '  <meta name="robots" content="noindex,nofollow" data-build-remove>\n'
THEME_LINE = '  <meta name="theme-color" content="#075985">\n'
OG_LOCALE_LINE = '  <meta property="og:locale" content="ja_JP">\n'

COMPANY = {
    "legalName": "株式会社RSF",
    "brand": "ふくづくりくらぶ",
    "streetAddress": "新宿5丁目4-1 Qフラットビル408",
    "addressLocality": "新宿区",
    "addressRegion": "東京都",
    "postalCode": "160-0022",
    "telephone": "+81-3-6233-8242",
    "email": "business@rsf-1.co.jp",
    "parentUrl": "https://rsf-1.co.jp/",
}


def validate_base_url(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise argparse.ArgumentTypeError("--base-url は https:// から始まる絶対URLで指定してください")
    return value if value.endswith("/") else value + "/"


def validate_line_url(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise argparse.ArgumentTypeError("--line-url は https:// から始まる絶対URLで指定してください")
    return value


def insert_after(source: str, needle: str, content: str) -> str:
    if needle not in source:
        raise RuntimeError(f"ビルドマーカーが見つかりません: {needle.strip()}")
    return source.replace(needle, needle + content, 1)


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def extract_faq(source: str) -> list[dict[str, str]]:
    """index.html の details/summary から FAQ を抽出する（本文との二重管理を避けるため）。"""
    pattern = re.compile(
        r"<details>\s*<summary>(?P<q>.*?)</summary>\s*<p>(?P<a>.*?)</p>\s*</details>",
        re.DOTALL,
    )
    faq = [
        {"q": strip_tags(m.group("q")), "a": strip_tags(m.group("a"))}
        for m in pattern.finditer(source)
    ]
    if not faq:
        raise RuntimeError("FAQを抽出できませんでした。index.html の details 構造を確認してください")
    return faq


def build_jsonld(base_url: str, faq: list[dict[str, str]]) -> str:
    org_id = urljoin(base_url, "#organization")
    site_id = urljoin(base_url, "#website")

    shipping = {
        "@type": "OfferShippingDetails",
        "shippingRate": {"@type": "MonetaryAmount", "value": 1000, "currency": "JPY"},
        "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "JP"},
    }

    def offer(name: str, price: int) -> dict:
        return {
            "@type": "Offer",
            "name": name,
            "price": price,
            "priceCurrency": "JPY",
            "availability": "https://schema.org/InStock",
            "seller": {"@id": org_id},
            "shippingDetails": shipping,
            "url": base_url,
        }

    graph = [
        {
            "@type": "Organization",
            "@id": org_id,
            "name": COMPANY["brand"],
            "legalName": COMPANY["legalName"],
            "url": base_url,
            "parentOrganization": {
                "@type": "Organization",
                "name": COMPANY["legalName"],
                "url": COMPANY["parentUrl"],
            },
            "email": COMPANY["email"],
            "telephone": COMPANY["telephone"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": COMPANY["streetAddress"],
                "addressLocality": COMPANY["addressLocality"],
                "addressRegion": COMPANY["addressRegion"],
                "postalCode": COMPANY["postalCode"],
                "addressCountry": "JP",
            },
        },
        {
            "@type": "WebSite",
            "@id": site_id,
            "url": base_url,
            "name": COMPANY["brand"],
            "inLanguage": "ja",
            "publisher": {"@id": org_id},
        },
        {
            "@type": "Product",
            "name": "オリジナルTシャツ（フルカラー印刷）",
            "description": "文化祭・体育祭・部活動向けのオリジナルTシャツ。1枚から注文可能。Tシャツ代、フルカラー印刷費、印刷用データ調整費、消費税込み。",
            "image": urljoin(base_url, "assets/ogp.jpg"),
            "brand": {"@id": org_id},
            "offers": [offer("片面フルカラー印刷", 1000), offer("両面フルカラー印刷", 1500)],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in faq
            ],
        },
    ]

    payload = json.dumps(
        {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2
    )
    payload = payload.replace("</", "<\\/")
    body = "\n".join("  " + line for line in payload.splitlines())
    return f'  <script type="application/ld+json">\n{body}\n  </script>\n'


def write_sitemap(base_url: str) -> None:
    today = date.today().isoformat()
    entries = []
    for filename in PAGES:
        loc = base_url if filename == "index.html" else urljoin(base_url, filename)
        priority = "1.0" if filename == "index.html" else "0.4"
        entries.append(
            "  <url>\n"
            f"    <loc>{html.escape(loc)}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    body = "\n".join(entries)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n",
        encoding="utf-8",
    )


def write_robots(base_url: str) -> None:
    (DIST / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n" f"Sitemap: {urljoin(base_url, 'sitemap.xml')}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, type=validate_base_url)
    parser.add_argument(
        "--line-url",
        type=validate_line_url,
        help="LINE友だち追加URLを差し替える場合に指定（省略時はHTMLの記述をそのまま使う）",
    )
    args = parser.parse_args()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    for name in EXTRA_FILES:
        source_file = ROOT / name
        if source_file.exists():
            shutil.copy2(source_file, DIST / name)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    index_source = (ROOT / "index.html").read_text(encoding="utf-8")
    faq = extract_faq(index_source)
    jsonld = build_jsonld(args.base_url, faq)

    line_replacements = 0
    for filename in PAGES:
        source = (ROOT / filename).read_text(encoding="utf-8")

        if NOINDEX_LINE not in source:
            raise RuntimeError(f"{filename}: noindex マーカーが見つかりません")
        source = source.replace(NOINDEX_LINE, "", 1)

        if args.line_url:
            found = re.findall(r'https://line\.me/R/ti/p/[^"\']+', source)
            line_replacements += len(found)
            for url in set(found):
                source = source.replace(url, args.line_url)

        page_url = args.base_url if filename == "index.html" else urljoin(args.base_url, filename)
        canonical = f'  <link rel="canonical" href="{html.escape(page_url, quote=True)}">\n'
        source = insert_after(source, THEME_LINE, canonical)

        if filename == "index.html":
            og_image = html.escape(urljoin(args.base_url, "assets/ogp.jpg"), quote=True)
            social_meta = (
                f'  <meta property="og:url" content="{html.escape(args.base_url, quote=True)}">\n'
                f'  <meta property="og:image" content="{og_image}">\n'
                '  <meta property="og:image:width" content="1200">\n'
                '  <meta property="og:image:height" content="630">\n'
                '  <meta property="og:site_name" content="ふくづくりくらぶ">\n'
            )
            source = insert_after(source, OG_LOCALE_LINE, social_meta + jsonld)

        (DIST / filename).write_text(source, encoding="utf-8")

    write_sitemap(args.base_url)
    write_robots(args.base_url)

    print(f"ビルド完了: {DIST}")
    print(f"  ベースURL      : {args.base_url}")
    print(f"  FAQ構造化データ: {len(faq)}件")
    if args.line_url:
        print(f"  LINE URL置換   : {line_replacements}箇所 -> {args.line_url}")


if __name__ == "__main__":
    main()
