from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import requests

from .config import YNABConfig


@dataclass
class YNABBudget:
    id: str
    name: str
    last_modified: datetime
    
@dataclass
class YNABAccount:
    id: str
    name: str
    type: str
    balance: float
    closed: bool = False

class YNABClient:
    def __init__(self, config: YNABConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}"
        })
    
    def get_budgets(self) -> List[YNABBudget]:
        """Get list of budgets."""
        response = self.session.get(f"{self.config.api_url}/budgets")
        response.raise_for_status()
        
        budgets = []
        for b in response.json()['data']['budgets']:
            budget = YNABBudget(
                id=b['id'],
                name=b['name'],
                last_modified=datetime.strptime(b['last_modified_on'], '%Y-%m-%dT%H:%M:%S%z')
            )
            budgets.append(budget)
            
        return budgets
    
    def get_accounts(self, budget_id: str) -> List[YNABAccount]:
        """Get list of accounts for a budget."""
        response = self.session.get(f"{self.config.api_url}/budgets/{budget_id}/accounts")
        response.raise_for_status()
        
        accounts = []
        for a in response.json()['data']['accounts']:
            account = YNABAccount(
                id=a['id'],
                name=a['name'],
                type=a['type'],
                balance=float(a['balance']) / 1000,  # Convert milliunits to actual amount
                closed=a['closed']
            )
            accounts.append(account)
            
        return accounts
    
    def get_transactions(self, budget_id: str, account_id: str = None, since_date: datetime = None) -> List[Dict[str, Any]]:
        """Get transactions for a budget and optionally specific account."""
        params = {}
        if since_date:
            params['since_date'] = since_date.strftime('%Y-%m-%d')
            
        # If account_id is provided, get transactions for specific account
        url = f"{self.config.api_url}/budgets/{budget_id}"
        if account_id:
            url += f"/accounts/{account_id}/transactions"
        else:
            url += "/transactions"
            
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()['data']['transactions']
