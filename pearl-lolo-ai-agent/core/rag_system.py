#!/usr/bin/env python3
"""
RAG System - Retrieval Augmented Generation for Pearl Lolo
"""

import os
import faiss
import numpy as np
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma, FAISS
from langchain.document_loaders import (
    PyPDFLoader, 
    TextLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader
)
from pathlib import Path

class RAGSystem:
    def __init__(self, config_manager):
        self.config = config_manager
        self.vector_store = None
        self.embeddings = None
        self.text_splitter = None
        self.vector_store_path = Path("data/embeddings/vector_store")
        
        self.setup_components()
        self.load_existing_store()
    
    def setup_components(self):
        """Initialize RAG components"""
        # Initialize embeddings
        embedding_model = self.config.get('rag.embedding_model', 'all-MiniLM-L6-v2')
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize text splitter
        chunk_size = self.config.get('rag.chunk_size', 1000)
        chunk_overlap = self.config.get('rag.chunk_overlap', 200)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    
    def load_existing_store(self):
        """Load existing vector store if available"""
        try:
            if self.vector_store_path.exists():
                vector_store_type = self.config.get('rag.vector_store', 'chromadb')
                
                if vector_store_type == 'chromadb':
                    self.vector_store = Chroma(
                        persist_directory=str(self.vector_store_path),
                        embedding_function=self.embeddings
                    )
                elif vector_store_type == 'faiss':
                    self.vector_store = FAISS.load_local(
                        str(self.vector_store_path),
                        self.embeddings
                    )
                
                print(f"✅ Loaded existing vector store with {self.get_document_count()} documents")
            else:
                print("📁 No existing vector store found")
        except Exception as e:
            print(f"❌ Failed to load vector store: {e}")
            self.vector_store = None
    
    def add_document(self, file_path: str) -> bool:
        """Add a document to the RAG system"""
        try:
            # Load document based on file type
            loader = self._get_document_loader(file_path)
            if not loader:
                return False
            
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            if self.vector_store is None:
                self._create_new_store(chunks)
            else:
                self.vector_store.add_documents(chunks)
                self._save_store()
            
            print(f"✅ Added {len(chunks)} chunks from {Path(file_path).name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add document {file_path}: {e}")
            return False
    
    def _get_document_loader(self, file_path: str):
        """Get appropriate document loader for file type"""
        file_ext = Path(file_path).suffix.lower()
        
        loaders = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.docx': Docx2txtLoader,
            '.pptx': UnstructuredPowerPointLoader,
            '.xlsx': UnstructuredExcelLoader,
        }
        
        loader_class = loaders.get(file_ext)
        if loader_class:
            return loader_class(file_path)
        
        print(f"❌ Unsupported file type: {file_ext}")
        return None
    
    def _create_new_store(self, chunks):
        """Create new vector store"""
        vector_store_type = self.config.get('rag.vector_store', 'chromadb')
        
        if vector_store_type == 'chromadb':
            self.vector_store = Chroma.from_documents(
                chunks,
                self.embeddings,
                persist_directory=str(self.vector_store_path)
            )
        elif vector_store_type == 'faiss':
            self.vector_store = FAISS.from_documents(
                chunks,
                self.embeddings
            )
            self._save_store()
    
    def _save_store(self):
        """Save vector store to disk"""
        try:
            if isinstance(self.vector_store, Chroma):
                self.vector_store.persist()
            elif isinstance(self.vector_store, FAISS):
                self.vector_store.save_local(str(self.vector_store_path))
        except Exception as e:
            print(f"❌ Failed to save vector store: {e}")
    
    def get_relevant_context(self, query: str, k: int = 5) -> str:
        """Get relevant context for a query"""
        if self.vector_store is None:
            return ""
        
        try:
            # Search for relevant documents
            docs = self.vector_store.similarity_search(query, k=k)
            
            # Combine relevant content
            context = "\n\n".join([doc.page_content for doc in docs])
            
            return context
            
        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            return ""
    
    def clear_documents(self) -> bool:
        """Clear all documents from RAG system"""
        try:
            if self.vector_store_path.exists():
                import shutil
                shutil.rmtree(self.vector_store_path)
            
            self.vector_store = None
            print("✅ Cleared all documents from RAG system")
            return True
            
        except Exception as e:
            print(f"❌ Failed to clear documents: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get number of documents in the vector store"""
        if self.vector_store is None:
            return 0
        
        try:
            if isinstance(self.vector_store, Chroma):
                return self.vector_store._collection.count()
            elif isinstance(self.vector_store, FAISS):
                return self.vector_store.index.ntotal
            else:
                return 0
        except:
            return 0
    
    def search_similar(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.vector_store is None:
            return []
        
        try:
            docs = self.vector_store.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs:
                results.append({
                    'content': doc.page_content,
                    'score': float(score),
                    'metadata': doc.metadata
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return []