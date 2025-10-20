from flask import Flask, render_template
import os
import shutil

app = Flask(__name__)

# Создаем папку для статического сайта
output_dir = "static_site"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# Копируем статические файлы
shutil.copytree("static", os.path.join(output_dir, "static"))

# Генерируем HTML страницы
pages = [
    ('index.html', 'index'),
    ('karta.html', 'karta'), 
    ('lor.html', 'lor'),
    ('ankety.html', 'ankety')
]

for filename, route in pages:
    with app.test_request_context():
        if route == 'index':
            html = render_template('index.html')
        elif route == 'karta':
            html = render_template('karta.html')
        else:
            html = f"<h1>Страница {route}</h1>"
        
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        f.write(html)

print("Статический сайт сгенерирован!")
