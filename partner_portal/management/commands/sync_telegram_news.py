from django.core.management.base import BaseCommand

from partner_portal.telegram import sync_telegram_news


class Command(BaseCommand):
    help = 'Sync company news from Telegram channel'

    def handle(self, *args, **options):
        sync_telegram_news()
        self.stdout.write(
            self.style.SUCCESS('Telegram news synced successfully')
        )