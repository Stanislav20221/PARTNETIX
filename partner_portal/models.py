from django.db import models

# Create your models here.
class CompanyNews(models.Model):
    telegram_message_id = models.BigIntegerField(unique=True)
    text = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.text[:80]
    
class TelegramMessage(models.Model):
    telegram_user_id = models.BigIntegerField(
        verbose_name='Telegram ID'
    )

    username = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Username'
    )

    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя'
    )

    text = models.TextField(
        verbose_name='Сообщение'
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата сообщения'
    )

    class Meta:
        verbose_name = 'Сообщение Telegram'
        verbose_name_plural = 'Сообщения Telegram'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name or self.username}: {self.text[:40]}'    
class TelegramSyncState(models.Model):
    key = models.CharField(max_length=50, unique=True)
    last_update_id = models.BigIntegerField(default=0)