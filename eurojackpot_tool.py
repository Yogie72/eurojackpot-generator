import streamlit as st
import pandas as pd
import random
import io
from fpdf import FPDF

# 📈 Häufigste und seltenste Zahlen (Beispielwerte vom aktuellen Datensatz)
hot = [20,34,49,11,17]     # meist gezogen
cold = [25,33,19,5,40]    # am seltensten

st.title("🎯 Eurojackpot Tipp-Generator + Statistik")
st.markdown("Wähle Optionen & generiere Tipps, inkl. Download als Excel oder PDF")

# Optionale Strategien
anzahl = st.slider("Anzahl Tipps:", 1, 10, 5)
use_hot = st.checkbox("Bevorzuge häufig gezogene Zahlen (Hot)", value=False)
use_cold = st.checkbox("Bevorzuge seltene Zahlen (Cold)", value=False)
parity = st.checkbox("Mische gerade/ungerade (2–3)", True)
range_mix = st.checkbox("Mische hoch/niedrig (2–3 ≤25)", True)

def valid_comb(pick):
    if parity:
        even = sum(n%2==0 for n in pick)
        if even<2 or even>3: return False
    if range_mix:
        low = sum(n<=25 for n in pick)
        if low<2 or low>3: return False
    return True

tips = []
for _ in range(anzahl):
    while True:
        pool = list(range(1,51))
        if use_hot:
            pool += hot*2
        if use_cold:
            pool += cold*2
        pick = sorted(random.sample(pool, 5))
        if valid_comb(set(pick)):
            euro = sorted(random.sample(range(1,13), 2))
            tips.append((pick, euro))
            break

# Ergebnisdaten
df = pd.DataFrame([{"Zahlen": tup[0], "Eurozahlen": tup[1]} for tup in tips])
st.table(df)

# 📥 Download als Excel
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Tipps")
excel_data = buffer.getvalue()
st.download_button("Excel herunterladen", excel_data, file_name="eurojackpot_tipps.xlsx", mime="application/vnd.ms-excel")

# 📄 PDF-Report generieren
if st.button("PDF generieren"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Eurojackpot Tipps", ln=True)
    pdf.ln(5)
    for idx, (p, e) in enumerate(tips, 1):
        pdf.cell(0, 8, f"Tipp {idx}: {p} + Eurozahlen: {e}", ln=True)
    pdf_bytes = pdf.output(dest="S").encode('latin-1')
    b64 = io.base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="tipps.pdf">PDF herunterladen</a>'
    st.markdown(href, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import random
import plotly.express as px

st.set_page_config(page_title="Eurojackpot Tipp-Tool", layout="centered")

st.title("Eurojackpot Tipp-Tool mit Statistik")

# --- Beispiel-Daten: Häufigkeit der Zahlen (1 bis 50) ---
# Hier kannst du später deine echten Daten reinladen
zahlen_haeufigkeit = {
    1: 85, 2: 42, 3: 58, 4: 33, 5: 77,
    6: 49, 7: 95, 8: 22, 9: 60, 10: 55,
    11: 70, 12: 15, 13: 38, 14: 80, 15: 44,
    16: 29, 17: 66, 18: 90, 19: 35, 20: 50,
    21: 28, 22: 43, 23: 62, 24: 27, 25: 72,
    26: 31, 27: 48, 28: 53, 29: 36, 30: 40,
    31: 75, 32: 20, 33: 55, 34: 63, 35: 47,
    36: 37, 37: 67, 38: 58, 39: 30, 40: 52,
    41: 39, 42: 69, 43: 22, 44: 44, 45: 73,
    46: 26, 47: 41, 48: 50, 49: 59, 50: 34
}

# Umwandeln in DataFrame
df_stat = pd.DataFrame({
    'Zahl': list(zahlen_haeufigkeit.keys()),
    'Häufigkeit': list(zahlen_haeufigkeit.values())
})

# --- Visualisierung ---
fig = px.bar(df_stat, x='Zahl', y='Häufigkeit',
             title='Häufigkeit der Eurojackpot-Zahlen',
             labels={'Zahl': 'Zahl', 'Häufigkeit': 'Anzahl Ziehungen'},
             color='Häufigkeit', color_continuous_scale='Viridis')

st.plotly_chart(fig, use_container_width=True)

# --- Hot- und Cold-Zahlen berechnen ---
anzahl_hot_cold = 10  # Anzahl der Hot/Cold Zahlen

hot = sorted(df_stat.sort_values('Häufigkeit', ascending=False)['Zahl'][:anzahl_hot_cold])
cold = sorted(df_stat.sort_values('Häufigkeit', ascending=True)['Zahl'][:anzahl_hot_cold])

st.markdown(f"**Hot-Zahlen (am häufigsten gezogen):** {hot}")
st.markdown(f"**Cold-Zahlen (am seltensten gezogen):** {cold}")

# --- Tipp-Generator ---
st.header("Tipp-Generator")

anzahl_tipps = st.slider("Wie viele Tipps möchtest du generieren?", min_value=1, max_value=10, value=3)
st.markdown("Tipps werden aus Hot- und Cold-Zahlen gemischt: 3 Hot + 2 Cold pro Tipp.")

def generiere_tipp():
    tipp = random.sample(hot, 3) + random.sample(cold, 2)
    return sorted(tipp)

tipps = [generiere_tipp() for _ in range(anzahl_tipps)]

for i, tipp in enumerate(tipps, 1):
    st.write(f"Tipp {i}: {tipp}")
