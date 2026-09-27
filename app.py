"""Локальный просмотр сайта: python app.py → http://127.0.0.1:5000/

Страницы собираются на лету из того же реестра, что и generate_static.py,
поэтому правки в content/ видны сразу после обновления страницы.
"""
from flask import Flask, abort, redirect, render_template

from nair_site import Site

app = Flask(__name__)


@app.route('/')
@app.route('/<slug>.html')
def page(slug='index'):
    site = Site()
    if slug in site.aliases:
        return redirect(f'/{site.aliases[slug]}.html', code=301)
    if slug not in site.pages:
        abort(404)
    return render_template(site.pages[slug]['template'], **site.context(slug))


if __name__ == '__main__':
    app.run(debug=True)
