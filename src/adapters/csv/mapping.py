from typing import Dict, Type

from .base_csv import BaseCSVAdapter
from .lhv_csv import LHVCSVAdapter

BANK_ADAPTER_MAPPING: Dict[str, Type[BaseCSVAdapter]] = {
    'lhv': LHVCSVAdapter,
    # Add other banks here
}

def get_csv_adapter(bank_name: str, file_path: str) -> BaseCSVAdapter:
    adapter_class = BANK_ADAPTER_MAPPING.get(bank_name.lower())
    if not adapter_class:
        raise ValueError(f"No adapter found for bank: {bank_name}")
    return adapter_class(file_path) 