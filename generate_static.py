import os
import shutil
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template('index.html', 
                             title='Главная - Наир',
                             active_page='index')
    
    @app.route('/karta')
    def karta():
        return render_template('karta.html',
                             title='Карта - Наир', 
                             active_page='karta')
    
    @app.route('/lor')
    def lor():
        return render_template('lor.html',
                             title='Лор - Наир',
                             active_page='lor')
    
    @app.route('/ankety')
    def ankety():
        return render_template('ankety.html',
                             title='Анкеты - Наир', 
                             active_page='ankety')
    
    return app

def generate_static_site():
    print("🚀 Начинаем генерацию статического сайта...")
    
    # Создаем приложение
    app = create_app()
    
    # Выходная директория
    output_dir = "docs"
    
    # Очищаем выходную директорию
    if os.path.exists(output_dir):
        print(f"🧹 Очищаем папку {output_dir}...")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir)
    print(f"📁 Создана папка {output_dir}")
    
    # Копируем статические файлы
    print("📸 Копируем статические файлы...")
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(output_dir, 'static'))
        print("✅ Статические файлы скопированы")
    else:
        print("❌ Папка static не найдена!")
        return False
    
    # Функция для замены Flask путей на относительные
    def fix_urls(html_content):
        replacements = {
            "{{ url_for('static', filename='": "static/",
            "{{ url_for('index') }}": "index.html",
            "{{ url_for('karta') }}": "karta.html", 
            "{{ url_for('lor') }}": "lor.html",
            "{{ url_for('ankety') }}": "ankety.html",
            "') }}": ""  # Убираем оставшиеся закрывающие теги
        }
        
        for old, new in replacements.items():
            html_content = html_content.replace(old, new)
            
        return html_content
    
    # Генерируем HTML страницы
    print("📄 Генерируем HTML страницы...")
    
    pages = [
        ('index.html', 'index', {'title': 'Главная - Наир', 'active_page': 'index'}),
        ('karta.html', 'karta', {'title': 'Карта - Наир', 'active_page': 'karta'}),
        ('lor.html', 'lor', {'title': 'Лор - Наир', 'active_page': 'lor'}),
        ('ankety.html', 'ankety', {'title': 'Анкеты - Наир', 'active_page': 'ankety'})
    ]
    
    with app.test_request_context():
        for filename, template_name, context in pages:
            print(f"  📝 Генерируем {filename} из шаблона {template_name}...")
            try:
                # Рендерим шаблон с контекстом
                html = render_template(template_name, **context)
                fixed_html = fix_urls(html)
                
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(fixed_html)
                print(f"    ✅ {filename} создан успешно")
                
            except Exception as e:
                print(f"    ❌ Ошибка при создании {filename}: {e}")
                # Создаём заглушку с ошибкой для отладки
                error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Ошибка</title>
</head>
<body>
    <h1>Ошибка при генерации {filename}</h1>
    <p>Шаблон: {template_name}</p>
    <p>Ошибка: {e}</p>
</body>
</html>
"""
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(error_html)
    
    # Создаем .nojekyll файл
    with open(os.path.join(output_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    print(f"✅ Статический сайт успешно сгенерирован в папке {output_dir}!")
    
    # Показываем что создалось
    print("📋 Созданные файлы:")
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isfile(item_path):
            print(f"  📄 {item}")
        else:
            print(f"  📁 {item}/")
    
    return True

if __name__ == '__main__':
    success = generate_static_site()
    exit(0 if success else 1)