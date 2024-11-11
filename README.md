# YNAB Harmonizer

A Streamlit application that helps you reconcile bank transactions between YNAB (You Need A Budget) and your bank's CSV exports.

## Features

### Transaction Import
- Import transactions from YNAB API
- Import transactions from bank CSV files

Currently supported banks:
- LHV

### Transaction Matching
Compare transactions between YNAB and your bank's CSV export to:
- Find matching transactions based on date and amount
- Identify transactions present in YNAB but missing from bank export
- Identify transactions present in bank export but missing from YNAB

Configurable matching parameters:
- Date tolerance (number of days)
- Amount threshold for matching

## Installation
1. Clone the repository
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Configure YNAB API access:
    - Get your YNAB API key from https://app.ynab.com/settings/developer
    - Set it in environment variables:
        ```bash
        export YNAB_API_KEY=your_api_key_here
        ```
    - Or add it to `config.yaml`:   
        ```yaml
        api_key: "your_api_key_here"
        ```

## Usage
1. Start the application:
    ```bash
    streamlit run app.py
    ```
2. Use the sidebar to navigate between:
    - **Home**: Import and view transactions from a single source
    - **Transaction Matcher**: Compare transactions between YNAB and bank CSV

3. Transaction Matcher
    - Select your YNAB budget and account
    - Upload your bank's CSV export
    - Set matching parameters:
        - Date tolerance for matching transactions
Amount threshold for small discrepancies
Click "Find Matches" to see:
        - Number of matched transactions
        - Unmatched transactions from both sources

## Adding New Bank Support
1. Create a new adapter in src/adapters/csv/
2. Implement the required methods from BaseCSVAdapter
    - Add the adapter to the mapping in src/adapters/csv/mapping.py
