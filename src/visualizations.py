import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

def plot_revenue_trend(companies_data, tickers):
    """
    Create a line chart showing revenue trends for multiple companies
    
    Args:
        companies_data (dict): Financial data for companies
        tickers (list): List of ticker symbols
        
    Returns:
        plotly.graph_objects.Figure: Revenue trend chart
    """
    fig = go.Figure()
    
    for ticker in tickers:
        try:
            income_stmt = companies_data[ticker]['income_statement']
            revenue = income_stmt.loc['Total Revenue']
            
            # Sort by date
            revenue = revenue.sort_index()
            
            fig.add_trace(go.Scatter(
                x=revenue.index,
                y=revenue.values,
                mode='lines+markers',
                name=ticker,
                line=dict(width=3),
                marker=dict(size=8)
            ))
        except Exception as e:
            print(f"Error plotting revenue for {ticker}: {e}")
    
    fig.update_layout(
        title='Revenue Trend Comparison',
        xaxis_title='Year',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_margin_comparison(metrics_df):
    """
    Create a grouped bar chart comparing margins
    
    Args:
        metrics_df (pd.DataFrame): Metrics for all companies
        
    Returns:
        plotly.graph_objects.Figure: Margin comparison chart
    """
    margin_columns = ['Gross Margin (%)', 'Operating Margin (%)', 'Net Margin (%)']
    
    fig = go.Figure()
    
    for margin in margin_columns:
        if margin in metrics_df.columns:
            fig.add_trace(go.Bar(
                name=margin.replace(' (%)', ''),
                x=metrics_df['Company'],
                y=metrics_df[margin],
                text=metrics_df[margin].round(2),
                textposition='auto'
            ))
    
    fig.update_layout(
        title='Profitability Margins Comparison',
        xaxis_title='Company',
        yaxis_title='Margin (%)',
        barmode='group',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_fcf_trend(companies_data, tickers):
    """
    Create a line chart showing free cash flow trends
    
    Args:
        companies_data (dict): Financial data for companies
        tickers (list): List of ticker symbols
        
    Returns:
        plotly.graph_objects.Figure: FCF trend chart
    """
    fig = go.Figure()
    
    for ticker in tickers:
        try:
            cash_flow = companies_data[ticker]['cash_flow']
            operating_cf = cash_flow.loc['Operating Cash Flow']
            capex = cash_flow.loc['Capital Expenditure']
            
            fcf = operating_cf + capex  # capex is negative
            fcf = fcf.sort_index()
            
            fig.add_trace(go.Scatter(
                x=fcf.index,
                y=fcf.values,
                mode='lines+markers',
                name=ticker,
                line=dict(width=3),
                marker=dict(size=8)
            ))
        except Exception as e:
            print(f"Error plotting FCF for {ticker}: {e}")
    
    fig.update_layout(
        title='Free Cash Flow Trend',
        xaxis_title='Year',
        yaxis_title='Free Cash Flow (USD)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_financial_health_score(metrics_df):
    """
    Create a radar chart showing financial health across multiple dimensions
    
    Args:
        metrics_df (pd.DataFrame): Metrics for all companies
        
    Returns:
        plotly.graph_objects.Figure: Radar chart
    """
    # Normalize metrics to 0-100 scale
    categories = ['Gross Margin (%)', 'Operating Margin (%)', 
                  'ROE (%)', 'ROA (%)', 'Current Ratio']
    
    fig = go.Figure()
    
    for idx, row in metrics_df.iterrows():
        values = []
        for cat in categories:
            if cat in metrics_df.columns:
                val = row[cat]
                # Normalize (simple approach - you can make this more sophisticated)
                if cat == 'Current Ratio':
                    normalized = min(val * 50, 100)  # 2.0 ratio = 100
                else:
                    normalized = min(max(val, 0), 100)
                values.append(normalized)
            else:
                values.append(0)
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=row['Company']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title='Financial Health Score Comparison',
        height=600
    )
    
    return fig


def plot_metrics_over_time(companies_data, ticker, metric_name):
    """
    Plot a specific metric over time for one company
    
    Args:
        companies_data (dict): Financial data
        ticker (str): Company ticker
        metric_name (str): Name of metric to plot
        
    Returns:
        plotly.graph_objects.Figure: Time series chart
    """
    from data_processing import FinancialMetricsCalculator
    
    calculator = FinancialMetricsCalculator(
        companies_data[ticker]['income_statement'],
        companies_data[ticker]['balance_sheet'],
        companies_data[ticker]['cash_flow']
    )
    
    all_metrics = calculator.calculate_all_metrics()
    
    if metric_name in all_metrics.columns:
        metric_data = all_metrics[metric_name].sort_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=metric_data.index,
            y=metric_data.values,
            mode='lines+markers',
            name=metric_name,
            line=dict(width=3, color='#1f77b4'),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title=f'{ticker} - {metric_name} Over Time',
            xaxis_title='Year',
            yaxis_title=metric_name,
            template='plotly_white',
            height=400
        )
        
        return fig
    else:
        return None


def create_financial_summary_table(companies_data, ticker):
    """
    Create a summary table of key metrics
    
    Args:
        companies_data (dict): Financial data
        ticker (str): Company ticker
        
    Returns:
        pd.DataFrame: Summary table
    """
    from data_processing import FinancialMetricsCalculator
    
    calculator = FinancialMetricsCalculator(
        companies_data[ticker]['income_statement'],
        companies_data[ticker]['balance_sheet'],
        companies_data[ticker]['cash_flow']
    )
    
    metrics = calculator.calculate_all_metrics()
    
    # Get most recent year
    if not metrics.empty:
        latest = metrics.iloc[0]
        
        # Format for display
        summary = pd.DataFrame({
            'Metric': latest.index,
            'Value': latest.values
        })
        
        # Round numeric values
        summary['Value'] = summary['Value'].apply(
            lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x
        )
        
        return summary
    
    return pd.DataFrame()