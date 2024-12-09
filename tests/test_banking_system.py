import unittest
from datetime import datetime, timedelta
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
        self.banking_system.create_account('654321', 'Jane Smith', 'checking', 1000, 'password456')

    def test_create_account(self):
        """Test account creation with valid and invalid input."""
        self.banking_system.create_account('112233', 'New User', 'savings', 2000, 'password789')
        account = self.banking_system.accounts['112233']
        self.assertEqual(account.name, 'New User')
        self.assertEqual(account.account_type, 'savings')

        # Test duplicate account creation
        with self.assertRaises(ValueError):
            self.banking_system.create_account('123456', 'Test User', 'checking', 500, 'password123')

    def test_transfer_money(self):
        """Test money transfer functionality."""
        account1 = self.banking_system.accounts['123456']
        account2 = self.banking_system.accounts['654321']

        account1.transfer_money(500, account2)
        self.assertEqual(account1.balance, 4500)
        self.assertEqual(account2.balance, 1500)

        # Test insufficient balance
        with self.assertRaises(ValueError):
            account1.transfer_money(10000, account2)

        # Test overdraft protection
        account1.set_overdraft_protection(True)
        account1.transfer_money(5000, account2)
        self.assertEqual(account1.balance, -500)
        self.assertEqual(account2.balance, 6500)

    def test_overdraft_protection(self):
        """Test enabling and disabling overdraft protection."""
        account = self.banking_system.accounts['123456']
        account.set_overdraft_protection(True)
        self.assertTrue(account.overdraft_protection)
        account.withdraw(6000)  # Allowed with overdraft
        self.assertEqual(account.balance, -1000)

        account.set_overdraft_protection(False)
        with self.assertRaises(ValueError):
            account.withdraw(1000)  # Disallowed without overdraft

    def test_notifications(self):
        """Test notification functionality."""
        account = self.banking_system.accounts['123456']
        account.deposit(500)
        account.withdraw(1000)
        notifications = account.view_notifications()
        self.assertEqual(len(notifications), 2)

    def test_account_suspension_and_activation(self):
        """Test account suspension and activation."""
        account = self.banking_system.accounts['123456']
        account.suspend_account()
        with self.assertRaises(ValueError):
            account.deposit(500)

        account.activate_account()
        account.deposit(500)  # Should work after activation
        self.assertEqual(account.balance, 5500)

    def test_password_change(self):
        """Test changing account password."""
        account = self.banking_system.accounts['123456']
        account.change_password('password123', 'newpassword')
        self.assertTrue(account.verify_password('newpassword'))

        # Test incorrect old password
        with self.assertRaises(ValueError):
            account.change_password('wrongpassword', 'anotherpassword')

    def test_account_type_change(self):
        """Test changing account type."""
        account = self.banking_system.accounts['123456']
        account.change_account_type('checking')
        self.assertEqual(account.account_type, 'checking')

        # Test invalid account type
        with self.assertRaises(ValueError):
            account.change_account_type('invalid')

    def test_transaction_history(self):
        """Test retrieving transaction history."""
        account = self.banking_system.accounts['123456']
        account.deposit(1000)
        account.withdraw(500)
        transactions = account.get_transaction_history()
        self.assertEqual(len(transactions), 2)

    def test_generate_account_statement(self):
        """Test generating account statement."""
        account = self.banking_system.accounts['123456']
        account.deposit(1000)
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        statement = account.generate_account_statement(start_date, end_date)
        self.assertEqual(len(statement), 1)

    def test_recurring_deposit(self):
        """Test recurring deposit functionality."""
        account = self.banking_system.accounts['123456']
        account.start_recurring_deposit(500, 12, 5)
        rd = account.view_recurring_deposit()
        self.assertEqual(rd["monthly_amount"], 500)

        # Test duplicate RD creation
        with self.assertRaises(ValueError):
            account.start_recurring_deposit(100, 6, 3)

    def test_loan_repayment(self):
        """Test loan repayment functionality."""
        account = self.banking_system.accounts['123456']
        account.apply_for_loan(10000)
        account.repay_loan(5000)
        self.assertEqual(account.loan_amount, 5000)

        # Test overpayment
        with self.assertRaises(ValueError):
            account.repay_loan(6000)

    def test_login_success(self):
        result = self.banking_system.login('123456', 'password123')
        self.assertTrue(result)
        self.assertEqual(self.banking_system.current_user.account_number, '123456')

    def test_login_incorrect_password(self):
        with self.assertRaises(ValueError) as context:
            self.banking_system.login('123456', 'WrongPassword')
        self.assertEqual(str(context.exception), "Incorrect password.")

    def test_login_account_not_found(self):
        with self.assertRaises(ValueError) as context:
            self.banking_system.login('000000', 'Password123')
        self.assertEqual(str(context.exception), "Account does not exist.")

    def test_logout(self):
        self.banking_system.login('654321', 'password456')
        self.banking_system.logout()
        self.assertIsNone(self.banking_system.current_user)

    def test_list_accounts(self):
        accounts = self.banking_system.list_accounts()
        self.assertEqual(len(accounts), 2)
        self.assertEqual(accounts[0].name, 'John Doe')
        self.assertEqual(accounts[1].name, 'Jane Smith')

    def test_set_interest_rate_success(self):
        self.banking_system.set_interest_rate('savings', 3.5)
        self.assertEqual(self.banking_system.interest_rates['savings'], 3.5)

        self.banking_system.set_interest_rate('checking', 1.5)
        self.assertEqual(self.banking_system.interest_rates['checking'], 1.5)

    def test_set_interest_rate_invalid_account_type(self):
        with self.assertRaises(ValueError) as context:
            self.banking_system.set_interest_rate('business', 4.0)
        self.assertEqual(str(context.exception), "Invalid account type. Choose 'savings' or 'checking'.")

if __name__ == '__main__':
    unittest.main()
