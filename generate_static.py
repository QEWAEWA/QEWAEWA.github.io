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
    
    with app.test_request_context():
        try:
            # Главная страница
            print("  📝 index.html...")
            html = render_template('index.html', 
                                 title='Главная - Наир',
                                 active_page='index')
            fixed_html = fix_urls(html)
            with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(fixed_html)
            
            # Карта
            print("  📝 karta.html...")
            html = render_template('karta.html',
                                 title='Карта - Наир',
                                 active_page='karta')
            fixed_html = fix_urls(html)
            with open(os.path.join(output_dir, 'karta.html'), 'w', encoding='utf-8') as f:
                f.write(fixed_html)
            
            # Лор
            print("  📝 lor.html...")
            html = render_template('lor.html',
                                 title='Лор - Наир', 
                                 active_page='lor')
            fixed_html = fix_urls(html)
            with open(os.path.join(output_dir, 'lor.html'), 'w', encoding='utf-8') as f:
                f.write(fixed_html)
            
            # Анкеты
            print("  📝 ankety.html...")
            html = render_template('ankety.html',
                                 title='Анкеты - Наир',
                                 active_page='ankety')
            fixed_html = fix_urls(html)
            with open(os.path.join(output_dir, 'ankety.html'), 'w', encoding='utf-8') as f:
                f.write(fixed_html)
                
        except Exception as e:
            print(f"❌ Ошибка при генерации HTML: {e}")
            return False
    
    # Создаем .nojekyll файл
    with open(os.path.join(output_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    # Создаем CNAME файл если нужен домен (опционально)
    # with open(os.path.join(output_dir, 'CNAME'), 'w') as f:
    #     f.write('your-domain.com')
    
    print(f"✅ Статический сайт успешно сгенерирован в папке {output_dir}!")
    print("📋 Содержимое папки docs:")
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')
    
    return True

if __name__ == '__main__':
    success = generate_static_site()
    exit(0 if success else 1)