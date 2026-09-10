from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
from ultralytics import YOLO
 
PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from robot_vision import RobotVisionSystem
from robot_vision import save_detection
from robot_vision import get_detection_history
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart Warehouse Management",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

.main-title {
    width: 100%;
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    line-height: 1.25;
    padding: 10px 5px;
    margin-bottom: 4px;
    overflow-wrap: break-word;
}

.subtitle {
    width: 100%;
    text-align: center;
    font-size: 16px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 15px;
}

.metric-card {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.25);
    text-align: center;
    min-height: 120px;
}

.metric-title {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 24px;
    font-weight: 800;
}

.robot-card {
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "products.csv"

# =========================================================
# YOLO AI MODEL
# =========================================================

YOLO_MODEL = "yolo11n.pt"

try:
    yolo_model = YOLO(YOLO_MODEL)
    YOLO_AVAILABLE = True

except Exception as e:
    yolo_model = None
    YOLO_AVAILABLE = False
    YOLO_ERROR = str(e)

try:
    df = pd.read_csv(DATA_FILE)
except Exception:
    df = pd.DataFrame()

# =========================================================
# COLUMN DETECTION
# =========================================================
def find_column(possible_names):
    for name in possible_names:
        for col in df.columns:
            if str(col).strip().lower() == name.lower():
                return col
    return None


product_id_col = find_column(
    ["Product_ID", "Product ID", "ID"]
)

product_name_col = find_column(
    ["Product_Name", "Product Name", "Name"]
)

category_col = find_column(
    ["Category", "Product_Category"]
)

quantity_col = find_column(
    ["Quantity", "Stock", "Stock_Quantity"]
)

price_col = find_column(
    ["Price", "Unit_Price"]
)

reorder_col = find_column(
    ["Reorder_Level", "Reorder Level", "Reorder"]
)

warehouse_col = find_column(
    ["Warehouse_Section", "Warehouse Section", "Section"]
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 📦 SMART WAREHOUSE")
st.sidebar.caption("Inventory & Analytics System")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MAIN MENU",
    [
        "🏠 Dashboard",
        "📦 Products",
        "📊 Analytics",
        "⚠️ Low Stock",
        "🤖 Robot Vision",
        "🕒 Vision History",
        "📋 Reports",
        "ℹ️ About"
    ]
)
st.sidebar.markdown("---")

st.sidebar.info(
    "Smart Warehouse\n"
    "Advanced Inventory Management\n\n"
    "Version 3.0"
)

# =========================================================
# EMPTY DATA CHECK
# =========================================================
if df.empty:
    st.error(
        "products.csv file not found.\n\n"
        "Expected location: data/products.csv"
    )
    st.stop()

# =========================================================
# CALCULATIONS
# =========================================================
total_products = len(df)

if quantity_col:
    quantity = pd.to_numeric(
        df[quantity_col],
        errors="coerce"
    ).fillna(0)
else:
    quantity = pd.Series(
        [0] * len(df),
        index=df.index
    )

total_stock = quantity.sum()

if quantity_col and price_col:
    price = pd.to_numeric(
        df[price_col],
        errors="coerce"
    ).fillna(0)

    inventory_value = (quantity * price).sum()
else:
    inventory_value = 0

# =========================================================
# LOW STOCK CALCULATION
# =========================================================
if quantity_col and reorder_col:

    reorder = pd.to_numeric(
        df[reorder_col],
        errors="coerce"
    ).fillna(0)

    quantity = pd.to_numeric(
        quantity,
        errors="coerce"
    ).fillna(0)

    reorder = pd.to_numeric(
        reorder,
        errors="coerce"
    ).fillna(0)

    low_stock_mask = quantity <= reorder
    low_stock_count = int(
        low_stock_mask.sum()
    )

else:

    low_stock_mask = pd.Series(
        [False] * len(df),
        index=df.index
    )

    low_stock_count = 0

# =========================================================
# AUTOMATIC LOW STOCK ALERT
# =========================================================

if low_stock_count > 0:

    st.sidebar.warning(
        f"⚠️ Low Stock Alert: {low_stock_count} product(s) need attention!"
    )

else:

    st.sidebar.success(
        "✅ Stock Status: All products are above reorder level."
    )
# =========================================================
# DASHBOARD
# =========================================================
if menu == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">'
        'Smart Warehouse Management Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Real-time inventory monitoring & analytics'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">TOTAL PRODUCTS</div>
                <div class="metric-value">📦 {total_products}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">TOTAL STOCK</div>
                <div class="metric-value">📊 {total_stock:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">INVENTORY VALUE</div>
                <div class="metric-value">₹ {inventory_value:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">LOW STOCK ITEMS</div>
                <div class="metric-value">⚠️ {low_stock_count}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📊 Inventory Overview</div>',
        unsafe_allow_html=True
    )

    if category_col and quantity_col:

        chart_df = df.copy()

        chart_df[quantity_col] = pd.to_numeric(
            chart_df[quantity_col],
            errors="coerce"
        ).fillna(0)

        category_data = (
            chart_df
            .groupby(category_col)[quantity_col]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            category_data,
            x=category_col,
            y=quantity_col,
            title="Stock by Category",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================================================
# PRODUCTS
# =========================================================
elif menu == "📦 Products":

    st.title("📦 Product Management")

    search = st.text_input(
        "🔍 Search Product"
    )

    display_df = df.copy()

    if search and product_name_col:
        display_df = display_df[
            display_df[product_name_col]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# ANALYTICS
# =========================================================
elif menu == "📊 Analytics":

    st.title("📊 Warehouse Analytics")

    a1, a2, a3 = st.columns(3)

    with a1:
        st.metric(
            "Total Products",
            total_products
        )

    with a2:
        st.metric(
            "Total Stock",
            f"{total_stock:,.0f}"
        )

    with a3:
        st.metric(
            "Inventory Value",
            f"₹ {inventory_value:,.0f}"
        )

    if category_col and quantity_col:

        st.subheader("📦 Category-wise Stock")

        analytics_df = df.copy()

        analytics_df[quantity_col] = pd.to_numeric(
            analytics_df[quantity_col],
            errors="coerce"
        ).fillna(0)

        category_data = (
            analytics_df
            .groupby(category_col)[quantity_col]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            category_data,
            names=category_col,
            values=quantity_col,
            title="Stock Distribution by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================================================
# LOW STOCK
# =========================================================
elif menu == "⚠️ Low Stock":

    st.title("⚠️ Low Stock Monitoring")

    if reorder_col and quantity_col:

        low_stock_df = df[low_stock_mask].copy()

        if low_stock_df.empty:

            st.info(
                "ℹ️ Currently no actual low-stock products found."
            )

            st.subheader("⚠️ Low Stock Demo")

            demo_low_stock = df.head(3).copy()

            demo_low_stock["Stock Status"] = "LOW STOCK"

            st.warning(
                "⚠️ Demo: Products requiring attention"
            )

            st.dataframe(
                demo_low_stock,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                f"⚠️ {len(low_stock_df)} "
                "products require attention."
            )

            st.dataframe(
                low_stock_df,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "Quantity and Reorder Level columns "
            "are required."
        )
# =========================================================
# ROBOT VISION
# =========================================================
elif menu == "🤖 Robot Vision":

    st.title("🤖 Robot Vision System")

    st.write(
        "Warehouse image analysis and inventory product matching."
    )
# =========================================================
# BARCODE / QR CODE SCANNER - OPENCV
# =========================================================

st.markdown("---")

st.subheader("📦 Barcode / QR Code Scanner")

st.info(
    "Capture a QR code or barcode using your camera."
)

barcode_image = st.camera_input(
    "📷 Scan Barcode / QR Code",
    key="barcode_scanner"
)

if barcode_image is not None:

    image = Image.open(barcode_image).convert("RGB")

    st.image(
        image,
        caption="Scanned Code Image",
        use_container_width=True
    )

    try:

        import cv2
        import numpy as np

        image_array = np.array(image)

        # OpenCV QR detector
        qr_detector = cv2.QRCodeDetector()

        data, points, _ = qr_detector.detectAndDecode(
            image_array
        )

        if data:

            product_id = data.strip()

            st.success(
                f"✅ QR Code Detected: {product_id}"
            )

            # Search Product ID in inventory
            if "Product_ID" in df.columns:

                product = df[
                    df["Product_ID"]
                    .astype(str)
                    .str.upper()
                    == product_id.upper()
                ]

                if not product.empty:

                    product = product.iloc[0]

                    st.write("### 📦 Product Details")

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.metric(
                            "Product ID",
                            product["Product_ID"]
                        )

                    with c2:
                        st.metric(
                            "Product Name",
                            product["Product_Name"]
                        )

                    with c3:
                        st.metric(
                            "Quantity",
                            product["Quantity"]
                        )

                    st.write(
                        f"**Category:** "
                        f"{product['Category']}"
                    )

                    st.write(
                        f"**Price:** ₹{product['Price']}"
                    )

                    st.write(
                        f"**Warehouse Section:** "
                        f"{product['Warehouse_Section']}"
                    )

                    quantity_value = float(
                        product["Quantity"]
                    )

                    reorder_value = float(
                        product["Reorder_Level"]
                    )

                    if quantity_value <= reorder_value:

                        st.error(
                            "⚠️ LOW STOCK"
                        )

                    else:

                        st.success(
                            "✅ STOCK AVAILABLE"
                        )

                else:

                    st.warning(
                        f"⚠️ Product ID '{product_id}' "
                        "was not found in inventory."
                    )

        else:

            st.warning(
                "⚠️ QR code not detected. "
                "Keep the QR code clear and centered."
            )

    except Exception as e:

        st.error(
            f"❌ Scanner error: {e}"
        )
    # =====================================================
    # SYSTEM STATUS
    # =====================================================

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric("🤖 Robot Status", "ONLINE")

    with r2:
        st.metric("📷 Camera", "READY")

    with r3:
        st.metric("🔎 Vision Engine", "ACTIVE")

    st.markdown("---")

    # =====================================================
    # IMAGE UPLOAD
    # =====================================================

    st.subheader("📷 Product Image Detection")

    uploaded_image = st.file_uploader(
        "Upload warehouse/product image",
        type=["jpg", "jpeg", "png"],
        key="robot_image"
    )

    if uploaded_image is not None:

        st.image(
            uploaded_image,
            caption="Uploaded Warehouse Image",
            width="stretch"
        )

        # =================================================
        # AUTOMATIC PRODUCT DETECTION
        # =================================================

        file_name = uploaded_image.name.lower()

        if "ssd" in file_name:
            detected_product_name = "SSD"

        elif "mouse" in file_name:
            detected_product_name = "Mouse"

        else:
            detected_product_name = None
         # =========================================================
# REAL-TIME CAMERA / LIVE ROBOT VISION
# =========================================================

st.markdown("---")

st.subheader("📹 Live Robot Vision")

st.info(
    "Use your camera to capture a warehouse product image "
    "for Robot Vision analysis."
)

camera_image = st.camera_input(
    "📷 Capture Product using Camera"
)

if camera_image is not None:

    st.success("✅ Camera image captured successfully!")

    image = Image.open(camera_image)

    st.image(
        image,
        caption="Captured Product Image",
        use_container_width=True
    )

    # Save captured image temporarily
    temp_camera_path = "robot_camera_temp.jpg"

    image.convert("RGB").save(
        temp_camera_path,
        format="JPEG"
    )

    st.info("🔍 Processing captured image...")

    try:

        vision_system = RobotVisionSystem()

        result = vision_system.process_image(
            temp_camera_path
        )

        st.success(
            "🤖 Robot Vision Processing Completed!"
        )

        st.write("### 🔎 Detection Result")

        if result:

            st.json(result)

        else:

            st.warning(
                "⚠️ No product detected."
            )

    except Exception as e:

        st.error(
            f"❌ Vision processing error: {e}"
        )

        # =================================================
        # SAVE TEMPORARY IMAGE
        # =================================================

        temp_image = Path("robot_temp.jpg")

        with open(temp_image, "wb") as file:
            file.write(uploaded_image.getbuffer())

        # =================================================
        # ROBOT VISION ANALYSIS
        # =================================================

        robot = RobotVisionSystem()

        result = robot.process_image(temp_image)

        st.markdown("---")

        st.subheader("🔎 Robot Vision Analysis")

        if result["status"] == "SUCCESS":

            d1, d2, d3 = st.columns(3)

            with d1:
                st.metric(
                    "🔍 Detected Objects",
                    result["detected_objects"]
                )

            with d2:
                st.metric(
                    "📏 Image Height",
                    f'{result["image_height"]} px'
                )

            with d3:
                st.metric(
                    "📐 Image Width",
                    f'{result["image_width"]} px'
                )

            st.success(
                "✅ Image analysis completed successfully."
            )

            st.caption(
                f'Detection Time: {result["detection_time"]}'
            )

            # =================================================
            # INVENTORY PRODUCT MATCHING
            # =================================================

            st.markdown("---")

            st.subheader(
                "📦 Inventory Product Matching"
            )

            product_list = (
                df[product_name_col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if detected_product_name in product_list:

                selected_product = detected_product_name

                st.success(
                    f"🤖 Detected Product: {selected_product}"
                )

            else:

                selected_product = st.selectbox(
                    "Select detected product",
                    product_list,
                    key="vision_product_select"
                )

            matched_product = df[
                df[product_name_col].astype(str)
                == selected_product
            ]

            if not matched_product.empty:

                product = matched_product.iloc[0]

                current_stock = float(
                    pd.to_numeric(
                        product[quantity_col],
                        errors="coerce"
                    )
                )

                reorder_level = float(
                    pd.to_numeric(
                        product[reorder_col],
                        errors="coerce"
                    )
                )

                warehouse_section = str(
                    product[warehouse_col]
                )

                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.metric(
                        "📦 Product",
                        selected_product
                    )

                with m2:
                    st.metric(
                        "📊 Stock",
                        int(current_stock)
                    )

                with m3:
                    st.metric(
                        "🔄 Reorder Level",
                        int(reorder_level)
                    )

                with m4:
                    st.metric(
                        "📍 Section",
                        warehouse_section
                    )

                if current_stock <= reorder_level:

                    stock_status = "LOW STOCK"

                    st.error(
                        "⚠️ LOW STOCK — Reorder recommended."
                    )

                else:

                    stock_status = "AVAILABLE"

                    st.success(
                        "✅ Stock level is healthy."
                    )

                # =================================================
                # SAVE VISION SCAN
                # =================================================

                if st.button(
                    "💾 Save Vision Scan",
                    key="save_robot_scan"
                ):

                    save_detection(
                        selected_product,
                        result["detected_objects"],
                        current_stock,
                        warehouse_section,
                        stock_status
                    )

                    st.success(
                        "✅ Vision scan saved successfully!"
                    )

        else:

            st.error(
                f'❌ {result["message"]}'
            )


        # =========================================================
# VISION HISTORY
# =========================================================
if menu == "🕒 Vision History":

    st.title("🕒 Robot Vision Detection History")

    history = get_detection_history()

    if history.empty:

        st.info(
            "📷 No vision scans recorded yet."
        )

    else:

        h1, h2, h3 = st.columns(3)

        with h1:
            st.metric(
                "🔍 Total Scans",
                len(history)
            )

        with h2:
            st.metric(
                "📦 Products Scanned",
                history["product_name"].nunique()
            )

        with h3:
            alerts = (
                history["status"]
                .astype(str)
                .str.contains(
                    "LOW",
                    case=False,
                    na=False
                )
                .sum()
            )

            st.metric(
                "⚠️ Alerts",
                int(alerts)
            )

        st.markdown("---")

        st.markdown('---')
        st.subheader("📋 Professional Scan History")

        if not history.empty:

            # FILTERS
            f1, f2, f3 = st.columns(3)

            with f1:
                product_options = ["All Products"] + sorted(
                    history["product_name"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                selected_history_product = st.selectbox(
                    "📦 Product",
                    product_options,
                    key="history_product_filter"
                )

            with f2:
                status_options = ["All Status"] + sorted(
                    history["status"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                selected_history_status = st.selectbox(
                    "⚠️ Status",
                    status_options,
                    key="history_status_filter"
                )

            with f3:
                search_history = st.text_input(
                    "🔎 Search",
                    key="history_search"
                )

            # APPLY FILTERS
            filtered_history = history.copy()

            if selected_history_product != "All Products":
                filtered_history = filtered_history[
                    filtered_history["product_name"]
                    .astype(str)
                    == selected_history_product
                ]

            if selected_history_status != "All Status":
                filtered_history = filtered_history[
                    filtered_history["status"]
                    .astype(str)
                    == selected_history_status
                ]

            if search_history.strip():
                filtered_history = filtered_history[
                    filtered_history["product_name"]
                    .astype(str)
                    .str.contains(
                        search_history.strip(),
                        case=False,
                        na=False
                    )
                ]

            # METRICS
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "🔍 Total Scans",
                    len(filtered_history)
                )

            with c2:
                st.metric(
                    "📦 Products",
                    filtered_history["product_name"]
                    .astype(str)
                    .nunique()
                )

            with c3:
                low_stock = filtered_history["status"].astype(
                    str
                ).str.contains(
                    "LOW",
                    case=False,
                    na=False
                ).sum()

                st.metric(
                    "⚠️ Low Stock",
                    int(low_stock)
                )

            with c4:
                available = filtered_history["status"].astype(
                    str
                ).str.contains(
                    "AVAILABLE",
                    case=False,
                    na=False
                ).sum()

                st.metric(
                    "✅ Available",
                    int(available)
                )

            st.markdown("---")

            # TABLE
            if filtered_history.empty:

                st.info(
                    "📭 No scan records found."
                )

            else:

                st.dataframe(
                    filtered_history,
                    width="stretch",
                    hide_index=True
                )

                # CSV EXPORT
                csv_data = filtered_history.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "📥 Export Scan History CSV",
                    data=csv_data,
                    file_name="vision_scan_history.csv",
                    mime="text/csv",
                    key="export_vision_history"
                )

        else:

            st.info(
                "📷 No vision scans recorded yet."
            )
# =========================================================
# REPORTS
# =========================================================

if menu == "📋 Reports":

    st.title("📋 Warehouse Reports")

    st.write(
        "Generate and download warehouse inventory reports."
    )

    st.markdown("---")

    report_file = Path(
        "reports/warehouse_inventory_report.csv"
    )

    if report_file.exists():

        report_df = pd.read_csv(report_file)

        st.subheader("📦 Inventory Report")

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # =====================================================
        # CSV DOWNLOAD
        # =====================================================

        csv_data = report_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name="warehouse_inventory_report.csv",
            mime="text/csv"
        )

        # =====================================================
        # PDF GENERATION
        # =====================================================

        pdf_buffer = BytesIO()

        document = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=25,
            leftMargin=25,
            topMargin=30,
            bottomMargin=30
        )

        pdf_data = []

        # PDF Title
        pdf_data.append(
            Paragraph(
                "<b>SMART WAREHOUSE MANAGEMENT</b>",
                getSampleStyleSheet()["Title"]
            )
        )

        pdf_data.append(
            Paragraph(
                "Warehouse Inventory Report",
                getSampleStyleSheet()["Heading2"]
            )
        )

        pdf_data.append(Spacer(1, 15))

        # Convert DataFrame to PDF table
        table_data = [
            list(report_df.columns)
        ]

        table_data.extend(
            report_df.astype(str).values.tolist()
        )

        report_table = Table(
            table_data,
            repeatRows=1
        )

        report_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.black
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        pdf_data.append(report_table)

        document.build(pdf_data)

        pdf_buffer.seek(0)

        st.markdown("---")

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="warehouse_inventory_report.pdf",
            mime="application/pdf"
        )

        st.success(
            "✅ PDF report is ready to download."
        )

    else:

        st.warning(
            "⚠️ Report file not found."
        )
        # =========================================================
# ABOUT
# =========================================================

if menu == "ℹ️ About":

    st.title("ℹ️ About Smart Warehouse System")

    st.markdown("---")

    st.subheader("📦 Smart Warehouse Management Dashboard")

    st.write(
        "A professional warehouse inventory management "
        "and analytics system developed using Python "
        "and Streamlit."
    )

    st.markdown("### 🚀 System Features")

    st.markdown("""
    - 📦 Inventory Management
    - 📊 Real-Time Analytics
    - 🔍 Product Search & Filtering
    - ⚠️ Low Stock Monitoring
    - 🤖 Robot Vision System
    - 🕒 Vision Detection History
    - 📋 Inventory Reports
    - 💰 Inventory Value Tracking
    """)

    st.markdown("---")

    st.subheader("🛠️ Technologies Used")

    st.write(
        "Python • Pandas • Streamlit • Plotly • SQLite • OpenCV"
    )

    st.markdown("---")

    st.subheader("🎯 Project Objective")

    st.write(
        "The system helps warehouse managers monitor "
        "inventory, identify low-stock products, analyze "
        "warehouse performance, and make better inventory "
        "decisions using data analytics."
    )

    st.markdown("---")

    st.info(
        "📌 Smart Warehouse Management & Robot Vision System"
    )

    st.caption("Version 3.0")
