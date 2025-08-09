# -*- coding: utf-8 -*-
from django.urls import path
from core.views.administracao import whatsapp as views

app_name = 'whatsapp'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Contas
    path('accounts/', views.accounts_list, name='accounts_list'),
    
    # API
    
    
    # Listas
    path('contacts/<int:account_id>/', views.contacts_list, name='contacts_list'),
    path('messages/', views.messages_list, name='messages_list'),
    
    # Modals CRUD
    path('account/create/', views.account_create_modal, name='account_create_modal'),
    path('account/<int:account_id>/edit/', views.account_edit_modal, name='account_edit_modal'),
    path('account/<int:account_id>/delete/', views.account_delete_modal, name='account_delete_modal'),
    path('account/<int:account_id>/test/', views.account_test_modal, name='account_test_modal'),
    
    # Debug
    path('account/<int:account_id>/debug/', views.webhook_debug, name='webhook_debug'),
    path('account/<int:account_id>/test-webhook/', views.test_webhook, name='test_webhook'),
    
    # Templates
    path('account/<int:account_id>/templates/', views.templates_list, name='templates_list'),
    path('template/create/', views.template_create_modal, name='template_create_modal'),
    path('template/<int:template_id>/edit/', views.template_edit_modal, name='template_edit_modal'),
    path('template/<int:template_id>/delete/', views.template_delete_modal, name='template_delete_modal'),
    path('template/<int:template_id>/preview/', views.template_preview_modal, name='template_preview_modal'),
    path('template/<int:template_id>/submit-approval/', views.template_submit_approval, name='template_submit_approval'),
    path('template/<int:template_id>/check-status/', views.template_check_status, name='template_check_status'),
    
    # API Debug
    path('account/<int:account_id>/api-test/', views.api_permissions_test, name='api_permissions_test'),
    
    # Envio em Massa
    path('account/<int:account_id>/bulk-send/', views.bulk_send_modal, name='bulk_send_modal'),
    path('account/<int:account_id>/bulk-send/process/', views.bulk_send_process, name='bulk_send_process'),
    path('bulk-send/load-recipients/', views.load_recipients, name='load_recipients'),
    path('bulk-send/filter-recipients/', views.filter_recipients, name='filter_recipients'),
    path('bulk-send/template-preview/', views.template_preview, name='template_preview'),
    path('bulk-send/update-count/', views.update_count, name='update_count'),
    path('bulk-send/select-all/', views.select_all_recipients, name='select_all_recipients'),
    path('bulk-send/clear-selection/', views.clear_selection, name='clear_selection'),
    path('bulk-send/count-selected/', views.count_selected, name='count_selected'),
    path('bulk-send/update-preview/', views.update_preview, name='update_preview'),
]