import pandas as pd

def validasi_matematis(file_raw, file_temuan):
    print("--- MEMULAI VALIDASI SISTEM ---")
    
    # Load semua file
    print("Membaca data...")
    sales = pd.read_excel(file_raw, sheet_name='sales_pos')
    settlement = pd.read_excel(file_raw, sheet_name='settlement_report')
    bocor = pd.read_excel(file_temuan)
    
    # 1. Validasi Baris (Row Count Integrity)
    print("\n[1] VALIDASI JUMLAH TRANSAKSI")
    total_pos = len(sales)
    total_settled = len(settlement)
    total_bocor = len(bocor)
    
    print(f"Total Transaksi POS    : {total_pos}")
    print(f"Total di Settlement    : {total_settled}")
    print(f"Total Transaksi Bocor  : {total_bocor}")
    print(f"Settlement + Bocor     : {total_settled + total_bocor}")
    
    if total_pos == (total_settled + total_bocor):
        print(">> STATUS: ✅ VALID (Tidak ada baris yang hilang/ganda)")
    else:
        print(">> STATUS: ❌ INVALID (Ada anomali data)")

    # 2. Validasi Nilai Finansial (Financial Integrity)
    print("\n[2] VALIDASI NILAI GROSS SALES")
    # Hanya menghitung nilai transaksi yang berhasil masuk settlement
    sales_settled = sales[sales['Transaction_ID'].isin(settlement['Transaction_ID'])]
    
    uang_seharusnya = sales_settled['Gross_Sales'].sum()
    uang_bocor = bocor['Gross_Sales'].sum()
    uang_total_pos = sales['Gross_Sales'].sum()
    
    print(f"Total Uang di POS (Gross)          : Rp {uang_total_pos:,.0f}")
    print(f"Total Uang Seharusnya (Settled)    : Rp {uang_seharusnya:,.0f}")
    print(f"Total Uang Bocor                   : Rp {uang_bocor:,.0f}")
    print(f"Seharusnya + Bocor                 : Rp {uang_seharusnya + uang_bocor:,.0f}")
    
    if round(uang_total_pos, 2) == round(uang_seharusnya + uang_bocor, 2):
        print(">> STATUS: ✅ VALID (Perhitungan uang akurat)")
    else:
        print(">> STATUS: ❌ INVALID (Perhitungan uang meleset)")

if __name__ == "__main__":
    validasi_matematis('Kopi_Senja_Audit_Raw.xlsx', 'TEMUAN_AUDIT_BOCOR.xlsx')