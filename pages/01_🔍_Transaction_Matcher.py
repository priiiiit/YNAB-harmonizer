from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from src.adapters.csv.mapping import get_csv_adapter
from src.adapters.ynab.source import YNABSourceAdapter
from src.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Transaction Matcher",
    page_icon="🔍",
    layout="wide"
)

def load_ynab_transactions():
    try:
        ynab_adapter = YNABSourceAdapter(budget_id="")
        budgets = ynab_adapter.get_budgets()
        
        selected_budget = st.selectbox(
            "Select YNAB Budget",
            options=budgets,
            format_func=lambda x: x.name
        )
        
        if selected_budget:
            ynab_adapter = YNABSourceAdapter(budget_id=selected_budget.id)
            accounts = ynab_adapter.get_accounts()
            active_accounts = [a for a in accounts if not a.closed]
            
            selected_account = st.selectbox(
                "Select Account",
                options=active_accounts,
                format_func=lambda x: f"{x.name} (Balance: {x.balance:,.2f})"
            )
            
            return ynab_adapter, selected_budget, selected_account
    except Exception as e:
        st.error(f"Error accessing YNAB: {str(e)}")
        return None, None, None

def load_csv_transactions():
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your bank transaction CSV file"
    )
    
    if uploaded_file is not None:
        bank_name = st.selectbox(
            "Select your bank",
            options=['LHV']  # Add other banks as needed
        )
        
        temp_path = Path("data/user_uploads/temp.csv")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        try:
            adapter = get_csv_adapter(bank_name, str(temp_path))
            return adapter
        except Exception as e:
            st.error(f"Error processing CSV: {str(e)}")
            return None

def find_matching_transactions(ynab_trans, csv_trans, tolerance_days=1, amount_threshold=0.01):
    matches = []
    unmatched_ynab = []
    unmatched_csv = []
    
    csv_matched = set()
    
    for yt in ynab_trans:
        found_match = False
        for i, ct in enumerate(csv_trans):
            if i in csv_matched:
                continue
                
            amount_matches = abs(yt.amount - ct.amount) <= amount_threshold
            date_diff = abs((yt.date - ct.date).days)
            date_matches = date_diff <= tolerance_days
            
            if amount_matches and date_matches:
                matches.append((yt, ct))
                csv_matched.add(i)
                found_match = True
                break
        
        if not found_match:
            unmatched_ynab.append(yt)
    
    for i, ct in enumerate(csv_trans):
        if i not in csv_matched:
            unmatched_csv.append(ct)
    
    return matches, unmatched_ynab, unmatched_csv

# Main content
st.title("Transaction Matcher")
render_sidebar()

# Create two columns for YNAB and CSV inputs
col1, col2 = st.columns(2)

with col1:
    st.header("YNAB Source")
    ynab_adapter, selected_budget, selected_account = load_ynab_transactions()
    
    # Add date range selection for YNAB
    st.subheader("Date Range")
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=90),
            help="Include transactions from this date"
        )
    with col_end:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="Include transactions until this date"
        )
    
    if start_date > end_date:
        st.error("Start date must be before end date")

with col2:
    st.header("CSV Source")
    csv_adapter = load_csv_transactions()

# Matching parameters
st.header("Matching Parameters")
col3, col4 = st.columns(2)
with col3:
    tolerance_days = st.number_input("Date Tolerance (days)", min_value=0, value=1)
with col4:
    amount_threshold = st.number_input("Amount Threshold", min_value=0.0, value=0.01)

# Only show the match button if both sources are ready and dates are valid
if all([ynab_adapter, selected_budget, selected_account, csv_adapter]) and start_date <= end_date:
    if st.button("Find Matches"):
        # Create final YNAB adapter with date range
        ynab_adapter = YNABSourceAdapter(
            budget_id=selected_budget.id,
            account_id=selected_account.id,
            since_date=datetime.combine(start_date, datetime.min.time())
        )
        
        # Get transactions from both sources
        ynab_transactions = ynab_adapter.load_transactions()
        
        # Filter YNAB transactions by date range
        end_datetime = datetime.combine(end_date, datetime.max.time())
        ynab_transactions = [
            t for t in ynab_transactions 
            if start_date <= t.date.date() <= end_date
        ]
        
        csv_transactions = csv_adapter.load_transactions()
        
        # Find matches and unmatched transactions
        matches, unmatched_ynab, unmatched_csv = find_matching_transactions(
            ynab_transactions,
            csv_transactions,
            tolerance_days,
            amount_threshold
        )
        
        # Display results
        st.header("Results")
        st.write(f"Found {len(matches)} matching transactions")
        st.write(f"Analyzed {len(ynab_transactions)} YNAB transactions and {len(csv_transactions)} CSV transactions")
        
        # Display unmatched transactions
        col5, col6 = st.columns(2)
        with col5:
            st.subheader(f"Unmatched YNAB Transactions ({len(unmatched_ynab)})")
            if unmatched_ynab:
                df_ynab = pd.DataFrame([vars(t) for t in unmatched_ynab])
                st.dataframe(df_ynab)
            else:
                st.info("No unmatched YNAB transactions")
        
        with col6:
            st.subheader(f"Unmatched CSV Transactions ({len(unmatched_csv)})")
            if unmatched_csv:
                df_csv = pd.DataFrame([vars(t) for t in unmatched_csv])
                st.dataframe(df_csv)
            else:
                st.info("No unmatched CSV transactions")
