import os
import shutil
from flask import Flask, render_template

def generate_static_site():
    print("🚀 Начинаем генерацию статического сайта...")
    
    # Создаем приложение с явным указанием путей
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Регистрируем роуты
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
    
    # Выходная директория
    output_dir = "docs"
    
    # Очищаем выходную директорию
    if os.path.exists(output_dir):
        print(f"🧹 Очищаем папку {output_dir}...")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir)
    print(f"📁 Создана папка {output_dir}")
    
    # Проверяем существование необходимых папок
    print("🔍 Проверяем необходимые папки...")
    if not os.path.exists('templates'):
        print("❌ Папка templates не найдена!")
        print("Создайте папку templates с файлами: base.html, index.html и т.д.")
        return False
    
    if not os.path.exists('static'):
        print("❌ Папка static не найдена!")
        return False
    
    print("✅ Все необходимые папки существуют")
    
    # Копируем статические файлы
    print("📸 Копируем статические файлы...")
    shutil.copytree('static', os.path.join(output_dir, 'static'))
    print("✅ Статические файлы скопированы")
    
    # Показываем какие шаблоны есть
    print("📋 Доступные шаблоны:")
    templates = os.listdir('templates')
    for template in templates:
        print(f"   📄 {template}")
    
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
        ('index.html', 'index.html', {'title': 'Главная - Наир', 'active_page': 'index'}),
        ('karta.html', 'karta.html', {'title': 'Карта - Наир', 'active_page': 'karta'}),
        ('lor.html', 'lor.html', {'title': 'Лор - Наир', 'active_page': 'lor'}),
        ('ankety.html', 'ankety.html', {'title': 'Анкеты - Наир', 'active_page': 'ankety'})
    ]
    
    with app.test_request_context():
        for filename, template_name, context in pages:
            print(f"  📝 Генерируем {filename} из шаблона {template_name}...")
            try:
                # Проверяем существование шаблона
                template_path = os.path.join('templates', template_name)
                if not os.path.exists(template_path):
                    print(f"    ❌ Шаблон {template_name} не найден!")
                    continue
                
                # Рендерим шаблон с контекстом
                html = render_template(template_name, **context)
                fixed_html = fix_urls(html)
                
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(fixed_html)
                print(f"    ✅ {filename} создан успешно")
                
            except Exception as e:
                print(f"    ❌ Ошибка при создании {filename}: {str(e)}")
                # Создаём подробную заглушку для отладки
                error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Ошибка генерации</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ background: #ffe6e6; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Ошибка при генерации {filename}</h1>
        <p><strong>Шаблон:</strong> {template_name}</p>
        <p><strong>Ошибка:</strong> {str(e)}</p>
        <p><strong>Рабочая директория:</strong> {os.getcwd()}</p>
        <p><strong>Существующие шаблоны:</strong> {', '.join(os.listdir('templates')) if os.path.exists('templates') else 'папка не существует'}</p>
    </div>
</body>
</html>
"""
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(error_html)
    
    # Создаем .nojekyll файл
    with open(os.path.join(output_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    print(f"✅ Статический сайт сгенерирован в {output_dir}!")
    return True

if __name__ == '__main__':
    success = generate_static_site()
    exit(0 if success else 1)