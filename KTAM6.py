from datetime import datetime
import streamlit as st

# Cấu hình trang Streamlit (Giao diện Dark Mode phù hợp với Logistics SaaS)
st.set_page_config(
    page_title="LogiSpace Simulator - Sales Forwarding Edition",
    page_icon="🚢",
    layout="wide",
)

# --- CSS TÙY CHỈNH GIAO DIỆN ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #020617;
        color: #f8fafc;
    }
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 16px;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- DỮ LIỆU MẪU (DATABASE) ---
PORTS_DATABASE = [
    {"code": "VNVUT", "name": "Cái Mép TCIT (VNVUT)", "country": "Vietnam"},
    {"code": "VNCLI", "name": "Cát Lái (VNCLI)", "country": "Vietnam"},
    {"code": "VNHPH", "name": "Hải Phòng (VNHPH)", "country": "Vietnam"},
    {"code": "VNDAD", "name": "Đà Nẵng (VNDAD)", "country": "Vietnam"},
    {"code": "VNUIH", "name": "Quy Nhơn (VNUIH)", "country": "Vietnam"},
    {"code": "CNSHA", "name": "Shanghai (CNSHA)", "country": "China"},
    {"code": "CNNGB", "name": "Ningbo (CNNGB)", "country": "China"},
    {"code": "CNYAN", "name": "Shenzhen / Yantian (CNYAN)", "country": "China"},
    {"code": "CNTAO", "name": "Qingdao (CNTAO)", "country": "China"},
    {"code": "KRPUS", "name": "Busan (KRPUS)", "country": "South Korea"},
    {"code": "SGSIN", "name": "Singapore (SGSIN)", "country": "Singapore"},
    {"code": "USLAX", "name": "Los Angeles, CA (USLAX)", "country": "United States"},
    {"code": "USLGB", "name": "Long Beach, CA (USLGB)", "country": "United States"},
    {
        "code": "USNYC",
        "name": "New York / New Jersey (USNYC)",
        "country": "United States",
    },
    {"code": "NLRTM", "name": "Rotterdam (NLRTM)", "country": "Netherlands"},
    {"code": "DEHAM", "name": "Hamburg (DEHAM)", "country": "Germany"},
    {"code": "BEANR", "name": "Antwerp (BEANR)", "country": "Belgium"},
]

CONTAINER_TYPES = [
    "20'GP",
    "40'GP",
    "40'HC",
    "45'HC",
    "Reefer 20'",
    "Reefer 40'",
    "Open Top",
    "Flat Rack",
]

CARRIERS_LIST = [
    "Maersk Line",
    "CMA CGM",
    "MSC",
    "Evergreen",
    "Wan Hai Lines",
    "ONE (Ocean Network Express)",
    "Hapag-Lloyd",
]

INITIAL_QUOTATIONS = [
    {
        "id": "QT-01",
        "carrier": "Maersk Line",
        "pol": "VNVUT",
        "pod": "USLAX",
        "containerType": "40'HC",
        "etd": "2026-10-15",
        "eta": "2026-10-30",
        "oceanFreight": 3200,
        "pss": 300,
        "gri": 0,
        "bafLss": 250,
        "localCharges": 180,
        "docFee": 50,
        "trucking": 350,
        "slotFee": 0,
        "otherFees": 0,
        "source": "LIVE",
        "sourceName": "Maersk API Connect",
    },
    {
        "id": "QT-02",
        "carrier": "Wan Hai Lines",
        "pol": "VNVUT",
        "pod": "USLAX",
        "containerType": "40'HC",
        "etd": "2026-10-15",
        "eta": "2026-10-30",
        "oceanFreight": 3100,
        "pss": 250,
        "gri": 100,
        "bafLss": 220,
        "localCharges": 170,
        "docFee": 50,
        "trucking": 350,
        "slotFee": 0,
        "otherFees": 0,
        "source": "MANUAL",
        "sourceName": "Local Rate Sheet Q4",
    },
]

INITIAL_SPACES = [
    {
        "id": "SP-01",
        "pol": "VNVUT",
        "pod": "USLAX",
        "containerType": "40'HC",
        "carrier": "Maersk Line",
        "availableSpace": 3,
        "source": "LIVE",
        "sourceName": "Carrier Allocation Portal",
    }
]

PEAK_EVENTS = [
    {
        "id": "EVT-01",
        "name": "Tet Nguyen Dan (Lunar New Year)",
        "reason": "Nhà máy đóng cửa trước Tết, nhu cầu đẩy hàng trước kỳ nghỉ tăng vọt, nguy cơ thiếu vỏ container.",
        "certainty": "Cao",
        "source": "Historical shipping trend",
    },
    {
        "id": "EVT-02",
        "name": "Peak Season Q4 / Black Friday",
        "reason": "Mùa cao điểm mua sắm cuối năm lễ hội, nhu cầu xuất khẩu sang Âu Mỹ tăng mạnh.",
        "certainty": "Cao",
        "source": "Global Market Forecast",
    },
]

