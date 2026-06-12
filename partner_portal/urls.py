from django.urls import path
from . import views
from users.views import chat_send_file, chat_transcribe_voice
from .views import PartnerLoginView, dashboard, accruals, request_withdrawal, card_bin_lookup, bank_bin_lookup, partner_leads, partner_create_lead, partner_update_lead, partner_reports, partner_education, partner_materials, partner_chat, partner_chat_topic
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('dashboard/', views.dashboard, name='partner_dashboard'),
    path('login/',  PartnerLoginView.as_view(), name='partner_login'),
    path('referral-program/', views.referral_program, name='partner_referral_program'),
    path('referral-program/link/create/', views.create_partner_link, name='create_partner_link'),
    path('logout/', LogoutView.as_view(next_page='partner_login'), name='partner_logout'),
    path('accruals/', accruals, name='partner_accruals'),
    path('accruals/request-withdrawal/',   request_withdrawal,    name='request_withdrawal'),
    path('accruals/card-bin-lookup/', card_bin_lookup, name='card_bin_lookup'),
    path('accruals/bank-bin-lookup/', bank_bin_lookup, name='bank_bin_lookup'),
    path('news/ajax/', views.news_ajax, name='partner_news_ajax'),
    path('profile/', views.profile, name='partner_profile'),
    path('leads/', partner_leads, name='partner_leads'),
    path('leads/create/', partner_create_lead, name='partner_create_lead'),
    path('leads/<int:lead_id>/update/', partner_update_lead, name='partner_update_lead'),
    path('reports/', partner_reports, name='partner_reports'),
    path('partner/reports/export/word/', views.export_partner_reports_word, name='export_partner_reports_word'),
    path('partner/reports/export/pdf/', views.export_partner_reports_pdf,  name='export_partner_reports_pdf'),
    path('partner/reports/export/csv/',  views.export_partner_reports_csv, name='export_partner_reports_csv'),
    path('partner/education/',  views.partner_education, name='partner_education'),
    path('materials/', views.partner_materials, name='partner_materials'),
    path('chat/', views.partner_chat, name='partner_chat'),
    path('chat/<int:topic_id>/send-file/', chat_send_file,  name='partner_chat_send_file'),
    path('chat/<int:topic_id>/',  views.partner_chat_topic, name='partner_chat_topic'),
    path('chat/create-topic/', views.partner_chat_create_topic, name='partner_chat_create_topic'),
    path('chat/<int:topic_id>/send/', views.partner_chat_send_message, name='partner_chat_send_message'),
    path('chat/<int:topic_id>/voice/', views.partner_chat_send_voice, name='partner_chat_send_voice'),
    path('chat/<int:topic_id>/messages/', views.partner_chat_messages,  name='partner_chat_messages'),
    path('chat/<int:topic_id>/typing/', views.partner_chat_typing, name='partner_chat_typing'),
    path('chat/latest-unread-topic/', views.partner_chat_latest_unread_topic,  name='partner_chat_latest_unread_topic'),
    path('partner/chat/<int:topic_id>/admin-status/', views.partner_admin_status, name='partner_admin_status'),
    path('chat/<int:topic_id>/read-statuses/', views.chat_read_statuses, name='partner_chat_read_statuses'),
    path('chat/<int:topic_id>/mark-read/', views.partner_chat_mark_read, name='partner_chat_mark_read'),
    path('chat/<int:topic_id>/send-video-note/',  views.partner_chat_send_video_note, name='partner_chat_send_video_note'),   
    path('chat/<int:topic_id>/transcribe-voice/', chat_transcribe_voice, name='chat_transcribe_voice'),
    path('chat/<int:topic_id>/toggle-status/', views.partner_chat_toggle_topic_status, name='partner_chat_toggle_topic_status'),
    path('chat/topic-data/<int:topic_id>/', views.partner_chat_topic_data,  name='partner_chat_topic_data'),
]