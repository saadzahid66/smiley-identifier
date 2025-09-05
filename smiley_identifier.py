import streamlit as st
import json

# --- Load schema ---
with open("schemas.json") as f:
    schemas = json.load(f)

# --- Card template ---
card_style = """
<div style="background-color:#f5f5f5;padding:15px;margin-bottom:10px;
            border-radius:10px;color:black;">
<h4 style="margin:0;color:black;">{title}</h4>
<p style="margin:0;font-size:18px;">{value}</p>
</div>
"""

# --- Serial Parser ---
def parse_serial(serial: str):
    serial = serial.upper()
    result = {}
    errors = []

    if len(serial) >= 2:
        result["year"] = "20" + serial[:2]
    if len(serial) >= 4:
        result["week"] = serial[2:4]

    schema = None
    if len(serial) >= 5:
        type_code = serial[4]
        for name, s in schemas.items():
            if type_code in s.get("type", {}):
                result["device"] = s["type"][type_code]
                schema = s
                result["schema_name"] = name
                break
        else:
            errors.append(f"Invalid type code '{type_code}'")

    if not schema:
        return result, errors

    if len(serial) >= 6:
        gen_code = serial[5]
        gen_val = schema.get("generation", {}).get(gen_code)
        if gen_val:
            result["generation"] = gen_val
        else:
            errors.append(f"Invalid generation code '{gen_code}' for {result.get('device', '')}")

    if len(serial) >= 7:
        radio_code = serial[6]
        radio_val = schema.get("radio", {}).get(radio_code)
        if radio_val:
            result["radio"] = radio_val
            if "(" in radio_val and ")" in radio_val:
                result["network"] = radio_val.split("(")[1].replace(")","")
            else:
                result["network"] = radio_val
        else:
            errors.append(f"Invalid radio code '{radio_code}' for {result.get('device','')}")

    if len(serial) >= 8:
        hw_val = None
        hw_key = f"R{serial[6]}-1"
        hw_val = schema.get("hardware", {}).get(hw_key) or schema.get("hardware", {}).get(f"R{serial[6]}-0")
        if hw_val:
            result["hardware"] = hw_val
        else:
            errors.append(f"Invalid hardware for radio '{serial[6]}'")

    if len(serial) >= 10:
        wd_code = serial[8:10]
        changelog_val = schema.get("changelog", {}).get(wd_code)
        if changelog_val:
            result["changelog"] = changelog_val
        else:
            errors.append(f"Unknown changelog code '{wd_code}'")

    if len(serial) >= 14:
        result["sequence"] = serial[10:14]

    return result, errors

# --- Streamlit UI ---
st.set_page_config(page_title="Smiley Identifier", page_icon="happyornot_logo.svg", layout="wide")
st.title("📟 HoN Smiley Identifier")
st.divider()

# --- Sidebar Input ---
st.sidebar.image("happyornot_logo.svg", use_container_width=True)
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
serial_input = st.sidebar.text_input("Enter Serial Number", "").upper()
submit = st.sidebar.button("Enter")

# --- Main Screen Output ---
if submit and serial_input:
    parsed, errors = parse_serial(serial_input)

    for e in errors:
        st.error(f"❌ {e}")

    # --- Two Columns ---
    col1, col2 = st.columns([1, 1])  # Left: cards, Right: image

    # Left column: cards
    with col1:
        st.subheader("🔍 Device Information")
        for key, title in [
            ("device", "💻 Type"),
            ("network", "🌐 Network"),
            ("generation", "🔢 Model/Generation"),
            ("hardware", "📟 Hardware"),
            ("radio", "📡 Radio Chipset")
        ]:
            if key in parsed:
                st.markdown(card_style.format(title=title, value=parsed[key]), unsafe_allow_html=True)

        st.divider()
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("🔍 Production Information")
        for key, title in [
            ("year", "📅 Year"),
            ("week", "📆 Week"),
            ("sequence", "🔢 Device Number"),
            ("changelog", "📝 Changelog")
        ]:
            if key in parsed:
                st.markdown(card_style.format(title=title, value=parsed[key]), unsafe_allow_html=True)

    # Right column: device image
    with col2:
        device_name = parsed.get("device", "")
        # Map device to image file path
        device_images = {
            "Smiley Mini": "mini_standard.png",
            "Smiley Terminal (Standard, Table, Rail)": "images/smiley_terminal.png",
            "Smiley Wall (Wall attachment)": "images/smiley_wall.png",
            "Smiley Touch": "images/smiley_touch.png",
            "Smiley Touch with camera hole": "images/smiley_touch_camera.png"
        }
        img_path = device_images.get(device_name, "mini_standard.png")
        st.image(img_path, caption=device_name, use_container_width=True)
