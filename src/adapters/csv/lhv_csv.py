from datetime import datetime
from typing import Any, Dict

from .base_csv import BaseCSVAdapter


class LHVCSVAdapter(BaseCSVAdapter):
    def _get_column_mapping(self) -> Dict[str, str]:
        return {
            'date': 'Date',
            'description': 'Description',
            'amount': 'Amount',
            'transaction_type': 'Debit/Credit (D/C)',
            'account_id': 'Customer account no',
            'counterparty_name': 'Sender/receiver name',
            'counterparty_account': 'Sender/receiver account',
            'reference': 'Reference number'
        }

    def _preprocess_amount(self, amount: Any) -> float:
        amount_str = str(amount).replace(',', '.')
        amount_float = float(amount_str)
        
        row = self._current_row
        if row['transaction_type'] == 'D':
            amount_float = -abs(amount_float)
        
        return amount_float

    def _parse_date(self, date_str: str) -> datetime:
        # Updated to handle YYYY-MM-DD format
        return datetime.strptime(date_str, '%Y-%m-%d')

    def get_bank_name(self) -> str:
        return "LHV"

    def get_source_type(self) -> str:
        return "CSV"
        