import streamlit as st
from PIL import Image
import os
from main import generate_and_save_diagram

st.title("Architecture Diagram Generator 💻")

user_prompt = st.text_area("Describe your architecture:", height=300, placeholder="e.g., A web server connected to a database and cache...")

if st.button("Generate Diagram"):
    if user_prompt:
        with st.spinner("Generating diagram..."):
            diagram_path = generate_and_save_diagram(user_prompt)
            if diagram_path and os.path.exists(diagram_path):
                st.success("Diagram generated successfully!")
                st.image(Image.open(diagram_path), caption="Generated Architecture Diagram")
            else:
                st.error("Diagram could not be generated. Please check your input or try again.")
    else:
        st.error("Please provide a description of your architecture.")

 