import streamlit as st
from pymongo import MongoClient
import pandas as pd
from hashlib import sha256
import re
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from environment variables
mongo_uri = os.getenv("MONGO_URI")
# Initialize MongoDB client
client = MongoClient(mongo_uri)  # Replace with your MongoDB URI
db = client["address_data"] 
collection = db["details"]
users_collection = db['users']

# Function to check user credentials
def check_credentials(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

# Login Page
def login_page():
    st.markdown("<h1 style='text-align: center; color:rgb(241 6 201);'>Login</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username")
        print(username)
        password = st.text_input("Password", type="password")
        print(password)
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

# Main Page
def main_page():
    st.markdown("""
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
        <style>
            body {
                background-color: #f8f9fa;
            }
            .form-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                margin: 20px auto;
                max-width: 600px;
            }
            .input-group-text {
                background-color: #007bff;
                color: white;
            }
            .form-select, .form-control {
                border: 1px solid #ced4da;
                border-radius: 5px;
            }
            .btn-primary {
                background-color: #007bff;
                border: none;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            .stButton>button {
                background-color: rgb(241 6 201);
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            .stSelectbox label, .stTextInput label {
                font-weight: bold;
                color: rgb(241 6 201);
            }
            .table-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                margin: 20px auto;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: rgb(241 6 201);'>BSL Township Occupancy Status</h1>", unsafe_allow_html=True)
    # Define the columns that can be selected with proper formatting
    columns = {
        'address': 'Address',
        'name': 'Name',
        'bsl_on_roll': 'BSL On Roll',
        'lease': 'Lease',
        'licence': 'Licence',
        # Add other columns here if needed
    }
    # Create a form-like layout using Streamlit's columns and widgets
    with st.container():
        # Dropdown to select the column
        selected_column_key = st.selectbox("Select the criteria", list(columns.keys()), format_func=lambda x: columns[x])

        # Text input to enter the value for the selected column
        entered_value = st.text_input(f"Enter the value for {columns[selected_column_key]}")

        # Button to trigger the search
        if st.button("Search"):
            # Preprocess entered value: strip, normalize spaces
            entered_value = entered_value.strip()
            normalized_value = re.sub(r'\s+', ' ', entered_value)  # Replace multiple spaces with a single space
            
            if normalized_value:  # Only perform the query if normalized_value is not empty
                # Escape special characters in the normalized value
                escaped_value = re.escape(normalized_value)
                # Create regex pattern to match value with optional spaces
                regex_pattern = f'^{escaped_value}$'.replace(r'\ ', r'\s*')

                # Use $regex with $options to handle case insensitivity in MongoDB
                query = {
                    selected_column_key: {
                        '$regex': regex_pattern,
                        '$options': 'i'
                    }
                }
                result = collection.find_one(query)
                if result:
                    # Remove the '_id' key from the result dictionary
                    result.pop('_id', None)  # Use pop to remove '_id', if it exists
                    
                    # Format the result with user-friendly column names
                    formatted_result = {columns.get(key, key): value for key, value in result.items()}
                    
                    # Convert the result to a DataFrame
                    df = pd.DataFrame([formatted_result])

                    # Apply Bootstrap styles to the DataFrame
                    styled_df = df.style.set_table_attributes('class="table table-striped table-bordered"').set_table_styles([
                        {'selector': 'thead th', 'props': [('background-color', '#007bff'), ('color', 'white')]},
                        {'selector': 'tbody td', 'props': [('padding', '10px'), ('border', '1px solid #ddd')]}
                    ])

                    # Display the styled DataFrame in Streamlit
                    st.markdown("<div class='table-container'>" + styled_df.to_html() + "</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: red;'>No document found with the given criteria.</p>", unsafe_allow_html=True)

# Streamlit App Main Function
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
