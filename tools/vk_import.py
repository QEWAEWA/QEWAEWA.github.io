"""Перенос вики-страниц меню ВК в черновики Markdown.

Примеры:
    python tools/vk_import.py 55340430            # одна страница → _vk_drafts/
    python tools/vk_import.py --crawl 54743839    # всё меню, начиная со страницы
    python tools/vk_import.py 55340430 --refresh  # скачать заново, мимо кэша

Картинки скачиваются в static/photo/vk/<id>.jpg (ссылки ВК со временем
протухают, поэтому храним копии у себя). Сырые страницы кэшируются в
_vk_cache/. Ссылки на другие вики-страницы пишутся как (vk:<id>) — при
сборке сайта они становятся ссылками на уже перенесённые страницы или на ВК,
если страницы на сайте ещё нет.

Черновик нужно просмотреть руками: поправить заголовки, parent, order.
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

GROUP = '182026147'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, 'static', 'photo', 'vk')
DRAFTS_DIR = os.path.join(ROOT, '_vk_drafts')
CACHE_DIR = os.path.join(ROOT, '_vk_cache')

TRANSLIT = dict(zip(
    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
    ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p',
     'r', 's', 't', 'u', 'f', 'h', 'c', 'ch', 'sh', 'sch', '', 'y', '', 'e', 'yu', 'ya']))


def slugify(title):
    s = ''.join(TRANSLIT.get(ch, ch) for ch in title.lower())
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'page'


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ru'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except OSError:
            if attempt == 2:
                raise
            time.sleep(3)


def fetch_page(vk_id, refresh=False):
    cache = os.path.join(CACHE_DIR, f'{vk_id}.html')
    if os.path.exists(cache) and not refresh:
        with open(cache, encoding='utf-8') as f:
            text = f.read()
    else:
        # вики-страницы ВК отдаются в cp1251
        text = http_get(f'https://vk.com/page-{GROUP}_{vk_id}').decode('cp1251', 'replace')
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache, 'w', encoding='utf-8') as f:
            f.write(text)
    title = re.search(r'<div class="ui_crumb" >(.*?)</div>', text)
    title = html.unescape(title.group(1)).strip() if title else str(vk_id)
    start = text.find('<div class="wk_text">')
    if start < 0:
        raise RuntimeError(f'На странице {vk_id} нет вики-текста (закрыта или удалена?)')
    depth = 0
    for m in re.finditer(r'<div\b|</div>', text[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return title, text[start:start + m.end()]
    return title, text[start:]


def download_image(wiki_id, src):
    os.makedirs(IMG_DIR, exist_ok=True)
    name = f'{wiki_id}.jpg'
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        data = optimize_image(http_get(html.unescape(src), timeout=60))
        with open(path, 'wb') as f:
            f.write(data)
    return f'photo/vk/{name}'


def optimize_image(raw, max_side=1200):
    """Уменьшает картинку до ширины контента сайта и пережимает JPEG (нужен Pillow)."""
    try:
        import io
        from PIL import Image
    except ImportError:
        return raw
    im = Image.open(io.BytesIO(raw))
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=85, optimize=True, progressive=True)
    return buf.getvalue() if len(buf.getvalue()) < len(raw) * 0.9 else raw


def page_id_from_href(href):
    m = re.search(rf'page-{GROUP}_(\d+)', href or '')
    return m.group(1) if m else None


def external_href(href):
    href = html.unescape(href or '')
    if href.startswith('/away.php'):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        return q.get('to', [href])[0]
    if href.startswith('/'):
        return 'https://vk.com' + href
    return href


FORMAT_TAGS = {'b': '**', 'strong': '**', 'i': '_', 'em': '_', 's': '~~'}
BLOCK_END_TAGS = ('h1', 'h2', 'h3', 'h4', 'center', 'p', 'blockquote')


class WikiToMarkdown(HTMLParser):
    """Переводит HTML вики-страницы ВК в Markdown.

    Таблицы, в которых почти все ячейки — картинки-ссылки на другие страницы,
    считаются меню: они не попадают в текст, а сохраняются в self.menu
    (порядок дочерних страниц и их картинки-кнопки).

    Жирный/курсив в ВК часто тянется через переносы строк, а в Markdown так
    нельзя, поэтому на каждом переносе открытое оформление закрывается и
    открывается снова уже на следующей строке с текстом.
    """

    def __init__(self, download=True):
        super().__init__(convert_charrefs=True)
        self.download = download
        self.out = []
        self.link = None
        self.list_stack = []
        self.table = None
        self.menu = []          # [(vk_id, title, image)]
        self.in_hider_title = False
        self.hider_title = ''
        self.open = []          # оформление, уже выведенное в текст
        self.pending = []       # оформление, которое откроется с первым словом

    # --- вывод -------------------------------------------------------
    def target(self):
        if self.table is not None:
            return self.table['cell']
        if self.link is not None:
            return self.link['text']
        return self.out

    def emit(self, text):
        self.target().append(text)

    def close_marker(self, marker):
        chunks = self.target()
        trailing = ''
        if chunks and chunks[-1] != chunks[-1].rstrip():
            chunks[-1] = chunks[-1].rstrip()
            trailing = ' '
        chunks.append(marker + trailing)

    def newline(self, text):
        reopen = []
        while self.open:
            marker = self.open.pop()
            self.close_marker(marker)
            reopen.insert(0, marker)
        self.pending = reopen + self.pending
        self.emit(text)

    def image(self, attrs):
        src = attrs.get('src')
        # id картинки ВК пишет либо на <img>, либо на обёртке <a class="wk_photo">
        wiki_id = attrs.get('wiki') or (self.link or {}).get('wiki')
        if not src:
            return ''
        if not wiki_id:
            wiki_id = 'x' + hashlib.md5(src.split('?')[0].encode()).hexdigest()[:16]
        return download_image(wiki_id, src) if self.download else f'photo/vk/{wiki_id}.jpg'

    # --- теги --------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '')
        if tag in FORMAT_TAGS:
            self.pending.append(FORMAT_TAGS[tag])
        elif tag == 'br':
            self.newline('\n')
        elif tag == 'div' and 'wk_hider_title' in cls:
            self.in_hider_title = True
            self.hider_title = ''
            self.list_stack = []
        elif tag == 'div' and 'wk_header' in cls:
            self.newline('\n\n## ')
        elif tag in ('h1', 'h2', 'h3', 'h4'):
            self.newline('\n\n' + '#' * (int(tag[1]) + 1) + ' ')
        elif tag in ('ul', 'ol'):
            self.list_stack.append(tag)
            self.newline('\n')
        elif tag == 'li':
            marker = '1.' if self.list_stack and self.list_stack[-1] == 'ol' else '-'
            # ВК часто не закрывает <ul>, поэтому вложенность не учитываем
            self.newline('\n' + marker + ' ')
        elif tag == 'blockquote':
            self.newline('\n\n> ')
        elif tag == 'table':
            self.newline('\n\n')
            self.table = {'rows': [], 'row': None, 'cell': [], 'links': []}
        elif tag == 'tr' and self.table is not None:
            self.table['row'] = []
        elif tag in ('td', 'th') and self.table is not None:
            self.table['cell'] = []
        elif tag == 'a':
            self.newline('')  # оформление не должно пересекать границу ссылки
            self.link = {'href': a.get('href'), 'title': a.get('title'), 'wiki': a.get('wiki'), 'text': []}
        elif tag == 'img':
            path = self.image(a)
            if path and self.link is not None:
                self.link['image'] = path
            elif path:
                self.newline(f'\n\n![](/static/{path})\n\n')

    def handle_endtag(self, tag):
        if tag in FORMAT_TAGS:
            marker = FORMAT_TAGS[tag]
            if marker in self.pending:
                self.pending.remove(marker)
            elif marker in self.open:
                self.open.remove(marker)
                self.close_marker(marker)
        elif tag == 'div' and self.in_hider_title:
            self.in_hider_title = False
            self.newline(f'\n\n## {self.hider_title.strip()}\n\n')
        elif tag in BLOCK_END_TAGS:
            self.newline('\n\n')
        elif tag in ('ul', 'ol'):
            if self.list_stack:
                self.list_stack.pop()
            self.newline('\n\n')
        elif tag == 'a' and self.link is not None:
            self.finish_link()
        elif tag in ('td', 'th') and self.table is not None and self.table['row'] is not None:
            self.newline('')
            self.table['row'].append(''.join(self.table['cell']).strip())
            self.table['cell'] = []
        elif tag == 'tr' and self.table is not None and self.table['row'] is not None:
            if any(c for c in self.table['row']):
                self.table['rows'].append(self.table['row'])
            self.table['row'] = None
        elif tag == 'table' and self.table is not None:
            self.finish_table()

    def handle_data(self, data):
        if self.in_hider_title:
            self.hider_title += data
            return
        data = re.sub(r'\s+', ' ', data)
        if not data.strip():
            if data:
                self.emit(' ')
            return
        if data[0] == ' ':
            self.emit(' ')
        for marker in self.pending:
            self.emit(marker)
            self.open.append(marker)
        self.pending = []
        self.emit(data.lstrip())

    def finish_link(self):
        self.newline('')
        link, self.link = self.link, None
        text = ''.join(link['text']).strip()
        vk_id = page_id_from_href(link['href'])
        if link.get('image'):
            if vk_id:
                entry = (vk_id, link['title'] or text, link['image'])
                if self.table is not None:
                    self.table['links'].append(entry)
                    self.table['cell'].append('\x00MENU\x00')
                else:
                    self.menu.append(entry)
                return
            self.emit(f'\n\n![](/static/{link["image"]})\n\n')
            return
        if not text:
            return
        if vk_id:
            self.emit(f'[{text}](vk:{vk_id})')
        elif link['href'] and not link['href'].startswith('#'):
            self.emit(f'[{text}]({external_href(link["href"])})')
        else:
            self.emit(text)

    def finish_table(self):
        t, self.table = self.table, None
        cells = [c for row in t['rows'] for c in row if c]
        menu_cells = [c for c in cells if '\x00MENU\x00' in c]
        self.menu.extend(t['links'])
        if t['links'] and len(menu_cells) >= len(cells) / 2:
            rest = [re.sub(r'\x00MENU\x00', '', c).strip() for c in cells]
            rest = [c for c in rest if c]
            if rest:
                self.out.append('\n\n' + '\n\n'.join(rest) + '\n\n')
            return
        rows = [[re.sub(r'\x00MENU\x00', '', c).replace('\n', ' ').replace('|', '/') for c in r]
                for r in t['rows']]
        if not rows:
            return
        width = max(len(r) for r in rows)
        rows = [r + [''] * (width - len(r)) for r in rows]
        lines = ['| ' + ' | '.join(rows[0]) + ' |', '|' + ' --- |' * width]
        lines += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
        self.out.append('\n\n' + '\n'.join(lines) + '\n\n')

    def markdown(self):
        self.newline('')
        text = ''.join(self.out).replace(' ', ' ')
        lines = [ln.strip() for ln in text.split('\n')]
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip() + '\n'


class ArticleToMarkdown(HTMLParser):
    """Переводит статью ВК (vk.com/@-182026147-...) в Markdown.

    <cite> — крупные разделы статьи (##), абзац из одного жирного текста —
    подраздел (###), <figure> — картинка или галерея с подписью.
    """

    def __init__(self, download=True):
        super().__init__(convert_charrefs=True)
        self.download = download
        self.out = []
        self.block = None       # текущий абзац: {'tag', 'parts'}
        self.figure = None      # {'attrs': [...], 'caption': [...]}
        self.in_caption = False
        self.link = None
        self.table = None       # строки таблицы
        self.cell = None        # абзацы текущей ячейки

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'table':
            self.table = []
        elif tag == 'tr' and self.table is not None:
            self.table.append([])
        elif tag in ('td', 'th') and self.table is not None:
            self.cell = []
        if tag == 'figure':
            self.figure = {'attrs': [], 'caption': []}
        if self.figure is not None:
            self.figure['attrs'].extend(v for _, v in attrs if v)
            if tag == 'figcaption':
                self.in_caption = True
            return
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'cite', 'li', 'blockquote'):
            self.block = {'tag': tag, 'parts': []}
        elif self.block is not None:
            if tag in ('strong', 'b'):
                self.block['parts'].append('**')
            elif tag in ('em', 'i'):
                self.block['parts'].append('_')
            elif tag == 'br':
                self.block['parts'].append('\n')
            elif tag == 'a':
                self.link = a.get('href')
                self.block['parts'].append('[')

    def handle_endtag(self, tag):
        if self.figure is not None:
            if tag == 'figcaption':
                self.in_caption = False
            if tag == 'figure':
                self.finish_figure()
            return
        if tag in ('td', 'th') and self.cell is not None:
            self.table[-1].append(' '.join(self.cell).replace('|', '/'))
            self.cell = None
        elif tag == 'table' and self.table is not None:
            rows, self.table = [r for r in self.table if any(r)], None
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [''] * (width - len(r)) for r in rows]
                lines = ['| ' + ' | '.join(rows[0]) + ' |', '|' + ' --- |' * width]
                lines += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
                self.out.append('\n'.join(lines))
        if self.block is None:
            return
        if tag in ('strong', 'b'):
            self.block['parts'].append('**')
        elif tag in ('em', 'i'):
            self.block['parts'].append('_')
        elif tag == 'a' and self.link is not None:
            href = external_href(self.link)
            vk_id = page_id_from_href(href)
            self.block['parts'].append(f'](vk:{vk_id})' if vk_id else f']({href})')
            self.link = None
        elif tag == self.block['tag']:
            self.finish_block()

    def handle_data(self, data):
        if self.figure is not None:
            if self.in_caption:
                self.figure['caption'].append(data)
            return
        if self.block is not None:
            self.block['parts'].append(re.sub(r'\s+', ' ', data))

    def finish_block(self):
        block, self.block = self.block, None
        text = ''.join(block['parts']).strip()
        text = re.sub(r'\*\*\s*\*\*', '', text).strip()
        if not text:
            return
        if self.cell is not None:
            self.cell.append(text)
            return
        tag = block['tag']
        plain = text.strip('*').strip()
        if tag == 'cite' or tag in ('h1', 'h2'):
            self.out.append(f'## {plain[:1].upper() + plain[1:].lower()}')
        elif tag in ('h3', 'h4') or (text.startswith('**') and text.endswith('**') and '**' not in text[2:-2]):
            self.out.append(f'### {plain.rstrip(":")}')
        elif tag == 'li':
            self.out.append(f'- {text}')
        elif tag == 'blockquote':
            self.out.append(f'> {text}')
        else:
            self.out.append(text)

    def finish_figure(self):
        fig, self.figure = self.figure, None
        raw = html.unescape(' '.join(fig['attrs'])).replace('\\/', '/')
        photos = {}
        for url in re.findall(r'https://[^"\s,\]]+?\.(?:jpg|png)\?[^"\s\]]+', raw):
            key = url.split('?')[0]
            size = re.search(r'cs=(\d+)x0', url)
            size = int(size.group(1)) if size else 0
            if size <= 1280 and size >= photos.get(key, (0, ''))[0]:
                photos[key] = (size, url)
        caption = ' '.join(''.join(fig['caption']).split())
        for key, (_, url) in photos.items():
            name = 'a' + hashlib.md5(key.encode()).hexdigest()[:16]
            path = download_image(name, url) if self.download else f'photo/vk/{name}.jpg'
            self.out.append(f'![{caption}](/static/{path})')
        if caption and photos:
            self.out.append(f'_{caption}_')

    def markdown(self):
        text = '\n\n'.join(self.out)
        return re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'


def convert_article(slug, download=True, refresh=False):
    """slug — часть адреса после vk.com/@-182026147- (например, imperiya-korvas)."""
    cache = os.path.join(CACHE_DIR, f'article-{slug}.html')
    if os.path.exists(cache) and not refresh:
        with open(cache, encoding='utf-8') as f:
            text = f.read()
    else:
        text = http_get(f'https://vk.com/@-{GROUP}-{slug}').decode('cp1251', 'replace')
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache, 'w', encoding='utf-8') as f:
            f.write(text)
    title = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.S)
    title = html.unescape(re.sub(r'<[^>]+>', '', title.group(1))).strip() if title else slug
    start = text.find('<h1')
    end = text.find('article_bottom', start)
    body = text[text.find('>', start) + 1: end if end > 0 else len(text)]
    body = body[body.find('</h1>') + 5:]
    parser = ArticleToMarkdown(download=download)
    parser.feed(body)
    return title, parser.markdown()


def convert(vk_id, download=True, refresh=False):
    title, body = fetch_page(vk_id, refresh=refresh)
    parser = WikiToMarkdown(download=download)
    parser.feed(body)
    return title, parser.markdown(), parser.menu


def write_draft(vk_id, title, md, menu, out_dir, parent=None, image=None):
    os.makedirs(out_dir, exist_ok=True)
    slug = slugify(title)
    head = [f'title: {title}', f'parent: {parent or "index"}', f'vk: {vk_id}']
    if image:
        head.append(f'image: {image}')
    if menu:
        head.append('# меню ВК: ' + ', '.join(f'{t} ({i})' for i, t, _ in menu))
    path = os.path.join(out_dir, f'{slug}.md')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            if f'vk: {vk_id}\n' not in f.read():
                path = os.path.join(out_dir, f'{slug}-{vk_id}.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(head) + '\n\n' + md)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page', help='id вики-страницы ВК (число после page-182026147_)')
    ap.add_argument('--crawl', action='store_true', help='пройти по всем ссылкам меню')
    ap.add_argument('--out', default=DRAFTS_DIR, help='куда писать черновики')
    ap.add_argument('--no-images', action='store_true', help='не скачивать картинки')
    ap.add_argument('--refresh', action='store_true', help='скачать страницы заново, мимо кэша')
    ap.add_argument('--article', action='store_true',
                    help='page — это адрес статьи (часть после vk.com/@-182026147-)')
    args = ap.parse_args()

    if args.article:
        title, md = convert_article(args.page, download=not args.no_images, refresh=args.refresh)
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, f'article-{args.page}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'title: {title}\nparent: index\n\n' + md)
        print(f'✅ статья {args.page} {title} → {os.path.relpath(path, ROOT)}')
        return

    queue = [(args.page, None, None)]
    seen, index = set(), []
    while queue:
        vk_id, parent, image = queue.pop(0)
        if vk_id in seen:
            continue
        seen.add(vk_id)
        try:
            title, md, menu = convert(vk_id, download=not args.no_images, refresh=args.refresh)
        except Exception as e:
            print(f'❌ {vk_id}: {e}', file=sys.stderr, flush=True)
            continue
        path = write_draft(vk_id, title, md, menu, args.out, parent=parent, image=image)
        index.append({'vk': vk_id, 'title': title, 'parent': parent, 'image': image,
                      'file': os.path.relpath(path, ROOT),
                      'menu': [{'vk': i, 'title': t, 'image': img} for i, t, img in menu]})
        print(f'✅ {vk_id} {title} → {os.path.relpath(path, ROOT)}', flush=True)
        if args.crawl:
            for child_id, _, child_image in menu:
                queue.append((child_id, slugify(title), child_image))
            for child_id in re.findall(r'\(vk:(\d+)\)', md):
                queue.append((child_id, slugify(title), None))

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, '_index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
