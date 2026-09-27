"""Сборка статического сайта в папку docs/ (запускается в GitHub Actions).

Список страниц берётся из nair_site.py: вручную свёрстанные шаблоны
плюс все Markdown-файлы из content/.
"""
import os
import shutil

from flask import Flask, render_template

from nair_site import Site

OUTPUT_DIR = 'docs'
REDIRECT = ('<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
            '<meta http-equiv="refresh" content="0; url={url}"><link rel="canonical" href="{url}">'
            '<title>Страница переехала</title></head>'
            '<body><a href="{url}">Страница переехала</a></body></html>')


def build():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    site = Site()

    # очищаем содержимое, а не саму папку (её может держать локальный сервер)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copytree('static', os.path.join(OUTPUT_DIR, 'static'))

    errors = 0
    with app.test_request_context():
        for slug, page in site.pages.items():
            try:
                html = render_template(page['template'], **site.context(slug))
            except Exception as e:  # продолжаем сборку, но падаем в конце
                errors += 1
                print(f'❌ {slug}.html: {e}')
                continue
            with open(os.path.join(OUTPUT_DIR, f'{slug}.html'), 'w', encoding='utf-8') as f:
                f.write(html)

    # старые адреса переименованных страниц → перенаправление на новые
    for old, new in site.aliases.items():
        with open(os.path.join(OUTPUT_DIR, f'{old}.html'), 'w', encoding='utf-8') as f:
            f.write(REDIRECT.format(url=f'{new}.html'))

    with open(os.path.join(OUTPUT_DIR, '.nojekyll'), 'w') as f:
        f.write('')

    print(f'🎉 Собрано страниц: {len(site.pages) - errors}, ошибок: {errors}')
    return errors == 0


if __name__ == '__main__':
    raise SystemExit(0 if build() else 1)
