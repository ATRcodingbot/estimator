import streamlit as st
from fpdf import FPDF
import csv
import os
import re
import pandas as pd

# ----- Estimate Calculation -----
def estimate_project(project_type, length, width=None, height=None, material="pressure-treated wood", markup=0):
    labor_rate = 65
    rates = {
        "deck": {"pressure-treated wood": 25, "composite": 45, "PVC": 50},
        "patio": {"concrete": 15, "pavers": 22, "stone": 30},
        "fence": {"wood": 30, "vinyl": 40, "chain-link": 20}
    }

    sqft = length * (width if width else height if project_type == "fence" else 1)
    material_cost_per_sqft = rates[project_type].get(material, 25)
    material_cost = material_cost_per_sqft * sqft
    labor_hours = sqft / 20
    labor_cost = labor_hours * labor_rate
    base_total = material_cost + labor_cost
    total_cost = base_total * (1 + markup / 100)

    return {
        "sqft": sqft,
        "material_cost": round(material_cost, 2),
        "labor_cost": round(labor_cost, 2),
        "total_estimate": round(total_cost, 2),
        "duration_days": round(labor_hours / 8, 1)
    }

# ----- PDF Generation -----
def generate_pdf(data, project_type, material):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"{project_type.title()} Estimate", ln=True)
    pdf.cell(200, 10, f"Material: {material}", ln=True)
    for key, value in data.items():
        pdf.cell(200, 10, f"{key.replace('_', ' ').title()}: {value}", ln=True)
    pdf.output("estimate.pdf")

# ----- Save to CSV -----
def save_to_csv(data, client_name, client_email, address, filename="mhic_estimates.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            headers = ["Name", "Email", "Address"] + list(data.keys())
            writer.writerow(headers)
        row = [client_name, client_email, address] + list(data.values())
        writer.writerow(row)

# ----- ZIP Code Check -----
def zip_requires_permit(address):
    match = re.search(r"\b(21\d{3})\b", address)
    if match:
        zip_code = int(match.group(1))
        return zip_code in [21201, 21230, 21740]  # Customize this list
    return False

# ----- Streamlit UI -----
st.set_page_config(page_title="MHIC Estimate Tool", layout="centered")
st.title("📐 MHIC Estimator Tool (Maryland)")

project_type = st.selectbox("Project Type", ["deck", "patio", "fence"])
length = st.number_input("Length (ft)", min_value=1)

if project_type in ["deck", "patio"]:
    width = st.number_input("Width (ft)", min_value=1)
    height = None
else:
    height = st.number_input("Height (ft)", min_value=1)
    width = None

material = st.selectbox("Material", {
    "deck": ["pressure-treated wood", "composite", "PVC"],
    "patio": ["concrete", "pavers", "stone"],
    "fence": ["wood", "vinyl", "chain-link"]
}[project_type])

markup = st.slider("Markup %", 0, 50, 20)

st.subheader("Client Info")
client_name = st.text_input("Name")
client_email = st.text_input("Email")
client_address = st.text_area("Project Address")

st.subheader("Project Files (optional)")
uploaded_files = st.file_uploader("Upload photos or sketches", accept_multiple_files=True)

if st.button("Calculate Estimate"):
    result = estimate_project(project_type, length, width, height, material, markup)
    st.success(f"Total Estimate: ${result['total_estimate']}")
    st.write(result)

    if zip_requires_permit(client_address):
        st.info("⚠️ This ZIP Code may require a permit in Maryland.")

    if client_name and client_email:
        save_to_csv(result, client_name, client_email, client_address)
        st.success("Saved to mhic_estimates.csv!")
    else:
        st.warning("Client name and email are required to save.")

    if st.button("Generate PDF"):
        generate_pdf(result, project_type, material)
        st.success("PDF saved as estimate.pdf")

# ----- Optional: Show Past Estimates -----
if os.path.exists("mhic_estimates.csv"):
    st.subheader("📊 Past Estimates")
    df = pd.read_csv("mhic_estimates.csv")
    st.dataframe(df)
