from datetime import datetime
from pathlib import Path

import streamlit as st

from src.adapters.csv.mapping import get_csv_adapter
from src.adapters.ynab.source import YNABSourceAdapter
from src.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Bank Transactions Analyzer",
    page_icon="💰",
    layout="wide"
)

def main():
    render_sidebar()
    st.title("Bank Transactions Analyzer")
    
    source_type = st.selectbox(
        "Select source type",
        options=['CSV', 'YNAB']
    )
    
    if source_type == 'CSV':
        # File uploader component
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your bank transaction CSV file"
        )
        
        if uploaded_file is not None:
            bank_name = st.selectbox(
                "Select your bank",
                options=['LHV', 'Wells Fargo', 'Bank of America']
            )
            
            # Save uploaded file temporarily
            temp_path = Path("data/user_uploads/temp.csv")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            try:
                adapter = get_csv_adapter(bank_name, str(temp_path))
                transactions = adapter.load_transactions()
                
                if transactions:
                    st.write(f"Found {len(transactions)} transactions")
                    
                    import pandas as pd
                    df = pd.DataFrame([vars(t) for t in transactions])
                    st.dataframe(df)
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    elif source_type == 'YNAB':
        try:
            # Initialize adapter without budget_id first
            ynab_adapter = YNABSourceAdapter(budget_id="")
            
            # Get available budgets
            budgets = ynab_adapter.get_budgets()
            if not budgets:
                st.error("No budgets found in YNAB")
                return
                
            # Let user select budget
            selected_budget = st.selectbox(
                "Select YNAB Budget",
                options=budgets,
                format_func=lambda x: x.name
            )
            
            if selected_budget:
                # Update adapter with selected budget
                ynab_adapter = YNABSourceAdapter(budget_id=selected_budget.id)
                
                # Get accounts for selected budget
                accounts = ynab_adapter.get_accounts()
                active_accounts = [a for a in accounts if not a.closed]
                
                if not active_accounts:
                    st.error("No active accounts found in this budget")
                    return
                    
                # Let user select account
                selected_account = st.selectbox(
                    "Select Account",
                    options=active_accounts,
                    format_func=lambda x: f"{x.name} (Balance: {x.balance:,.2f})"
                )
                
                # Date selection
                since_date = st.date_input("Since date")
                
                if st.button("Load Transactions"):
                    # Create final adapter with all selections
                    ynab_adapter = YNABSourceAdapter(
                        budget_id=selected_budget.id,
                        account_id=selected_account.id if selected_account else None,
                        since_date=datetime.combine(since_date, datetime.min.time())
                    )
                    
                    transactions = ynab_adapter.load_transactions()
                    if transactions:
                        st.write(f"Found {len(transactions)} transactions")
                        import pandas as pd
                        df = pd.DataFrame([vars(t) for t in transactions])
                        st.dataframe(df)
                    else:
                        st.info("No transactions found for the selected criteria")
                        
        except Exception as e:
            st.error(f"Error accessing YNAB: {str(e)}")

if __name__ == "__main__":
    main()