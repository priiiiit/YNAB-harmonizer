from datetime import datetime
from typing import List, Optional

from ...services.ynab.client import YNABAccount, YNABBudget, YNABClient
from ...services.ynab.config import YNABConfig
from ..base import DataSourceAdapter, Transaction


class YNABSourceAdapter(DataSourceAdapter):
    def __init__(self, budget_id: str, account_id: Optional[str] = None, since_date: Optional[datetime] = None):
        self.config = YNABConfig.load()
        self.client = YNABClient(self.config)
        self.budget_id = budget_id
        self.account_id = account_id
        self.since_date = since_date
    
    def get_budgets(self) -> List[YNABBudget]:
        return self.client.get_budgets()
    
    def get_accounts(self) -> List[YNABAccount]:
        return self.client.get_accounts(self.budget_id)
    
    def load_transactions(self) -> List[Transaction]:
        raw_transactions = self.client.get_transactions(
            self.budget_id,
            self.account_id,
            self.since_date
        )
        
        transactions = []
        for t in raw_transactions:
            transaction = Transaction(
                date=datetime.strptime(t['date'], '%Y-%m-%d'),
                description=t['payee_name'] or t.get('memo', ''),
                amount=float(t['amount']) / 1000,
                category=t.get('category_name', ''),
                transaction_type='outflow' if t['amount'] < 0 else 'inflow',
                account_id=t['account_id'],
                bank_name='YNAB',
                raw_data=t
            )
            transactions.append(transaction)
            
        return transactions
    
    def get_source_type(self) -> str:
        return "YNAB"
