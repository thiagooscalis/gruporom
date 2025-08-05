# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import WhatsAppTemplate, WhatsAppAccount
from django.db import models
from core.services.whatsapp_api import WhatsAppAPIService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza o status de todos os templates do WhatsApp com a API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--account',
            type=int,
            help='ID da conta específica para sincronizar (opcional)'
        )
        
        parser.add_argument(
            '--pending-only',
            action='store_true',
            help='Sincroniza apenas templates com status pending'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem fazer mudanças'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 Iniciando sincronização de status dos templates...')
        )
        
        # Filtra templates para sincronizar
        templates = WhatsAppTemplate.objects.select_related('account')
        
        if options['account']:
            templates = templates.filter(account_id=options['account'])
            self.stdout.write(f"📌 Sincronizando apenas conta ID: {options['account']}")
        
        if options['pending_only']:
            templates = templates.filter(status='pending')
            self.stdout.write("⏳ Sincronizando apenas templates pendentes")
        
        # Filtra apenas templates que foram submetidos (têm template_id ou nome)
        templates = templates.filter(
            models.Q(template_id__isnull=False) | 
            models.Q(name__isnull=False)
        ).exclude(name='')
        
        total_templates = templates.count()
        
        if total_templates == 0:
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhum template encontrado para sincronizar')
            )
            return
        
        self.stdout.write(f"📊 Total de templates para verificar: {total_templates}")
        
        updated_count = 0
        error_count = 0
        
        for template in templates:
            try:
                self.stdout.write(f"🔍 Verificando: {template.name} ({template.get_status_display()})")
                
                if options['dry_run']:
                    self.stdout.write(f"   [DRY RUN] Simulando verificação de {template.name}")
                    continue
                
                # Cria serviço da API
                api_service = WhatsAppAPIService(template.account)
                
                # Atualiza status
                result = api_service.update_template_status(template)
                
                if result['success']:
                    if result['updated']:
                        old_status = result.get('old_status', '')
                        new_status = result.get('new_status', '')
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"   ✅ Atualizado: {old_status} → {new_status}"
                            )
                        )
                        
                        if new_status == 'rejected':
                            reason = result.get('rejection_reason', '')
                            if reason:
                                self.stdout.write(f"      💬 Motivo: {reason}")
                        
                        updated_count += 1
                    else:
                        self.stdout.write("   ℹ️ Status inalterado")
                else:
                    error_msg = result.get('error', 'Erro desconhecido')
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ Erro: {error_msg}")
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   💥 Exceção: {str(e)}")
                )
                logger.error(f"Erro ao sincronizar template {template.id}: {e}")
                error_count += 1
        
        # Resumo final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📋 RESUMO DA SINCRONIZAÇÃO"))
        self.stdout.write(f"📊 Templates verificados: {total_templates}")
        self.stdout.write(
            self.style.SUCCESS(f"✅ Templates atualizados: {updated_count}")
        )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f"❌ Erros encontrados: {error_count}")
            )
        
        unchanged_count = total_templates - updated_count - error_count
        if unchanged_count > 0:
            self.stdout.write(f"📝 Templates inalterados: {unchanged_count}")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING("🧪 Modo DRY RUN - Nenhuma mudança foi feita")
            )
        
        self.stdout.write(
            self.style.SUCCESS(f"🏁 Sincronização concluída às {timezone.now()}")
        )