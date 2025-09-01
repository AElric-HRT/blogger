#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Any, Dict, List, Optional

import yt_dlp


def extract_streams(url: str, extractor_args: Optional[List[str]] = None) -> Dict[str, Any]:
    ydl_opts: Dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "skip_download": True,
        "format": "best/bestvideo+bestaudio",
        "outtmpl": {"default": "-"},
        "http_headers": {
            # Some hosts require a Referer; add common permissive headers.
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        },
    }

    if extractor_args:
        # Allow passing raw yt-dlp extractor args like --add-header Referer:https://...
        # Expose minimal subset via ydl_opts for safety.
        for arg in extractor_args:
            if arg.lower().startswith("referer:"):
                ydl_opts.setdefault("http_headers", {})["Referer"] = arg.split(":", 1)[1].strip()
            elif arg.lower().startswith("origin:"):
                ydl_opts.setdefault("http_headers", {})["Origin"] = arg.split(":", 1)[1].strip()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    def simplify(entry: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": entry.get("id"),
            "title": entry.get("title"),
            "ext": entry.get("ext"),
            "protocol": entry.get("protocol"),
            "url": entry.get("url"),
            "format_id": entry.get("format_id"),
            "format_note": entry.get("format_note"),
            "acodec": entry.get("acodec"),
            "vcodec": entry.get("vcodec"),
            "tbr": entry.get("tbr"),
            "filesize": entry.get("filesize"),
            "height": entry.get("height"),
            "width": entry.get("width"),
            "fps": entry.get("fps"),
        }

    result: Dict[str, Any] = {
        "source_url": url,
        "webpage_url": info.get("webpage_url", url),
        "title": info.get("title"),
        "extractor": info.get("extractor_key"),
        "duration": info.get("duration"),
        "formats": sorted(
            [simplify(f) for f in info.get("formats", []) if isinstance(f, dict) and f.get("url")],
            key=lambda f: (f.get("height") or 0, f.get("tbr") or 0),
        ),
    }
    # Best guess direct stream: prefer m3u8/hls if present, else best mp4
    preferred = None
    for f in reversed(result["formats"]):
        url_f = (f.get("url") or "").lower()
        if "m3u8" in url_f or f.get("protocol") == "m3u8_native" or f.get("protocol") == "m3u8" or f.get("ext") == "mp4":
            preferred = f
            break
    result["preferred"] = preferred
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai links de vídeo (m3u8/mp4) usando yt-dlp")
    parser.add_argument("urls", nargs="+", help="URL(s) da página do episódio ou player")
    parser.add_argument(
        "--header",
        action="append",
        dest="headers",
        help="Cabeçalhos opcionais (ex: Referer:https://site-alvo)",
    )
    parser.add_argument("--json", action="store_true", help="Saída em JSON completa")
    args = parser.parse_args()

    all_results: List[Dict[str, Any]] = []
    for url in args.urls:
        try:
            data = extract_streams(url, extractor_args=args.headers)
            all_results.append(data)
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao extrair {url}: {exc}", file=sys.stderr)
            continue

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
    else:
        for it in all_results:
            print(f"\nTítulo: {it.get('title')} | URL: {it.get('webpage_url')} | Extractor: {it.get('extractor')}")
            pref = it.get("preferred")
            if pref:
                print(f"Link preferido: {pref.get('url')}")
            else:
                print("Nenhum formato preferido encontrado. Use --json para ver todos os formatos.")


if __name__ == "__main__":
    main()

