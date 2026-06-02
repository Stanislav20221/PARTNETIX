import os
import time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from partner_portal.telegram import sync_telegram_news

while True:
    try:
        sync_telegram_news()
        print('Новости синхронизированы')
    except Exception as e:
        print('Ошибка:', e)

    time.sleep(30)