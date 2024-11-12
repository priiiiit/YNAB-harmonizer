from datetime import datetime
from typing import Any, Dict

from .base_csv import BaseCSVAdapter


class LHVCSVAdapter(BaseCSVAdapter):
    # Define header mappings for Estonian and English only
    HEADER_MAPPINGS = {
        'en': {
            'account_id': 'Customer account no',
            'date': 'Date',
            'description': 'Description',
            'amount': 'Amount',
            'transaction_type': 'Debit/Credit (D/C)',
            'counterparty_name': 'Sender/receiver name',
            'counterparty_account': 'Sender/receiver account',
            'reference': 'Reference number'
        },
        'et': {
            'account_id': 'Kliendi konto',
            'date': 'Kuupäev',
            'description': 'Selgitus',
            'amount': 'Summa',
            'transaction_type': 'Deebet/Kreedit (D/C)',
            'counterparty_name': 'Saaja/maksja nimi',
            'counterparty_account': 'Saaja/maksja konto',
            'reference': 'Viitenumber'
        }
    }

    def __init__(self, file_path: str):
        self.file_path = file_path  # Set file_path before detecting language
        self.detected_language = self._detect_language()  # Detect language first
        super().__init__(file_path)  # Then initialize parent class

    def _detect_language(self) -> str:
        """Detect if CSV is in Estonian or English"""
        import pandas as pd
        
        headers = pd.read_csv(self.file_path, nrows=0).columns.tolist()
        
        # Check for Estonian headers first
        if any(header in headers for header in self.HEADER_MAPPINGS['et'].values()):
            return 'et'
        
        return 'en'  # Default to English if not Estonian

    def _get_column_mapping(self) -> Dict[str, str]:
        """Get column mapping for detected language"""
        mappings = self.HEADER_MAPPINGS[self.detected_language]
        return {
            'date': mappings['date'],
            'description': mappings['description'],
            'amount': mappings['amount'],
            'transaction_type': mappings['transaction_type'],
            'account_id': mappings['account_id'],
            'counterparty_name': mappings['counterparty_name'],
            'counterparty_account': mappings['counterparty_account'],
            'reference': mappings['reference']
        }

    def _preprocess_amount(self, amount: Any) -> float:
        amount_str = str(amount).replace(',', '.')
        amount_float = float(amount_str)
        
        row = self._current_row
        if row['transaction_type'] == 'D':
            amount_float = -abs(amount_float)
        
        return amount_float

    def _parse_date(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, '%Y-%m-%d')

    def get_bank_name(self) -> str:
        return "LHV"

    def get_source_type(self) -> str:
        return "CSV"
        