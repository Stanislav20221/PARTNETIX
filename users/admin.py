from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Accrual, Subscription, WithdrawalRequest, BankBin, PartnerPaymentDetails, EducationVideo, EducationDocument, MarketingMaterial, ChatTopic, ChatMessage 

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': (
                'role',
                'payment_status',
                'balance',
                'referral_code',
                'referred_by',
                'phone',
                'company',
            )
        }),
    )

    list_display = (
        'id',
        'username',
        'email',
        'role',
        'payment_status',
        'balance',
        'is_staff'
    )
@admin.register(Accrual)
class AccrualAdmin(admin.ModelAdmin):
    list_display = (
        'accrual_id',
        'amount',
        'lead',
        'partner',
        'offer',
        'admin',
        'created_at',
    )

    search_fields = (
        'accrual_id',
        'lead__title',
        'partner__email',
        'offer__title',
    )

    list_filter = (
        'created_at',
        'offer',
    )

    readonly_fields = (
        'accrual_id',
        'created_at',
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tariff', 'status', 'started_at', 'expires_at')
    list_filter = ('status', 'tariff')
    search_fields = ('user__email', 'user__username')

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('partner', 'admin', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('partner__email', 'partner__username', 'admin__email')    

@admin.register(BankBin)
class BankBinAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'bin_prefix', 'is_active')
    list_filter = ('is_active', 'bank_name')
    search_fields = ('bank_name', 'bin_prefix')

@admin.register(PartnerPaymentDetails)
class PartnerPaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('partner', 'bank_name', 'payment_system', 'card_mask', 'recipient_name', 'updated_at')
    search_fields = ('partner__email', 'partner__username', 'bank_name', 'card_mask')    
admin.site.register(EducationVideo)
admin.site.register(EducationDocument)    

@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer', 'material_type', 'created_at')
    list_filter = ('offer', 'material_type', 'created_at')
    search_fields = ('title', 'description', 'text_content', 'offer__title')

@admin.register(ChatTopic)
class ChatTopicAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'partner',
        'admin',
        'status',
        'priority',
        'category',
        'updated_at',
    )

    list_filter = (
        'status',
        'priority',
        'category',
        'created_at',
    )

    search_fields = (
        'title',
        'partner__email',
        'partner__first_name',
        'partner__last_name',
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'topic',
        'sender',
        'is_read',
        'created_at',
    )

    list_filter = (
        'is_read',
        'created_at',
    )

    search_fields = (
        'topic__title',
        'sender__email',
        'text',
    )    