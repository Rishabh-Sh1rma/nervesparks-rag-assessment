import streamlit as st
from dotenv import load_dotenv
import os

# --- Our Custom Modules ---
from core.utils import clone_repo
from core.rag_pipeline import RAGPipeline

# Load environment variables from .env file
load_dotenv()

# --- Function to load our custom CSS ---
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="CodeNavigator AI",
    page_icon="🤖",
    layout="wide"
)

# Load our custom stylesheet
load_css("static/style.css")

# --- UI Rendering ---

st.title("CodeNavigator AI 🧭")
st.markdown("##### Chat with any public GitHub repository using the power of Retrieval-Augmented Generation.")

# Use a container for the main input section for better visual grouping
with st.container():
    repo_url = st.text_input("Enter a public GitHub Repository URL to begin:", placeholder="e.g., https://github.com/langchain-ai/langchain")
    
    if st.button("Analyze Repository", key="analyze_button"):
        if repo_url:
            with st.spinner("Analyzing repository... This may take a few minutes for large repos."):
                try:
                    repo_path = clone_repo(repo_url)
                    pipeline = RAGPipeline(repo_path=repo_path)
                    pipeline.initialize()
                    st.session_state.rag_pipeline = pipeline # Store pipeline in session state
                    st.success("Repository analyzed successfully! You can now ask questions below.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a GitHub repository URL.")

# --- Question Answering Interface ---

# This section only appears after the pipeline has been successfully initialized
if 'rag_pipeline' in st.session_state and st.session_state.rag_pipeline is not None:
    st.markdown("---")
    
    question = st.text_input("Ask a question about the codebase:", placeholder="e.g., How is the RetrievalQA chain implemented?")

    if question:
        with st.spinner("Searching for answers..."):
            try:
                answer = st.session_state.rag_pipeline.ask_question(question)
                st.info("Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")