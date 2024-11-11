from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Transaction:
    date: datetime
    description: str
    amount: float
    category: str = ""
    transaction_type: str = ""
    account_id: str = ""
    bank_name: str = ""
    raw_data: Dict[str, Any] = None  # Store original data if needed

class DataSourceAdapter(ABC):
    @abstractmethod
    def load_transactions(self) -> List[Transaction]:
        """Load transactions from the data source"""
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        """Return the type of data source"""
        pass