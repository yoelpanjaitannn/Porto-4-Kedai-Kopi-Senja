import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kopi Senja - Financial Command Center", layout="wide")

st.title("☕ Kopi Senja: Financial Command Center")
st.markdown("### Executive Dashboard & Automated Audit Settlement")
st.divider()

@st.cache_data
def load_data():
    sales = pd.read_excel('Kopi_Senja_Audit_Raw.xlsx', sheet_name='sales_pos')
    bocor = pd.read_excel('TEMUAN_AUDIT_BOCOR.xlsx')
    return sales, bocor

df_sales, df_bocor = load_data()

# --- METRIC CARDS ---
col1, col2, col3 = st.columns(3)

total_gross = df_sales['Gross_Sales'].sum()
total_bocor = df_bocor['Gross_Sales'].sum()
persentase_bocor = (total_bocor / total_gross) * 100

with col1:
    st.metric("Total Penjualan (POS)", f"Rp {total_gross:,.0f}")
with col2:
    st.metric("Dana Nyangkut / Hilang", f"Rp {total_bocor:,.0f}", f"-{persentase_bocor:.2f}%", delta_color="normal")
with col3:
    st.metric("Total Transaksi Terdampak", f"{len(df_bocor)} Transaksi")

st.divider()

# --- DUA GRAFIK BERDAMPINGAN ---
col_left, col_right = st.columns(2)

with col_left:
    # Grafik Anomali (Merah)
    bocor_per_cabang = df_bocor.groupby('Branch_ID')['Gross_Sales'].sum().reset_index()
    fig_bocor = px.bar(bocor_per_cabang, x='Branch_ID', y='Gross_Sales', 
                 text_auto='.2s', 
                 title="🔴 High Risk Area (Total Kerugian)",
                 color_discrete_sequence=['#D32F2F']) 
    fig_bocor.update_layout(xaxis_title="Cabang Bermasalah", yaxis_title="Nilai Kebocoran (Rp)")
    st.plotly_chart(fig_bocor, use_container_width=True)

with col_right:
    # Grafik Cabang Sehat (Peringkat Penjualan - Abu-abu)
    cabang_bermasalah = df_bocor['Branch_ID'].unique()
    df_sehat = df_sales[~df_sales['Branch_ID'].isin(cabang_bermasalah)]
    
    # Hitung performa penjualan cabang sehat
    performa_sehat = df_sehat.groupby('Branch_ID')['Gross_Sales'].sum().reset_index()
    performa_sehat = performa_sehat.sort_values(by='Gross_Sales', ascending=False)
    
    fig_sehat = px.bar(performa_sehat, x='Branch_ID', y='Gross_Sales', 
                 text_auto='.2s', 
                 title="⚪ Top 5 Healthy Branches (Total Sales)",
                 color_discrete_sequence=['#E0E0E0']) 
    fig_sehat.update_layout(xaxis_title="Cabang Sehat", yaxis_title="Total Penjualan (Rp)")
    st.plotly_chart(fig_sehat, use_container_width=True)

# --- TABEL DETAIL DENGAN NAMA KOLOM BARU ---
st.subheader("📋 Detail Transaksi Unsettled (Butuh Investigasi)")

# Mapping nama kolom sesuai permintaan Yoel
df_tampilan = df_bocor[['Transaction_ID', 'Branch_ID', 'Timestamp', 'Item_Name', 'Payment_Method', 'Gross_Sales']].copy()
df_tampilan.columns = ['Kode Transaksi', 'Cabang', 'Waktu', 'Produk', 'Metode Bayar', 'Nilai Transaksi (Rp)']

st.dataframe(df_tampilan, use_container_width=True)