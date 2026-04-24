import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Konfigurasi Layout Wide
st.set_page_config(page_title="Kopi Senja - Command Center", layout="wide")

# CSS untuk screenshot tajam & font terbaca di HP
st.markdown("""
<style>
    p, li, .stMarkdown { font-size: 1.2rem !important; line-height: 1.6 !important; }
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { font-size: 1.2rem !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

st.title("☕ Kopi Senja: Command Center")

st.info("**Konteks Audit:** Kopi Senja adalah bisnis F&B dengan 8 cabang. Command Center ini mendeteksi anomali cashflow, melacak kebocoran kas, dan mengontrol resolusi dana secara otomatis.")

# --- LOAD DATA ---
@st.cache_data
def load_all_data():
    sales = pd.read_excel('Kopi_Senja_Audit_Raw.xlsx', sheet_name='sales_pos')
    bocor = pd.read_excel('TEMUAN_AUDIT_BOCOR.xlsx')
    sales_tax = pd.read_excel('LAPORAN_FASE_2_PAJAK_STOK.xlsx', sheet_name='Tax_Separation')
    inv_audit = pd.read_excel('LAPORAN_FASE_2_PAJAK_STOK.xlsx', sheet_name='Inventory_Reconciliation')
    return sales, bocor, sales_tax, inv_audit

try:
    df_sales, df_bocor, df_tax, df_inv = load_all_data()
except Exception as e:
    st.error("Data tidak ditemukan! Pastikan file Excel berada di folder yang sama.")
    st.stop()

# --- MENU NAVIGASI ---
modul = st.selectbox(
    "PILIH MODUL INVESTIGASI:",
    (
        "Fase 1: Deteksi Revenue Leakage (Uang)", 
        "Fase 2: Forensic, Tax & Inventory (Pajak & Barang)", 
        "Fase 3: Automated Control & Recovery (Resolusi)",
        "Fase 4: Cashflow Forecasting (Proyeksi Masa Depan)"
    )
)
st.divider()

# =====================================================================
# TAMPILAN FASE 1
# =====================================================================
if modul == "Fase 1: Deteksi Revenue Leakage (Uang)":
    st.markdown("🎯 **Fokus Fase 1:** Mengidentifikasi cabang dengan uang gagal masuk ke rekening.")
    st.warning("📌 **Temuan Kritis:** 3 cabang (BTR, JGK, KBY) menyumbang Rp 161,9 juta *revenue* tidak ter-*settle*.")
    
    col1, col2, col3 = st.columns(3)
    total_gross = df_sales['Gross_Sales'].sum()
    total_bocor = df_bocor['Gross_Sales'].sum() 
    with col1: st.metric("Total Penjualan", f"Rp {total_gross:,.0f}")
    with col2: st.metric("Revenue Leakage", f"Rp {total_bocor:,.0f}", f"-{(total_bocor/total_gross)*100:.2f}%")
    with col3: st.metric("Total Transaksi Terdampak", f"{len(df_bocor)} Transaksi")
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l: st.plotly_chart(px.bar(df_bocor.groupby('Branch_ID')['Gross_Sales'].sum().reset_index(), x='Branch_ID', y='Gross_Sales', text_auto='.2s', title="🔴 Area Risiko Tinggi", color_discrete_sequence=['#D32F2F']), use_container_width=True)
    with c_r: st.plotly_chart(px.bar(df_sales[~df_sales['Branch_ID'].isin(df_bocor['Branch_ID'].unique())].groupby('Branch_ID')['Gross_Sales'].sum().reset_index(), x='Branch_ID', y='Gross_Sales', text_auto='.2s', title="⚪ Top Cabang Sehat", color_discrete_sequence=['#E0E0E0']), use_container_width=True)

    st.subheader("📋 Detail Transaksi Unsettled")
    st.dataframe(df_bocor[['Transaction_ID', 'Branch_ID', 'Timestamp', 'Gross_Sales']].style.set_properties(**{'font-size': '15px'}), use_container_width=True)

# =====================================================================
# TAMPILAN FASE 2
# =====================================================================
elif modul == "Fase 2: Forensic, Tax & Inventory (Pajak & Barang)":
    st.markdown("🔗 **Menyambung Fase 1:** Investigasi kepatuhan PPN 11% dan indikasi pencurian stok.")
    st.error("📌 **Temuan Kritis:** Terdapat selisih material stok kopi 39.80 KG di KBY & BTR (Pelanggaran SOP).")
    
    m1, m2, m3, m4 = st.columns(4)
    total_shrinkage = df_inv['Shrinkage_KG'].sum()
    kerugian_stok_rp = total_shrinkage * 200000 
    
    with m1: st.metric("Total Penjualan (Bruto)", f"Rp {df_tax['Gross_Sales'].sum():,.0f}")
    with m2: st.metric("Hutang PPN 11%", f"Rp {df_tax['PPN_11'].sum():,.0f}")
    with m3: st.metric("Net Sales (Uang Bersih)", f"Rp {df_tax['Net_Sales'].sum():,.0f}")
    with m4: st.metric("Selisih Stok Fisik", f"{total_shrinkage:.2f} KG", f"Rp {kerugian_stok_rp:,.0f}", delta_color="inverse")
    
    st.caption("**Asumsi harga biji kopi:** Rp 200.000 / KG (Estimasi Harga Perolehan)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_tax, col_inv = st.columns([6, 4])
    with col_tax: st.plotly_chart(px.pie(values=[df_tax['Net_Sales'].sum(), df_tax['PPN_11'].sum()], names=['Uang Perusahaan', 'Uang Negara'], title="🔵 Komposisi Bruto", color_discrete_sequence=['#2E7D32', '#C62828']), use_container_width=True)
    
    # REVISI: Mengembalikan visual cue merah untuk selisih stok
    with col_inv: 
        fig_inv = px.bar(df_inv, x='Branch_ID', y='Shrinkage_KG', title="🔴 Selisih Stok (KG)", color='Shrinkage_KG', color_continuous_scale='Reds')
        fig_inv.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_inv, use_container_width=True)

    st.subheader("📋 Laporan Rekonsiliasi Stok Fisik")
    df_inv_display = df_inv[['Branch_ID', 'Actual_Usage_KG', 'Shrinkage_KG']].copy()
    df_inv_display.columns = ['Cabang', 'Pakai Fisik Aktual (KG)', 'Selisih Material (KG)']
    st.dataframe(df_inv_display.style.set_properties(**{'font-size': '15px'}), use_container_width=True)

# =====================================================================
# TAMPILAN FASE 3
# =====================================================================
elif modul == "Fase 3: Automated Control & Recovery (Resolusi)":
    st.markdown("🛡️ **Tindakan Korektif & Otomasi:** *Tracking* pengembalian dana (*Recovery*) dengan metrik SLA.")
    st.success("🎯 **Target Recovery:** Minimal 80% dana ditarik kembali dalam batas SLA (14 Hari).")
    
    # Logika Data Jalur Resolusi
    df_recovery = df_bocor.copy()
    df_recovery['Jalur_Resolusi'] = np.where(df_recovery['Branch_ID'] == 'JGK', 'Klaim EDC Bank', 'Investigasi Internal HR')
    
    total_leakage = df_bocor['Gross_Sales'].sum()
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Risiko Finansial", f"Rp {total_leakage:,.0f}")
    with m2: st.metric("Target Recovery EDC", f"Rp {df_bocor[df_bocor['Branch_ID']=='JGK']['Gross_Sales'].sum():,.0f}")
    with m3: st.metric("Tindak Lanjut HR", f"Rp {df_bocor[df_bocor['Branch_ID'].isin(['KBY','BTR'])]['Gross_Sales'].sum():,.0f}")
    with m4: st.metric("Estimasi Dana Kembali", f"Rp {total_leakage*0.8:,.0f}", "Minimal 80%")

    st.markdown("<br>", unsafe_allow_html=True)
    col_d, col_b = st.columns([4, 6])
    
    # REVISI: Mengembalikan Donut Chart ke Jalur Resolusi (Bank vs HR) agar konsisten dengan postingan
    with col_d: 
        fig_res = px.pie(df_recovery, values='Gross_Sales', names='Jalur_Resolusi', hole=0.5, 
                         title="🔵 Jalur Resolusi Dana",
                         color='Jalur_Resolusi',
                         color_discrete_map={'Klaim EDC Bank':'#1976D2', 'Investigasi Internal HR':'#FBC02D'})
        fig_res.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_res, use_container_width=True)
        
    with col_b: 
        st.markdown("#### 📑 Rencana Tindakan Executive")
        st.dataframe(pd.DataFrame({"Cabang": ["JGK", "KBY", "BTR"], "Masalah": ["EDC Gagal", "Selisih Stok", "Selisih Stok"], "Trigger": ["Auto-Email Bank", "Telegram SPV", "Telegram SPV"], "Tindakan": ["Monitor SLA", "Audit & HR", "Audit & HR"]}), use_container_width=True)

    st.info("#### ➡️ **Next Step:** Proyeksi dampak *cashflow* pasca-recovery dimodelkan di **Fase 4: Forecasting**.")

# =====================================================================
# TAMPILAN FASE 4
# =====================================================================
elif modul == "Fase 4: Cashflow Forecasting (Proyeksi Masa Depan)":
    st.markdown("📈 **Financial Stress Test:** Proyeksi sisa uang tunai (*Cash Runway*) berdasarkan asumsi pemulihan dana.")
    
    col_inp1, col_inp2 = st.columns(2)
    with col_inp1:
        recovery_rate = st.slider("Target Recovery (%)", 0, 100, 80, 5, key="state_recovery")
    with col_inp2:
        monthly_opex_juta = st.slider("Asumsi Pengeluaran (OpEx) - Juta Rp", 100, 500, 250, 10, key="state_opex")
    
    st.caption("**Asumsi Kas Awal:** Rp 500 Juta (Estimasi saldo operasional)")
    
    monthly_opex = monthly_opex_juta * 1000000
    base_cash = 500000000 
    total_leakage = df_bocor['Gross_Sales'].sum()
    recovered_funds = total_leakage * (recovery_rate / 100)
    new_cash_balance = base_cash + recovered_funds
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Dana Diselamatkan", f"Rp {recovered_funds:,.0f}")
    with c2: st.metric("Cash Runway (Baseline)", f"{base_cash/monthly_opex:.1f} Bln")
    with c3: st.metric("Runway + Recovery", f"{new_cash_balance/monthly_opex:.1f} Bln")

    st.markdown("<br>", unsafe_allow_html=True)
    
    months = np.arange(0, 13)
    cash_baseline = [max(0, base_cash - (monthly_opex * m)) for m in months]
    cash_scenario = [max(0, new_cash_balance - (monthly_opex * m)) for m in months]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=cash_baseline, name='Baseline', line=dict(color='#E53935', dash='dot')))
    fig.add_trace(go.Scatter(x=months, y=cash_scenario, name='Scenario', line=dict(color='#43A047', width=4), fill='tonexty'))
    
    fig.update_layout(
        title="📉 Proyeksi Penurunan Kas (12 Bulan)",
        xaxis=dict(title="Bulan Ke-", tickmode='linear', dtick=1),
        yaxis=dict(title="Sisa Kas (Rp)"),
        hovermode="x unified",
        height=500
    )
    
    runway_val = new_cash_balance / monthly_opex
    if runway_val <= 12:
        fig.add_annotation(x=runway_val, y=0, text=f"Zero Cash: Bln {runway_val:.1f}", showarrow=True, arrowhead=1, bgcolor="#43A047", font=dict(color="white"))

    st.plotly_chart(fig, use_container_width=True)
    st.success(f"**Kesimpulan:** Dengan recovery {recovery_rate}%, Anda mendapatkan tambahan waktu operasional kritis selama **{((new_cash_balance/monthly_opex)-(base_cash/monthly_opex))*30:.0f} hari**.")