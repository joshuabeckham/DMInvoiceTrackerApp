import streamlit as st
import pandas as pd

st.title("Demand Machine Invoice Tracker")

@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    if 'Open balance' in data.columns and 'Amount' in data.columns:
        data['Open balance'] = data['Open balance'].replace('[\$,]', '', regex=True)
        data['Amount'] = data['Amount'].replace('[\$,]', '', regex=True)
        try:
            data['Open balance'] = pd.to_numeric(data['Open balance'])
            data['Amount'] = pd.to_numeric(data['Amount'])
        except Exception as e:
            st.error(f"Error converting columns to numeric: {e}")
    return data

def process_data(data):
    if data.empty:
        st.error("The loaded data is empty.")
        return pd.DataFrame(), pd.DataFrame()
    
    if 'Open balance' not in data.columns:
        st.error("'Open balance' column is missing in the loaded data.")
        return pd.DataFrame(), pd.DataFrame()

    current_invoices = data[data['Open balance'] > 0]
    past_invoices = data[data['Open balance'] == 0]

    return current_invoices, past_invoices

def display_t_chart(current_invoices):
    if not current_invoices.empty:
        st.title("Total Amount Owed By Client")
        total_amount = current_invoices.groupby('Customer full name')['Amount'].sum().reset_index()
        total_amount['Amount'] = total_amount['Amount'].apply(lambda x: f"{x:,.2f}")
        st.table(total_amount)

def home_page(current_invoices):
    display_t_chart(current_invoices)
    
    if not current_invoices.empty:
        overall_total = current_invoices['Amount'].sum()
        st.write(f"Overall Total: ${overall_total:,.2f}")
      
        st.write()
        
        st.title("Current Invoices:")
        customers = current_invoices['Customer full name'].unique()
        for customer in customers:
            st.subheader(customer)
            customer_invoices = current_invoices[current_invoices['Customer full name'] == customer].copy()
            customer_invoices['Amount'] = customer_invoices['Amount'].apply(lambda x: f"{x:,.2f}")
            st.table(customer_invoices[['Invoice date', 'Invoice number', 'Amount']])
            if st.button(f"See Past Invoices for {customer}"):
                st.session_state.customer = customer
                st.experimental_rerun()
    else:
        st.warning("No current invoices to display.")

def past_invoices_page(customer, all_invoices):
    st.title(f"All Invoices for {customer}")
    
    if not all_invoices.empty:
        customer_invoices = all_invoices[all_invoices['Customer full name'] == customer].copy()
        customer_invoices['Amount'] = customer_invoices['Amount'].apply(lambda x: f"{x:,.2f}")
        
        # Segregate between Currently Due and Already Paid Invoices
        currently_due_invoices = customer_invoices[customer_invoices['Open balance'] > 0]
        already_paid_invoices = customer_invoices[customer_invoices['Open balance'] == 0]

        # Display Currently Due Invoices
        if not currently_due_invoices.empty:
            st.subheader("Currently Due:")
            st.table(currently_due_invoices[['Invoice date', 'Invoice number', 'Amount']])
        else:
            st.write("No Currently Due Invoices for this customer.")

        # Display Already Paid Invoices
        if not already_paid_invoices.empty:
            st.subheader("Already Paid:")
            st.table(already_paid_invoices[['Invoice date', 'Invoice number', 'Amount']])
        else:
            st.write("No Already Paid Invoices for this customer.")
    else:
        st.warning(f"No invoices found for {customer}.")
    
    if st.button("Return to Home Page"):
        if 'customer' in st.session_state:
            del st.session_state['customer']
        st.experimental_rerun()

def main():
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        data = load_data(uploaded_file)
        current_invoices, past_invoices = process_data(data)

        # Combining both current and past invoices
        all_invoices = pd.concat([current_invoices, past_invoices])

        if 'customer' in st.session_state:
            past_invoices_page(st.session_state.customer, all_invoices)
        else:
            home_page(current_invoices)
    else:
        st.write("Please upload a CSV file to proceed.")

if __name__ == '__main__':
    main()
