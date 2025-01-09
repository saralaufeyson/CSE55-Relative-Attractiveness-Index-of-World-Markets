import streamlit as st

# Map options to labels for Home and Predictions
option_map = {
    0: "Home",
    1: "Predictions",
}

# Create pills for navigation
selection = st.pills(
    "Navigation",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)

# Conditional rendering based on selected pill
if selection == 0:  # Home
    st.title("Welcome to the Home Page!")
    st.write("This is the main landing page.")
elif selection == 1:  # Predictions
    st.title("Predictions Page")
    st.write("Here you can view and analyze predictions.")
