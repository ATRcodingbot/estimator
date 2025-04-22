import streamlit as st
from fpdf import FPDF
import re
import io

# ----- Estimate Calculation -----
def estimate_project(project_type, length, width=None, height=None, material="Pressure-treated wood"):
    labor_rate = 65
    rates = {
        "Deck": {"Pressure-treated wood": 25, "Composite": 45, "PVC": 50},
        "Patio": {"Concrete": 15, "Pavers": 22, "Stone": 30},
        "Fence": {"Wood": 30, "Vinyl": 40, "Chain-link": 20}
    }

    sqft = length * (width if width else height if project_type == "Fence" else 1)
    material_cost_per_sqft = rates[project_type].get(material, 25)
    material_cost = material_cost_per_sqft * sqft
    total_cost = material_cost * 3.2
    labor_hours = sqft / 20
    labor_cost = labor_hours * labor_rate
    down_payment = total_cost / 3
    duration_days = round(labor_hours / 8, 1)

    return {
        "sqft": round(sqft, 2),
        "material_cost": round(material_cost, 2),
        "labor_cost": round(labor_cost, 2),
        "total_estimate": round(total_cost, 2),
        "down_payment": round(down_payment, 2),
        "duration_days": duration_days
    }

# ----- Generate PDF in Memory -----
def generate_pdf(data, project_type, material, client_name, client_email, client_phone, client_address):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, f"{project_type} Estimate", ln=True)
    pdf.cell(200, 10, f"Client: {client_name}", ln=True)
    pdf.cell(200, 10, f"Email: {client_email}", ln=True)
    pdf.cell(200, 10, f"Phone: {client_phone}", ln=True)
    pdf.cell(200, 10, f"Address: {client_address}", ln=True)
    pdf.cell(200, 10, f"Material: {material}", ln=True)
    pdf.ln(10)

    for key, value in data.items():
        pdf.cell(200, 10, f"{key.replace('_', ' ').title()}: {value}", ln=True)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# ----- ZIP Code Check -----
def zip_requires_permit(address):
    match = re.search(r"\b(21\d{3})\b", address)
    if match:
        zip_code = int(match.group(1))
        return zip_code in [21201, 21230, 21740]
    return False

# ----- Streamlit UI -----
st.set_page_config(page_title="MHIC Estimate Tool", layout="centered")
st.title("📐 MHIC Estimator Tool (Maryland)")

project_type = st.selectbox("Project Type", ["Deck", "Patio", "Fence"])

material_options = {
    "Deck": ["Pressure-treated wood", "Composite", "PVC"],
    "Patio": ["Concrete", "Pavers", "Stone"],
    "Fence": ["Wood", "Vinyl", "Chain-link"]
}

length = st.number_input("Length (ft)", min_value=1)
width = None
height = None

if project_type in ["Deck", "Patio"]:
    width = st.number_input("Width (ft)", min_value=1)
else:
    height = st.number_input("Height (ft)", min_value=1)

material = st.selectbox("Material", material_options[project_type])

st.subheader("Client Info")
client_name = st.text_input("Name")
client_email = st.text_input("Email")
client_phone = st.text_input("Phone Number")
client_address = st.text_area("Project Address")

st.subheader("Project Files (optional)")
uploaded_files = st.file_uploader("Upload photos or sketches", accept_multiple_files=True)

if st.button("Calculate Estimate"):
    result = estimate_project(project_type, length, width, height, material)
    st.success(f"Total Estimate: ${result['total_estimate']}")
    st.write(result)

    if zip_requires_permit(client_address):
        st.info("⚠️ This ZIP Code may require a permit in Maryland.")

    if client_name and client_email and client_phone:
        st.success("Client info validated. Ready to generate PDF.")
        
        pdf_bytes = generate_pdf(result, project_type, material, client_name, client_email, client_phone, client_address)
        st.download_button(
            label="📄 Download Estimate PDF",
            data=pdf_bytes,
            file_name=f"{client_name.replace(' ', '_')}_estimate.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please complete client info to generate a downloadable PDF.")
