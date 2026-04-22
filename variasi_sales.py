import pandas as pd
import numpy as np

def buat_variasi_sales():
    file_path = 'Kopi_Senja_Audit_Raw.xlsx'
    print("Menyuntikkan variasi performa sales agar lebih realistis...")
    
    # Load data
    sales = pd.read_excel(file_path, sheet_name='sales_pos')
    
    # Multiplier untuk membuat peringkat (Ranking)
    # Cabang Sehat
    multipliers = {
        'CWG': 1.45, # Cawang - Prime (Paling Laku)
        'MKG': 1.25, # Kelapa Gading - Mall (Ramai)
        'PIK': 1.00, # PIK - Baseline
        'CKG': 0.80, # Cakung - Industrial
        'KNG': 0.60, # Kuningan - Office (Sepi di weekend)
        # Cabang Bermasalah (juga diberi variasi sedikit)
        'KBY': 1.10,
        'BTR': 1.00,
        'JGK': 0.90
    }
    
    for branch, mult in multipliers.items():
        mask = sales['Branch_ID'] == branch
        # Tambahkan randomness +/- 5% agar tiap transaksi tidak kelipatan bulat
        random_noise = np.random.uniform(0.95, 1.05, size=mask.sum())
        sales.loc[mask, 'Gross_Sales'] = (sales.loc[mask, 'Gross_Sales'] * mult * random_noise).round(-2)

    # Simpan kembali ke Excel
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        sales.to_excel(writer, sheet_name='sales_pos', index=False)
        
    print("✅ Variasi sales berhasil disuntikkan. Sekarang ada peringkat performa!")

if __name__ == "__main__":
    buat_variasi_sales()