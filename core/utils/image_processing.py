# -*- coding: utf-8 -*-
"""
Utilities para processamento de imagens
"""
import io
import os
from PIL import Image
from django.core.files.base import ContentFile


def crop_to_square(image_file, quality=85, max_size=800):
    """
    Recorta uma imagem para formato quadrado a partir do centro.
    O limite será a altura ou largura, o que terminar primeiro.
    
    Args:
        image_file: Arquivo de imagem (InMemoryUploadedFile ou similar)
        quality: Qualidade do JPEG final (1-100)
        max_size: Tamanho máximo da imagem final (largura/altura em pixels)
        
    Returns:
        ContentFile: Arquivo da imagem processada
    """
    try:
        # Abrir a imagem original
        original_image = Image.open(image_file)
        
        # Converter para RGB se necessário (para PNG com transparência, etc.)
        if original_image.mode in ('RGBA', 'LA', 'P'):
            # Criar fundo branco
            background = Image.new('RGB', original_image.size, (255, 255, 255))
            if original_image.mode == 'P':
                original_image = original_image.convert('RGBA')
            background.paste(original_image, mask=original_image.split()[-1] if original_image.mode in ('RGBA', 'LA') else None)
            original_image = background
        elif original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        # Obter dimensões originais
        width, height = original_image.size
        
        # Determinar o tamanho do quadrado (menor dimensão)
        square_size = min(width, height)
        
        # Calcular posição para recorte central
        left = (width - square_size) // 2
        top = (height - square_size) // 2
        right = left + square_size
        bottom = top + square_size
        
        # Fazer o recorte quadrado
        cropped_image = original_image.crop((left, top, right, bottom))
        
        # Redimensionar se necessário (mantendo qualidade)
        if square_size > max_size:
            cropped_image = cropped_image.resize((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Salvar em memória como JPEG
        output_buffer = io.BytesIO()
        cropped_image.save(
            output_buffer, 
            format='JPEG', 
            quality=quality, 
            optimize=True,
            progressive=True
        )
        output_buffer.seek(0)
        
        # Gerar nome do arquivo
        original_name = getattr(image_file, 'name', 'foto.jpg')
        name_without_ext = os.path.splitext(original_name)[0]
        final_name = f"{name_without_ext}_square.jpg"
        
        # Retornar ContentFile
        return ContentFile(
            output_buffer.getvalue(),
            name=final_name
        )
        
    except Exception as e:
        # Log do erro (em produção, usar logging adequado)
        print(f"Erro ao processar imagem: {str(e)}")
        raise ValueError(f"Erro ao processar imagem: {str(e)}")


def needs_processing(image_file, max_size=800):
    """
    Verifica se uma imagem precisa de processamento (recorte ou otimização).
    
    Args:
        image_file: Arquivo de imagem
        max_size: Tamanho máximo permitido
        
    Returns:
        dict: {
            'needs_crop': bool,
            'needs_resize': bool, 
            'needs_format_conversion': bool,
            'is_square': bool,
            'width': int,
            'height': int,
            'format': str
        }
    """
    try:
        image = Image.open(image_file)
        width, height = image.size
        
        is_square = width == height
        needs_resize = max(width, height) > max_size
        needs_format_conversion = image.mode not in ('RGB', 'L') or image.format != 'JPEG'
        needs_crop = not is_square
        
        # Reset file pointer
        image_file.seek(0)
        
        return {
            'needs_crop': needs_crop,
            'needs_resize': needs_resize,
            'needs_format_conversion': needs_format_conversion,
            'is_square': is_square,
            'width': width,
            'height': height,
            'format': image.format,
            'needs_any_processing': needs_crop or needs_resize or needs_format_conversion
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'needs_any_processing': True  # Por segurança, assume que precisa
        }


def get_image_info(image_file):
    """
    Obtém informações básicas de uma imagem.
    
    Args:
        image_file: Arquivo de imagem
        
    Returns:
        dict: Informações da imagem (width, height, format, size)
    """
    try:
        image = Image.open(image_file)
        return {
            'width': image.size[0],
            'height': image.size[1],
            'format': image.format,
            'mode': image.mode,
            'size_bytes': getattr(image_file, 'size', 0)
        }
    except Exception as e:
        return {
            'error': str(e)
        }


def is_valid_image(image_file, max_size_mb=5, allowed_formats=None):
    """
    Valida se um arquivo é uma imagem válida.
    
    Args:
        image_file: Arquivo a ser validado
        max_size_mb: Tamanho máximo em MB
        allowed_formats: Lista de formatos permitidos (ex: ['JPEG', 'PNG'])
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if allowed_formats is None:
        allowed_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
    
    try:
        # Verificar tamanho do arquivo
        if hasattr(image_file, 'size') and image_file.size > max_size_mb * 1024 * 1024:
            return False, f"Arquivo muito grande. Máximo: {max_size_mb}MB"
        
        # Verificar se é uma imagem válida
        image = Image.open(image_file)
        
        # Verificar formato
        if image.format not in allowed_formats:
            return False, f"Formato não suportado. Formatos aceitos: {', '.join(allowed_formats)}"
        
        # Verificar dimensões mínimas (200px conforme solicitado)
        width, height = image.size
        if width < 200 or height < 200:
            return False, "Imagem muito pequena. Mínimo: 200x200 pixels"
        
        # Verificar dimensões máximas (opcional)
        if width > 10000 or height > 10000:
            return False, "Imagem muito grande. Máximo: 10000x10000 pixels"
        
        return True, None
        
    except Exception as e:
        return False, f"Arquivo não é uma imagem válida: {str(e)}"