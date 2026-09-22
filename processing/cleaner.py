import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self, data: pd.DataFrame):
        self.df = data.copy()
        
    def deduplicate(self):
        """
        Multi-OTA Deduplication:
        If we scrape the same flight (same airline, route, date) multiple times within the same hour 
        from different sources (e.g., direct API vs OTA), we only keep one observation to prevent bias.
        """
        if self.df.empty: return self.df
        
        # Create an 'hour_bucket' for deduplication
        self.df['timestamp_dt'] = pd.to_datetime(self.df['timestamp'])
        self.df['hour_bucket'] = self.df['timestamp_dt'].dt.floor('H')
        
        # Sort by price to keep the cheapest if duplicates exist
        self.df = self.df.sort_values('price')
        
        # Flag duplicates
        duplicate_mask = self.df.duplicated(
            subset=['origin', 'destination', 'departure_date', 'airline', 'hour_bucket'], 
            keep='first'
        )
        self.df['is_duplicate'] = duplicate_mask
        
        logger.info(f"Flagged {duplicate_mask.sum()} duplicate rows.")
        return self.df

    def flag_outliers_mad(self):
        """
        MAD (Median Absolute Deviation) Modified Z-Score:
        More robust than standard deviation because it is not influenced by extreme outliers.
        Formula: M_i = (0.6745 * (x_i - median)) / MAD
        """
        if self.df.empty: return self.df
        
        self.df['is_outlier'] = False
        self.df['outlier_method'] = None
        
        # Group by Route and Date
        groups = self.df.groupby(['origin', 'destination', 'departure_date'])
        
        for name, group in groups:
            # We need at least 4 observations for statistically meaningful MAD
            if len(group) < 4:
                continue
                
            prices = group['price']
            median_val = prices.median()
            
            # Calculate MAD
            mad = np.median(np.abs(prices - median_val))
            
            # If MAD is 0 (all prices are exactly the same), no outliers exist
            if mad == 0:
                continue
                
            # Calculate Modified Z-Score
            mod_z_score = 0.6745 * (prices - median_val) / mad
            
            # Flag if absolute modified Z-score > 3.0 (standard statistical threshold)
            outlier_idx = group[np.abs(mod_z_score) > 3.0].index
            
            if len(outlier_idx) > 0:
                self.df.loc[outlier_idx, 'is_outlier'] = True
                self.df.loc[outlier_idx, 'outlier_method'] = 'MAD_Z_SCORE'
                
        outlier_count = self.df['is_outlier'].sum()
        logger.info(f"Flagged {outlier_count} anomalous prices using MAD Z-Score.")
        
        return self.df
        
    def process_all(self):
        """Run the full cleaning pipeline"""
        self.deduplicate()
        self.flag_outliers_mad()
        return self.df
