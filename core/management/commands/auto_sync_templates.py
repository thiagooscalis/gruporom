# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta
from core.models import WhatsAppTemplate
from core.services.whatsapp_api import WhatsAppAPIService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincronização automática de templates pendentes (para uso em cron/scheduler)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=168,  # 7 dias
            help='Sincroniza apenas templates criados/atualizados nas últimas N horas (padrão: 168 = 7 dias)'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Número máximo de templates para processar por execução (padrão: 10)'
        )
    
    def handle(self, *args, **options):
        max_age_hours = options['max_age_hours']
        batch_size = options['batch_size']
        
        # Calcula data limite
        cutoff_date = timezone.now() - timedelta(hours=max_age_hours)
        
        # Busca templates que precisam ser sincronizados
        templates = WhatsAppTemplate.objects.select_related('account').filter(
            models.Q(status='pending') | 
            models.Q(status='rejected'),  # Rejeitados podem ser reaprovados
            atualizado_em__gte=cutoff_date
        ).filter(
            # Apenas templates que foram submetidos
            models.Q(template_id__isnull=False) | 
            models.Q(name__isnull=False)
        ).exclude(
            name=''
        ).order_by('-atualizado_em')[:batch_size]
        
        total = templates.count()
        
        if total == 0:
            logger.info("Auto-sync: Nenhum template pendente para sincronizar")
            return
        
        logger.info(f"Auto-sync: Iniciando sincronização de {total} templates")
        
        updated_count = 0
        error_count = 0
        
        for template in templates:
            try:
                api_service = WhatsAppAPIService(template.account)
                result = api_service.update_template_status(template)
                
                if result['success'] and result['updated']:
                    old_status = result.get('old_status', '')
                    new_status = result.get('new_status', '')
                    
                    logger.info(
                        f"Auto-sync: Template {template.name} atualizado: {old_status} → {new_status}"
                    )
                    updated_count += 1
                    
                    # Log especial para aprovações/rejeições
                    if new_status == 'approved':
                        logger.info(f"✅ Template APROVADO: {template.name}")
                    elif new_status == 'rejected':
                        reason = result.get('rejection_reason', '')
                        logger.warning(f"❌ Template REJEITADO: {template.name} - {reason}")
                
            except Exception as e:
                logger.error(f"Auto-sync: Erro ao processar template {template.name}: {e}")
                error_count += 1
        
        # Log do resumo
        if updated_count > 0 or error_count > 0:
            logger.info(
                f"Auto-sync finalizado: {updated_count} atualizados, {error_count} erros"
            )