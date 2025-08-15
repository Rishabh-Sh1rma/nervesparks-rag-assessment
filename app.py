import nest_asyncio
nest_asyncio.apply()

import streamlit as st
from dotenv import load_dotenv
import os
import shutil # Import shutil for the cleanup logic

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

# --- Initialize Session State ---
# This is crucial for remembering the pipeline and the path of the last repo
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'last_repo_path' not in st.session_state:
    st.session_state.last_repo_path = None

# --- UI Rendering ---
st.title("CodeNavigator AI 🧭")
st.markdown("##### Chat with any public GitHub repository using the power of Retrieval-Augmented Generation.")

# Use a container for the main input section for better visual grouping
with st.container():
    repo_url = st.text_input("Enter a public GitHub Repository URL to begin:", placeholder="e.g., https://github.com/langchain-ai/langchain")
    
    if st.button("Analyze Repository", key="analyze_button"):
        if repo_url:
            with st.spinner("Analyzing repository... This may take a few minutes for large repos."):
                
                # --- NEW CLEANUP LOGIC ---
                # Clean up the directory from the PREVIOUS run, if it exists.
                # This prevents old temp folders from piling up.
                if st.session_state.last_repo_path and os.path.exists(st.session_state.last_repo_path):
                    print(f"Cleaning up previous directory: {st.session_state.last_repo_path}")
                    shutil.rmtree(st.session_state.last_repo_path, ignore_errors=True)
                # --- END NEW CLEANUP LOGIC ---

                try:
                    # The clone_repo function now returns a NEW, UNIQUE path each time
                    repo_path = clone_repo(repo_url)
                    # Store this new path so we can clean it up on the NEXT run
                    st.session_state.last_repo_path = repo_path 
                    
                    pipeline = RAGPipeline(repo_path=repo_path)
                    pipeline.initialize()
                    
                    st.session_state.rag_pipeline = pipeline # Store the new pipeline in session state
                    st.success("Repository analyzed successfully! You can now ask questions below.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a GitHub repository URL.")

# --- Question Answering Interface ---
if st.session_state.rag_pipeline:
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