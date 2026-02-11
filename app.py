import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ================= GOOGLE SHEET CONNECTION =================

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\DELL\Desktop\Python\service_account.json", scope)

client = gspread.authorize(creds)

sheet_id = "1gjdB2tfLGTGdS94cWCImHrTRrfJbRF0CYv1kdhIIQlM"

bill_sheet = client.open_by_key(sheet_id).worksheet("Sheet1")
setting_sheet = client.open_by_key(sheet_id).worksheet("Setting")

# ================= HEADER DESIGN =================

st.markdown("""
    <h1 style='background-color:blue;color:white;padding:15px;text-align:center;border-radius:10px;'>
    Vendor Payment Management
    </h1>
""", unsafe_allow_html=True)

# ================= SAFE VENDOR LOAD FUNCTION =================

def load_vendors():
    try:
        col_data = setting_sheet.col_values(1)

        if len(col_data) > 1:
            vendors = [v.strip() for v in col_data[1:] if v.strip() != ""]
            vendors = list(dict.fromkeys(vendors))  # remove duplicate
        else:
            vendors = []

        return vendors

    except Exception as e:
        st.error(f"Vendor Load Error: {e}")
        return []

# ================= SIDEBAR =================

menu = st.sidebar.radio("Select Option", 
                        ["Vendor Bill Receipt", 
                         "Vendor Payment", 
                         "Outstanding Data"])

# ============================================================
# ================= VENDOR BILL RECEIPT ======================
# ============================================================

if menu == "Vendor Bill Receipt":

    st.subheader("Vendor Bill Entry")

    date = st.date_input("Date")
    month = st.selectbox("Month",
                         ["Jan","Feb","Mar","Apr","May","Jun",
                          "Jul","Aug","Sep","Oct","Nov","Dec"])

    vendor_list = load_vendors()
    vendor_name = st.selectbox("Vendor Name", [""] + vendor_list)

    invoice_no = st.text_input("Invoice Number")
    payment_day = st.date_input("Payment Day")
    bill_amount = st.number_input("Bill Amount")

    col1, col2 = st.columns(2)

    if col1.button("Save"):

        if vendor_name == "":
            st.warning("Please Select Vendor")
        else:
            new_row = [str(date), month, vendor_name,
                       invoice_no, str(payment_day),
                       bill_amount, "Pending", ""]

            bill_sheet.append_row(new_row)
            st.success("Data Saved Successfully")
            st.rerun()

    if col2.button("ESC"):
        st.rerun()

    st.markdown("---")
    st.subheader("Create New Vendor")

    with st.expander("Create Vendor"):

        new_vendor = st.text_input("Vendor Name")
        mobile = st.text_input("Mobile Number")
        gst = st.text_input("GST No")
        email = st.text_input("Email")

        if st.button("Create Vendor"):

            vendor_list = load_vendors()

            if new_vendor.strip() == "":
                st.warning("Vendor Name Required")

            elif new_vendor in vendor_list:
                st.error("Vendor Already Exists ❌")

            else:
                setting_sheet.append_row(
                    [new_vendor, mobile, gst, email])
                st.success("Vendor Created Successfully ✅")
                st.rerun()

# ============================================================
# ================= VENDOR PAYMENT ===========================
# ============================================================

elif menu == "Vendor Payment":

    st.subheader("Vendor Payment Entry")

    vendor_list = load_vendors()
    selected_vendor = st.selectbox("Select Vendor", [""] + vendor_list)

    try:
        all_data = bill_sheet.get_all_values()

        if len(all_data) > 1:
            headers = [h.strip() for h in all_data[0]]
            data = all_data[1:]
            bill_df = pd.DataFrame(data, columns=headers)
        else:
            bill_df = pd.DataFrame()

    except Exception as e:
        st.error(f"Sheet Load Error: {e}")
        bill_df = pd.DataFrame()

    if not bill_df.empty and selected_vendor != "":

        if "Vendor Name" not in bill_df.columns:
            st.error("Sheet1 me 'Vendor Name' header missing hai")
        elif "Status" not in bill_df.columns:
            st.error("Sheet1 me 'Status' header missing hai")
        else:

            pending_df = bill_df[
                (bill_df["Vendor Name"] == selected_vendor) &
                (bill_df["Status"] == "Pending")
            ]

            if not pending_df.empty:

                st.write("Pending Bills")

                for index, row in pending_df.iterrows():

                    st.write(
                        f"Invoice: {row['Invoice Number']} | Amount: {row['Bill Amount']}")

                    pay_amount = st.number_input(
                        f"Pay Amount for {row['Invoice Number']}",
                        key=f"num{index}")

                    if st.button(f"Pay {row['Invoice Number']}", key=f"btn{index}"):

                        actual_row = index + 2  # header skip

                        bill_sheet.update_cell(actual_row, 7, "Paid")
                        bill_sheet.update_cell(actual_row, 8, pay_amount)

                        st.success("Payment Updated")
                        st.rerun()

            else:
                st.info("No Pending Bills")

# ============================================================
# ================= OUTSTANDING ==============================
# ============================================================

else:
    st.subheader("Outstanding Data")
    st.info("Coming Soon...")
