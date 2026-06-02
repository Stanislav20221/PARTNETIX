import random

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def generate_offer_id():
    return random.randint(1000000000, 9999999999)


class Offer(models.Model):
    PAYOUT_TYPE_CHOICES = (
        ('fixed', 'Фиксированная (₽)'),
        ('partner_status', 'По статусу партнера (%)'),
    )

    offer_id = models.BigIntegerField(
        unique=True,
        editable=False,
        verbose_name='ID оффера'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Название оффера'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание оффера'
    )
    payout_type = models.CharField(
        max_length=20,
        choices=PAYOUT_TYPE_CHOICES,
        default='fixed',
        verbose_name='Форма выплаты'
    )
    reward = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Вознаграждение'
    )
    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Сумма начислений'
    )
    activity_start = models.DateField(
        verbose_name='Начало активности оффера'
    )
    activity_end = models.DateField(
        verbose_name='Конец активности оффера'
    )
    landing_page = models.URLField(
        default='https://partnetix.ru',
        verbose_name='Посадочная страница'
    )
    current_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name='Текущий пользователь'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Оффер по умолчанию'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    stats_reset_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата сброса статистики'
    )

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'
        ordering = ['-created_at']

    def clean(self):
        if self.activity_end and self.activity_start and self.activity_end < self.activity_start:
            raise ValidationError('Дата окончания не может быть раньше даты начала.')

        if self.pk and not self.is_default:
            old_offer = Offer.objects.filter(pk=self.pk).first()

            if old_offer and old_offer.is_default:
                has_other_default = Offer.objects.filter(
                    current_user=self.current_user,
                    is_default=True
                ).exclude(pk=self.pk).exists()

                if not has_other_default:
                    raise ValidationError(
                        'Нельзя снять галочку: у пользователя должен быть один оффер по умолчанию.'
                    )


    def save(self, *args, **kwargs):
        if not self.offer_id:
            unique_id = generate_offer_id()
            while Offer.objects.filter(offer_id=unique_id).exists():
                unique_id = generate_offer_id()
            self.offer_id = unique_id

        if self.current_user_id:
            user_offers = Offer.objects.filter(current_user=self.current_user)

            if self.pk:
                user_offers = user_offers.exclude(pk=self.pk)

            if not user_offers.exists():
                self.is_default = True
            elif not user_offers.filter(is_default=True).exists():
                self.is_default = True

        super().save(*args, **kwargs)

        if self.is_default:
            Offer.objects.filter(
                current_user=self.current_user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

    @property
    def status(self):
        if not self.activity_start or not self.activity_end:
            return 'Неактивный'

        today = timezone.localdate()

        if self.activity_start <= today <= self.activity_end:
            return 'Активный'
        return 'Неактивный'

    @property
    def partner_link(self):
        if self.current_user and self.offer_id:
            return f'{settings.SITE_URL}/partners_register/?referral={self.current_user.user_id}&offer={self.offer_id}'
        return ''

    @property
    def promo_files_count(self):
        return self.promo_files.count()

    @property
    def clicks_count(self):
        visits = self.visits.all()

        if self.stats_reset_at:
            visits = visits.filter(created_at__gte=self.stats_reset_at)

        return visits.count()

    @property
    def registrations_count(self):
        registrations = self.partner_registrations.filter(is_approved=True)

        if self.stats_reset_at:
            registrations = registrations.filter(created_at__gte=self.stats_reset_at)

        return registrations.count()

    def __str__(self):
        return f'{self.offer_id} — {self.title}'


class OfferPromoMaterial(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='promo_files',
        verbose_name='Оффер'
    )
    file = models.FileField(
        upload_to='promo_materials/',
        verbose_name='Файл'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Загружено'
    )

    class Meta:
        verbose_name = 'Промоматериал'
        verbose_name_plural = 'Промоматериалы'
        ordering = ['uploaded_at']

    def __str__(self):
        return self.file.name.split('/')[-1]

    def clean(self):
        if self.offer_id and self.offer.promo_files.exclude(pk=self.pk).count() >= 10:
            raise ValidationError('Нельзя загрузить больше 10 файлов для одного оффера.')


class OfferVisit(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name='Оффер'
    )
    referral_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_visits',
        verbose_name='Кто пригласил'
    )
    visitor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visited_offers',
        verbose_name='Зарегистрированный пользователь'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP адрес'
    )
    is_registered = models.BooleanField(
        default=False,
        verbose_name='Регистрация завершена'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    partner_link = models.ForeignKey(
        'PartnerLink',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        verbose_name='Партнерская ссылка'
    )

    class Meta:
        verbose_name = 'Переход по офферу'
        verbose_name_plural = 'Переходы по офферам'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.offer.title} — {self.referral_user}'


