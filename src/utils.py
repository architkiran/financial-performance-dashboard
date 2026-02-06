import os
import pickle
from datetime import datetime, timedelta

def cache_data(data, cache_file, cache_duration_hours=24):
    """
    Save data to cache file
    
    Args:
        data: Data to cache
        cache_file (str): Path to cache file
        cache_duration_hours (int): How long cache is valid
    """
    cache_dir = 'data/cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_path = os.path.join(cache_dir, cache_file)
    
    with open(cache_path, 'wb') as f:
        pickle.dump({
            'data': data,
            'timestamp': datetime.now()
        }, f)
    
    print(f"Data cached to {cache_path}")


def load_cached_data(cache_file, cache_duration_hours=24):
    """
    Load data from cache if it exists and is not expired
    
    Args:
        cache_file (str): Path to cache file
        cache_duration_hours (int): How long cache is valid
        
    Returns:
        Data if cache is valid, None otherwise
    """
    cache_path = os.path.join('data/cache', cache_file)
    
    if not os.path.exists(cache_path):
        return None
    
    with open(cache_path, 'rb') as f:
        cached = pickle.load(f)
    
    # Check if cache is still valid
    age = datetime.now() - cached['timestamp']
    if age < timedelta(hours=cache_duration_hours):
        print(f"Loading data from cache (age: {age})")
        return cached['data']
    else:
        print("Cache expired")
        return None
    
def validate_financial_data(dataframe, required_fields):
    """
    Validate that required fields exist in financial data
    
    Args:
        dataframe (pd.DataFrame): Financial statement data
        required_fields (list): List of required field names
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    if dataframe.empty:
        return False, required_fields
    
    existing_fields = dataframe.index.tolist()
    missing = [field for field in required_fields if field not in existing_fields]
    
    return len(missing) == 0, missing


def clean_financial_data(df):
    """
    Clean financial data by handling NaN values and ensuring proper types
    
    Args:
        df (pd.DataFrame): Raw financial data
        
    Returns:
        pd.DataFrame: Cleaned data
    """
    # Replace inf with NaN
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Fill NaN with 0 or forward fill (choose based on your needs)
    # df = df.fillna(0)  # Option 1: Fill with zero
    # df = df.fillna(method='ffill')  # Option 2: Forward fill
    
    return df