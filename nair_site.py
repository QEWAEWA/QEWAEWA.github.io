"""Общий реестр страниц сайта Наир.

Страницы бывают двух видов:
  * шаблонные — вручную свёрстанные шаблоны из templates/ (TEMPLATE_PAGES);
  * контентные — Markdown-файлы из content/, найденные автоматически.

Чтобы добавить новую контентную страницу, достаточно положить .md файл
в content/ (подпапки только для порядка). Шапка файла:

    title: Граальды
    parent: rasy            # slug родительской страницы
    order: 10               # порядок среди соседей (необязательно)
    summary: Коротко о...   # подпись на карточке (необязательно)
    image: photo/vk/533473434_457240853.jpg   # картинка карточки
    banner: photo/vk/...    # широкая картинка в шапке страницы
    group: Типы магии       # заголовок группы карточек у родителя
    nav_title: Сюжет        # подпись в левом меню, если отличается
    art: photo/kratko.webp  # арт для больших карточек-кнопок (как в Экономике)
    art_nav: a b c          # у раздела: slug'и страниц для карточек с артами;
                            # показываются на самой странице и всех её потомках
    art_position: center 20%  # какую часть арта показывать на кнопке
    art_size: auto 150%     # масштаб арта на кнопке (CSS background-size), для «покрупнее»
    art_fit: contain        # показать арт на кнопке целиком, по бокам — размытый фон
    cards: art              # у раздела: дочерние страницы — большие кнопки с артами
    card_columns: 3         # у раздела: сколько кнопок-артов в ряд (по умолчанию 2; 1 — широкая)
    card_style: special     # у страницы: особый вид её кнопки (другой цвет и рамка)
    hero: photo/...         # шапка с картинкой, названием и подзаголовком внутри
    subtitle: Бестиарий     # подзаголовок в шапке hero
    hero_position: center 25%  # какую часть картинки показывать в шапке hero
    layout: profile         # портрет из начала страницы ставится рядом с первым разделом
    portrait: photo/...     # у страницы бога (layout: god): арт в шапке, если отличается от арта кнопки
    related: golm           # кнопки-арты на связанные страницы в конце страницы
    related_title: Дополнительная информация   # заголовок над ними
    vk: 55340430            # id вики-страниц ВК, откуда перенесено (можно несколько)
    aliases: gond           # старые адреса страницы: gond.html перенаправит на новую

Интерактивные блоки вставляются в текст строкой [[widget:имя]] — рисуется
шаблон templates/widgets/<имя>.html с данными из data/<имя>.json.

Имя файла без .md — это slug, страница собирается в <slug>.html.
Ссылки вида (vk:55340430) превращаются в ссылку на перенесённую страницу,
а если её ещё нет на сайте — в ссылку на страницу ВК.
"""
import html as html_lib
import json
import os
import re

import markdown
from markupsafe import Markup

CONTENT_DIR = 'content'
VK_PAGE_URL = 'https://vk.com/page-182026147_{}'

# Вручную свёрстанные страницы
TEMPLATE_PAGES = [
    {'slug': 'index', 'title': 'Главная', 'template': 'index.html', 'parent': None, 'vk': '54743839'},
    {'slug': 'karta', 'title': 'Карта', 'template': 'karta.html', 'parent': 'index', 'order': 60},
    {'slug': 'economy', 'title': 'Экономика', 'template': 'economy.html', 'parent': 'index', 'order': 42,
     'summary': 'Валюты, торговля и цены', 'vk': '54761810'},
    {'slug': 'leveling', 'title': 'Система прокачки', 'template': 'leveling.html', 'parent': 'index', 'order': 44, 'vk': '54762143'},
    {'slug': 'kuznec', 'title': 'Кузнечество', 'template': 'kuznec.html', 'parent': 'economy', 'order': 50,
     'image': 'photo/kuznec.png', 'summary': 'Цены на металлы и руду', 'vk': '55281736'},
    {'slug': 'oruzie', 'title': 'Оружие', 'template': 'oruzie.html', 'parent': 'economy', 'order': 10,
     'image': 'photo/oruzie.png', 'summary': 'Цены на оружие и покрытие серебром', 'vk': '54931996'},
    {'slug': 'bronya', 'title': 'Броня', 'template': 'bronya.html', 'parent': 'economy', 'order': 20,
     'image': 'photo/bronya.png', 'summary': 'Цены на доспехи и броню', 'vk': '54932002'},
    {'slug': 'zelya', 'title': 'Зелья', 'template': 'zelya.html', 'parent': 'economy', 'order': 30,
     'image': 'photo/zelya.png', 'summary': 'Цены на зелья и снадобья', 'vk': '54931999'},
    {'slug': 'prochee', 'title': 'Прочее', 'template': 'prochee.html', 'parent': 'economy', 'order': 40,
     'image': 'photo/prochee.png', 'summary': 'Тёмные писания и другое', 'vk': '54932010'},
    {'slug': 'about', 'title': 'О Проекте', 'template': 'about.html', 'parent': 'index', 'order': 90},
]

# Левое меню: slug'и в порядке показа (None — разделитель)
NAV = ['index', None, 'pravila', 'syuzhet-kratko', 'lor', 'magic',
       'economy', 'leveling', 'ankety', 'karta', 'about']

# nl2br: в текстах из ВК одиночный перенос строки — это настоящий перенос
MD_EXTENSIONS = ['meta', 'tables', 'attr_list', 'md_in_html', 'sane_lists', 'nl2br']


# Иконки для типовых разделов (иначе берётся иконка страницы)
SECTION_ICONS = {
    'общее описание': 'bi-info-circle',
    'названия': 'bi-tag',
    'внешность, строение и особенности': 'bi-person-bounding-box',
    'внешность': 'bi-person-bounding-box',
    'внешность и строение': 'bi-person-bounding-box',
    'культура, типичное поведение, положение среди остальных и места обитания': 'bi-globe2',
    'дополнительная информация': 'bi-link-45deg',
    'история': 'bi-hourglass-split',
    'характер': 'bi-emoji-neutral',
    'способности': 'bi-stars',
    'физические параметры': 'bi-heart-pulse',
    'прочие особенности': 'bi-three-dots',
    'места обитания': 'bi-geo-alt',
    'питание': 'bi-egg-fried',
    'образ жизни': 'bi-house',
    'поведение': 'bi-activity',
    'можно ли приручить?': 'bi-hand-index',
    # правила
    'коротко о главном': 'bi-lightning-charge',
    'правила флуда и общения вне ролевой': 'bi-chat-dots',
    'правила ведения игры, ролевой беседы': 'bi-feather',
    'заполнение анкеты': 'bi-file-earmark-person',
    'ведение боя': 'bi-shield-shaded',
    'общее': 'bi-exclamation-octagon',
    # фауна
    'активные способности': 'bi-lightning',
    'пассивные способности': 'bi-shield-check',
    'прочие особенности и детали': 'bi-journal-text',
    'поведение в бою': 'bi-crosshair',
    'зависимость от скверны': 'bi-exclamation-diamond',
    'краткое описание': 'bi-info-circle',
}


