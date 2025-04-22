from fpdf import FPDF
import os

def generate_pdf(data, project_type, material, client_name, client_email, client_phone, client_address):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add logo (top-left)
    logo_path = "logo.png"  # Make sure this is in the root or accessible path
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)

    # Add header title
    pdf.set_xy(50, 10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Mike's Contracting", ln=True, align="C")

    # Move cursor below logo/header
    pdf.set_y(35)
    pdf.set_font("Arial", size=12)

    # Client and project info
    pdf.cell(200, 10, f"{project_type} Estimate", ln=True)
    pdf.cell(200, 10, f"Client: {client_name}", ln=True)
    pdf.cell(200, 10, f"Email: {client_email}", ln=True)
    pdf.cell(200, 10, f"Phone: {client_phone}", ln=True)
    pdf.cell(200, 10, f"Address: {client_address}", ln=True)
    pdf.cell(200, 10, f"Material: {material}", ln=True)
    pdf.ln(10)

    for key, value in data.items():
        pdf.cell(200, 10, f"{key.replace('_', ' ').title()}: {value}", ln=True)

    # Footer
    pdf.set_y(-30)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Mike", ln=True, align="C")
    pdf.cell(0, 10, "443-467-0899", ln=True, align="C")
    pdf.cell(0, 10, "www.Attractiveremodels.com", ln=True, align="C")

    # Output as bytes
    return pdf.output(dest='S').encode('latin1')
