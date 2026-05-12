# CRM система учета картриджей и принтеров

Система управления учетом заправки картриджей, регистрации принтеров, их перемещения и ответственных лиц. Разработана на Django + SQLite.

## 📋 Оглавление

- [Возможности системы](#возможности-системы)
- [Требования к окружению](#требования-к-окружению)
- [Структура проекта](#структура-проекта)
- [Быстрый старт (Разработка)](#быстрый-старт-разработка)
- [Развертывание на Production сервере](#развертывание-na-production-сервере)
- [Администрирование системы](#администрирование-системы)
- [Обслуживание и мониторинг](#обслуживание-и-мониторинг)
- [Безопасность](#безопасность)
- [Решение проблем](#решение-проблем)

---

## 🚀 Возможности системы

### Учет оборудования
- **Принтеры**: регистрация моделей, серийных номеров, мест установки, текущего состояния
- **Картриджи**: учет заправок, ресурса, текущего расположения, истории обслуживания
- **История перемещений**: автоматическое ведение журнала перемещения принтеров и картриджей

### Управление персоналом
- **Справочник сотрудников**: должности, контакты, статус материальной ответственности
- **Ответственные лица**: закрепление оборудования за конкретными сотрудниками
- **Профиль МОЛ**: специальный интерфейс для материально ответственных лиц

### Складской учет
- **Помещения**: справочник зданий, этажей, комнат, складов
- **Складское хранение**: учет наличия картриджей и принтеров на складе
- **Перемещение между складами**: трекинг перемещений оборудования

### Администрирование
- **Панель администратора**: полный CRUD для всех сущностей системы
- **Отчетность**: статистика по оборудованию, сотрудникам, помещениям
- **Аудит**: полная история всех операций с оборудованием

---

## 💻 Требования к окружению

### Минимальные требования
- **ОС**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 7+)
- **Python**: 3.8 или выше
- **Память**: 512 MB RAM (минимум), 1 GB RAM (рекомендуется)
- **Диск**: 1 GB свободного места
- **Веб-сервер**: Nginx (рекомендуется) или Apache
- **WSGI сервер**: Gunicorn или uWSGI

### Зависимости Python
```
Django>=4.2,<5.0
gunicorn>=21.0.0
python-decouple>=3.8
```

---

## 📁 Структура проекта

```
/workspace/
├── conf/                       # Конфигурация проекта Django
│   ├── __init__.py
│   ├── settings.py             # Основные настройки
│   ├── urls.py                 # Маршрутизация URL
│   ├── wsgi.py                 # WSGI конфигурация
│   └── asgi.py                 # ASGI конфигурация
├── core/                       # Основное приложение
│   ├── migrations/             # Миграции базы данных
│   ├── templates/core/         # HTML шаблоны
│   ├── management/commands/    # Пользовательские команды
│   ├── models.py               # Модели данных
│   ├── admin.py                # Настройки админ-панели
│   ├── views.py                # Представления
│   └── urls.py                 # URL приложения
├── static/                     # Статические файлы
├── media/                      # Загружаемые файлы
├── manage.py                   # Утилита управления Django
├── requirements.txt            # Зависимости Python
├── .env                        # Переменные окружения
└── README.md                   # Документация
```

---

## ⚡ Быстрый старт (Разработка)

### 1. Установка зависимостей
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Применение миграций
```bash
python manage.py migrate
```

### 3. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 4. Загрузка тестовых данных
```bash
python manage.py create_test_data
```

### 5. Запуск сервера
```bash
python manage.py runserver 0.0.0.0:8000
```

### 6. Доступ к системе
- **Главная панель**: http://localhost:8000/
- **Админ-панель**: http://localhost:8000/admin/
- **Логин**: `admin`
- **Пароль**: `admin123`

---

## 🛠️ Развертывание на Production сервере

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка пакетов
sudo apt install -y python3-pip python3-venv python3-dev \
                    build-essential libssl-dev libffi-dev \
                    nginx curl git
```

### 2. Настройка проекта

```bash
# Создание пользователя
sudo useradd -m -s /bin/bash crm-user
sudo mkdir -p /var/www/crm-system
sudo chown crm-user:crm-user /var/www/crm-system

# Клонирование и установка
sudo -u crm-user -i
cd /var/www/crm-system
git clone <repository-url> .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn python-decouple
```

### 3. Настройка переменных окружения

Создайте файл `.env`:
```env
SECRET_KEY=your-super-secret-key-min-50-characters
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=sqlite:///db.sqlite3
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. База данных и статика

```bash
python manage.py migrate
python manage.py createsuperuser
mkdir -p staticfiles media
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data staticfiles media
```

### 5. Настройка Gunicorn

Создайте `gunicorn.conf.py`:
```python
bind = "unix:/var/www/crm-system/gunicorn.sock"
workers = 3
timeout = 30
accesslog = "/var/log/crm-system/gunicorn_access.log"
errorlog = "/var/log/crm-system/gunicorn_error.log"
pidfile = "/var/www/crm-system/gunicorn.pid"
user = "crm-user"
group = "crm-user"
```

### 6. Настройка systemd

Создайте `/etc/systemd/system/crm-system.service`:
```ini
[Unit]
Description=CRM System Gunicorn instance
After=network.target

[Service]
User=crm-user
Group=crm-user
WorkingDirectory=/var/www/crm-system
ExecStart=/var/www/crm-system/venv/bin/gunicorn --config gunicorn.conf.py conf.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crm-system
sudo systemctl start crm-system
```

### 7. Настройка Nginx

Создайте `/etc/nginx/sites-available/crm-system`:
```nginx
upstream crm_server {
    server unix:/var/www/crm-system/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location /static/ {
        alias /var/www/crm-system/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/crm-system/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://crm_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:
```bash
sudo ln -s /etc/nginx/sites-available/crm-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Настройка HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 Администрирование системы

### Резервное копирование
```bash
# Бэкап базы данных
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Экспорт данных
python manage.py dumpdata core --indent 2 > backup.json
```

### Обновление системы
```bash
cd /var/www/crm-system
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart crm-system
```

---

## 📊 Обслуживание и мониторинг

### Логи
```bash
# Просмотр логов Gunicorn
sudo journalctl -u crm-system -f

# Логи Nginx
sudo tail -f /var/log/nginx/crm-access.log
```

### Ротация логов
Создайте `/etc/logrotate.d/crm-system`:
```
/var/log/crm-system/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 crm-user crm-user
}
```

---

## 🔒 Безопасность

### Рекомендации
1. Регулярно обновляйте зависимости: `pip list --outdated`
2. Настройте брандмауэр: `sudo ufw allow 'Nginx Full'`
3. Используйте сложные пароли
4. Включите HTTPS обязательно
5. Ограничьте доступ к админке по IP

### Проверка настроек безопасности
Убедитесь, что в `settings.py`:
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

---

## 🐛 Решение проблем

### Nginx возвращает 502 Bad Gateway
```bash
sudo systemctl status crm-system
sudo tail -f /var/log/crm-system/gunicorn_error.log
sudo systemctl restart crm-system nginx
```

### Статические файлы не загружаются
```bash
python manage.py collectstatic --clear --noinput
sudo chown -R www-data:www-data staticfiles
```

### Ошибки базы данных
```bash
sqlite3 db.sqlite3 "PRAGMA integrity_check;"
cp db.sqlite3.backup.* db.sqlite3
```

---

## 📝 Чек-лист перед запуском в Production

- [ ] `DEBUG = False`
- [ ] Уникальный `SECRET_KEY`
- [ ] Настроен `ALLOWED_HOSTS`
- [ ] Создан суперпользователь
- [ ] Применены миграции
- [ ] Собрана статика
- [ ] Настроен Gunicorn
- [ ] Настроен Nginx
- [ ] Получен SSL сертификат
- [ ] Настроено резервное копирование
- [ ] Настроен брандмауэр

---

**Версия системы**: 1.0.0  
**Дата обновления**: 2024
