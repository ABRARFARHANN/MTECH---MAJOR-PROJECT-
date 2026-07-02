import pandas as pd
import numpy as np
from datetime import timedelta, date

# Set seed for reproducibility (proves deterministic generation)
np.random.seed(42)

def generate_sleep_csv(output_filename='sleep_data.csv', num_days=30):
    # 1. Define the parameters for the 5 clinical stages (G1-G5)
    # Each profile defines mean values for sleep hours and typical awakenings
    stage_params = {
        'G1': {'sleep_mean': 7.6, 'sleep_std': 0.3, 'awaken_base': 0, 'awaken_range': 1},
        'G2': {'sleep_mean': 5.8, 'sleep_std': 0.8, 'awaken_base': 2, 'awaken_range': 3},
        'G3': {'sleep_mean': 5.3, 'sleep_std': 1.0, 'awaken_base': 4, 'awaken_range': 3},
        'G4': {'sleep_mean': 4.1, 'sleep_std': 0.6, 'awaken_base': 7, 'awaken_range': 4},
        'G5': {'sleep_mean': 3.5, 'sleep_std': 0.4, 'awaken_base': 12, 'awaken_range': 6}
    }
    
    start_date = date(2025, 11, 5)
    records = []
    
    # Generate num_days for each of the 5 profiles (default 30, can be 365 for a year)
    for profile_id in ['G1', 'G2', 'G3', 'G4', 'G5']:
        params = stage_params[profile_id]
        
        for day in range(num_days):
            current_date = start_date + timedelta(days=day)
            
            # 2. Sample Total Sleep Hours from normal distribution defined by the stage
            sleep_hours = round(float(np.abs(np.random.normal(params['sleep_mean'], params['sleep_std']))), 1)
            
            # Ensure a bare minimum floor for sleep hours to maintain clinical realism
            sleep_hours = max(2.5, sleep_hours)
            
            # 3. Simulate Awakenings
            # The worse the stage, the higher the base amount of awakenings
            awakenings = params['awaken_base'] + np.random.randint(0, params['awaken_range'] + 1)
            
            # 4. Enforce Physiological Constraints: Calculate Sleep Efficiency
            # The calculation is Total Sleep / Time In Bed.
            # Time in Bed is mathematically constructed to always be higher than sleep time.
            # As awakenings go up, the gap between Time In Bed and actual Sleep Hours widens.
            time_awake_in_bed = awakenings * np.random.uniform(0.1, 0.4) 
            time_in_bed = sleep_hours + time_awake_in_bed + 0.5 # 0.5 buffer for falling asleep
            
            sleep_efficiency = round((sleep_hours / time_in_bed), 2)
            
            # 5. Append daily log
            records.append({
                'user_id': profile_id,
                'date': current_date.strftime('%Y-%m-%d'),
                'total_sleep_hours': sleep_hours,
                'awakenings': int(awakenings),
                'sleep_efficiency': sleep_efficiency
            })
            
    # 6. Save directly to CSV
    df = pd.DataFrame(records)
    df.to_csv(output_filename, index=False)
    print(f"Successfully generated {len(df)} sleep records across 5 risk profiles.")
    print(f"Saved to {output_filename}")
    
    return df

# Execute the generation
if __name__ == "__main__":
    df = generate_sleep_csv()
    
    # Display the first few rows of the Healthy baseline (G1)
    print("\n--- Phase 1: Healthy Baseline (Profile G1) Sample ---")
    print(df[df['user_id'] == 'G1'].head(3))
    
    # Display the first few rows of the Severe Risk (G5)
    print("\n--- Phase 5: Chronic High-Risk (Profile G5) Sample ---")
    print(df[df['user_id'] == 'G5'].head(3))