# --- HÀM TÍNH TOÁN NGHIỆP VỤ ---


def calculate_total_cost(quotation, quantity):
  if not quotation:
    return 0
  unit_items = (
      quotation.get("oceanFreight", 0)
      + quotation.get("pss", 0)
      + quotation.get("gri", 0)
      + quotation.get("bafLss", 0)
      + quotation.get("localCharges", 0)
      + quotation.get("docFee", 0)
      + quotation.get("trucking", 0)
      + quotation.get("slotFee", 0)
      + quotation.get("otherFees", 0)
  )
  return unit_items * quantity


def calculate_profit_metrics(
    total_cost, selling_price_per_unit, quantity, target_margin_percent=10
):
  if (
      not selling_price_per_unit
      or selling_price_per_unit <= 0
      or quantity <= 0
      or total_cost <= 0
  ):
    min_price = (
        (total_cost / quantity) / (1 - target_margin_percent / 100)
        if total_cost > 0
        else 0
    )
    return {
        "revenue": 0,
        "grossProfit": 0,
        "marginPercent": 0,
        "minSellingPricePerUnit": min_price,
        "status": "Chưa đủ dữ liệu",
    }

  revenue = selling_price_per_unit * quantity
  gross_profit = revenue - total_cost
  margin_percent = (gross_profit / revenue) * 100
  min_selling_price = (total_cost / quantity) / (
      1 - target_margin_percent / 100
  )

  status = "Chưa đạt mục tiêu"
  if abs(gross_profit) <= 0.005:
    status = "Hòa vốn"
  elif gross_profit < 0:
    status = "Thua lỗ"
  elif margin_percent >= target_margin_percent:
    status = "Đạt mục tiêu"

  return {
      "revenue": revenue,
      "grossProfit": gross_profit,
      "marginPercent": margin_percent,
      "minSellingPricePerUnit": min_selling_price,
      "status": status,
  }


def calculate_space_deficit(demand_quantity, available_space):
  deficit = max(0, demand_quantity - available_space)
  fulfillment_rate = (
      min(100, (available_space / demand_quantity) * 100)
      if demand_quantity > 0
      else 100
  )
  return {"deficit": deficit, "fulfillmentRate": fulfillment_rate}


# --- QUẢN LÝ SESSION STATE ---
if "shipment_state" not in st.session_state:
  st.session_state.shipment_state = {
      "shipper": "QA Furniture Co., Ltd (Binh Phuoc)",
      "consignee": "MTA Cabinets LLC (Texas)",
      "sales": "Nguyen Van A (Sales Forwarding)",
      "pol": "VNVUT",
      "pod": "USLAX",
      "containerType": "40'HC",
      "quantity": 5,
      "carrier": "Wan Hai Lines",
      "commodity": "Wooden kitchen cabinets (HS 940340)",
      "bookingDate": datetime.strptime("2026-10-13", "%Y-%m-%d").date(),
      "etd": datetime.strptime("2026-10-15", "%Y-%m-%d").date(),
      "eta": datetime.strptime("2026-10-30", "%Y-%m-%d").date(),
      "updatedAt": "12/10/2026 15:30",
  }

if "selling_prices" not in st.session_state:
  st.session_state.selling_prices = {"QT-01": 5900, "QT-02": 5850}

if "slots" not in st.session_state:
  st.session_state.slots = [
      {
          "id": "SLOT-01",
          "provider": "Global Forwarder Vina",
          "pol": "VNVUT",
          "pod": "USLAX",
          "carrier": "Evergreen",
          "vesselVoyage": "EVER GIVEN 042E",
          "containerType": "40'HC",
          "remainingSlots": 3,
          "sellingPrice": 4100,
          "source": "DEMO",
          "sourceName": "Slot Exchange Network",
      }
  ]

# --- HEADER ỨNG DỤNG ---
st.markdown(
    "### LOGISPACE SIMULATOR <span style='font-size: 12px; background-color: #2563eb; color: white; padding: 2px 8px; border-radius: 4px;'>Sales Forwarding Edition</span>",
    unsafe_allow_html=True,
)
st.caption(
    "Hệ thống hỗ trợ Sales Forwarding, Báo giá cước, Dự báo Space & Sàn Slot"
)
st.divider()

# --- LAYOUT CHÍNH: SIDEBAR (THÔNG TIN LÔ HÀNG) & MAIN AREA (CÁC TAB) ---

