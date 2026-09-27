"""Нарезает большую карту (static/photo/Karta.png) на плитки webp для Leaflet.

Уровни 0..MAX_ZOOM, плитка 512×512; на последнем уровне — исходное разрешение.
Крайние плитки дополняются прозрачностью до полного размера.
Запуск после обновления карты:  python tools/make_map_tiles.py
"""
import math
import os
import shutil

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SRC = 'static/photo/Karta.png'
OUT = 'static/photo/map-tiles'
TILE = 512
QUALITY = 80


def main():
    src = Image.open(SRC).convert('RGB')
    w, h = src.size
    max_zoom = math.ceil(math.log2(max(w, h) / TILE))
    shutil.rmtree(OUT, ignore_errors=True)
    total = 0
    for z in range(max_zoom + 1):
        k = 2 ** (max_zoom - z)
        level = src if k == 1 else src.resize((math.ceil(w / k), math.ceil(h / k)), Image.LANCZOS)
        cols, rows = math.ceil(level.width / TILE), math.ceil(level.height / TILE)
        for x in range(cols):
            os.makedirs(f'{OUT}/{z}/{x}', exist_ok=True)
            for y in range(rows):
                box = (x * TILE, y * TILE, min((x + 1) * TILE, level.width), min((y + 1) * TILE, level.height))
                tile = level.crop(box)
                if tile.size != (TILE, TILE):
                    padded = Image.new('RGBA', (TILE, TILE), (0, 0, 0, 0))
                    padded.paste(tile, (0, 0))
                    tile = padded
                tile.save(f'{OUT}/{z}/{x}/{y}.webp', 'WEBP', quality=QUALITY, method=6)
                total += 1
        print(f'z{z}: {cols}x{rows}')
    # превью целиком — фон под плитками, пока они грузятся
    preview = src.copy()
    preview.thumbnail((1024, 1024), Image.LANCZOS)
    preview.save(f'{OUT}/preview.webp', 'WEBP', quality=70)
    print(f'плиток: {total}, размер карты {w}x{h}, maxZoom {max_zoom}')


if __name__ == '__main__':
    main()
