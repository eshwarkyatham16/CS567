import unittest
from datetime import datetime
from code.banking_system import BankingSystem, Account
import logging

# Disable logging for test output readability
logging.disable(logging.CRITICAL)

class TestBankingSystem(unittest.TestCase):

    def setUp(self):
        """Set up the BankingSystem instance before each test."""
        self.banking_system = BankingSystem()
        # Create a test account
        self.banking_system.create_account('123456', 'John Doe', 'savings', 5000, 'password123')

    def test_create_account(self):
        """Test account creation with valid and invalid input."""
        # Test valid account creation
        self.banking_system.create_account('654321', 'Jane Doe', 'checking', 1000, 'password123')
        account = self.banking_system.accounts['654321']
        self.assertEqual(account.name, 'Jane Doe')
        self.assertEqual(account.account_type, 'checking')
        self.assertEqual(account.balance, 1000)
        
        # Test duplicate account creation
        with self.assertRaises(ValueError):
            self.banking_system.create_account('123456', 'Test User', 'checking', 500, 'password123')

        # Test invalid account type
        with self.assertRaises(ValueError):
            self.banking_system.create_account('112233', 'Invalid User', 'invalid', 1000, 'password123')

    def test_deposit(self):
        """Test deposit functionality."""
        account = self.banking_system.accounts['123456']
        account.deposit(1000)
        self.assertEqual(account.balance, 6000)

        # Test invalid deposit amount
        with self.assertRaises(ValueError):
            account.deposit(-500)
        
        # Test deposit of zero
        with self.assertRaises(ValueError):
            account.deposit(0)

    def test_withdraw(self):
        """Test withdrawal functionality."""
        account = self.banking_system.accounts['123456']
        account.withdraw(1000)
        self.assertEqual(account.balance, 4000)

        # Test insufficient balance
        with self.assertRaises(ValueError):
            account.withdraw(5000)

        # Test invalid withdrawal amount
        with self.assertRaises(ValueError):
            account.withdraw(-500)

        # Test withdrawal exceeding spending limit
        account.set_spending_limit(2000)
        with self.assertRaises(ValueError):
            account.withdraw(3000)

    def test_login(self):
        """Test login functionality."""
        account = self.banking_system.accounts['123456']
        self.assertTrue(self.banking_system.login('123456', 'password123'))
        self.assertEqual(self.banking_system.current_user, account)

        # Test incorrect password
        with self.assertRaises(ValueError):
            self.banking_system.login('123456', 'wrongpassword')

        # Test non-existent account
        with self.assertRaises(ValueError):
            self.banking_system.login('000000', 'password123')

    def test_logout(self):
        """Test logout functionality."""
        account = self.banking_system.accounts['123456']
        self.banking_system.login('123456', 'password123')
        self.banking_system.logout()
        self.assertIsNone(self.banking_system.current_user)

    def test_account_balance(self):
        """Test account balance retrieval."""
        account = self.banking_system.accounts['123456']
        self.assertEqual(account.get_balance(), 5000)

    def test_add_fixed_deposit(self):
        """Test adding fixed deposit functionality."""
        account = self.banking_system.accounts['123456']
        account.add_fixed_deposit(2000, 12, 5)
        self.assertEqual(len(account.fixed_deposits), 1)

        # Test insufficient funds for fixed deposit
        with self.assertRaises(ValueError):
            account.add_fixed_deposit(10000, 12, 5)

    def test_apply_for_loan(self):
        """Test loan application functionality."""
        account = self.banking_system.accounts['123456']
        self.assertTrue(account.apply_for_loan(10000))  # Below pre-approval limit
        self.assertFalse(account.apply_for_loan(60000))  # Above pre-approval limit

if __name__ == '__main__':
    unittest.main()