class PartnerStatus(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Статус'
    )
    reward_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Вознаграждение (%)'
    )

    class Meta:
        verbose_name = 'Статус партнера'
        verbose_name_plural = 'Статусы партнеров'
        ordering = ['reward_percent']

    def __str__(self):
        return f'{self.name} — {self.reward_percent}%'


class PartnerLink(models.Model):
    title = models.CharField(
        max_length=255,
        default='Моя новая ссылка',
        verbose_name='Название'
    )
    url = models.URLField(
        unique=True,
        verbose_name='Ссылка'
    )
    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partner_links',
        verbose_name='Партнер'
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='partner_links',
        verbose_name='Оффер'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.partner}'


class PartnerRegistration(models.Model):
    PARTNER_TYPE_CHOICES = (
        ('individual', 'Физическое лицо'),
        ('company', 'Юридическое лицо'),
        ('self_employed', 'Самозанятый'),
    )

    partner_type = models.CharField(
        max_length=20,
        choices=PARTNER_TYPE_CHOICES,
        verbose_name='Тип партнера'
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='ФИО'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=30,
        verbose_name='Телефон'
    )
    activity_type = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Вид деятельности'
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Название компании'
    )
    company_full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Полное название организации'
    )
    company_short_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Сокращенное название организации'
    )
    postal_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Почтовый адрес'
    )
    legal_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Юридический адрес'
    )
    inn = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='ИНН'
    )
    kpp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='КПП'
    )
    contact_person_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='ФИО контактного лица'
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_registrations',
        verbose_name='Оффер'
    )
    referral_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_registrations',
        verbose_name='Пользователь по ссылке'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_registration',
        verbose_name='Созданный пользователь'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Подтвержден'
    )
    is_active_partner = models.BooleanField(
    default=True,
    verbose_name='Активный партнер'
    )
    status = models.ForeignKey(
        PartnerStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partners',
        verbose_name='Статус партнера'
    )
    leads_count = models.PositiveIntegerField(
    default=0,
    verbose_name='Количество лидов'
  )

    reward_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Сумма вознаграждения'
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Баланс'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Оффер по умолчанию'
    )
    partner_link = models.ForeignKey(
        'PartnerLink',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registrations'
    )
    class Meta:
        verbose_name = 'Регистрация партнера'
        verbose_name_plural = 'Регистрации партнеров'
        ordering = ['-created_at']
 
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.user:
            if self.is_approved:
                self.user.role = 'partner'
                self.user.is_active = True
                self.user.save(update_fields=['role', 'is_active'])

            elif not self.is_approved:
                self.user.is_active = False
                self.user.save(update_fields=['is_active'])

        if self.is_approved and self.user and self.offer:
            existing_link = PartnerLink.objects.filter(
                partner=self.user,
                offer=self.offer
            ).first()

            if not existing_link:
                link_code = str(random.randint(1000000000, 9999999999))

                while PartnerLink.objects.filter(url__contains=f'link={link_code}').exists():
                    link_code = str(random.randint(1000000000, 9999999999))

                partner_url = (
                    f'{settings.SITE_URL}/users/client/register/'
                    f'?referral={self.user.user_id}'
                    f'&offer={self.offer.offer_id}'
                    f'&link={link_code}'
                )
                PartnerLink.objects.create(
                    partner=self.user,
                    offer=self.offer,
                    title='Моя новая ссылка',
                    url=partner_url,
                )
    def __str__(self):
            return f'{self.get_partner_type_display()} — {self.email}'

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый лид'),
        ('in_progress', 'В работе'),
        ('cancelled', 'Отменен'),
        ('deal', 'Сделка'),
    )

    title = models.CharField(
        max_length=255,
        default='Новый лид',
        verbose_name='Название лида'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    deal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Сумма сделки'
    )

    partner_reward = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Вознаграждение партнера'
    )

    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name='Партнер'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус лида'
    )

    offer = models.ForeignKey(
        Offer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Оффер'
    )
    tariff = models.ForeignKey(
        'Tariff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Тарифный план'
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_leads',
        verbose_name='Администратор'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linkleads',
        verbose_name='Клиент'
    )
    partner_link = models.ForeignKey(
        'PartnerLink',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    class Meta:
        verbose_name = 'Лид'
        verbose_name_plural = 'Лиды'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Tariff(models.Model):
    PERIOD_CHOICES = (
        ('monthly', 'Месячный тариф'),
        ('yearly', 'Годовой тариф'),
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Название тарифа'
    )

    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        verbose_name='Период'
    )

    leads_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Лимит лидов'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость'
    )

    trial_days = models.PositiveIntegerField(
        default=0,
        verbose_name='Бесплатный период, дней'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ['period', 'price']

    def __str__(self):
        limit = 'без ограничений' if self.leads_limit is None else f'до {self.leads_limit} лидов'
        return f'{self.get_period_display()} — {self.name} ({limit})'
