#!/usr/bin/env python3
import argparse
from typing import List


def generate_urls(template: str, start: int, end: int, zfill: int = 0) -> List[str]:
    urls: List[str] = []
    for i in range(start, end + 1):
        num = str(i).zfill(zfill) if zfill > 0 else str(i)
        urls.append(template.replace("{num}", num))
    return urls


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera URLs de episódios a partir de um template com {num}")
    parser.add_argument("--template", required=True, help="Ex.: https://site/temporada-01/episodio-{num}/")
    parser.add_argument("--start", type=int, required=True, help="Número inicial")
    parser.add_argument("--end", type=int, required=True, help="Número final (inclusive)")
    parser.add_argument("--zfill", type=int, default=0, help="Zero padding do número (ex.: 2 => 01, 02)")
    args = parser.parse_args()

    for url in generate_urls(args.template, args.start, args.end, args.zfill):
        print(url)


if __name__ == "__main__":
    main()