port_codes = [p["code"] for p in PORTS_DATABASE]
port_names = {p["code"]: p["name"] for p in PORTS_DATABASE}

with st.sidebar:
  st.markdown("#### 📋 THÔNG TIN LÔ HÀNG")
  st.caption("Đang chỉnh sửa (Nháp)")

  with st.expander("1. Các Bên Liên Quan", expanded=True):
    shipper = st.text_input(
        "Shipper", st.session_state.shipment_state["shipper"]
    )
    consignee = st.text_input(
        "Consignee", st.session_state.shipment_state["consignee"]
    )
    sales = st.text_input("Sales Phụ Trách", st.session_state.shipment_state["sales"])

  with st.expander("2. Tuyến Vận Tải (POL / POD)", expanded=True):
    pol = st.selectbox(
        "Cảng Đi (POL)",
        port_codes,
        index=port_codes.index(st.session_state.shipment_state["pol"]),
        format_func=lambda x: port_names[x],
    )
    pod = st.selectbox(
        "Cảng Đến (POD)",
        port_codes,
        index=port_codes.index(st.session_state.shipment_state["pod"]),
        format_func=lambda x: port_names[x],
    )
    commodity = st.text_input(
        "Loại Hàng Hóa", st.session_state.shipment_state["commodity"]
    )

  with st.expander("3. Quy Mô & Container", expanded=True):
    container_type = st.selectbox(
        "Loại Cont",
        CONTAINER_TYPES,
        index=CONTAINER_TYPES.index(
            st.session_state.shipment_state["containerType"]
        ),
    )
    quantity = st.number_input(
        "Số Lượng",
        min_value=1,
        value=st.session_state.shipment_state["quantity"],
    )
    carrier = st.selectbox(
        "Hãng Tàu Mong Muốn",
        CARRIERS_LIST,
        index=CARRIERS_LIST.index(st.session_state.shipment_state["carrier"])
        if st.session_state.shipment_state["carrier"] in CARRIERS_LIST
        else 0,
    )
    target_margin = st.number_input("Mục tiêu Biên Lãi (%)", value=10.0, step=0.5)

  with st.expander("4. Lịch Trình (ETD / ETA)", expanded=True):
    booking_date = st.date_input(
        "Ngày Book Chỗ", st.session_state.shipment_state["bookingDate"]
    )
    etd = st.date_input("ETD Thực Tế", st.session_state.shipment_state["etd"])
    eta = st.date_input("ETA Dự Kiến", st.session_state.shipment_state["eta"])

  if eta < etd:
    st.warning("⚠️ Cảnh báo: ETA nhỏ hơn ETD!")

  if st.button("Hoàn thành và cập nhật dữ liệu", type="primary", use_container_width=True):
    if pol == pod:
      st.error("POL và POD không được trùng nhau!")
    else:
      now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
      st.session_state.shipment_state = {
          "shipper": shipper,
          "consignee": consignee,
          "sales": sales,
          "pol": pol,
          "pod": pod,
          "containerType": container_type,
          "quantity": quantity,
          "carrier": carrier,
          "commodity": commodity,
          "bookingDate": booking_date,
          "etd": etd,
          "eta": eta,
          "updatedAt": now_str,
      }
      st.success(f"Cập nhật lô hàng thành công lúc {now_str}!")

# --- KHU VỰC HIỂN THỊ CHÍNH (TABS) ---
state = st.session_state.shipment_state

matching_quotations = [
    q
    for q in INITIAL_QUOTATIONS
    if q["pol"] == state["pol"]
    and q["pod"] == state["pod"]
    and q["containerType"] == state["containerType"]
]
matching_spaces = [
    s
    for s in INITIAL_SPACES
    if s["pol"] == state["pol"]
    and s["pod"] == state["pod"]
    and s["containerType"] == state["containerType"]
]
matching_slots = [
    sl
    for sl in st.session_state.slots
    if sl["pol"] == state["pol"]
    and sl["pod"] == state["pod"]
    and sl["containerType"] == state["containerType"]
]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard Tổng quan",
    "💰 Báo giá & Lợi nhuận",
    "📦 Dự báo Space",
    "⚡ Mùa cao điểm",
    "🔄 Sàn Slot (DEMO)",
])

