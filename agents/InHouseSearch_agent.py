import os
from pathlib import Path
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

from tools.rag_tool import RAGRetriever, VectorStore, EmbeddingManager
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
import uuid

load_dotenv()

class IHouseRAGAgent:
    def __init__(self, model_name="mistral-large-latest", top_k=5, pdf_directory="./data"):
        """
        Fully self-contained RAG agent.
        Processes PDFs, generates embeddings, stores in vector store, retrieves, and answers.
        """
        self.top_k = top_k
        self.pdf_directory = pdf_directory

        # Load LLM
        mistral_api_key = os.getenv("MISTRALAI_API_KEY")
        if not mistral_api_key:
            raise ValueError("MISTRALAI_API_KEY not set in .env")
        
        self.llm = ChatMistralAI(
            mistral_api_key=mistral_api_key,
            model_name=model_name,
            max_tokens=2048,
            temperature=0.2
        )

        # Initialize embedding manager and vector store
        self.embedder = EmbeddingManager()
        self.vstore = VectorStore()
        self.retriever = RAGRetriever(self.vstore, self.embedder)

        # System prompt for context-grounded answers
        self.system_prompt = (
            "You are a RAG agent. Use ONLY the retrieved context to answer the question. "
            "Provide a detailed, well-structured, and complete explanation. "
            "Do not hallucinate or add info not found in the context. "
            "If context lacks information, say so clearly."
        )

        # Process PDFs and store embeddings if vector store is empty
        if self.vstore.collection.count() == 0:
            self._process_pdfs_to_vectorstore()

    def _process_pdfs_to_vectorstore(self):
        """Load PDFs, split into chunks, generate embeddings, store in vector store"""
        print("Processing PDFs and generating embeddings...")
        pdf_dir = Path(self.pdf_directory)
        all_documents = []

        # Load PDFs
        pdf_files = list(pdf_dir.glob("**/*.pdf"))
        print(f"Found {len(pdf_files)} PDFs to process")
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                for doc in docs:
                    doc.metadata['source_file'] = pdf_file.name
                    doc.metadata['file_type'] = 'pdf'
                all_documents.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {e}")

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, length_function=len, separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(all_documents)
        print(f"Split {len(all_documents)} documents into {len(chunks)} chunks")

        # Generate embeddings
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedder.generate_embeddings(texts)

        # Add to vector store
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [dict(chunk.metadata) for chunk in chunks]
        self.vstore.add_documents(chunks, embeddings)
        print("PDF processing and embedding generation complete.")

    def run(self, query: str) -> str:
        """Retrieve docs from vector store, feed to LLM, return answer."""
        results = self.retriever.retrieve(query, top_k=self.top_k)
        context = "\n\n".join([doc["content"] for doc in results]) if results else ""

        if not context:
            return "No relevant documents found in the knowledge base."

        final_prompt = (
            f"{self.system_prompt}\n\n"
            f"### CONTEXT:\n{context}\n\n"
            f"### USER QUESTION:\n{query}\n\n"
            f"### ANSWER (detailed and context-grounded):"
        )

        response = self.llm.invoke(final_prompt)
        return response.content
