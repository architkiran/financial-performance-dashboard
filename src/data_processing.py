import pandas as pd
import numpy as np

class FinancialMetricsCalculator:
    """
    Calculate financial metrics from financial statements
    """
    
    def __init__(self, income_stmt, balance_sheet, cash_flow):
        """
        Initialize with financial statements
        
        Args:
            income_stmt (pd.DataFrame): Income statement
            balance_sheet (pd.DataFrame): Balance sheet
            cash_flow (pd.DataFrame): Cash flow statement
        """
        self.income_stmt = income_stmt
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow
    
    def calculate_revenue_growth(self):
        """
        Calculate year-over-year revenue growth
        
        Returns:
            pd.Series: Revenue growth percentages
        """
        try:
            # Get total revenue row
            revenue = self.income_stmt.loc['Total Revenue']
            
            # Calculate percentage change
            growth = revenue.pct_change(periods=-1) * 100  # periods=-1 for chronological order
            
            return growth
        except Exception as e:
            print(f"Error calculating revenue growth: {e}")
            return pd.Series()
    
    def calculate_gross_margin(self):
        """
        Calculate gross profit margin
        Gross Margin = (Gross Profit / Revenue) * 100
        
        Returns:
            pd.Series: Gross margin percentages
        """
        try:
            revenue = self.income_stmt.loc['Total Revenue']
            gross_profit = self.income_stmt.loc['Gross Profit']
            
            margin = (gross_profit / revenue) * 100
            
            return margin
        except Exception as e:
            print(f"Error calculating gross margin: {e}")
            return pd.Series()
    
    def calculate_operating_margin(self):
        """
        Calculate operating profit margin
        Operating Margin = (Operating Income / Revenue) * 100
        
        Returns:
            pd.Series: Operating margin percentages
        """
        try:
            revenue = self.income_stmt.loc['Total Revenue']
            operating_income = self.income_stmt.loc['Operating Income']
            
            margin = (operating_income / revenue) * 100
            
            return margin
        except Exception as e:
            print(f"Error calculating operating margin: {e}")
            return pd.Series()
    
    def calculate_net_margin(self):
        """
        Calculate net profit margin
        Net Margin = (Net Income / Revenue) * 100
        
        Returns:
            pd.Series: Net margin percentages
        """
        try:
            revenue = self.income_stmt.loc['Total Revenue']
            net_income = self.income_stmt.loc['Net Income']
            
            margin = (net_income / revenue) * 100
            
            return margin
        except Exception as e:
            print(f"Error calculating net margin: {e}")
            return pd.Series()
    
    def calculate_free_cash_flow(self):
        """
        Calculate free cash flow
        FCF = Operating Cash Flow - Capital Expenditures
        
        Returns:
            pd.Series: Free cash flow values
        """
        try:
            operating_cf = self.cash_flow.loc['Operating Cash Flow']
            capex = self.cash_flow.loc['Capital Expenditure']
            
            # Note: CapEx is usually negative in the data
            fcf = operating_cf + capex  # Adding because capex is negative
            
            return fcf
        except Exception as e:
            print(f"Error calculating free cash flow: {e}")
            return pd.Series()
    
    def calculate_current_ratio(self):
        """
        Calculate current ratio
        Current Ratio = Current Assets / Current Liabilities
        
        Returns:
            pd.Series: Current ratio values
        """
        try:
            current_assets = self.balance_sheet.loc['Current Assets']
            current_liabilities = self.balance_sheet.loc['Current Liabilities']
            
            ratio = current_assets / current_liabilities
            
            return ratio
        except Exception as e:
            print(f"Error calculating current ratio: {e}")
            return pd.Series()
    
    def calculate_debt_to_equity(self):
        """
        Calculate debt-to-equity ratio
        D/E = Total Debt / Total Equity
        
        Returns:
            pd.Series: Debt-to-equity ratio values
        """
        try:
            total_debt = self.balance_sheet.loc['Total Debt']
            stockholders_equity = self.balance_sheet.loc['Stockholders Equity']
            
            ratio = total_debt / stockholders_equity
            
            return ratio
        except Exception as e:
            print(f"Error calculating debt-to-equity: {e}")
            return pd.Series()
    
    def calculate_roe(self):
        """
        Calculate Return on Equity
        ROE = (Net Income / Stockholders' Equity) * 100
        
        Returns:
            pd.Series: ROE percentages
        """
        try:
            net_income = self.income_stmt.loc['Net Income']
            equity = self.balance_sheet.loc['Stockholders Equity']
            
            roe = (net_income / equity) * 100
            
            return roe
        except Exception as e:
            print(f"Error calculating ROE: {e}")
            return pd.Series()
    
    def calculate_roa(self):
        """
        Calculate Return on Assets
        ROA = (Net Income / Total Assets) * 100
        
        Returns:
            pd.Series: ROA percentages
        """
        try:
            net_income = self.income_stmt.loc['Net Income']
            total_assets = self.balance_sheet.loc['Total Assets']
            
            roa = (net_income / total_assets) * 100
            
            return roa
        except Exception as e:
            print(f"Error calculating ROA: {e}")
            return pd.Series()
    
    def calculate_all_metrics(self):
        """
        Calculate all financial metrics and return as a DataFrame
        
        Returns:
            pd.DataFrame: All calculated metrics
        """
        metrics = {
            'Revenue Growth (%)': self.calculate_revenue_growth(),
            'Gross Margin (%)': self.calculate_gross_margin(),
            'Operating Margin (%)': self.calculate_operating_margin(),
            'Net Margin (%)': self.calculate_net_margin(),
            'Free Cash Flow': self.calculate_free_cash_flow(),
            'Current Ratio': self.calculate_current_ratio(),
            'Debt to Equity': self.calculate_debt_to_equity(),
            'ROE (%)': self.calculate_roe(),
            'ROA (%)': self.calculate_roa()
        }
        
        df = pd.DataFrame(metrics)
        
        # Sort by date (newest first)
        df = df.sort_index(ascending=False)
        
        return df


def create_comparison_dataframe(companies_data):
    """
    Create a comparison dataframe for multiple companies
    
    Args:
        companies_data (dict): Dictionary with company data
        
    Returns:
        pd.DataFrame: Comparison metrics for all companies
    """
    comparison_data = []
    
    for ticker, data in companies_data.items():
        calculator = FinancialMetricsCalculator(
            data['income_statement'],
            data['balance_sheet'],
            data['cash_flow']
        )
        
        metrics = calculator.calculate_all_metrics()
        
        # Get the most recent year's data
        if not metrics.empty:
            latest = metrics.iloc[0].to_dict()
            latest['Company'] = ticker
            comparison_data.append(latest)
    
    return pd.DataFrame(comparison_data)


# Example usage
if __name__ == "__main__":
    from data_extraction import FinancialDataExtractor
    
    # Test with Apple
    ticker = "AAPL"
    extractor = FinancialDataExtractor(ticker)
    data = extractor.get_all_statements()
    
    # Calculate metrics
    calculator = FinancialMetricsCalculator(
        data['income_statement'],
        data['balance_sheet'],
        data['cash_flow']
    )
    
    all_metrics = calculator.calculate_all_metrics()
    print(f"\n{ticker} Financial Metrics:")
    print(all_metrics)