def _plain(html):
    return html_lib.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(html))).strip())


_IMG_RUN = re.compile(
    r'((?:<p><img alt="[^"]*" src="[^"]+"\s*/?></p>\s*)+)(?:<p><em>((?:(?!</?p>).)*?)</em></p>)?', re.S)


def _figures(html):
    """Картинки в тексте: одна — картинка с подписью, несколько подряд — карусель.
    У каждой картинки своя подпись (alt); строка курсивом после группы — общий заголовок карусели.
    Если alt у всех одинаковый (как в ВК), он и есть общая подпись."""
    def repl(m):
        imgs = re.findall(r'<img alt="([^"]*)" src="([^"]+)"', m.group(1))
        group = (m.group(2) or '').strip()
        alts = [a.strip() for a, _ in imgs]
        own = len(set(alts)) > 1 or len(imgs) == 1
        slides = []
        for i, (alt, src) in enumerate(imgs, 1):
            cap = (alt.strip() or group) if own else ''
            count = f'<span class="nf-count">{i} / {len(imgs)}</span>' if len(imgs) > 1 else ''
            capt = f'<figcaption><span>{cap}</span>{count}</figcaption>' if cap or count else ''
            slides.append(f'<figure class="nf-slide"><a class="nf-img" href="{src}" data-lightbox>'
                          f'<img src="{src}" alt="{alt}" loading="lazy"></a>{capt}</figure>')
        if len(slides) == 1:
            return f'<div class="nf-single">{slides[0]}</div>\n'
        title = group or (alts[0] if not own else '')
        head = f'<div class="nf-title"><span class="orn"></span> {title}</div>' if title else ''
        return (f'<div class="nf-carousel" data-carousel>{head}<div class="nf-stage"><div class="nf-track">' + ''.join(slides) + '</div>'
                '<button type="button" class="nf-nav nf-prev" aria-label="Назад"><i class="bi bi-chevron-left"></i></button>'
                '<button type="button" class="nf-nav nf-next" aria-label="Вперёд"><i class="bi bi-chevron-right"></i></button></div></div>\n')
    return _IMG_RUN.sub(repl, str(html))


def _years(n):
    n = int(n)
    if n % 10 == 1 and n % 100 != 11:
        return 'год'
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return 'года'
    return 'лет'


def _first_sentence(text, limit=320):
    text = text.strip()
    m = re.match(r'(.+?[.!?])(\s|$)', text)
    s = m.group(1) if m else text
    return s if len(s) <= limit else s[:limit].rsplit(' ', 1)[0] + '…'


def _taming(text):
    """Ответ из раздела «Можно ли приручить?» → yes / maybe / no."""
    t = text.lower().strip()
    if t.startswith(('нет', 'однозначно нет')) or 'неприручаем' in t or 'невозможно приручить' in t:
        return 'no'
    if 'подружиться' in t or 'сдружиться' in t:
        return 'maybe'
    if t.startswith(('да', 'можно')) or 'легко приручаем' in t or 'питомец' in t:
        return 'yes'
    return 'maybe'


_TRANSLIT = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                     ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
                      'u', 'f', 'h', 'c', 'ch', 'sh', 'sch', '', 'y', '', 'e', 'yu', 'ya']))


def _anchor(title):
    """«Архипелаги аанари» → arhipelagi-aanari (постоянный якорь для ссылок на раздел)."""
    text = ''.join(_TRANSLIT.get(ch, ch) for ch in _plain(title).lower())
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


TAMING_LABELS = {'yes': 'Приручаем', 'maybe': 'Можно подружиться', 'no': 'Не приручить'}


def _rules_sections(sections):
    """Страница правил: «Коротко о главном» — карточки, остальные разделы —
    нумерованные пункты (1.1, 1.2…) с якорями; «! » в начале пункта — важный."""
    number = 0
    for section in sections:
        body = str(section['body'])
        title = re.sub(r'<[^>]+>', '', str(section.get('title') or '')).strip().lower()
        items = re.findall(r'<li>(.*?)</li>', body, flags=re.S)
        if not items:
            continue
        if title == 'коротко о главном':
            cards = []
            for item in items:
                item = re.sub(r'^\s*<p>|</p>\s*$', '', item.strip())
                m = re.match(r'\[(bi-[\w-]+)\]\s*<strong>(.*?)</strong>\s*(?:—\s*)?(.*)', item, flags=re.S)
                if not m:
                    continue
                cards.append(f'<div class="nair-rules-key"><i class="bi {m.group(1)}"></i>'
                             f'<div><div class="nair-rules-key-title">{m.group(2)}</div>'
                             f'<div class="nair-rules-key-text">{m.group(3)}</div></div></div>')
            section['kind'] = 'summary'
            section['body'] = Markup(f'<div class="nair-rules-keys">{"".join(cards)}</div>')
            continue
        number += 1
        rows = []
        for k, item in enumerate(items, 1):
            item = re.sub(r'^\s*<p>|</p>\s*$', '', item.strip())
            important = item.startswith('! ')
            item = item[2:] if important else item
            anchor = f'rule-{number}-{k}'
            rows.append(f'<li id="{anchor}" class="nair-rule{" nair-rule--important" if important else ""}">'
                        f'<a class="nair-rule-num" href="#{anchor}" title="Ссылка на пункт {number}.{k}">{number}.{k}</a>'
                        f'<div class="nair-rule-body">{item}</div></li>')
        section['kind'] = 'rules'
        section['number'] = number
        section['count'] = len(items)
        section['anchor'] = f'rules-{number}'
        section['body'] = Markup(f'<ol class="nair-rules">{"".join(rows)}</ol>')
    return sections


def _paragraphs(text):
    """В ВК абзацы разделены одиночным переносом строки. Длинные строки прозы
    делаем отдельными абзацами; короткие (стихи, молитвы, строки «Имя - ...»)
    остаются переносами внутри одного абзаца."""
    lines = text.split('\n')
    out = []
    special = re.compile(r'^\s*([-*] |\d+\. |#|\||!\[|>)')
    for i, line in enumerate(lines):
        out.append(line)
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            if (line.strip() and nxt.strip() and not special.match(line) and not special.match(nxt)
                    and (len(line) > 120 or len(nxt) > 120)):
                out.append('')
    return '\n'.join(out)


def _is_wide(src):
    """Горизонтальная ли картинка: такие ставятся над текстом во всю ширину,
    вертикальные — крупно рядом с текстом."""
    try:
        from PIL import Image
        with Image.open(src.lstrip('/')) as im:
            w, h = im.size
        return w / h > 1.15
    except Exception:
        return False


def _meta_value(meta, key, default=None):
    value = meta.get(key)
    if not value:
        return default
    return ' '.join(value).strip()


