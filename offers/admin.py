from django.contrib import admin
from django.utils.html import format_html
from .models import Offer, PartnerStatus, PartnerRegistration, PartnerLink, Lead, Tariff
from django.utils import timezone
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'offer_id',
        'title',
        'payout_type',
        'reward',
        'activity_start',
        'activity_end',
        'get_user_id',
        'status_display',
        'is_default',
        'partner_link_display',
    )
    
    search_fields = ('offer_id', 'title')
    list_filter = ('payout_type', 'activity_start', 'activity_end')
    readonly_fields = (
        'offer_id',
        'created_at',
        'stats_reset_at',
        'status_display',
        'partner_link_display',
    )
    actions = ['reset_stats_for_selected_offers']

    def get_user_id(self, obj):
        if obj.current_user:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/users/user/{obj.current_user.id}/change/',
                obj.current_user.user_id
            )
        return '-'

    get_user_id.short_description = 'ID пользователя'

    def status_display(self, obj):
        if obj.status == 'Активный':
            return format_html(
                '<span style="color: {};">● {}</span>',
                'green',
                'Активный'
            )
        return format_html(
            '<span style="color: {};">● {}</span>',
            'red',
            'Неактивный'
        )

    status_display.short_description = 'Активность'

    def partner_link_display(self, obj):
        if obj.partner_link:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.partner_link,
                obj.partner_link
            )
        return '-'

    partner_link_display.short_description = 'Партнерская ссылка'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'current_user':
            field.label_from_instance = lambda obj: f'{obj.user_id} — {obj.username}'

        return field
    def save_model(self, request, obj, form, change):
        # если админ поставил галочку
        make_default = form.cleaned_data.get('is_default')

        if make_default:
            Offer.objects.filter(
                current_user=obj.current_user,
                is_default=True
            ).exclude(pk=obj.pk).update(is_default=False)

            obj.is_default = True

        super().save_model(request, obj, form, change)

    @admin.action(description='Сбросить статистику по выбранным офферам')
    def reset_stats_for_selected_offers(self, request, queryset):
        reset_time = timezone.now()
        updated_count = queryset.update(stats_reset_at=reset_time)

        self.message_user(
            request,
            f'Статистика сброшена у офферов: {updated_count}'
        )
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if not request.user.is_superuser:
            readonly.append('is_default')

        return readonly    

@admin.register(PartnerStatus)
class PartnerStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'reward_percent')
    search_fields = ('name',)


@admin.register(PartnerRegistration)
class PartnerRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'partner_type',
        'status',
        'offer',
        'referral_user',
        'user',
        'is_approved',
        'leads_count',
        'reward_display',
        'balance_display',
        'is_active_partner',
        'is_default',
        'created_at',
    )
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []

        return [
            'partner_type',
            'full_name',
            'email',
            'phone',
            'activity_type',
            'company_name',
            'company_full_name',
            'company_short_name',
            'postal_address',
            'legal_address',
            'inn',
            'kpp',
            'contact_person_name',
            'offer',
            'referral_user',
            'user',
            'status',
            'leads_count',
            'reward_amount',
            'balance',
            'created_at',
        ]
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(referral_user=request.user)


    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return obj.referral_user == request.user

    def has_add_permission(self, request):
        return request.user.is_superuser


    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    def active_display(self, obj):
            if obj.is_active_partner:
                return format_html('<span style="color: green;">● Активный</span>')
            return format_html('<span style="color: red;">● Неактивный</span>')
    active_display.short_description = 'Активность'

    def reward_display(self, obj):
            return f"{int(obj.reward_amount):,}".replace(',', ' ')

    reward_display.short_description = 'Вознаграждение'

    def balance_display(self, obj):
        return f"{int(obj.balance):,}".replace(',', ' ')

    balance_display.short_description = 'Баланс'
        
    list_filter = ('partner_type', 'status', 'is_approved', 'created_at')
    search_fields = (
        'email',
        'phone',
        'full_name',
        'company_name',
        'company_full_name',
        'company_short_name',
        'inn',
        'kpp',
    )
    actions = ['approve_selected_registrations', 'reject_selected_registrations']

    @admin.action(description='Подтвердить выбранные заявки')
    def approve_selected_registrations(self, request, queryset):
        approved_count = 0

        for registration in queryset:
            registration.is_approved = True
            registration.save()
            approved_count += 1

        self.message_user(
            request,
            f'Подтверждено заявок: {approved_count}'
        )

    @admin.action(description='Снять подтверждение у выбранных заявок')
    def reject_selected_registrations(self, request, queryset):
        rejected_count = 0

        for registration in queryset:
            registration.is_approved = False
            registration.save()
            rejected_count += 1

        self.message_user(
            request,
            f'Снято подтверждение у заявок: {rejected_count}'
        )
@admin.register(PartnerLink)
class PartnerLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'partner', 'offer', 'url', 'created_at')
    search_fields = ('title', 'url', 'partner__username', 'partner__email', 'offer__title')
    list_filter = ('created_at',)    
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_at',
        'deal_amount',
        'partner_reward',
        'partner',
        'status',
        'offer',
        'admin',
    )

    list_filter = (
        'status',
        'created_at',
        'offer',
        'admin',
    )

    search_fields = (
        'title',
        'partner__username',
        'partner__email',
        'offer__title',
        'admin__username',
        'admin__email',
    )

    readonly_fields = (
        'created_at',
    )    

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'period',
        'leads_limit',
        'price',
        'trial_days',
        'is_active',
    )

    list_filter = (
        'period',
        'is_active',
    )

    search_fields = (
        'name',
    )