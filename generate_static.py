import os
import shutil
from flask import Flask, render_template

class StaticSiteGenerator:
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.output_dir = "docs"
        self.setup_routes()
    
    def setup_routes(self):
        """Настройка маршрутов Flask"""
        @self.app.route('/')
        def index():
            return render_template('index.html', 
                                 title='Главная - Наир',
                                 active_page='index')
        
        @self.app.route('/karta')
        def karta():
            return render_template('karta.html',
                                 title='Карта - Наир', 
                                 active_page='karta')
        
        @self.app.route('/lor')
        def lor():
            return render_template('lor.html',
                                 title='Лор - Наир',
                                 active_page='lor')
        
        @self.app.route('/ankety')
        def ankety():
            return render_template('ankety.html',
                                 title='Анкеты - Наир', 
                                 active_page='ankety')
        
        @self.app.route('/magic')
        def magic():
            return render_template('magic.html',
                                 title='Магия - Наир', 
                                 active_page='magic')
        
        @self.app.route('/economy')
        def economy():
            return render_template('economy.html',
                                 title='Экономика - Наир', 
                                 active_page='economy')
        
        @self.app.route('/leveling')
        def leveling():
            return render_template('leveling.html',
                                 title='Система прокачки - Наир', 
                                 active_page='leveling')
        
        @self.app.route('/kuznec')
        def kuznec():
            return render_template('kuznec.html',
                                 title='Кузнечество - Наир',
                                 active_page='kuznec')
        
        @self.app.route('/oruzie')
        def oruzie():
            return render_template('oruzie.html',
                                 title='Оружие - Наир',
                                 active_page='oruzie')
        
        @self.app.route('/bronya')
        def bronya():
            return render_template('bronya.html',
                                 title='Броня - Наир',
                                 active_page='bronya')
        
        @self.app.route('/zelya')
        def zelya():
            return render_template('zelya.html',
                                 title='Зелья - Наир',
                                 active_page='zelya')
        
        @self.app.route('/prochee')
        def prochee():
            return render_template('prochee.html',
                                 title='Прочее - Наир',
                                 active_page='prochee')
        
        @self.app.route('/about')
        def about():
            return render_template('about.html',
                                 title='О Проекте - Наир',
                                 active_page='about')
    
    def clean_output_dir(self):
        """Очистка выходной директории"""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
    
    def copy_static_files(self):
        """Копирование статических файлов"""
        if os.path.exists('static'):
            shutil.copytree('static', os.path.join(self.output_dir, 'static'))
            return True
        return False
    
    def fix_urls(self, html_content):
        """Замена Flask url_for на относительные пути"""
        replacements = {
            "{{ url_for('static', filename='": "static/",
            "{{ url_for('index') }}": "index.html",
            "{{ url_for('karta') }}": "karta.html", 
            "{{ url_for('lor') }}": "lor.html",
            "{{ url_for('ankety') }}": "ankety.html",
            "{{ url_for('magic') }}": "magic.html",
            "{{ url_for('economy') }}": "economy.html",
            "{{ url_for('leveling') }}": "leveling.html",
            "') }}": "",
            # Убираем проверки активной страницы, так как request.endpoint не будет работать в статическом сайте
            "{% if request.endpoint == 'index' %}active{% endif %}": "",
            "{% if request.endpoint == 'karta' %}active{% endif %}": "",
            "{% if request.endpoint == 'lor' %}active{% endif %}": "",
            "{% if request.endpoint == 'ankety' %}active{% endif %}": "",
            "{% if request.endpoint == 'magic' %}active{% endif %}": "",
            "{% if request.endpoint == 'economy' %}active{% endif %}": "",
            "{% if request.endpoint == 'leveling' %}active{% endif %}": "",
            "{% if request.endpoint == 'kuznec' %}active{% endif %}": "",
            "{% if request.endpoint == 'oruzie' %}active{% endif %}": "",
            "{% if request.endpoint == 'bronya' %}active{% endif %}": "",
            "{% if request.endpoint == 'zelya' %}active{% endif %}": "",
            "{% if request.endpoint == 'prochee' %}active{% endif %}": "",
            "{% if request.endpoint == 'about' %}active{% endif %}": ""
        }
        
        for old, new in replacements.items():
            html_content = html_content.replace(old, new)
        
        return html_content
    
    def generate_pages(self):
        """Генерация HTML страниц"""
        pages_config = [
            ('index.html', 'index.html', {
                'title': 'Главная - Наир',
                'active_page': 'index'
            }),
            ('karta.html', 'karta.html', {
                'title': 'Карта - Наир', 
                'active_page': 'karta'
            }),
            ('lor.html', 'lor.html', {
                'title': 'Лор - Наир',
                'active_page': 'lor'
            }),
            ('ankety.html', 'ankety.html', {
                'title': 'Анкеты - Наир', 
                'active_page': 'ankety'
            }),
            ('magic.html', 'magic.html', {
                'title': 'Магия - Наир', 
                'active_page': 'magic'
            }),
            ('economy.html', 'economy.html', {
                'title': 'Экономика - Наир', 
                'active_page': 'economy'
            }),
            ('leveling.html', 'leveling.html', {
                'title': 'Система прокачки - Наир', 
                'active_page': 'leveling'
            }),
            ('kuznec.html', 'kuznec.html', {
                'title': 'Кузнечество - Наир',
                'active_page': 'kuznec'
            }),
            ('oruzie.html', 'oruzie.html', {
                'title': 'Оружие - Наир',
                'active_page': 'oruzie'
            }),
            ('bronya.html', 'bronya.html', {
                'title': 'Броня - Наир',
                'active_page': 'bronya'
            }),
            ('zelya.html', 'zelya.html', {
                'title': 'Зелья - Наир',
                'active_page': 'zelya'
            }),
            ('prochee.html', 'prochee.html', {
                'title': 'Прочее - Наир',
                'active_page': 'prochee'
            }),
            ('about.html', 'about.html', {
                'title': 'О Проекте - Наир',
                'active_page': 'about'
            })
        ]
        
        with self.app.test_request_context():
            for filename, template_name, context in pages_config:
                self.generate_page(filename, template_name, context)
    
    def generate_page(self, filename, template_name, context):
        """Генерация одной страницы"""
        try:
            html = render_template(template_name, **context)
            fixed_html = self.fix_urls(html)
            
            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(fixed_html)
            
            print(f"✅ {filename}")
            
        except Exception as e:
            print(f"❌ Ошибка в {filename}: {e}")
            self.create_error_page(filename, template_name, str(e))
    
    def create_error_page(self, filename, template_name, error):
        """Создание страницы с ошибкой"""
        error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Ошибка</title>
    <style>
        body {{ font-family: Arial; margin: 40px; }}
        .error {{ background: #ffe6e6; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Ошибка генерации {filename}</h1>
        <p><strong>Шаблон:</strong> {template_name}</p>
        <p><strong>Ошибка:</strong> {error}</p>
    </div>
</body>
</html>
"""
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(error_html)
    
    def create_nojekyll(self):
        """Создание .nojekyll файла"""
        with open(os.path.join(self.output_dir, '.nojekyll'), 'w') as f:
            f.write('')
    
    def generate(self):
        """Основной метод генерации"""
        print("🚀 Запуск генерации статического сайта...")
        
        # Проверка необходимых папок
        if not all(os.path.exists(folder) for folder in ['templates', 'static']):
            print("❌ Отсутствуют необходимые папки: templates или static")
            return False
        
        # Очистка и подготовка
        self.clean_output_dir()
        print("✅ Выходная директория очищена")
        
        # Копирование статических файлов
        if not self.copy_static_files():
            print("❌ Ошибка копирования статических файлов")
            return False
        print("✅ Статические файлы скопированы")
        
        # Генерация страниц
        print("📄 Генерация HTML страниц:")
        self.generate_pages()
        
        # Создание служебных файлов
        self.create_nojekyll()
        
        print(f"🎉 Статический сайт сгенерирован в {self.output_dir}/")
        return True

def main():
    generator = StaticSiteGenerator()
    success = generator.generate()
    exit(0 if success else 1)

if __name__ == '__main__':
    main()