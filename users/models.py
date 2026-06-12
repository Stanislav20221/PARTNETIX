from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import random
from django.utils import timezone
from datetime import timedelta
from offers.models import Tariff, Offer
import os

def generate_user_id():
    return random.randint(1000000000, 9999999999)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('partner', 'Партнер'),
        ('admin', 'Администратор'),
    )

    PAYMENT_CHOICES = (
        ('no', 'Нет'),
        ('yes', 'Да'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='no')

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=100, unique=True, null=True, blank=True)

    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    user_id = models.BigIntegerField(
        unique=True,
        null=True,
        editable=False,
        verbose_name='ID пользователя'        
    )
    chat_online = models.BooleanField(
        default=False,
        verbose_name='Онлайн в чате'
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Последняя активность'
    )
    typing_updated_at = models.DateTimeField(
        null=True,
        blank=True
    )
    @property
    def is_online(self):

        if not self.last_activity:
            return False

        return self.last_activity >= timezone.now() - timedelta(minutes=2)
    @property
    def last_seen_text(self):
        if self.is_online:
            return 'online'

        if not self.last_activity:
            return 'offline'

        now = timezone.now()
        diff = now - self.last_activity

        minutes = int(diff.total_seconds() // 60)

        if minutes < 1:
            return 'только что'

        if minutes < 60:
            return f'был в сети {minutes} мин. назад'

        hours = minutes // 60

        if hours < 24:
            return f'был в сети {hours} ч. назад'

        days = hours // 24

        return f'был в сети {days} дн. назад'
    @property
    def is_typing(self):

        if not self.typing_updated_at:
            return False

        return timezone.now() - self.typing_updated_at < timedelta(seconds=15)
    def save(self, *args, **kwargs):
        if not self.user_id:
            unique_id = generate_user_id()
            while User.objects.filter(user_id=unique_id).exists():
                unique_id = generate_user_id()
            self.user_id = unique_id

        if self.payment_status == 'yes':
            self.role = 'admin'
        elif self.role != 'partner':
            self.role = 'client'

        super().save(*args, **kwargs)

    def __str__(self):
        if self.first_name:
            return f'{self.first_name} ({self.email})'
        return self.email
def generate_accrual_id():
    while True:
        value = str(random.randint(1000000000, 9999999999))
        if not Accrual.objects.filter(accrual_id=value).exists():
            return value


class Accrual(models.Model):
    accrual_id = models.CharField(
        max_length=10,
        unique=True,
        default=generate_accrual_id,
        editable=False,
        verbose_name='ID начисления'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Сумма'
    )

    lead = models.ForeignKey(
        'offers.Lead',
        on_delete=models.CASCADE,
        related_name='accruals',
        verbose_name='Лид'
    )

    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partner_accruals',
        verbose_name='Партнер'
    )

    offer = models.ForeignKey(
        'offers.Offer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accruals',
        verbose_name='Оффер'
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_accruals',
        verbose_name='Администратор'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата начисления'
    )
    PAYOUT_STATUS_CHOICES = (
        ('available', 'Доступно к выплате'),
        ('requested', 'Запрошено'),
        ('paid', 'Выплачено'),
    )

    payout_status = models.CharField(
        max_length=20,
        choices=PAYOUT_STATUS_CHOICES,
        default='available',
        verbose_name='Статус выплаты'
    )
    class Meta:
        verbose_name = 'Начисление'
        verbose_name_plural = 'Начисления'
        ordering = ['-created_at']

    def __str__(self):
        return f'Начисление #{self.accrual_id}'    



class Subscription(models.Model):
    STATUS_CHOICES = (
        ('trial', 'Пробный период'),
        ('active', 'Активна'),
        ('expired', 'Истекла'),
        ('cancelled', 'Отменена'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Пользователь'
    )

    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions',
        verbose_name='Тариф'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial',
        verbose_name='Статус'
    )

    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата начала'
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата окончания'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} — {self.tariff}'    

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('processing', 'В обработке'),
        ('paid', 'Выплачено'),
        ('rejected', 'Отклонено'),
    )

    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='withdrawal_requests',
        verbose_name='Партнер'
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_withdrawal_requests',
        verbose_name='Администратор'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма заявки'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана'
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Обработана'
    )
    accruals = models.ManyToManyField(
        Accrual,
        related_name='withdrawal_requests',
        blank=True,
        verbose_name='Начисления'
    )
    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Получатель'
    )

    card_mask = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Маска карты'
    )

    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Последние 4 цифры'
    )
    encrypted_card_number = models.TextField(
        blank=True,
        verbose_name='Зашифрованный номер карты'
    )
    bank_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Банк'
    )

    payment_system = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Платежная система'
    )
    card_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Тип карты'
    )

    card_country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Страна карты'
    )
    settlement_account = models.CharField(
    max_length=20,
    blank=True,
    verbose_name='Расчётный счёт'
    )

    bik = models.CharField(
        max_length=9,
        blank=True,
        verbose_name='БИК'
    )

    correspondent_account = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Корреспондентский счёт'
    )


    legal_bank_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Полное название банка'
    )
    bank_inn = models.CharField(
    max_length=10,
    blank=True,
    verbose_name='ИНН банка'
    )

    bank_kpp = models.CharField(
        max_length=9,
        blank=True,
        verbose_name='КПП банка'
    )
    class Meta:
        verbose_name = 'Заявка на выплату'
        verbose_name_plural = 'Заявки на выплату'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.partner} — {self.amount} ₽'
    
