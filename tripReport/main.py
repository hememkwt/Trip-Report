import os
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
from datetime import datetime

# Get script & template directory - FIXED FOR STREAMLIT CLOUD
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
templates_dir = os.path.join(script_dir, "templates")
assets_dir = os.path.join(script_dir, "assets")

# -------- LINK CALLBACK --------
def link_callback(uri, rel):
    if uri.startswith('assets/'):
        filename = uri.replace('assets/', '')
        path = os.path.join(assets_dir, filename)
        if os.path.exists(path):
            return path
    path = os.path.join(script_dir, uri)
    if os.path.exists(path):
        return path
    return uri

# -------- HEADER --------
st.set_page_config(
    page_title="Trip Report Generator",
    page_icon="🚛",
    layout="wide"
)
st.header("Trip Report Generator")

# -------- HIDE +/- BUTTONS --------
st.markdown("""
    <style>
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# -------- USER INPUTS --------
col1, col2 = st.columns(2)
with col1:
    print_date = st.date_input(
        "Print Date",
        value=datetime.now().date()
    )
    ticket_no = st.text_input("Ticket No")
    vehicle_no = st.text_input("Vehicle No", value="91/56491")
    gross_weight = st.number_input(
        "Gross Weight (ton)",
        min_value=0.0,
        format="%.0f",
        value=0.0
    )
    float_glass_input = st.number_input(
        "Float Glass (ton)",
        min_value=0.0,
        format="%.0f",
        value=0.0
    )
with col2:
    print_time = st.text_input(
        "Print Time",
        placeholder="HH:MM:SS"
    )
    customer = st.selectbox(
        "Customer",
        options=["Avenues Mall", "360 Mall", "Khiran Mall"]
    )
    material = st.selectbox(
        "Material",
        options=["Bottle Glass", "Mixed Glass"]
    )
    tare_weight = st.number_input(
        "Tare Weight (ton)",
        min_value=0.0,
        format="%.0f",
        value=0.0
    )

# -------- NET WEIGHT & FLOAT GLASS CALCULATION --------
st.markdown("---")

# If float glass is entered → net = gross - tare + float_glass
# If float glass is 0 → net = gross - tare
if float_glass_input > 0:
    net_weight = gross_weight - tare_weight + float_glass_input
    float_glass_display = f"{float_glass_input:.3f}"
else:
    net_weight = gross_weight - tare_weight
    float_glass_display = "0.000"

col_a, col_b, col_c = st.columns(3)
with col_b:
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; background-color: #f0f2f6;
                border-radius: 10px; border: 2px solid #ff4b4b;'>
        <h3 style='color: #333; margin-bottom: 10px;'>NET WEIGHT</h3>
        <h1 style='color: #ff4b4b; margin: 0; font-size: 2.5em;'>
            {net_weight:.2f} ton
        </h1>
    </div>
    """, unsafe_allow_html=True)

# -------- PDF GENERATION --------
st.markdown("---")
button_container = st.container()
with button_container:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "**📄 GENERATE PDF**",
            type="primary",
            use_container_width=True
        ):
            print_time_str = print_time
            print_date_str = print_date.strftime("%d/%m/%Y")
            if net_weight <= 0:
                st.error("Net weight must be greater than 0 to generate PDF!")
            else:
                try:
                    env = Environment(loader=FileSystemLoader(templates_dir))
                    template = env.get_template("invoice.html")
                    recycled_glass = net_weight
                    landfill_m3 = net_weight * 2 * 0.7646
                    water_liters = net_weight * 30 * 3.78541
                    energy_kwh = net_weight * 47
                    co2_kg = net_weight * 315
                    html_out = template.render(
                        print_date=print_date_str,
                        print_time=print_time_str,
                        ticket_no=ticket_no,
                        vehicle_no=vehicle_no,
                        customer=customer,
                        material=material,
                        gross_weight=f"{gross_weight:.3f}",
                        tare_weight=f"{tare_weight:.3f}",
                        net_weight=f"{net_weight:.3f}",
                        float_glass=float_glass_display,
                        recycled_glass=f"{recycled_glass:.2f}",
                        water_liters=f"{water_liters:,.0f}",
                        co2_kg=f"{co2_kg:,.0f}",
                        energy_kwh=f"{energy_kwh:,.0f}",
                        landfill_m3=f"{landfill_m3:.2f}"
                    )
                    pdf_buffer = io.BytesIO()
                    pisa_status = pisa.CreatePDF(
                        html_out,
                        dest=pdf_buffer,
                        link_callback=link_callback,
                        encoding='UTF-8'
                    )
                    if pisa_status.err:
                        st.error(f"PDF generation failed: {pisa_status.err}")
                    else:
                        pdf_buffer.seek(0)
                        st.download_button(
                            "**📥 DOWNLOAD PDF NOW**",
                            pdf_buffer,
                            file_name=f"trip_report_{print_date_str.replace('/', '')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# -------- FOOTER INFO --------
st.caption(
    f"📅 Current date: {datetime.now().strftime('%d/%m/%Y')} | "
    "⏰ PDFs use generation timestamp"
)
