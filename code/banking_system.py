import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Account:
    def __init__(self, account_number, name, account_type, initial_balance=0, password="1234", currency="USD"):
        self.account_number = account_number
        self.name = name
        self.account_type = account_type 
        self.balance = initial_balance
        self.password = password
        self.currency = currency
        self.transactions = []
        self.fixed_deposits = []
        self.recurring_deposit = None
        self.notifications = []
        self.spending_limit = None
        self.pre_approval_limit = 50000 if account_type == "savings" else 20000
        self.loan_amount = 0
        self.overdraft_protection = False
        self.suspended = False
        logger.info(f"Created {self.account_type} account for {self.name} (Account: {self.account_number})")

    def deposit(self, amount):
        if self.suspended:
            logger.warning(f"Account {self.account_number} is suspended. Deposit failed.")
            raise ValueError("Account is suspended.")
        if amount > 0:
            self.balance += amount
            self._log_transaction("Deposit", amount)
            self.notifications.append(f"Deposited {amount} to your account. New balance: {self.balance}")
            logger.info(f"Deposited {amount} to account {self.account_number}. New balance: {self.balance}")
        else:
            logger.warning(f"Invalid deposit amount: {amount}")
            raise ValueError("Deposit amount must be positive.")

    def withdraw(self, amount):
        if self.suspended:
            logger.warning(f"Account {self.account_number} is suspended. Withdrawal failed.")
            raise ValueError("Account is suspended.")
        if amount <= 0:
            logger.warning(f"Invalid withdrawal amount: {amount}")
            raise ValueError("Withdrawal amount must be positive.")
        if self.spending_limit and amount > self.spending_limit:
            logger.warning(f"Withdrawal amount exceeds spending limit for account {self.account_number}")
            raise ValueError("Withdrawal amount exceeds spending limit.")
        if amount > self.balance:
            if self.overdraft_protection:
                logger.info(f"Overdraft protection used for account {self.account_number}")
                self.balance -= amount
                self._log_transaction("Withdrawal (Overdraft)", amount)
                self.notifications.append(f"Used overdraft protection. New balance: {self.balance}")
            else:
                logger.warning(f"Insufficient funds in account {self.account_number}")
                raise ValueError("Insufficient funds.")
        else:
            self.balance -= amount
            self._log_transaction("Withdrawal", amount)
            self.notifications.append(f"Withdrew {amount} from your account. New balance: {self.balance}")
            logger.info(f"Withdrew {amount} from account {self.account_number}. New balance: {self.balance}")

    def get_balance(self):
        logger.info(f"Checked balance for account {self.account_number}")
        return self.balance

    def _log_transaction(self, transaction_type, amount):
        transaction = {
            "type": transaction_type,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.transactions.append(transaction)
        logger.info(f"Transaction recorded for account {self.account_number}: {transaction}")

    def get_transaction_history(self):
        logger.info(f"Retrieved transaction history for account {self.account_number}")
        return self.transactions

    def generate_account_statement(self, start_date, end_date):
        statement = [txn for txn in self.transactions if start_date <= datetime.strptime(txn["date"], "%Y-%m-%d %H:%M:%S") <= end_date]
        logger.info(f"Generated account statement for account {self.account_number} from {start_date} to {end_date}")
        return statement

    def calculate_interest(self, rate):
        if self.account_type == "savings":
            interest = self.balance * (rate / 100)
            self.balance += interest
            self._log_transaction("Interest", interest)
            self.notifications.append(f"Interest added to your account: {interest}. New balance: {self.balance}")
            logger.info(f"Interest added to account {self.account_number}: {interest}. New balance: {self.balance}")

    def verify_password(self, password):
        return self.password == password

    def add_fixed_deposit(self, amount, duration_in_months, rate):
        if amount > self.balance:
            logger.warning(f"Insufficient funds for FD creation in account {self.account_number}")
            raise ValueError("Insufficient funds for FD.")
        self.balance -= amount
        maturity_date = datetime.now() + timedelta(days=duration_in_months * 30)
        maturity_amount = amount * ((1 + (rate / 100)) ** (duration_in_months / 12))
        fd = {
            "amount": amount,
            "duration": duration_in_months,
            "rate": rate,
            "maturity_date": maturity_date.strftime("%Y-%m-%d"),
            "maturity_amount": round(maturity_amount, 2),
        }
        self.fixed_deposits.append(fd)
        self._log_transaction("Fixed Deposit", amount)
        self.notifications.append(f"FD created in your account: {fd}")
        logger.info(f"FD created in account {self.account_number}: {fd}")

    def view_fixed_deposits(self):
        return self.fixed_deposits

    def start_recurring_deposit(self, monthly_amount, duration_in_months, rate):
        if self.recurring_deposit:
            logger.warning(f"RD already exists for account {self.account_number}")
            raise ValueError("Recurring deposit already exists.")
        total_amount = monthly_amount * duration_in_months
        maturity_amount = total_amount * ((1 + (rate / 100)) ** (duration_in_months / 12))
        self.recurring_deposit = {
            "monthly_amount": monthly_amount,
            "duration": duration_in_months,
            "rate": rate,
            "total_amount": total_amount,
            "maturity_amount": round(maturity_amount, 2),
            "start_date": datetime.now().strftime("%Y-%m-%d"),
        }
        self._log_transaction("Recurring Deposit Started", monthly_amount)
        self.notifications.append(f"RD started in your account: {self.recurring_deposit}")
        logger.info(f"RD started in account {self.account_number}: {self.recurring_deposit}")

    def view_recurring_deposit(self):
        return self.recurring_deposit

    def set_spending_limit(self, limit):
        self.spending_limit = limit
        self.notifications.append(f"Spending limit set to {limit}")
        logger.info(f"Spending limit set to {limit} for account {self.account_number}")

    def apply_for_loan(self, loan_amount):
        if loan_amount <= self.pre_approval_limit:
            self.loan_amount = loan_amount
            self.notifications.append(f"Loan of {loan_amount} approved.")
            logger.info(f"Loan of {loan_amount} approved for account {self.account_number}")
            return True
        else:
            self.notifications.append(f"Loan of {loan_amount} exceeds your pre-approval limit.")
            logger.warning(f"Loan of {loan_amount} denied for account {self.account_number}")
            return False

    def repay_loan(self, amount):
        if self.loan_amount > 0 and amount <= self.loan_amount:
            self.loan_amount -= amount
            self._log_transaction("Loan Repayment", amount)
            self.notifications.append(f"Repaid {amount} of your loan. Remaining loan amount: {self.loan_amount}")
            logger.info(f"Repaid {amount} of loan for account {self.account_number}. Remaining loan: {self.loan_amount}")
        else:
            logger.warning(f"No loan outstanding for account {self.account_number}")
            raise ValueError("No loan outstanding.")

    def transfer_money(self, amount, recipient_account):
        if self.suspended:
            logger.warning(f"Account {self.account_number} is suspended. Transfer failed.")
            raise ValueError("Account is suspended.")
        if amount <= 0:
            logger.warning(f"Invalid transfer amount: {amount}")
            raise ValueError("Transfer amount must be positive.")
        if amount > self.balance:
            if self.overdraft_protection:
                logger.info(f"Overdraft protection used for account {self.account_number}")
                self.balance -= amount
                self._log_transaction("Transfer (Overdraft)", amount)
                recipient_account.deposit(amount)
                self.notifications.append(f"Transferred {amount} to account {recipient_account.account_number} using overdraft protection.")
            else:
                logger.warning(f"Insufficient funds for transfer from account {self.account_number}")
                raise ValueError("Insufficient funds for transfer.")
        else:
            self.balance -= amount
            self._log_transaction("Transfer", amount)
            recipient_account.deposit(amount)
            self.notifications.append(f"Transferred {amount} to account {recipient_account.account_number}.")
            logger.info(f"Transferred {amount} to account {recipient_account.account_number} from account {self.account_number}")

    def view_notifications(self):
        return self.notifications

    def suspend_account(self):
        self.suspended = True
        self.notifications.append("Your account has been suspended.")
        logger.info(f"Account {self.account_number} suspended.")

    def activate_account(self):
        self.suspended = False
        self.notifications.append("Your account has been activated.")
        logger.info(f"Account {self.account_number} activated.")

    def change_account_type(self, new_account_type):
        if new_account_type not in ["savings", "checking"]:
            logger.warning(f"Invalid account type change request for account {self.account_number}")
            raise ValueError("Invalid account type. Choose 'savings' or 'checking'.")
        self.account_type = new_account_type
        self.notifications.append(f"Your account type has been changed to {new_account_type}.")
        logger.info(f"Account {self.account_number} type changed to {new_account_type}")

    def set_overdraft_protection(self, status):
        self.overdraft_protection = status
        self.notifications.append(f"Overdraft protection set to {status}.")
        logger.info(f"Overdraft protection set to {status} for account {self.account_number}")

    def change_password(self, old_password, new_password):
        if self.verify_password(old_password):
            self.password = new_password
            self.notifications.append("Password changed successfully.")
            logger.info(f"Password changed for account {self.account_number}")
        else:
            logger.warning(f"Incorrect password attempt to change password for account {self.account_number}")
            raise ValueError("Incorrect old password.")

    def __repr__(self):
        return f"Account({self.account_number}, {self.name}, {self.account_type}, Balance: {self.balance})"

class BankingSystem:
    def __init__(self):
        self.accounts = {}
        self.current_user = None
        self.interest_rates = {"savings": 5, "checking": 2}  # Admin adjustable interest rates
        logger.info("Initialized Banking System")

    def create_account(self, account_number, name, account_type, initial_balance, password, currency="USD"):
        if account_number in self.accounts:
            logger.error(f"Duplicate account creation attempt: {account_number}")
            raise ValueError("Account number already exists.")
        if account_type not in ["savings", "checking"]:
            logger.error(f"Invalid account type: {account_type}")
            raise ValueError("Invalid account type. Choose 'savings' or 'checking'.")
        if account_type == "savings" and initial_balance < 1000:
            logger.warning(f"Insufficient initial balance for savings account: {initial_balance}")
            raise ValueError("Savings accounts require a minimum initial balance of 1000.")
        if account_type == "checking" and initial_balance < 500:
            logger.warning(f"Insufficient initial balance for checking account: {initial_balance}")
            raise ValueError("Checking accounts require a minimum initial balance of 500.")
        self.accounts[account_number] = Account(account_number, name, account_type, initial_balance, password, currency)
        logger.info(f"Account created successfully: {account_number}")

    def login(self, account_number, password):
        account = self.accounts.get(account_number)
        if account:
            if account.verify_password(password):
                self.current_user = account
                logger.info(f"User logged in: {account_number}")
                return True
            else:
                logger.warning(f"Password mismatch for account {account_number}")
                raise ValueError("Incorrect password.")
        logger.error(f"Login attempt failed. Account not found: {account_number}")
        raise ValueError("Account does not exist.")

    def logout(self):
        if self.current_user:
            logger.info(f"User logged out: {self.current_user.account_number}")
            self.current_user = None

    def list_accounts(self):
        logger.info("Listed all accounts")
        return list(self.accounts.values())

    def set_interest_rate(self, account_type, rate):
        if account_type not in self.interest_rates:
            logger.warning(f"Invalid account type for interest rate: {account_type}")
            raise ValueError("Invalid account type. Choose 'savings' or 'checking'.")
        self.interest_rates[account_type] = rate
        logger.info(f"Interest rate for {account_type} account set to {rate}%.")

def main():
    banking_system = BankingSystem()

    banking_system.create_account("123456789", "Alice", "savings", 2000, "alicepass")
    banking_system.create_account("987654321", "Bob", "checking", 1500, "bobpass")

    banking_system.login("123456789", "alicepass")
    alice_account = banking_system.current_user

    alice_account.deposit(500)
    alice_account.withdraw(300)
    alice_account.set_spending_limit(1000)
    alice_account.apply_for_loan(10000)
    alice_account.repay_loan(2000)
    alice_account.add_fixed_deposit(1000, 12, 5)

    banking_system.login("987654321", "bobpass")
    bob_account = banking_system.current_user

    bob_account.deposit(1000)
    bob_account.withdraw(200)
    bob_account.transfer_money(500, alice_account)

    print("Alice's Notifications:", alice_account.view_notifications())
    print("Bob's Notifications:", bob_account.view_notifications())

if __name__ == "__main__":
    main()