class BankBin(models.Model):
    bank_name = models.CharField(
        max_length=255,
        verbose_name='Банк'
    )

    bin_prefix = models.CharField(
        max_length=8,
        unique=True,
        verbose_name='Первые цифры карты'
    )

    logo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Путь к логотипу'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'BIN банка'
        verbose_name_plural = 'BIN банков'
        ordering = ['bank_name', 'bin_prefix']

    def __str__(self):
        return f'{self.bank_name} — {self.bin_prefix}'    
    
class PartnerPaymentDetails(models.Model):
    partner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_details',
        verbose_name='Партнёр'
    )

    encrypted_card_number = models.TextField(
        blank=True,
        verbose_name='Зашифрованный номер карты'
    )

    card_mask = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Маска карты'
    )

    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Последние 4 цифры'
    )

    bank_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Банк'
    )

    payment_system = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Платёжная система'
    )

    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Получатель'
    )

    card_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Тип карты'
    )

    card_country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Страна карты'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    settlement_account = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Расчётный счёт'
    )

    bik = models.CharField(
        max_length=9,
        blank=True,
        verbose_name='БИК'
    )

    correspondent_account = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Корреспондентский счёт'
    )


    legal_bank_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Полное название банка'
    )
    bank_inn = models.CharField(
    max_length=10,
    blank=True,
    verbose_name='ИНН банка'
    )

    bank_kpp = models.CharField(
        max_length=9,
        blank=True,
        verbose_name='КПП банка'
    )
    class Meta:
        verbose_name = 'Платёжные реквизиты партнёра'
        verbose_name_plural = 'Платёжные реквизиты партнёров'

    def __str__(self):
        return f'{self.partner} — {self.card_mask}'

#---------------------------------------Обучение----------------------------------------------------------------

class EducationDocument(models.Model):
    title = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )

    document_file = models.FileField(
        upload_to='education/documents/'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def file_extension(self):
        return os.path.splitext(
            self.document_file.name
        )[1].replace('.', '').upper()

    def __str__(self):
        return self.title
    
class EducationVideo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(
    blank=True,
    null=True
    )
    duration = models.CharField(max_length=100)

    video_file = models.FileField(
        upload_to='education/videos/'
    )

    preview_image = models.ImageField(
        upload_to='education/previews/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)    

#---------------------------------------Материалы-------------------------------------------------------------------
class MarketingMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('video', 'Видео'),
        ('image', 'Изображение'),
        ('text', 'Текстовый материал'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPE_CHOICES,
        verbose_name='Тип материала'
    )

    file = models.FileField(
        upload_to='marketing_materials/',
        blank=True,
        null=True,
        verbose_name='Файл'
    )

    text_content = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текстовый материал'
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='marketing_materials',
        verbose_name='Оффер'
    )
 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ''    
    
class ChatTopic(models.Model):
    STATUS_CHOICES = (
        ('open', 'Открыта'),
        ('closed', 'Закрыта'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Низкий'),
        ('normal', 'Обычный'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    )

    CATEGORY_CHOICES = (
        ('payments', 'Выплаты'),
        ('technical', 'Техническая проблема'),
        ('referral', 'Реферальная программа'),
        ('offers', 'Офферы'),
        ('leads', 'Лиды'),
        ('tariffs', 'Тарифы'),
        ('other', 'Другое'),
    )

    title = models.CharField(
        max_length=255,
        verbose_name='Тема'
    )

    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partner_chat_topics',
        verbose_name='Партнёр'
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_chat_topics',
        verbose_name='Администратор'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_chat_topics',
        verbose_name='Кто создал тему'
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name='Статус'
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name='Приоритет'
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Категория'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлена'
    )

    class Meta:
        verbose_name = 'Тема чата'
        verbose_name_plural = 'Темы чата'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    topic = models.ForeignKey(
        ChatTopic,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Тема'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Отправитель'
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
        verbose_name='Создано'
    )
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Текст'),
        ('voice', 'Голосовое'),
        ('image', 'Изображение'),
        ('file', 'Файл'),
        ('video_note', 'Видеокружок'),
    ]

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
        verbose_name='Тип сообщения',        
    )

    audio_file = models.FileField(
        upload_to='chat/audio/',
        null=True,
        blank=True,
        verbose_name='Аудиофайл'
    )
    video_note = models.FileField(
        upload_to='chat/video_notes/',
        blank=True,
        null=True
    )
    image_file = models.ImageField(
        upload_to='chat/images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    file = models.FileField(
        upload_to='chat/files/',
        blank=True,
        null=True,
        verbose_name='Файл'
    )
    @property
    def file_extension(self):
        if not self.file:
            return ''

        return os.path.splitext(self.file.name)[1].lower()
    @property
    def is_image(self):
        return self.file_extension in [
            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
            '.gif'
        ]
    @property
    def is_video(self):
        return self.file_extension in [
            '.mp4',
            '.webm',
            '.mov'
        ]
    @property
    def file_name(self):
        if not self.file:
            return ''

        return os.path.basename(self.file.name)
    
    @property
    def is_media(self):
        return (
            self.message_type in ['image', 'voice', 'video_note']
            or self.is_image
            or self.is_video
        ) 
    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} — {self.created_at}'