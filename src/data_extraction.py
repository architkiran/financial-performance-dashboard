import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class FinancialDataExtractor:
    """
    Class to extract financial data from yfinance API
    """
    
    def __init__(self, ticker):
        """
        Initialize with a stock ticker
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
        """
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
    
    def get_income_statement(self, quarterly=False):
        """
        Fetch income statement data
        
        Args:
            quarterly (bool): If True, get quarterly data; else annual
            
        Returns:
            pd.DataFrame: Income statement data
        """
        try:
            if quarterly:
                return self.stock.quarterly_income_stmt
            else:
                return self.stock.income_stmt
        except Exception as e:
            print(f"Error fetching income statement for {self.ticker}: {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, quarterly=False):
        """
        Fetch balance sheet data
        
        Args:
            quarterly (bool): If True, get quarterly data; else annual
            
        Returns:
            pd.DataFrame: Balance sheet data
        """
        try:
            if quarterly:
                return self.stock.quarterly_balance_sheet
            else:
                return self.stock.balance_sheet
        except Exception as e:
            print(f"Error fetching balance sheet for {self.ticker}: {e}")
            return pd.DataFrame()
    
    def get_cash_flow(self, quarterly=False):
        """
        Fetch cash flow statement data
        
        Args:
            quarterly (bool): If True, get quarterly data; else annual
            
        Returns:
            pd.DataFrame: Cash flow data
        """
        try:
            if quarterly:
                return self.stock.quarterly_cashflow
            else:
                return self.stock.cashflow
        except Exception as e:
            print(f"Error fetching cash flow for {self.ticker}: {e}")
            return pd.DataFrame()
    
    def get_company_info(self):
        """
        Get basic company information
        
        Returns:
            dict: Company metadata
        """
        try:
            return self.stock.info
        except Exception as e:
            print(f"Error fetching company info for {self.ticker}: {e}")
            return {}
    
    def get_all_statements(self, quarterly=False):
        """
        Fetch all three financial statements at once
        
        Args:
            quarterly (bool): If True, get quarterly data; else annual
            
        Returns:
            dict: Dictionary containing all statements
        """
        return {
            'income_statement': self.get_income_statement(quarterly),
            'balance_sheet': self.get_balance_sheet(quarterly),
            'cash_flow': self.get_cash_flow(quarterly),
            'company_info': self.get_company_info()
        }


def fetch_multiple_companies(tickers, quarterly=False):
    """
    Fetch financial data for multiple companies
    
    Args:
        tickers (list): List of ticker symbols
        quarterly (bool): If True, get quarterly data
        
    Returns:
        dict: Dictionary with ticker as key and financial data as value
    """
    all_data = {}
    
    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        extractor = FinancialDataExtractor(ticker)
        all_data[ticker] = extractor.get_all_statements(quarterly)
    
    return all_data


# Example usage
if __name__ == "__main__":
    # Test the code
    ticker = "AAPL"
    extractor = FinancialDataExtractor(ticker)
    
    # Get annual income statement
    income_stmt = extractor.get_income_statement()
    print(f"\n{ticker} Income Statement:")
    print(income_stmt.head())
    
    # Get company info
    info = extractor.get_company_info()
    print(f"\n{ticker} Company Name: {info.get('longName', 'N/A')}")
    print(f"Sector: {info.get('sector', 'N/A')}")
    print(f"Industry: {info.get('industry', 'N/A')}")