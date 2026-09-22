import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class InflationMathEngine:
    def __init__(self, base_period_data: pd.DataFrame, current_period_data: pd.DataFrame):
        """
        Engine for calculating highly accurate CPI metrics.
        Requires dataframes containing 'origin', 'destination', 'price'.
        """
        self.base = base_period_data
        self.current = current_period_data
        
    def jevons_geometric_mean(self, group: pd.DataFrame) -> float:
        """
        Calculates the Jevons Elementary Index (Geometric Mean).
        Why? Simple arithmetic means suffer from 'upward bias' (Carli bias).
        Central banks (like the ECB and MoSPI standards) require geometric means
        so that extreme price spikes in a single airline don't disproportionately 
        skew the average.
        """
        prices = group['price'].values
        if len(prices) == 0:
            return 0.0
        # Geometric mean: nth root of product of n numbers
        # Computed via logs to prevent overflow: exp(mean(log(x)))
        return np.exp(np.mean(np.log(prices)))

    def calculate_route_relatives(self) -> pd.DataFrame:
        """
        Calculates the price relative (Current Price / Base Price) for each specific route.
        Uses the Jevons index for aggregating prices within the same route first.
        """
        if self.base.empty or self.current.empty:
            return pd.DataFrame()
            
        # 1. Aggregate prices using Geometric Mean for both periods
        base_agg = self.base.groupby(['origin', 'destination']).apply(self.jevons_geometric_mean).reset_index(name='base_price')
        current_agg = self.current.groupby(['origin', 'destination']).apply(self.jevons_geometric_mean).reset_index(name='current_price')
        
        # 2. Merge to calculate relative inflation per route
        merged = pd.merge(base_agg, current_agg, on=['origin', 'destination'])
        merged['price_relative'] = merged['current_price'] / merged['base_price']
        
        return merged

    def laspeyres_index(self, weights: pd.DataFrame) -> float:
        """
        Standard Laspeyres Price Index: Sum(P_current * Q_base) / Sum(P_base * Q_base)
        Here we use Price Relatives: Sum(Weight * Price_Relative)
        """
        relatives = self.calculate_route_relatives()
        if relatives.empty: return 100.0
        
        # Merge with base weights (e.g., passenger volume per route)
        df = pd.merge(relatives, weights, on=['origin', 'destination'])
        
        # Normalize weights to sum to 1
        df['normalized_weight'] = df['weight'] / df['weight'].sum()
        
        # Calculate Index
        index_value = (df['price_relative'] * df['normalized_weight']).sum()
        return index_value * 100.0

    def paasche_index(self, current_weights: pd.DataFrame) -> float:
        """
        Paasche Price Index: Uses current period weights (volumes).
        """
        relatives = self.calculate_route_relatives()
        if relatives.empty: return 100.0
        
        df = pd.merge(relatives, current_weights, on=['origin', 'destination'])
        df['normalized_weight'] = df['weight'] / df['weight'].sum()
        
        # Paasche formula: 1 / Sum(Weight / Price_Relative)
        denominator = (df['normalized_weight'] / df['price_relative']).sum()
        return (1 / denominator) * 100.0

    def fisher_ideal_index(self, base_weights: pd.DataFrame, current_weights: pd.DataFrame) -> float:
        """
        Fisher Ideal Index (Geometric mean of Laspeyres and Paasche).
        This is a 'superlative' index that perfectly accounts for consumer substitution 
        (e.g., when Delhi->Mumbai flights get too expensive, people fly Delhi->Pune instead).
        """
        laspeyres = self.laspeyres_index(base_weights)
        paasche = self.paasche_index(current_weights)
        
        if laspeyres == 0 or paasche == 0:
            return 100.0
            
        return np.sqrt(laspeyres * paasche)
