import pandas as pd

def fix_data():
    file_path = 'Kopi_Senja_Audit_Raw.xlsx'
    print("Sedang memperbaiki metode pembayaran...")
    
    # Load data
    sales = pd.read_excel(file_path, sheet_name='sales_pos')
    
    # Mapping: Sesuaikan Credit/Debit Card menjadi EDC agar konsisten dengan spec
    mapping = {
        'Credit Card': 'EDC',
        'Debit Card': 'EDC'
    }
    
    sales['Payment_Method'] = sales['Payment_Method'].replace(mapping)
    
    # Simpan kembali ke Excel
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        sales.to_excel(writer, sheet_name='sales_pos', index=False)
        
    print("✅ Data Payment_Method berhasil dibersihkan.")

if __name__ == "__main__":
    fix_data()