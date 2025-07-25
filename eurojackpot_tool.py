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
    writer.save()
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