def load_content_pages():
    pages = []
    for root, _, files in os.walk(CONTENT_DIR):
        for name in sorted(files):
            if not name.endswith('.md'):
                continue
            path = os.path.join(root, name)
            with open(path, encoding='utf-8') as f:
                text = f.read()
            md = markdown.Markdown(extensions=MD_EXTENSIONS)
            head, sep, body = text.partition('\n\n')
            # апостроф в именах вроде «Эн`л» — не разметка кода (в шапке не трогаем)
            body = re.sub(r'(?<=[А-Яа-яЁё])`(?=[А-Яа-яЁё])', '&#96;', body)
            text = head + sep + _paragraphs(body)
            # зачёркивание ~~текст~~ (в Python-Markdown его нет из коробки)
            text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
            # список сразу под строкой текста (как в ВК) — Markdown требует пустую строку
            text = re.sub(r'(?m)^((?![-*] |\d+\. ).+)\n(?=[-*] |\d+\. )', r'\1\n\n', text)
            html = md.convert(text)
            meta = md.Meta
            order = _meta_value(meta, 'order')
            pages.append({
                'slug': name[:-3],
                'title': _meta_value(meta, 'title', name[:-3]),
                'nav_title': _meta_value(meta, 'nav_title'),
                'template': 'page.html',
                'parent': _meta_value(meta, 'parent', 'index'),
                'order': int(order) if order else 100,
                'summary': _meta_value(meta, 'summary'),
                'image': _meta_value(meta, 'image'),
                'banner': _meta_value(meta, 'banner'),
                'icon': _meta_value(meta, 'icon', 'bi-bookmark'),
                'group': _meta_value(meta, 'group'),
                'art': _meta_value(meta, 'art'),
                'art_nav': _meta_value(meta, 'art_nav'),
                'art_position': _meta_value(meta, 'art_position'),
                'art_size': _meta_value(meta, 'art_size'),
                'art_fit': _meta_value(meta, 'art_fit'),
                'cards': _meta_value(meta, 'cards'),
                'hero': _meta_value(meta, 'hero'),
                'subtitle': _meta_value(meta, 'subtitle'),
                'hero_position': _meta_value(meta, 'hero_position'),
                'layout': _meta_value(meta, 'layout'),
                'portrait': _meta_value(meta, 'portrait'),
                'card_columns': _meta_value(meta, 'card_columns'),
                'card_style': _meta_value(meta, 'card_style'),
                'related': _meta_value(meta, 'related'),
                'related_title': _meta_value(meta, 'related_title'),
                'vk': _meta_value(meta, 'vk'),
                'aliases': _meta_value(meta, 'aliases'),
                'leader': _meta_value(meta, 'leader'),
                'html': html,
                'source': path,
            })
    return pages


