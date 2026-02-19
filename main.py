import os
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

# Get script & template directory
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
assets_dir = os.path.join(script_dir, "assets")

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

# -------- PDF GENERATION WITH REPORTLAB --------
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
                    # Calculate impact
                    recycled_glass = net_weight
                    landfill_m3 = net_weight * 2 * 0.7646
                    water_liters = net_weight * 30 * 3.78541
                    energy_kwh = net_weight * 47
                    co2_kg = net_weight * 315
                    
                    # Create PDF
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=A4)
                    width, height = A4
                    
                    # Add logo (centered, at top)
                    logo_path = os.path.join(assets_dir, "logo.png")
                    if os.path.exists(logo_path):
                        c.drawImage(logo_path, width/2 - 106, height - 120, width=212, height=80, preserveAspectRatio=True, mask='auto')
                    
                    # Add arabic text image (centered, below logo)
                    arabic_path = os.path.join(assets_dir, "arabic-text.png")
                    if os.path.exists(arabic_path):
                        c.drawImage(arabic_path, width/2 - 185, height - 180, width=370, height=58, preserveAspectRatio=True, mask='auto')
                    
                    # Title
                    c.setFont("Helvetica-Bold", 22)
                    c.drawCentredString(width/2, height - 220, "TRIP REPORT")
                    
                    # Info table
                    y = height - 270
                    c.setFont("Helvetica", 11)
                    
                    # Row 1
                    c.drawString(50, y, "PRINT DATE")
                    c.drawString(170, y, f": {print_date_str}")
                    c.drawString(320, y, "PRINT TIME")
                    c.drawString(440, y, f": {print_time_str}")
                    
                    # Row 2
                    y -= 20
                    c.drawString(50, y, "TICKET NO.")
                    c.drawString(170, y, f": {ticket_no}")
                    c.drawString(320, y, "VEHICLE NO.")
                    c.drawString(440, y, f": {vehicle_no}")
                    
                    # Row 3
                    y -= 20
                    c.drawString(50, y, "CUSTOMER")
                    c.drawString(170, y, f": {customer}")
                    c.drawString(320, y, "MATERIAL")
                    c.drawString(440, y, f": {material}")
                    
                    # Row 4
                    y -= 20
                    c.drawString(50, y, "GROSS WEIGHT (ton)")
                    c.drawString(170, y, f": {gross_weight:.3f}")
                    c.drawString(320, y, "TARE WEIGHT (ton)")
                    c.drawString(440, y, f": {tare_weight:.3f}")
                    
                    # Row 5
                    y -= 20
                    c.drawString(50, y, "FLOAT GLASS (ton)")
                    c.drawString(170, y, f": {float_glass_display}")
                    c.drawString(320, y, "NET WEIGHT (ton)")
                    c.drawString(440, y, f": {net_weight:.3f}")
                    
                    # Impact section title
                    y -= 50
                    c.setFont("Helvetica-Bold", 20)
                    c.drawCentredString(width/2, y, "Impact calculation")
                    
                    # Impact subtitle
                    y -= 30
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(width/2, y, f"{recycled_glass:.2f} tons of Recycled Glass Saves:")
                    
                    # Green impact table
                    y -= 50
                    table_width = 305
                    table_x = (width - table_width) / 2
                    row_height = 50
                    
                    # Draw green background
                    c.setFillColorRGB(0.24, 0.64, 0.27)  # #3EA446
                    c.rect(table_x, y - row_height*4, table_width, row_height*4, fill=1, stroke=0)
                    
                    # Draw black lines between rows
                    c.setStrokeColorRGB(0, 0, 0)
                    c.setLineWidth(1)
                    for i in range(1, 4):
                        c.line(table_x, y - row_height*i, table_x + table_width, y - row_height*i)
                    
                    # Set white text color
                    c.setFillColorRGB(1, 1, 1)
                    c.setFont("Helvetica-Bold", 12)
                    
                    # Row 1: Water
                    icon_path = os.path.join(assets_dir, "water.png")
                    if os.path.exists(icon_path):
                        c.drawImage(icon_path, table_x + 20, y - 43, width=30, height=30, mask='auto')
                    c.drawString(table_x + 70, y - 28, "Water")
                    c.drawRightString(table_x + table_width - 20, y - 28, f"{water_liters:,.0f} Liter")
                    
                    # Row 2: CO2
                    y -= row_height
                    icon_path = os.path.join(assets_dir, "co2.png")
                    if os.path.exists(icon_path):
                        c.drawImage(icon_path, table_x + 20, y - 43, width=30, height=30, mask='auto')
                    c.drawString(table_x + 70, y - 28, "CO2 Emissions")
                    c.drawRightString(table_x + table_width - 20, y - 28, f"{co2_kg:,.0f} kg")
                    
                    # Row 3: Energy
                    y -= row_height
                    icon_path = os.path.join(assets_dir, "energy.png")
                    if os.path.exists(icon_path):
                        c.drawImage(icon_path, table_x + 20, y - 43, width=30, height=30, mask='auto')
                    c.drawString(table_x + 70, y - 28, "Energy")
                    c.drawRightString(table_x + table_width - 20, y - 28, f"{energy_kwh:,.0f} kWh")
                    
                    # Row 4: Landfill
                    y -= row_height
                    icon_path = os.path.join(assets_dir, "landfill.png")
                    if os.path.exists(icon_path):
                        c.drawImage(icon_path, table_x + 20, y - 43, width=30, height=30, mask='auto')
                    c.drawString(table_x + 70, y - 28, "Landfill")
                    c.drawRightString(table_x + table_width - 20, y - 28, f"{landfill_m3:.2f} M³")
                    
                    # Footer
                    c.setFillColorRGB(0.4, 0.4, 0.4)
                    c.setFont("Helvetica", 10)
                    c.drawCentredString(width/2, 60, "Mangaf - Block 4 - St 201 - Parcel 5410 - Mall 18 - Floor 1 M - Shop 3")
                    c.drawCentredString(width/2, 45, "Tel: +965660716969 / +96598888955")
                    c.drawCentredString(width/2, 30, "Email: Hemam@Hemam.green")
                    
                    c.save()
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
)