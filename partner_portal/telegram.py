import requests

from django.conf import settings
from django.utils import timezone
from .models import CompanyNews, TelegramSyncState
from .models import CompanyNews


def sync_telegram_news():
    state, _ = TelegramSyncState.objects.get_or_create(
        key='company_news'
    )

    params = {
        'timeout': 10,
    }

    if state.last_update_id:
        params['offset'] = state.last_update_id + 1

    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates'

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    max_update_id = state.last_update_id

    for item in data.get('result', []):
        update_id = item.get('update_id')

        if update_id and update_id > max_update_id:
            max_update_id = update_id

        post = item.get('channel_post')

        if not post:
            continue

        message_id = post.get('message_id')
        text = post.get('text') or post.get('caption') or ''

        if not text:
            continue

        CompanyNews.objects.update_or_create(
            telegram_message_id=message_id,
            defaults={
                'text': text,
                'published_at': timezone.datetime.fromtimestamp(
                    post.get('date'),
                    tz=timezone.get_current_timezone()
                )
            }
        )

    if max_update_id > state.last_update_id:
        state.last_update_id = max_update_id
        state.save(update_fields=['last_update_id'])