class Site:
    def __init__(self):
        self.pages = {}
        for page in TEMPLATE_PAGES + load_content_pages():
            page.setdefault('order', 100)
            if page['slug'] in self.pages:
                raise ValueError(f"Повторяющийся slug страницы: {page['slug']}")
            self.pages[page['slug']] = page
        # в vk может быть несколько id через пробел (объединённые страницы ВК)
        # старые адреса переименованных страниц: aliases: gond → turn.html
        self.aliases = {a: p['slug'] for p in self.pages.values() for a in (p.get('aliases') or '').split()}
        self.vk_to_slug = {vk: p['slug'] for p in self.pages.values() for vk in (p.get('vk') or '').split()}
        for page in self.pages.values():
            parent = page.get('parent')
            if parent and parent not in self.pages:
                raise ValueError(f"У страницы {page['slug']} неизвестный родитель: {parent}")

    def href(self, slug):
        return f'{slug}.html'

    def children(self, slug):
        kids = [p for p in self.pages.values() if p.get('parent') == slug]
        return sorted(kids, key=lambda p: (p['order'], p['title']))

    def child_groups(self, slug):
        """Дочерние страницы, разбитые на группы (как блоки кнопок в меню ВК)."""
        groups = []
        for child in self.children(slug):
            name = child.get('group')
            if not groups or groups[-1]['title'] != name:
                groups.append({'title': name, 'pages': []})
            groups[-1]['pages'].append(dict(child, href=self.href(child['slug'])))
        return groups

    def art_nav(self, slug):
        """Карточки с артами из ближайшего раздела, где задан art_nav."""
        page = self.pages.get(slug)
        while page and not page.get('art_nav'):
            page = self.pages.get(page.get('parent'))
        if not page:
            return []
        return [dict(self.pages[s], href=self.href(s), active=(s == slug))
                for s in page['art_nav'].split() if s in self.pages]

    def breadcrumbs(self, slug):
        chain = []
        page = self.pages.get(slug)
        while page:
            chain.insert(0, {'title': page['title'], 'href': self.href(page['slug'])})
            page = self.pages.get(page.get('parent'))
        return chain

    def nav_items(self):
        items = []
        for slug in NAV:
            if slug is None:
                items.append(None)
            elif slug in self.pages:
                page = self.pages[slug]
                items.append({'slug': slug, 'title': page.get('nav_title') or page['title'],
                              'href': self.href(slug)})
        return items

    def nav_ancestor(self, slug):
        """Ближайшая к странице позиция левого меню (для подсветки)."""
        page = self.pages.get(slug)
        while page:
            if page['slug'] in NAV:
                return page['slug']
            page = self.pages.get(page.get('parent'))
        return None

    def search_index(self):
        items = []
        for page in self.pages.values():
            parent = self.pages.get(page.get('parent'))
            items.append({'text': page['title'], 'href': self.href(page['slug']),
                          'section': parent['title'] if parent else ''})
        return json.dumps(sorted(items, key=lambda i: i['text']), ensure_ascii=False)

    def resolve_vk_links(self, html):
        def repl(match):
            vk_id = match.group(1)
            slug = self.vk_to_slug.get(vk_id)
            if slug:
                return f'href="{self.href(slug)}"'
            return f'href="{VK_PAGE_URL.format(vk_id)}" target="_blank" rel="noopener noreferrer"'
        return re.sub(r'href="vk:(\d+)"', repl, html)

    def render_widgets(self, html):
        """[[widget:race-mix]] → templates/widgets/race-mix.html с data/race-mix.json."""
        from flask import render_template

        def repl(match):
            name = match.group(1)
            data_path = os.path.join('data', f'{name}.json')
            data = {}
            if os.path.exists(data_path):
                with open(data_path, encoding='utf-8') as f:
                    data = json.load(f)
            pages = {slug: self.href(slug) for slug in self.pages}
            return render_template(f'widgets/{name}.html', data=data, pages=pages)
        return re.sub(r'(?:<p>)?\[\[widget:([\w-]+)\]\](?:</p>)?', repl, html)

    def render_body(self, page):
        """Разбивает Markdown-страницу на блоки по заголовкам второго уровня."""
        html = self.render_widgets(self.resolve_vk_links(page['html']))
        parts = re.split(r'(<h2>.*?</h2>)', html)
        sections = []
        intro = parts[0].strip()
        if intro:
            sections.append({'title': None, 'body': Markup(intro)})
        for i in range(1, len(parts), 2):
            title = re.sub(r'^<h2>|</h2>$', '', parts[i])
            if not parts[i + 1].strip():
                continue  # пустые разделы (в ВК бывают пустые подписи) не показываем
            icon = SECTION_ICONS.get(re.sub(r'<[^>]+>', '', title).strip().lower(), page.get('icon'))
            sections.append({'title': Markup(title), 'body': Markup(parts[i + 1].strip()), 'icon': icon})
        if (page.get('layout') == 'profile' and sections and sections[0]['title'] is not None
                and (page.get('art') or page.get('image'))):
            # картинки в начале нет — берём арт с кнопки страницы
            sections.insert(0, {'title': None, 'body': Markup(
                f'<p><img alt="" src="/static/{page.get("art") or page["image"]}" /></p>')})
        if page.get('layout') == 'profile' and sections and sections[0]['title'] is None:
            # портрет: вступление, состоящее из одной картинки
            m = re.fullmatch(r'<p><img alt="[^"]*" src="([^"]+)"\s*/?></p>', str(sections[0]['body']))
            if m:
                # портрет встаёт рядом со следующим разделом (обычно «Общее описание»)
                side = sections[1] if len(sections) > 1 else None
                sections[:2] = [{'portrait': m.group(1), 'side': side, 'wide': _is_wide(m.group(1))}]
        if page.get('layout') == 'rules':
            sections = _rules_sections(sections)
        if page.get('layout') == 'god':
            sections = self._god_sections(page, sections)
        if page.get('layout') == 'race':
            sections = self._race_sections(page, sections)
        if page.get('layout') == 'person':
            sections = self._person_sections(page, sections)
        if page.get('layout') == 'anketa':
            sections = self._anketa_sections(page, sections)
        if page.get('layout') == 'guild':
            sections = self._guild_sections(page, sections)
        used = set()
        for section in sections:
            if section.get('title') and not section.get('anchor'):
                base = _anchor(section['title']) or 'section'
                anchor, n = base, 2
                while anchor in used:
                    anchor, n = f'{base}-{n}', n + 1
                section['anchor'] = anchor
            used.add(section.get('anchor'))
        return sections

    @staticmethod
    def _person_sections(page, sections):
        """Страница персонажа: арт и строки «**Раса** — …» из начала текста уходят в шапку."""
        if sections and sections[0]['title'] is None:
            body = str(sections[0]['body'])
            body = re.sub(r'<p><img alt="[^"]*" src="/static/[^"]+"\s*/?></p>\s*', '', body, count=1)
            facts = {}
            def take(m):
                facts[_plain(m.group(1)).lower()] = _plain(m.group(2)).rstrip(';').strip()
                return ''
            body = re.sub(r'<p><strong>([^<]+)</strong>\s*[—–-]\s*(.*?)</p>\s*', take, body)
            status = facts.get('статус', '').rstrip('.')
            page['person'] = {
                'name': facts.get('известное имя'),
                'age': facts.get('примерный возраст'),
                'race': facts.get('раса'),
                'status': status,
                # коротко для карточки: «Король эльфов. Также является…» → «Король эльфов»
                'status_short': re.split(r';|\.\s', status)[0].rstrip('.') if status else '',
            }
            sections = ([dict(sections[0], body=Markup(body.strip()))] if body.strip() else []) + sections[1:]
        return sections

    def _magic_type_link(self, token):
        """«Льда» / «магия земли» / «Свет» → страница типа магии (по основе слова)."""
        word = re.sub(r'^магия\s+', '', token.strip().lower())
        for p in self.pages.values():
            if p.get('parent') == 'magic' and p['title'].lower().startswith('магия '):
                target = p['title'].lower()[6:]
                n = min(4, len(word), len(target))
                if n >= 3 and word[:n] == target[:n]:
                    return {'title': p['title'], 'href': self.href(p['slug'])}
        return {'title': token.strip(), 'href': None}

    @staticmethod
    def _guild_sections(page, sections):
        """Собирает галерею гильдии и краткое описание для её герба."""
        arts, out = [], []
        for section in sections:
            body = str(section['body'])
            arts += re.findall(r'<img[^>]+src="/static/([^"]+)"', body)
            # Отдельная иллюстрация перед статьёй уже доступна в галерее.
            if not section['title'] and re.fullmatch(r'<p>\s*<img\b[^>]*>\s*</p>', body.strip()):
                continue
            body = _figures(body).strip()
            if body:
                out.append(dict(section, body=Markup(body)))
        first = next((_plain(re.sub(r'<figure.*?</figure>', '', str(s['body']), flags=re.S)) for s in out
                      if _plain(s.get('title') or '').lower() == 'общее описание'), '')
        page['guild'] = {'arts': arts, 'teaser': _first_sentence(first, 200)}
        return out

    def _anketa_sections(self, page, sections):
        """Анкета игрока: арт и строки «**Раса** — …» в шапку, магия/избранный/активация —
        в плитки шапки, все арты — в галерею, способности — отдельными карточками."""
        info = {'facts': {}, 'arts': []}
        out = []
        for i, section in enumerate(sections):
            body = str(section['body'])
            info['arts'] += re.findall(r'<img[^>]+src="/static/([^"]+)"', body)
            body = re.sub(r'<p>\s*<img[^>]*>\s*</p>\s*', '', body)
            title = _plain(section.get('title') or '').lower()
            if section.get('title') is None and i == 0:
                def take(m):
                    info['facts'][_plain(m.group(1)).lower()] = Markup(m.group(2).strip().rstrip(';'))
                    return ''
                body = re.sub(r'<p><strong>([^<]+)</strong>\s*[—–-]\s*(.*?)</p>\s*', take, body, flags=re.S)
            elif title.startswith('подконтрольные элементы'):
                text = _plain(body)
                m = re.search(r'Элемент\w*:\s*(.*?)(?:[;.]?\s*Типы магии:\s*(.*))?$', text)
                if m:
                    info['elements'] = [e.strip().capitalize() for e in re.split(r',|\s+и\s+', m.group(1)) if e.strip()]
                    types = [t for t in re.split(r'[,;]|\s+и\s+', (m.group(2) or '').rstrip('.')) if t.strip()]
                    info['types'] = [self._magic_type_link(t) for t in types]
                    continue
            elif title == 'избранный':
                info['chosen'] = _plain(body).rstrip('.')
                continue
            elif title.startswith('способ активирования'):
                info['cast'] = _plain(body).rstrip('.')
                continue
            elif title == 'способности' and '<h3' in body:
                parts = re.split(r'<h3[^>]*>(.*?)</h3>', body)
                section = dict(section, abilities=[{'title': Markup(parts[k]), 'body': Markup(parts[k + 1].strip())}
                                                   for k in range(1, len(parts), 2)])
                body = parts[0]
            if body.strip() or section.get('abilities'):
                out.append(dict(section, body=Markup(body.strip())))
        page['anketa'] = info
        return out

    @staticmethod
    def _race_sections(page, sections):
        """Страница расы: арт из начала текста и раздел «Названия» уходят в шапку."""
        if sections and sections[0]['title'] is None:
            m = re.match(r'<p><img alt="[^"]*" src="/static/([^"]+)"\s*/?></p>\s*', str(sections[0]['body']))
            if m:
                page['race_portrait'] = m.group(1)
                rest = str(sections[0]['body'])[m.end():].strip()
                sections = ([dict(sections[0], body=Markup(rest))] if rest else []) + sections[1:]
        for section in sections:
            if _plain(section.get('title') or '').lower() == 'названия':
                page['race_names'] = _plain(section['body'])
        return [s for s in sections if _plain(s.get('title') or '').lower() != 'названия']

    @staticmethod
    def _god_sections(page, sections):
        """Страница бога: заголовок «Имя: титул» дублирует шапку — убираем;
        строку ранга («Четвёртый по значимости член семёрки.») выносим в шапку."""
        for section in sections:
            title = html_lib.unescape(re.sub(r'<[^>]+>', '', str(section.get('title') or '')))
            if title.startswith(page['title']):
                section['title'] = None
            body = str(section['body'])
            m = re.search(r'<p><em>([^<]*(?:божество|полубожество|сем[её]рки)[^<]*)</em></p>\s*', body, flags=re.I)
            if m and not page.get('rank_note'):
                page['rank_note'] = m.group(1).strip().rstrip('.')
                section['body'] = Markup(body.replace(m.group(0), '', 1))
        return [s for s in sections if s.get('title') or str(s['body']).strip()]

    def creature_facts(self, page, sections=None):
        """Короткая сводка о существе из его разделов: где живёт, чем питается,
        можно ли приручить, вес."""
        if sections is None:
            sections = self.render_body(page)
        by_title = {_plain(s.get('title') or '').lower(): _plain(s['body']) for s in sections if not s.get('portrait')}
        facts = []
        if by_title.get('места обитания'):
            facts.append({'icon': 'bi-geo-alt', 'label': 'Обитает', 'text': _first_sentence(by_title['места обитания'])})
        if by_title.get('питание'):
            facts.append({'icon': 'bi-egg-fried', 'label': 'Питание', 'text': _first_sentence(by_title['питание'])})
        body = ' '.join(by_title.values())
        weight = re.search(r'(?:[Вв]ес[ия]т|массы)[^.]*?(?:от (\d+) до |до (?:(\d+)[-–—])?)(\d+)\s*(?:кг|килограмм)', body)
        if weight:
            low = weight.group(1) or weight.group(2)
            text = f'{low}–{weight.group(3)} кг' if low else f'до {weight.group(3)} кг'
            facts.append({'icon': 'bi-speedometer2', 'label': 'Вес', 'text': text})
        taming = None
        tame_text = by_title.get('можно ли приручить?')
        if tame_text:
            taming = _taming(tame_text)
            facts.append({'icon': 'bi-hand-index-thumb', 'label': 'Приручение', 'text': _first_sentence(tame_text),
                          'tone': taming})
        return {'items': facts, 'taming': taming, 'taming_label': TAMING_LABELS.get(taming)}

    def creature_context(self, page, sections):
        kin = [p for p in self.children(page['parent']) if p.get('layout') == 'creature']
        i = next((k for k, p in enumerate(kin) if p['slug'] == page['slug']), 0)
        near = lambda p: dict(p, href=self.href(p['slug'])) if p else None
        shot = page.get('portrait') or page.get('art') or page.get('banner')
        return {
            'cr_prev': near(kin[i - 1]) if i > 0 else None,
            'cr_next': near(kin[i + 1]) if i + 1 < len(kin) else None,
            'cr_parent': dict(self.pages[page['parent']], href=self.href(page['parent'])),
            'cr_shot': shot,
            'cr_wide': _is_wide('static/' + shot),
            'cr_facts': self.creature_facts(page, sections),
        }

    def map_places(self):
        """Метки для страницы карты (data/map-places.json + данные страниц)."""
        if getattr(self, '_map_places', None) is not None:
            return self._map_places
        path = os.path.join('data', 'map-places.json')
        if not os.path.exists(path):
            return []
        with open(path, encoding='utf-8') as f:
            groups = json.load(f)['groups']
        result = []
        for group in groups:
            places = []
            for item in group['places']:
                page = self.pages.get(item['page'])
                if not page:
                    continue
                sections = self.render_body(page)
                if item.get('anchor'):
                    sections = [s for s in sections if s.get('anchor') == item['anchor']]
                text = next((_plain(s['body']) for s in sections if _plain(s['body'])), '')
                img = None
                if item.get('anchor') and sections:
                    m = re.search(r'<img[^>]+src="/static/([^"]+)"', str(sections[0]['body']))
                    img = m.group(1) if m else None
                places.append({
                    'id': item.get('anchor') or page['slug'],
                    'title': item.get('title') or page['title'],
                    'href': self.href(page['slug']) + (f"#{item['anchor']}" if item.get('anchor') else ''),
                    'text': page.get('summary') if not item.get('anchor') and page.get('summary') else _first_sentence(text, 220),
                    'image': img or (None if item.get('anchor') else page.get('image')),
                    'x': item.get('x'), 'y': item.get('y'), 'bounds': item.get('bounds'),
                    'kind': group['kind'],
                })
            result.append({'title': group['title'], 'kind': group['kind'], 'places': places})
        self._map_places = result
        return result

    def race_facts(self, page, sections=None):
        """Сводка о расе из текста: сколько живут, предел жизни, рост."""
        if sections is None:
            sections = self.render_body(page)
        body = ' '.join(_plain(s['body']) for s in sections)
        facts = []
        m = re.search(r'Живут в среднем от (\d+) до (\d+) лет', body)
        if m:
            facts.append({'icon': 'bi-hourglass-split', 'label': 'Живут в среднем', 'text': f'{m.group(1)}–{m.group(2)} {_years(m.group(2))}'})
        m = re.search(r'[Мм]аксимальн\w* (?:возраст|продолжительность)[^.]*?(\d+)(?:\s*[-–]\s*(\d+))? лет', body) or \
            re.search(r'(\d+)(?:\s*[-–]\s*(\d+))? лет максимум', body)
        if m:
            text = f'{m.group(1)}–{m.group(2)} {_years(m.group(2))}' if m.group(2) else f'до {m.group(1)} лет'
            facts.append({'icon': 'bi-hourglass-bottom', 'label': 'Предел жизни', 'text': text})
        m = re.search(r'(\d+)(?:\s*[-–]\s*(\d+))?\s*(?:сантиметр\w*|см) роста', body) or \
            re.search(r'[Рр]ост\w*[^.]*?(\d+)(?:\s*[-–]\s*(\d+))?\s*сантиметр', body)
        if m:
            text = f'{m.group(1)}–{m.group(2)} см' if m.group(2) else f'около {m.group(1)} см'
            facts.append({'icon': 'bi-rulers', 'label': 'Рост', 'text': text})
        return facts

    def continents(self):
        """Материки из «Материков Наира»: название, пометка, картинка, короткий текст, куда ведёт подробное."""
        src = self.pages.get('materiki')
        if not src:
            return []
        detail = {'бранн': '#brann', 'гольм': self.href('golm') if 'golm' in self.pages else None}
        result = []
        for s in self.render_body(src):
            if not s.get('title'):
                continue
            title = _plain(s['title'])
            m = re.match(r'(.*?)\s*\((.*)\)\s*$', title)
            name, note = (m.group(1), m.group(2)) if m else (title, None)
            body = str(s['body'])
            imgs = re.findall(r'<img[^>]+src="/static/([^"]+)"', body)
            text = re.sub(r'<p>\s*<img[^>]*>\s*</p>\s*', '', body).strip()
            anchor = s.get('anchor')
            key = 'brann' if name.lower() == 'бранн' else anchor
            art = f'photo/lokacii-web/cont-{key}.webp'  # арт материка для кнопки (карта остаётся в «Кратко»)
            result.append({'name': name, 'note': note, 'anchor': anchor, 'image': imgs[0] if imgs else None,
                           'art': art if os.path.exists('static/' + art) else None,
                           'text': Markup(text), 'detail': detail.get(name.lower())})
        return result

    def locations_context(self, page):
        kids = [dict(p, href=self.href(p['slug'])) for p in self.children('lokacii')]
        states = [p for p in kids if p.get('layout') == 'state']
        places = [p for p in kids if p.get('layout') == 'location']
        groups = []
        for p in places:
            if not groups or groups[-1]['title'] != p.get('group'):
                groups.append({'title': p.get('group'), 'pages': []})
            groups[-1]['pages'].append(p)
        # территория → страница государства («Территория Империи людей» → Империя Корвас и т. п.)
        state_of = {'Территория Империи людей': 'imperiya-korvas', 'Территория Альянса эльфов': 'alyans-elfov',
                    'Территория Великой Империи ящеров': 'velikaya-imperiya-yascherov'}
        for g in groups:
            st = self.pages.get(state_of.get(g['title'], ''))
            g['state'] = dict(st, href=self.href(st['slug'])) if st else None
        return {'continents': self.continents(), 'states': states, 'place_groups': groups, 'state_of': state_of}

    MAGIC_ELEMENTS = [('свет', 'bi-brightness-high'), ('тьма', 'bi-moon'), ('огонь', 'bi-fire'), ('вода', 'bi-droplet'),
                      ('воздух', 'bi-wind'), ('молния', 'bi-lightning'), ('земля', 'bi-triangle')]

    def magic_data(self):
        """Состав типов магии по элементам — со страницы «Элементы и типы магии»."""
        if getattr(self, '_magic', None) is not None:
            return self._magic
        src = self.pages.get('elementy-i-tipy-magii')
        comp = {}
        if src:
            for vk_id, rest in re.findall(r'<li><a href="vk:(\d+)">[^<]*</a>([^<]*)</li>', src['html']):
                slug = self.vk_to_slug.get(vk_id)
                m = re.search(r'\[([^\]]+)\]', rest)
                if slug:
                    comp[slug] = [t.strip().lower() for t in m.group(1).split('+')] if m else []
        icons = dict(self.MAGIC_ELEMENTS)
        types = []
        for p in self.children('magic'):
            if p.get('layout') != 'magic-type':
                continue
            parts = comp.get(p['slug'], [])
            def part(t):
                # составная часть — элемент (со значком) или другой тип магии (со ссылкой)
                if t in icons:
                    return {'name': t, 'icon': icons[t]}
                link = self._magic_type_link(t)
                return {'name': t, 'icon': None, 'href': link['href'], 'type_title': link['title'] if link['href'] else None}
            types.append(dict(p, href=self.href(p['slug']), parts=[part(t) for t in parts],
                              elements=[t for t in parts if t in icons]))
        # элементы входящих типов тоже считаем (лёд = вода + магия воздуха → вода, воздух) — для фильтра
        by_href = {t['href']: t for t in types}
        for t in types:
            for part in t['parts']:
                sub = by_href.get(part.get('href'))
                if sub:
                    t['elements'] += [e for e in sub['elements'] if e not in t['elements']]
        groups = [
            {'id': 'pure', 'title': 'Основанные на одном элементе', 'note': 'Тип магии, который использует один элемент',
             'types': [t for t in types if len(t['parts']) == 1]},
            {'id': 'mixed', 'title': 'Составные типы', 'note': 'Тип магии, который собирается из двух элементов или из элемента и другого типа магии',
             'types': [t for t in types if len(t['parts']) > 1]},
            {'id': 'other', 'title': 'Иные типы', 'note': 'Тип магии, для которого элементы не указаны',
             'types': [t for t in types if not t['parts']]},
        ]
        self._magic = {'types': types, 'groups': [g for g in groups if g['types']],
                       'elements': [{'name': n, 'icon': i} for n, i in self.MAGIC_ELEMENTS]}
        return self._magic

    QUEST_LEVELS = {'лёгкая': 1, 'легкая': 1, 'средняя': 2, 'высокая': 3, 'очень высокая': 4}
    QUEST_LABELS = ('Сложность', 'Локация принятия квеста', 'Награда')

    @staticmethod
    def _reward_short(text):
        m = re.search(r'(\d[\d\s]*)\s*(золот\w*|златник\w*)', text)
        if not m:
            return None
        return f"{m.group(1).strip()} {m.group(2)}" + (' каждому' if 'кажд' in text else '')

    def quest_info(self, page):
        """Строки «Сложность / Локация принятия квеста / Награда» → поля объявления."""
        if page.get('_quest') is not None:
            return page['_quest']
        html = self.resolve_vk_links(page['html'])
        text = _plain(html)
        info = {}
        for i, label in enumerate(self.QUEST_LABELS):
            rest = '|'.join(re.escape(l) for l in self.QUEST_LABELS if l != label)
            m = re.search(re.escape(label) + r':\s*(.*?)(?=\s*(?:' + rest + r'):|$)', text)
            if m:
                info[label] = m.group(1).strip().rstrip('.')
        diff = info.get('Сложность', '')
        level_name = diff.split(',')[0].strip()
        players = re.search(r'(\d+)\s*[-–]\s*(\d+)', diff)
        if players:
            last = int(players.group(2))
            word = 'игрока' if 2 <= last % 10 <= 4 and not 12 <= last % 100 <= 14 else 'игроков'
            players = f'{players.group(1)}–{players.group(2)} {word}'
        where = info.get('Локация принятия квеста', '')
        places = []
        for p in self.pages.values():
            if p.get('parent') != 'lokacii' or p['slug'] in {x['slug'] for x in places}:
                continue
            t = p['title']
            # «Джой» → «Джоем», «Каэльмор» → «Каэльмора»: ищем по основе слова
            stem = t if ' ' in t or "'" in t else (t[:-1] if t.endswith(('й', 'а', 'е')) or len(t) >= 5 else t)
            if re.search(r'(?<![А-Яа-яЁё])' + re.escape(stem), where):
                places.append({'slug': p['slug'], 'title': p['title'], 'href': self.href(p['slug']),
                               'map': f"{self.href('karta')}#{p['slug']}"})
        # описание: всё, кроме заголовка «Описание» и абзаца со строками объявления
        body = re.sub(r'<h2[^>]*>\s*Описание\s*</h2>', '', html)
        body = re.sub(r'<p><strong>Сложность:.*?</p>', '', body, flags=re.S)
        teaser = _first_sentence(_plain(body), 200)
        page['_quest'] = {
            'level': self.QUEST_LEVELS.get(level_name.lower(), 0), 'level_name': level_name,
            'players': players, 'where': where, 'places': places,
            'reward': info.get('Награда', ''), 'body': Markup(body.strip()), 'teaser': teaser,
            'reward_short': self._reward_short(info.get('Награда', '')),
        }
        return page['_quest']

    def showcase(self, page, sections):
        """Артефакты и металлы: из каждого раздела достаём картинку, владельца
        и характеристики, добавляем редкость и комплекты из data/showcase.json."""
        path = os.path.join('data', 'showcase.json')
        extra = {}
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                extra = json.load(f)
        sets = {}
        for s in extra.get('artifact_sets', []):
            for anchor in s['items']:
                sets[anchor] = s
        titles = {s.get('anchor'): _plain(s['title']) for s in sections if s.get('title')}
        credit = None
        items = []
        for section in sections:
            if not section.get('title'):
                items.append(section)
                continue
            body = str(section['body'])
            item = dict(section, showcase=True)
            m = re.search(r'<p><img alt="[^"]*" src="/static/([^"]+)"\s*/?></p>\s*', body)
            if m:
                item['image'] = m.group(1)
                tail = body[m.end():].strip()
                body = body[:m.start()]
                if re.fullmatch(r'<p><em>.*?</em></p>', tail, flags=re.S):
                    credit = Markup(tail)  # подпись ко всей странице («Автор многих металлов…»)
                else:
                    body += tail
            m = re.match(r'\s*<p><strong>Владелец:?</strong>:?\s*(?:[—–-]\s*)?(.*?)</p>\s*', body, flags=re.S)
            if m:
                item['owner'] = Markup(m.group(1).strip())
                body = body[m.end():]
            m = re.search(r'<p><strong>Характеристики:?</strong>:?\s*(.*?)</p>\s*', body, flags=re.S)
            if m:
                item['stats'] = Markup(m.group(1).strip())
                body = body[:m.start()] + body[m.end():]
            body = re.sub(r'^\s*<ul>\s*<li>(.*?)</li>\s*</ul>', r'<p>\1</p>', body, flags=re.S)
            item['body'] = Markup(body.strip())
            item['metal'] = extra.get('metals', {}).get(section.get('anchor'))
            s = sets.get(section.get('anchor'))
            if s:
                item['set'] = {'title': s['title'], 'others': [
                    {'anchor': a, 'title': titles.get(a, a)} for a in s['items'] if a != section.get('anchor')]}
            items.append(item)
        return items, credit

    def person_context(self, page):
        kin = [p for p in self.children(page['parent']) if p.get('layout') == 'person']
        i = next((k for k, p in enumerate(kin) if p['slug'] == page['slug']), 0)
        near = lambda p: dict(p, href=self.href(p['slug'])) if p else None
        shot = page.get('portrait') or page.get('art')
        return {
            'cr_prev': near(kin[i - 1]) if i > 0 else None,
            'cr_next': near(kin[i + 1]) if i + 1 < len(kin) else None,
            'cr_parent': dict(self.pages[page['parent']], href=self.href(page['parent'])),
            'cr_shot': shot,
            'cr_wide': _is_wide('static/' + shot),
        }

    def race_context(self, page, sections):
        kin = [p for p in self.children(page['parent']) if p.get('layout') == 'race']
        i = next((k for k, p in enumerate(kin) if p['slug'] == page['slug']), 0)
        near = lambda p: dict(p, href=self.href(p['slug'])) if p else None
        shot = page.get('race_portrait') or page.get('art')
        hub = 'rasy' if 'rasy' in self.pages else page['parent']
        return {
            'cr_prev': near(kin[i - 1]) if i > 0 else None,
            'cr_next': near(kin[i + 1]) if i + 1 < len(kin) else None,
            'cr_parent': dict(self.pages[hub], href=self.href(hub)),
            'cr_shot': shot,
            'cr_wide': _is_wide('static/' + shot),
            'race_facts': self.race_facts(page, sections),
        }

    def god_context(self, page):
        """Соседи по пантеону (для «предыдущий / следующий») и домены из summary."""
        gods = [p for p in self.children(page['parent']) if p.get('layout') == 'god']
        i = next((k for k, p in enumerate(gods) if p['slug'] == page['slug']), 0)
        near = lambda p: dict(p, href=self.href(p['slug'])) if p else None
        summary = page.get('summary') or ''
        m = re.match(r'^(Бог|Богиня)\s+', summary)
        kind = m.group(1) if m else ''
        summary = summary[m.end():] if m else summary
        # «Бог огня, войны и разрушения» → «Бог» + [огня, войны, разрушения]
        domains = [d.strip() for d in re.split(r',\s*|\s+и\s+', summary) if d.strip()]
        return {
            'god_prev': near(gods[i - 1]) if i > 0 else None,
            'god_next': near(gods[i + 1]) if i + 1 < len(gods) else None,
            'god_domains': domains,
            'god_kind': kind,
            'god_wide': _is_wide('static/' + (page.get('portrait') or page.get('art') or '')),
            'god_links': [dict(c, href=self.href(c['slug'])) for c in self.children(page['slug'])],
            'god_parent': dict(self.pages[page['parent']], href=self.href(page['parent'])),
        }

    def context(self, slug):
        page = self.pages[slug]
        ctx = {
            'page': page,
            'title': f"{page['title']} — Наир",
            'breadcrumbs': self.breadcrumbs(slug),
            'nav_items': self.nav_items(),
            'search_index': Markup(self.search_index()),
            'art_nav': self.art_nav(slug),
            'related': [dict(self.pages[r], href=self.href(r))
                        for r in (page.get('related') or '').split() if r in self.pages],
            'active_nav': self.nav_ancestor(slug),
        }
        # страницы, уже показанные карточками с артами, не дублируем снизу
        in_art_nav = {p['slug'] for p in ctx['art_nav']}
        ctx['child_groups'] = [dict(g, pages=[c for c in g['pages'] if c['slug'] not in in_art_nav])
                               for g in self.child_groups(slug)]
        ctx['child_groups'] = [g for g in ctx['child_groups'] if g['pages']]
        if page['template'] == 'page.html':
            ctx['sections'] = self.render_body(page)
        if page.get('layout') == 'god':
            ctx.update(self.god_context(page))
            ctx['child_groups'] = []  # молитвы и т. п. показываются кнопками в шапке
        if page.get('layout') == 'creature':
            ctx.update(self.creature_context(page, ctx['sections']))
        if slug == 'karta':
            ctx['map_places'] = self.map_places()
        elif slug in {p['id'] for g in self.map_places() for p in g['places']}:
            ctx['map_link'] = f'{self.href("karta")}#{slug}'
        if page.get('layout') == 'race':
            ctx.update(self.race_context(page, ctx['sections']))
        if page.get('layout') == 'person':
            ctx.update(self.person_context(page))
        if page.get('layout') in ('magic', 'magic-page', 'magic-type'):
            magic = self.magic_data()
            ctx['magic'] = magic
            ctx['magic_pages'] = [dict(p, href=self.href(p['slug'])) for p in self.children('magic')
                                  if p.get('layout') == 'magic-page']
            ctx['cr_parent'] = dict(self.pages['magic'], href=self.href('magic'))
            ctx['cr_shot'] = page.get('art')
            ctx['cr_wide'] = _is_wide('static/' + page['art']) if page.get('art') else False
            if page['layout'] == 'magic':
                ctx['child_groups'] = []
            if slug == 'elementy-i-tipy-magii':
                # списки элементов и типов заменяет интерактивная таблица (widgets/magic-types.html)
                for section in ctx['sections']:
                    section['body'] = Markup(re.sub(r'<p><em>Элементы:</em></p>.*?</ul>\s*<p><em>Типы магии:</em>.*?</ul>',
                                                    '', str(section['body']), flags=re.S))
            if page['layout'] == 'magic-type':
                types = magic['types']
                i = next((k for k, t in enumerate(types) if t['slug'] == slug), 0)
                me = types[i]
                ctx.update({
                    'mtype': me,
                    'cr_prev': types[i - 1] if i > 0 else None,
                    'cr_next': types[i + 1] if i + 1 < len(types) else None,
                    'mrelated': [t for t in types if t['slug'] != slug and set(t['elements']) & set(me['elements'])],
                })
        if page.get('layout') == 'locations':
            ctx.update(self.locations_context(page))
            ctx['child_groups'] = []
            ctx['sections'] = []
        if page.get('layout') in ('location', 'state'):
            loc = self.locations_context(page)
            kin = [p for g in loc['place_groups'] for p in g['pages']] if page['layout'] == 'location' else loc['states']
            i = next((k for k, p in enumerate(kin) if p['slug'] == slug), 0)
            st = self.pages.get(loc['state_of'].get(page.get('group'), ''))
            arts = []
            if page['layout'] == 'state' and ctx['sections']:
                # герб из начала текста уже стоит в шапке (новый арт) — убираем его с подписью
                first = ctx['sections'][0]
                body = re.sub(r'^\s*<p><img[^>]*></p>\s*(<p><em>[^<]*</em></p>\s*)?', '', str(first['body']))
                first['body'] = Markup(body)
                for section in ctx['sections']:
                    section['body'] = Markup(_figures(section['body']))
                ctx['sections'] = [s for s in ctx['sections'] if str(s['body']).strip() or s.get('title')]
            if page['layout'] == 'location':
                # картинки из текста — в галерею под шапкой и на свои места в тексте;
                # картинка в самом начале страницы — старая шапка из ВК, её уже заменяет арт в шапке
                for k, section in enumerate(ctx['sections']):
                    body = str(section['body'])
                    arts += re.findall(r'<img[^>]+src="/static/([^"]+)"', body)
                    if k == 0:
                        body = re.sub(r'^\s*<p><img[^>]*></p>\s*', '', body)
                    section['body'] = Markup(_figures(body).strip())
                ctx['sections'] = [s for s in ctx['sections'] if str(s['body']).strip()]
            ctx.update({
                'cr_prev': kin[i - 1] if i > 0 else None, 'cr_next': kin[i + 1] if i + 1 < len(kin) else None,
                'cr_parent': dict(self.pages['lokacii'], href=self.href('lokacii') + '#brann'),
                'cr_shot': page.get('art'), 'cr_wide': _is_wide('static/' + page['art']) if page.get('art') else False,
                'loc_state': dict(st, href=self.href(st['slug'])) if st else None, 'loc_arts': arts,
                'loc_children': [dict(c, href=self.href(c['slug'])) for c in self.children(slug)],
            })
        if page.get('layout') in ('guild', 'guilds'):
            kin = [dict(p, href=self.href(p['slug'])) for p in self.children('gildii') if p.get('layout') == 'guild']
            for g in kin:
                self.render_body(self.pages[g['slug']])
                g['guild'] = self.pages[g['slug']].get('guild')
                leader = self.pages.get(g.get('leader') or '')
                if leader:
                    self.render_body(leader)
                g['leader_page'] = dict(leader, href=self.href(leader['slug'])) if leader else None
            if page['layout'] == 'guilds':
                ctx['guilds'] = kin
                ctx['child_groups'] = []
            else:
                i = next((k for k, g in enumerate(kin) if g['slug'] == slug), 0)
                ctx.update({'me_guild': kin[i], 'cr_prev': kin[i - 1] if i > 0 else None,
                            'cr_next': kin[i + 1] if i + 1 < len(kin) else None,
                            'cr_parent': dict(self.pages['gildii'], href=self.href('gildii'))})
        if page.get('layout') == 'anketa':
            kin = [p for p in self.children(page['parent']) if p.get('layout') == 'anketa']
            i = next((k for k, p in enumerate(kin) if p['slug'] == page['slug']), 0)
            ctx.update({
                'cr_prev': dict(kin[i - 1], href=self.href(kin[i - 1]['slug'])) if i > 0 else None,
                'cr_next': dict(kin[i + 1], href=self.href(kin[i + 1]['slug'])) if i + 1 < len(kin) else None,
                'cr_parent': dict(self.pages[page['parent']], href=self.href(page['parent'])),
            })
        if page.get('layout') == 'ankety':
            for group in ctx['child_groups']:
                for child in group['pages']:
                    if child.get('layout') == 'anketa':
                        self.render_body(self.pages[child['slug']])
                        child['anketa'] = self.pages[child['slug']].get('anketa') or {}
        if page.get('layout') == 'quest':
            kin = [p for p in self.children(page['parent'])]
            i = next((k for k, p in enumerate(kin) if p['slug'] == page['slug']), 0)
            hub = self.pages[page['parent']]
            ctx['sections'] = []  # всё выводится объявлением (widgets/quest.html)
            ctx.update({
                'quest': self.quest_info(page),
                'cr_prev': dict(kin[i - 1], href=self.href(kin[i - 1]['slug'])) if i > 0 else None,
                'cr_next': dict(kin[i + 1], href=self.href(kin[i + 1]['slug'])) if i + 1 < len(kin) else None,
                'cr_parent': dict(hub, href=self.href(hub['slug'])),
            })
        if page.get('layout') == 'quests':
            for group in ctx['child_groups']:
                for child in group['pages']:
                    child['quest'] = self.quest_info(self.pages[child['slug']])
        if page.get('layout') in ('artifacts', 'materials'):
            ctx['sections'], ctx['credit'] = self.showcase(page, ctx['sections'])
        if page.get('layout') == 'people':
            for group in ctx['child_groups']:
                for child in group['pages']:
                    self.render_body(self.pages[child['slug']])
                    child['person'] = self.pages[child['slug']].get('person') or {}
        if page.get('layout') == 'races':
            for group in ctx['child_groups']:
                for child in group['pages']:
                    if child.get('layout') == 'race':
                        child['facts'] = self.race_facts(self.pages[child['slug']])
                        child['race_portrait'] = self.pages[child['slug']].get('race_portrait')
        if page.get('layout') == 'bestiary':
            for group in ctx['child_groups']:
                for child in group['pages']:
                    child['facts'] = self.creature_facts(self.pages[child['slug']])
        return ctx
