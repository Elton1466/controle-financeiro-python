import sys
import os
from pathlib import Path
import unittest
import tempfile
from datetime import datetime, timedelta

# Adiciona o diretório src ao PATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from finance_manager import FinanceManager
from utils import Utils

class TestFinanceManager(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.manager = FinanceManager()
        self.test_file = tempfile.mktemp(prefix='finance_test_', suffix='.dat')
        
        # Dados de teste
        self.sample_transaction = {
            'description': 'Salário',
            'amount': 5000.00,
            'transaction_type': 'receita',
            'category': 'Rendimento',
            'date': datetime.now()
        }

    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_transaction(self):
        """Testa adição de transações válidas"""
        result = self.manager.add_transaction(
            description=self.sample_transaction['description'],
            amount=self.sample_transaction['amount'],
            transaction_type=self.sample_transaction['transaction_type'],
            category=self.sample_transaction['category'],
            date=self.sample_transaction['date']
        )
        self.assertTrue(result)
        self.assertEqual(len(self.manager.transactions), 1)

    def test_add_invalid_transaction(self):
        """Testa adição de transações inválidas"""
        # Teste com tipo inválido
        invalid_trans = self.sample_transaction.copy()
        invalid_trans['transaction_type'] = 'inválido'
        result = self.manager.add_transaction(
            description=invalid_trans['description'],
            amount=invalid_trans['amount'],
            transaction_type=invalid_trans['transaction_type'],
            category=invalid_trans['category'],
            date=invalid_trans['date']
        )
        self.assertFalse(result)

    def test_calculate_balance(self):
        """Testa cálculo de saldo"""
        self.manager.add_transaction("Salário", 5000, "receita", "Rendimento", datetime.now())
        self.manager.add_transaction("Aluguel", 1500, "despesa", "Moradia", datetime.now())
        balance = self.manager.calculate_balance()
        self.assertEqual(balance['receita_total'], 5000)
        self.assertEqual(balance['despesa_total'], 1500)
        self.assertEqual(balance['saldo'], 3500)

class TestUtils(unittest.TestCase):
    def test_validate_amount(self):
        """Testa validação de valores monetários"""
        # Teste com valor válido
        result, value = Utils.validate_amount("1000")
        self.assertTrue(result)
        self.assertEqual(value, 1000)
        
        # Teste com valor inválido
        result, msg = Utils.validate_amount("abc")
        self.assertFalse(result)

    def test_validate_date(self):
        """Testa validação de datas"""
        # Teste com data válida
        result, date = Utils.validate_date("15-05-2023")
        self.assertTrue(result)
        self.assertIsInstance(date, datetime)
        
        # Teste com data inválida
        result, msg = Utils.validate_date("31-02-2023")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)