with tab1:
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.markdown(
        f"""<div class="metric-card"><p style="color: #94a3b8; font-size: 12px;">Tuyến vận chuyển</p><h4 style="color: #60a5fa; margin: 4px 0;">{state['pol']} -> {state['pod']}</h4><p style="color: #94a3b8; font-size: 11px; margin: 0;">{state['containerType']} ({state['quantity']} cont) - {state['commodity']}</p></div>""",
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        f"""<div class="metric-card"><p style="color: #94a3b8; font-size: 12px;">Báo giá khả dụng</p><h4 style="color: #34d399; margin: 4px 0;">{len(matching_quotations)} Hãng tàu</h4><p style="color: #94a3b8; font-size: 11px; margin: 0;">Sales: {state['sales']}</p></div>""",
        unsafe_allow_html=True,
    )
  with col3:
    risk_level = "Thấp"
    if matching_spaces:
      deficit_check = calculate_space_deficit(
          state["quantity"], matching_spaces[0]["availableSpace"]
      )
      if deficit_check["deficit"] > 0:
        risk_level = "Cao"
    else:
      risk_level = "Chưa đủ dữ liệu"
    st.markdown(
        f"""<div class="metric-card"><p style="color: #94a3b8; font-size: 12px;">Rủi ro Space</p><h4 style="color: #fbbf24; margin: 4px 0;">{risk_level}</h4><p style="color: #94a3b8; font-size: 11px; margin: 0;">ETD: {state['etd']}</p></div>""",
        unsafe_allow_html=True,
    )
  with col4:
    st.markdown(
        f"""<div class="metric-card"><p style="color: #94a3b8; font-size: 12px;">Mục tiêu Biên Lãi</p><h4 style="color: #60a5fa; margin: 4px 0;">{target_margin}%</h4><p style="color: #94a3b8; font-size: 11px; margin: 0;">Khách: {state['consignee']}</p></div>""",
        unsafe_allow_html=True,
    )

with tab2:
  st.markdown(
      f"#### So sánh phương án hãng tàu ({state['pol']} -> {state['pod']}) cho"
      f" {state['commodity']}"
  )
  if not matching_quotations:
    st.warning("Chưa có dữ liệu giá cước cho tuyến này.")
  else:
    for q in matching_quotations:
      total_cost = calculate_total_cost(q, state["quantity"])
      q_id = q["id"]
      current_price = st.session_state.selling_prices.get(q_id, 5900)

      cols = st.columns([2, 2, 2, 2, 2])
      with cols[0]:
        st.markdown(f"**{q['carrier']}**")
        st.caption(f"{q['etd']} / {q['eta']}")
      with cols[1]:
        st.text(f"Tổng chi phí:\n${total_cost:,.0f}")
      with cols[2]:
        new_price = st.number_input(
            "Giá bán đề xuất ($)",
            value=float(current_price),
            key=f"price_{q_id}",
        )
        st.session_state.selling_prices[q_id] = new_price
      metrics = calculate_profit_metrics(
          total_cost, new_price, state["quantity"], target_margin
      )
      with cols[3]:
        st.text(
            f"Biên lợi nhuận:\n{metrics['marginPercent']:.2f}% (Tối thiểu:"
            f" ${metrics['minSellingPricePerUnit']:.2f})"
        )
      with cols[4]:
        st.markdown(f"**Trạng thái:**\n`{metrics['status']}`")
      st.divider()

with tab3:
  st.markdown("#### Dự báo Space khả dụng")
  if not matching_spaces:
    st.warning("Chưa đủ dữ liệu xác định space khả dụng.")
  else:
    for sp in matching_spaces:
      deficit_obj = calculate_space_deficit(
          state["quantity"], sp["availableSpace"]
      )
      c1, c2, c3, c4 = st.columns(4)
      c1.markdown(f"Hãng tàu: **{sp['carrier']}**")
      c2.markdown(f"Space khả dụng: **{sp['availableSpace']} cont**")
      c3.markdown(f"Nhu cầu: **{state['quantity']} cont**")
      c4.markdown(f"Thiếu hụt: **{deficit_obj['deficit']} cont**")

with tab4:
  st.markdown("#### Mùa cao điểm & Booking")
  for ev in PEAK_EVENTS:
    with st.container():
      st.markdown(f"##### {ev['name']} (`Mức độ: {ev['certainty']}`)")
      st.write(ev["reason"])
      st.divider()

with tab5:
  st.markdown("#### Sàn Slot (DEMO)")
  if not matching_slots:
    st.info("Không có slot giao dịch nào phù hợp tuyến này.")
  else:
    for slot in matching_slots:
      col_a, col_b = st.columns([3, 1])
      with col_a:
        st.markdown(f"**{slot['provider']} - {slot['carrier']}**")
        st.text(
            f"Còn lại: {slot['remainingSlots']} slot | Giá:"
            f" ${slot['sellingPrice']}"
        )
      with col_b:
        if st.button("Mua Slot", key=f"buy_{slot['id']}"):
          if state["quantity"] > slot["remainingSlots"]:
            st.error("Vượt số slot còn lại!")
          else:
            slot["remainingSlots"] -= state["quantity"]
            st.success("Đã ghi nhận yêu cầu DEMO mua slot thành công!")
