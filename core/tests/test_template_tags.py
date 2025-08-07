from django.test import TestCase
from core.templatetags.core_tags import doc, fone


class TemplatTagsTest(TestCase):
    
    def test_doc_filter_cpf(self):
        """Testa formatação de CPF"""
        cpf = "12345678901"
        result = doc(cpf)
        expected = "123.456.789-01"
        self.assertEqual(result, expected)
    
    def test_doc_filter_cnpj(self):
        """Testa formatação de CNPJ"""
        cnpj = "12345678000195"
        result = doc(cnpj)
        expected = "12.345.678/0001-95"
        self.assertEqual(result, expected)
    
    def test_doc_filter_invalid_length(self):
        """Testa documento com tamanho inválido"""
        doc_invalid = "123456"
        result = doc(doc_invalid)
        self.assertEqual(result, doc_invalid)  # Retorna sem formatação
    
    def test_doc_filter_empty(self):
        """Testa documento vazio"""
        result = doc("")
        self.assertEqual(result, "")
    
    def test_doc_filter_none(self):
        """Testa documento None"""
        result = doc(None)
        self.assertIsNone(result)
    
    def test_fone_filter_fixo(self):
        """Testa formatação de telefone fixo"""
        fone_fixo = "1133334444"
        result = fone(fone_fixo)
        expected = "(11) 3333-4444"
        self.assertEqual(result, expected)
    
    def test_fone_filter_celular(self):
        """Testa formatação de celular"""
        celular = "11999998888"
        result = fone(celular)
        expected = "(11) 99999-8888"
        self.assertEqual(result, expected)