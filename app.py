from pathlib import Path

import streamlit as st

from src.adapters.csv.mapping import get_csv_adapter

st.set_page_config(
    page_title="Bank Transactions Analyzer",
    page_icon="💰",
    layout="wide"
)

def main():
    st.title("Bank Transactions Analyzer")
    
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

if __name__ == "__main__":
    main()