"""
Quick diagnostic script to check your financial data
Run this to see what's happening with your data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_extraction import FinancialDataExtractor
from src.data_processing import FinancialMetricsCalculator

def diagnose_company(ticker):
    print(f"\n{'='*60}")
    print(f"DIAGNOSING: {ticker}")
    print(f"{'='*60}\n")
    
    try:
        # Extract data
        print(f"1. Extracting data for {ticker}...")
        extractor = FinancialDataExtractor(ticker)
        data = extractor.get_all_statements()
        
        # Check income statement
        print(f"\n2. Checking Income Statement...")
        income_stmt = data['income_statement']
        print(f"   Shape: {income_stmt.shape}")
        print(f"   Columns (years): {list(income_stmt.columns)}")
        print(f"   Available fields: {list(income_stmt.index[:10])}")  # First 10 fields
        
        # Check if Total Revenue exists
        if 'Total Revenue' in income_stmt.index:
            print(f"   ✓ Total Revenue found")
            print(f"   Values: {income_stmt.loc['Total Revenue'].values}")
        else:
            print(f"   ✗ Total Revenue NOT found")
            print(f"   Trying alternatives...")
            # Look for alternatives
            revenue_fields = [idx for idx in income_stmt.index if 'revenue' in idx.lower()]
            print(f"   Revenue-related fields: {revenue_fields}")
        
        # Check balance sheet
        print(f"\n3. Checking Balance Sheet...")
        balance_sheet = data['balance_sheet']
        print(f"   Shape: {balance_sheet.shape}")
        if not balance_sheet.empty:
            print(f"   ✓ Balance sheet has data")
        else:
            print(f"   ✗ Balance sheet is EMPTY")
        
        # Check cash flow
        print(f"\n4. Checking Cash Flow...")
        cash_flow = data['cash_flow']
        print(f"   Shape: {cash_flow.shape}")
        if not cash_flow.empty:
            print(f"   ✓ Cash flow has data")
        else:
            print(f"   ✗ Cash flow is EMPTY")
        
        # Try to calculate metrics
        print(f"\n5. Attempting to calculate metrics...")
        try:
            calculator = FinancialMetricsCalculator(
                income_stmt,
                balance_sheet,
                cash_flow
            )
            
            metrics = calculator.calculate_all_metrics()
            print(f"   ✓ Metrics calculated successfully!")
            print(f"   Metrics shape: {metrics.shape}")
            print(f"\n   Latest metrics:")
            if not metrics.empty:
                print(metrics.iloc[0])
            else:
                print("   ✗ Metrics dataframe is EMPTY")
            
        except Exception as e:
            print(f"   ✗ Error calculating metrics: {e}")
            import traceback
            print(traceback.format_exc())
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    # Test with the three companies
    companies = ['AAPL', 'MSFT', 'GOOGL']
    
    for ticker in companies:
        diagnose_company(ticker)
    
    print(f"\n{'='*60}")
    print("DIAGNOSIS COMPLETE")
    print(f"{'='*60}\n")
