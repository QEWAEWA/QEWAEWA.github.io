from flask import Flask, render_template
import os
import shutil

def generate_static_site():
    # Создаем Flask приложение
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
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
    
    # Папка для выходных файлов (GitHub Pages использует /docs или /public)
    output_dir = "docs"
    
    # Очищаем выходную директорию
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Копируем статические файлы
    print("Копируем статические файлы...")
    shutil.copytree('static', os.path.join(output_dir, 'static'))
    
    # Функция для замены url_for на относительные пути
    def fix_urls(html_content):
        replacements = {
            "{{ url_for('static', filename='": "static/",
            "{{ url_for('index') }}": "index.html",
            "{{ url_for('karta') }}": "karta.html", 
            "{{ url_for('lor') }}": "lor.html",
            "{{ url_for('ankety') }}": "ankety.html"
        }
        
        for old, new in replacements.items():
            html_content = html_content.replace(old, new)
            
        return html_content
    
    # Генерируем HTML страницы
    print("Генерируем HTML страницы...")
    
    with app.test_request_context():
        # Главная страница
        html = render_template('index.html', 
                             title='Главная - Наир',
                             active_page='index')
        fixed_html = fix_urls(html)
        with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(fixed_html)
        
        # Карта
        html = render_template('karta.html',
                             title='Карта - Наир',
                             active_page='karta')
        fixed_html = fix_urls(html)
        with open(os.path.join(output_dir, 'karta.html'), 'w', encoding='utf-8') as f:
            f.write(fixed_html)
        
        # Лор
        html = render_template('lor.html',
                             title='Лор - Наир', 
                             active_page='lor')
        fixed_html = fix_urls(html)
        with open(os.path.join(output_dir, 'lor.html'), 'w', encoding='utf-8') as f:
            f.write(fixed_html)
        
        # Анкеты
        html = render_template('ankety.html',
                             title='Анкеты - Наир',
                             active_page='ankety')
        fixed_html = fix_urls(html)
        with open(os.path.join(output_dir, 'ankety.html'), 'w', encoding='utf-8') as f:
            f.write(fixed_html)
    
    # Создаем .nojekyll файл для GitHub Pages
    with open(os.path.join(output_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    print(f"✅ Статический сайт сгенерирован в папке {output_dir}!")
    print("📝 Не забудьте в настройках GitHub Pages указать source: docs")

if __name__ == '__main__':
    generate_static_site()