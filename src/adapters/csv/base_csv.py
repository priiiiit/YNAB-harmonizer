from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from ..base import DataSourceAdapter, Transaction


class BaseCSVAdapter(DataSourceAdapter):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.column_mapping: Dict[str, str] = self._get_column_mapping()
        
    @abstractmethod
    def _get_column_mapping(self) -> Dict[str, str]:
        """
        Return mapping of standard fields to bank-specific CSV columns
        Example: {'date': 'Transaction Date', 'amount': 'Amount (USD)'}
        """
        pass

    @abstractmethod
    def _preprocess_amount(self, amount: Any) -> float:
        """Handle bank-specific amount formatting"""
        pass

    @abstractmethod
    def _parse_date(self, date_str: str) -> datetime:
        """Handle bank-specific date formatting"""
        pass

    def load_transactions(self) -> List[Transaction]:
        df = pd.read_csv(self.file_path)
        
        # Rename columns based on mapping
        df = df.rename(columns={v: k for k, v in self.column_mapping.items()})
        
        transactions = []
        for _, row in df.iterrows():
            try:
                self._current_row = row  # Store current row for processing context
                transaction = Transaction(
                    date=self._parse_date(row['date']),
                    description=str(row['description']),
                    amount=self._preprocess_amount(row['amount']),
                    category=str(row.get('category', '')),
                    transaction_type=str(row.get('transaction_type', '')),
                    account_id=str(row.get('account_id', '')),
                    bank_name=self.get_bank_name(),
                    raw_data=row.to_dict()
                )
                transactions.append(transaction)
            except Exception as e:
                # Log error and continue
                print(f"Error processing row: {row}, Error: {e}")
            finally:
                self._current_row = None  # Clear the context
                
        return transactions

    @abstractmethod
    def get_bank_name(self) -> str:
        """Return the name of the bank"""
        pass

    def get_source_type(self) -> str:
        return "CSV"