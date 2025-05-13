# JS SEO Analyzer (Prototype - v1)

import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from datetime import date

st.set_page_config(page_title="JS SEO Analyzer", layout="centered")
st.title("📈 JS SEO Analyzer")
st.markdown("Upload your Google Search Console **queries.csv** or ZIP export file to begin SEO analysis.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload Search Console File", type=["csv", "zip"])

if uploaded_file:
    if uploaded_file.name.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            filenames = z.namelist()
            csv_files = [f for f in filenames if f.endswith("Queries.csv")]
            if not csv_files:
                st.error("No Queries.csv file found in ZIP.")
            else:
                df = pd.read_csv(z.open(csv_files[0]))
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        st.error("Unsupported file format.")

    # --- Clean Columns ---
    df.columns = [col.strip().capitalize() for col in df.columns]

    st.success("✅ File uploaded successfully!")

    # --- Summary Stats ---
    st.subheader("📊 Overview")
    st.write(f"**Total Queries:** {len(df)}")
    st.write(f"**Date:** {date.today().strftime('%B %d, %Y')}")

    top_clicks = df.sort_values("Clicks", ascending=False).head(10)
    low_ctr = df[df['Ctr'] < 0.05].sort_values("Ctr")
    high_impr_low_click = df[(df['Impressions'] > 50) & (df['Clicks'] < 3)].sort_values("Impressions", ascending=False)

    st.subheader("🔥 Top 10 Click Queries")
    st.dataframe(top_clicks[['Query', 'Clicks', 'Impressions', 'Ctr', 'Position']])

    st.subheader("⚠️ Low CTR Queries (< 5%)")
    st.dataframe(low_ctr[['Query', 'Clicks', 'Impressions', 'Ctr', 'Position']])

    st.subheader("👀 High Impression, Low Click Queries")
    st.dataframe(high_impr_low_click[['Query', 'Clicks', 'Impressions', 'Ctr', 'Position']])

    # --- Suggestions ---
    st.subheader("🧠 Suggested Improvements")
    st.markdown("**1. Create articles around queries with high impressions but low clicks.**")
    st.markdown("**2. Improve titles/meta for queries with CTR < 5%.**")
    st.markdown("**3. Add internal links to related posts ranking on position > 20.**")

    # --- Export to PDF ---
    from fpdf import FPDF

    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="JS SEO Analyzer Report", ln=True, align="C")
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Generated: {date.today().strftime('%B %d, %Y')}", ln=True)
        pdf.ln()

        pdf.set_font("Arial", 'B', size=11)
        pdf.cell(200, 10, txt="Top 5 High Impression Low Click Queries:", ln=True)
        pdf.set_font("Arial", size=10)

        top5 = high_impr_low_click[['Query', 'Impressions', 'Clicks']].head(5)
        for idx, row in top5.iterrows():
            pdf.multi_cell(0, 10, txt=f"- {row['Query']} | Impr: {row['Impressions']}, Clicks: {row['Clicks']}")

        pdf.ln()
        pdf.set_font("Arial", 'B', size=11)
        pdf.cell(200, 10, txt="SEO Tips:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, txt="\n1. Improve CTR queries with low click-through-rate.\n2. Target high impression queries with blog content.\n3. Use long-tail keywords from these queries in H1/H2 tags.")

        return pdf.output(dest='S').encode('latin-1')

    if st.button("📥 Download PDF Report"):
        pdf_bytes = generate_pdf()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="js_seo_report.pdf">Click here to download your PDF report</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("Please upload a Search Console export file to begin.")
