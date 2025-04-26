import streamlit as st
from PIL import Image
import os
from main import generate_and_save_diagram, update_diagram_with_feedback

# Set page configuration with a custom theme
st.set_page_config(
    page_title="Architecture Diagram Generator",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS to improve the look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #DCEDC8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🏗️ Architecture Diagram Generator</h1>", unsafe_allow_html=True)

# Initialize session state variables
if 'diagram_generated' not in st.session_state:
    st.session_state.diagram_generated = False
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""
if 'feedback_count' not in st.session_state:
    st.session_state.feedback_count = 0
if 'diagram_path' not in st.session_state:
    st.session_state.diagram_path = None
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = True

# Sidebar for instructions and examples
with st.sidebar:
    st.markdown("<h2 class='subheader'>How It Works</h2>", unsafe_allow_html=True)
    
    # Toggle for instructions
    if st.checkbox("Show Instructions", value=st.session_state.show_instructions):
        st.markdown("""
        ### 1. Describe Your Architecture
        Provide a detailed description of the architecture you want to visualize.
        
        ### 2. Generate Diagram
        Click the 'Generate Diagram' button to create your diagram using AI.
        
        ### 3. Refine With Feedback
        After viewing your diagram, provide feedback to refine it further.
        
        ### Example Prompts:
        - "Create a microservice architecture with API gateway, 3 services and a database"
        - "AWS architecture with EC2 instances, S3 storage, and RDS database"
        """)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Current Progress")
    progress_value = 0.3 if not st.session_state.diagram_generated else 0.7 if st.session_state.feedback_count == 0 else 1.0
    progress_label = "Step 1: Description" if not st.session_state.diagram_generated else "Step 2: Initial Diagram" if st.session_state.feedback_count == 0 else "Step 3: Refined Diagram"
    st.progress(progress_value, text=progress_label)
    
    if st.session_state.feedback_count > 0:
        st.markdown(f"Feedback iterations: {st.session_state.feedback_count}")

# Main content area
if not st.session_state.diagram_generated:
    # Initial prompt input section
    st.markdown("<h2 class='subheader'>Describe Your Architecture</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Provide a detailed description of the architecture you want to visualize. 
    Include components, connections, and any specific design patterns or technologies.
    </div>
    """, unsafe_allow_html=True)
    
    user_prompt = st.text_area(
        "Architecture Description:",
        height=200,
        placeholder="",
        key="prompt_input"
    )
    
    
    # Generate button
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    with generate_col2:
        if st.button("✨ Generate Diagram", key="generate_btn", use_container_width=True):
            if user_prompt:
                with st.spinner("🔄 Generating your architecture diagram... This may take a moment."):
                    st.session_state.user_prompt = user_prompt
                    diagram_path = generate_and_save_diagram(user_prompt)
                    if diagram_path and os.path.exists(diagram_path):
                        st.session_state.diagram_generated = True
                        st.session_state.diagram_path = diagram_path
                        st.rerun()
                    else:
                        st.error("❌ Diagram could not be generated. Please check your input or try again.")
            else:
                st.error("⚠️ Please provide a description of your architecture.")

else:
    # Diagram display and feedback section
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        st.markdown("<h2 class='subheader'>Your Architecture Diagram</h2>", unsafe_allow_html=True)
        
        if st.session_state.diagram_path and os.path.exists(st.session_state.diagram_path):
            # Display with expandable view
            with st.expander("View Full Size", expanded=True):
                st.image(
                    Image.open(st.session_state.diagram_path),
                     use_container_width=True
                )
            
            # Download button
            with open(st.session_state.diagram_path, "rb") as file:
                btn = st.download_button(
                    label="📥 Download Diagram",
                    data=file,
                    file_name="architecture_diagram.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            st.error("Diagram file not found. Please try generating again.")
    
    with col2:
        st.markdown("<h2 class='subheader'>Refine Your Diagram</h2>", unsafe_allow_html=True)
        
        # Feedback form
        st.markdown("""
        <div class="info-box">
        Provide feedback to refine your diagram. Be specific about what you want to change.
        </div>
        """, unsafe_allow_html=True)
        
        feedback = st.text_area(
            "Your Feedback:",
            height=150,
            placeholder="Example: 'Add more details to the database component' or 'Change the layout to horizontal flow'",
            key="feedback_input"
        )
        
        # Update button
        if st.button("🔄 Update Diagram", key="update_btn", use_container_width=True):
            if feedback:
                with st.spinner("Updating your diagram based on feedback..."):
                    st.session_state.feedback_count += 1
                    updated_path = update_diagram_with_feedback(st.session_state.user_prompt, feedback)
                    if updated_path and os.path.exists(updated_path):
                        st.session_state.diagram_path = updated_path
                        st.markdown("""
                        <div class="success-message">
                        ✅ Diagram updated successfully! Check the diagram view to see your changes.
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("❌ Failed to update the diagram. Please try again.")
            else:
                st.warning("⚠️ Please provide feedback to update the diagram.")
        
        # Display original prompt for reference
        st.markdown("### Original Description")
        st.markdown(f"<div class='info-box'>{st.session_state.user_prompt}</div>", unsafe_allow_html=True)
        
        # Finish button
        if st.button("🏁 Start New Diagram", key="finish_btn", use_container_width=True):
            # Reset the session state
            st.session_state.diagram_generated = False
            st.session_state.user_prompt = ""
            st.session_state.feedback_count = 0
            st.session_state.diagram_path = None
            st.rerun()

