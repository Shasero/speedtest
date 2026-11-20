#!/usr/bin/env python3
"""Замер скорости скачивания: N последовательных GET-запросов к URL."""

import argparse
import sys
import time
import urllib.error
import urllib.request


def download_once(url: str, timeout: float) -> tuple[float, int]:
    """Скачивает url целиком, возвращает (время_в_секундах, размер_в_байтах)."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "speedtest-cli/1.0"}
    )
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = 0
        # Читаем чанками, чтобы не держать весь файл в памяти
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
    elapsed = time.perf_counter() - start
    return elapsed, total


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Последовательно скачивает URL N раз и считает среднюю скорость."
    )
    parser.add_argument("url", help="URL для скачивания")
    parser.add_argument("-n", "--count", type=int, default=10,
                        help="Количество запросов (по умолчанию 10)")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="Таймаут одного запроса, сек (по умолчанию 30)")
    args = parser.parse_args()

    if args.count <= 0:
        print("Ошибка: --count должен быть > 0", file=sys.stderr)
        return 2

    times: list[float] = []
    total_bytes = 0

    for i in range(1, args.count + 1):
        try:
            elapsed, size = download_once(args.url, args.timeout)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"[{i}/{args.count}] ОШИБКА: {exc}", file=sys.stderr)
            return 1

        times.append(elapsed)
        total_bytes += size
        mbps = (size * 8) / elapsed / 1_000_000 if elapsed > 0 else 0.0
        print(f"[{i}/{args.count}] {size} байт за {elapsed:.3f} с  ({mbps:.2f} Mbit/s)")

    total_time = sum(times)
    avg_time = total_time / len(times)
    avg_speed = (total_bytes * 8) / total_time / 1_000_000 if total_time else 0.0

    print()
    print(f"Запросов:            {args.count}")
    print(f"Скачано всего:       {total_bytes} байт ({total_bytes / (1024 * 1024):.2f} MiB)")
    print(f"Общее время:         {total_time:.3f} с")
    print(f"Среднее время:       {avg_time:.3f} с/запрос")
    print(f"Средняя скорость:    {avg_speed:.2f} Mbit/s")
    return 0


if __name__ == "__main__":
    sys.exit(main())