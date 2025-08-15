import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

class RAGPipeline:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.vector_store = None
        self.llm = None
        self.readme_content = ""  # New: To store README content
        self.supported_extensions = [
            ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".go",
            ".html", ".css", ".scss", ".md", ".json", ".xml", ".yaml", ".yml",
            ".txt", "Dockerfile", ".sh"
        ]
        self.ignore_directories = [".git", "node_modules", "venv", "__pycache__"]
        self.ignore_files = [
            "package-lock.json", "yarn.lock", "pnpm-lock.yaml", 
            "Gemfile.lock", "poetry.lock"
        ]

    def _load_and_split_documents(self):
        documents = []
        readme_path = ""
        # First, find the README file
        for dirpath, _, filenames in os.walk(self.repo_path):
            for filename in filenames:
                if filename.lower() == "readme.md":
                    readme_path = os.path.join(dirpath, filename)
                    break
            if readme_path:
                break
        
        # If a README is found, load it and store its content
        if readme_path:
            try:
                print(f"Found README at: {readme_path}")
                loader = TextLoader(readme_path, encoding='utf-8')
                self.readme_content = loader.load()[0].page_content
                documents.extend(loader.load())
            except Exception as e:
                print(f"Failed to load README.md: {e}")

        # Now, load all other supported files
        for dirpath, dirnames, filenames in os.walk(self.repo_path):
            dirnames[:] = [d for d in dirnames if d not in self.ignore_directories]
            for filename in filenames:
                if filename.lower() == "readme.md" or filename in self.ignore_files:
                    continue
                if any(filename.endswith(ext) for ext in self.supported_extensions):
                    file_path = os.path.join(dirpath, filename)
                    try:
                        loader = TextLoader(file_path, encoding='utf-8')
                        documents.extend(loader.load())
                    except Exception as e:
                        print(f"Failed to load {file_path}: {e}")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        return text_splitter.split_documents(documents)

    def initialize(self):
        print("Loading and splitting documents...")
        split_docs = self._load_and_split_documents()
        
        if not split_docs:
            print("No supported documents found to process.")
            return

        print("Creating vector store with Google embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = Chroma.from_documents(documents=split_docs, embedding=embeddings)
        
        print("Initializing the language model...")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.2,
            convert_system_message_to_human=True
        )
        print("Pipeline initialized successfully.")

    def ask_question(self, question: str) -> str:
        if not self.llm or not self.vector_store:
            return "The pipeline has not been initialized. Please run the initialize method first."
        
        print(f"Retrieving documents for question: {question}")
        # Retrieve relevant documents from the vector store as before
        retriever = self.vector_store.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(question)
        retrieved_context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # --- NEW: Build a custom, more powerful prompt ---
        prompt = f"""
        You are an expert developer and AI assistant. Your task is to answer questions about a GitHub repository.
        
        Use the following context to answer the user's question. The README.md content is the most important for high-level summaries.
        The "Additional Retrieved Context" is from other files and provides specific details.

        ---
        **Primary Context (from README.md):**
        {self.readme_content}
        ---
        **Additional Retrieved Context (from other relevant files):**
        {retrieved_context}
        ---

        **User's Question:** {question}

        **Answer:**
        """
        
        print("Generating answer with custom prompt...")
        # Invoke the LLM directly with our custom prompt
        response = self.llm.invoke(prompt)
        return response.content