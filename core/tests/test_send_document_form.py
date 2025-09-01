# -*- coding: utf-8 -*-
import pytest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from core.forms.whatsapp import SendDocumentForm


class SendDocumentFormTest(TestCase):
    """Testes para o formulário SendDocumentForm"""

    def setUp(self):
        """Setup comum para os testes"""
        # Conteúdo PDF válido minimal
        self.pdf_content = b'''%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 24 Tf
100 700 Td
(Teste PDF) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
0000000185 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
279
%%EOF'''

    def test_valid_pdf_with_caption(self):
        """Testa formulário com PDF válido e legenda"""
        pdf_file = SimpleUploadedFile("test.pdf", self.pdf_content, content_type="application/pdf")
        form_data = {'caption': 'Documento de teste'}
        files_data = {'document': pdf_file}

        form = SendDocumentForm(form_data, files_data)
        
        self.assertTrue(form.is_valid(), f"Formulário deveria ser válido. Erros: {form.errors}")
        self.assertEqual(form.cleaned_data['caption'], 'Documento de teste')
        self.assertEqual(form.cleaned_data['document'].name, 'test.pdf')
        self.assertEqual(len(form.cleaned_data['document'].read()), len(self.pdf_content))

    def test_valid_pdf_without_caption(self):
        """Testa formulário com PDF válido sem legenda"""
        pdf_file = SimpleUploadedFile("test.pdf", self.pdf_content, content_type="application/pdf")
        files_data = {'document': pdf_file}

        form = SendDocumentForm({}, files_data)
        
        self.assertTrue(form.is_valid(), f"Formulário deveria ser válido. Erros: {form.errors}")
        self.assertEqual(form.cleaned_data['caption'], '')

    def test_invalid_file_extension(self):
        """Testa arquivo com extensão inválida (.txt)"""
        txt_file = SimpleUploadedFile("test.txt", b"Text content", content_type="text/plain")
        files_data = {'document': txt_file}

        form = SendDocumentForm({}, files_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('document', form.errors)
        self.assertIn('Apenas arquivos PDF são permitidos', str(form.errors['document']))

    def test_invalid_pdf_magic_number(self):
        """Testa arquivo .pdf com conteúdo inválido (sem magic number %PDF)"""
        fake_pdf = SimpleUploadedFile("fake.pdf", b"Not a real PDF file", content_type="application/pdf")
        files_data = {'document': fake_pdf}

        form = SendDocumentForm({}, files_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('document', form.errors)
        self.assertIn('Arquivo não é um PDF válido', str(form.errors['document']))

    def test_oversized_file(self):
        """Testa arquivo maior que 16MB"""
        # Cria conteúdo PDF válido mas muito grande (17MB)
        big_content = self.pdf_content + b'X' * (17 * 1024 * 1024)
        big_file = SimpleUploadedFile("big.pdf", big_content, content_type="application/pdf")
        files_data = {'document': big_file}

        form = SendDocumentForm({}, files_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('document', form.errors)
        self.assertIn('Arquivo muito grande', str(form.errors['document']))

    def test_missing_document_field(self):
        """Testa formulário sem campo documento (obrigatório)"""
        form = SendDocumentForm({}, {})
        
        self.assertFalse(form.is_valid())
        self.assertIn('document', form.errors)

    def test_caption_max_length(self):
        """Testa legenda excedendo limite de 1024 caracteres"""
        pdf_file = SimpleUploadedFile("test.pdf", self.pdf_content, content_type="application/pdf")
        long_caption = 'x' * 1025  # 1025 caracteres (limite é 1024)
        form_data = {'caption': long_caption}
        files_data = {'document': pdf_file}

        form = SendDocumentForm(form_data, files_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('caption', form.errors)

    def test_caption_exactly_max_length(self):
        """Testa legenda com exatamente 1024 caracteres (limite)"""
        pdf_file = SimpleUploadedFile("test.pdf", self.pdf_content, content_type="application/pdf")
        max_caption = 'x' * 1024  # Exatamente 1024 caracteres
        form_data = {'caption': max_caption}
        files_data = {'document': pdf_file}

        form = SendDocumentForm(form_data, files_data)
        
        self.assertTrue(form.is_valid(), f"Formulário deveria ser válido. Erros: {form.errors}")
        self.assertEqual(form.cleaned_data['caption'], max_caption)

    def test_empty_pdf_file(self):
        """Testa arquivo PDF vazio"""
        empty_file = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")
        files_data = {'document': empty_file}

        form = SendDocumentForm({}, files_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('document', form.errors)
        # Arquivo vazio não passa na validação do magic number

    def test_file_size_exactly_16mb(self):
        """Testa arquivo com exatamente 16MB (limite máximo)"""
        # Cria arquivo com exatamente 16MB
        size_16mb = 16 * 1024 * 1024
        content_size = size_16mb - len(self.pdf_content)
        big_content = self.pdf_content + b'X' * content_size
        
        big_file = SimpleUploadedFile("16mb.pdf", big_content, content_type="application/pdf")
        files_data = {'document': big_file}

        form = SendDocumentForm({}, files_data)
        
        self.assertTrue(form.is_valid(), f"Formulário deveria ser válido. Erros: {form.errors}")