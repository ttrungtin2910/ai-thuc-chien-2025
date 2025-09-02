import os
import re
from typing import List, Dict, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, data_dir: str = "data/thutuccongdan"):
        """
        Initialize document processor
        
        Args:
            data_dir: Directory containing markdown files
        """
        self.data_dir = data_dir
        self.chunk_size = 1000  # Maximum characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
        
    def read_markdown_files(self) -> List[Dict[str, Any]]:
        """
        Read all markdown files and extract content
        
        Returns:
            List of document dictionaries
        """
        documents = []
        data_path = Path(self.data_dir)
        
        if not data_path.exists():
            logger.error(f"Data directory not found: {self.data_dir}")
            return documents
        
        # Get all markdown files
        md_files = list(data_path.glob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract document metadata
                title, sections = self._parse_markdown_content(content)
                
                # Create document object
                doc = {
                    "file_name": md_file.name,
                    "title": title,
                    "content": content,
                    "sections": sections
                }
                
                documents.append(doc)
                logger.info(f"Processed file: {md_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to read file {md_file}: {e}")
        
        return documents
    
    def _parse_markdown_content(self, content: str) -> tuple:
        """
        Parse markdown content to extract title and sections
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (title, sections)
        """
        lines = content.split('\n')
        title = "Untitled"
        sections = []
        current_section = ""
        current_section_title = ""
        
        for line in lines:
            # Extract main title (# header)
            if line.startswith('# ') and not title or title == "Untitled":
                title = line[2:].strip()
            
            # Extract sections (## headers)
            elif line.startswith('## '):
                # Save previous section
                if current_section.strip():
                    sections.append({
                        "title": current_section_title,
                        "content": current_section.strip()
                    })
                
                # Start new section
                current_section_title = line[3:].strip()
                current_section = ""
            
            else:
                current_section += line + '\n'
        
        # Add last section
        if current_section.strip():
            sections.append({
                "title": current_section_title,
                "content": current_section.strip()
            })
        
        return title, sections
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks for embedding
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of chunked documents
        """
        chunked_docs = []
        
        for doc in documents:
            # Process each section separately
            for section_idx, section in enumerate(doc["sections"]):
                section_content = section["content"]
                section_title = section["title"]
                
                # Split section into chunks
                chunks = self._split_text(section_content)
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunked_doc = {
                        "file_name": doc["file_name"],
                        "chunk_id": section_idx * 100 + chunk_idx,  # Unique chunk ID
                        "content": chunk,
                        "title": doc["title"],
                        "section": section_title
                    }
                    chunked_docs.append(chunked_doc)
            
            # Also create chunks for the full document
            full_content_chunks = self._split_text(doc["content"])
            for chunk_idx, chunk in enumerate(full_content_chunks):
                chunked_doc = {
                    "file_name": doc["file_name"],
                    "chunk_id": 9000 + chunk_idx,  # Different range for full document chunks
                    "content": chunk,
                    "title": doc["title"],
                    "section": "Full Document"
                }
                chunked_docs.append(chunked_doc)
        
        logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to find a good break point (sentence ending)
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + self.chunk_size - 100, start)
                search_text = text[search_start:end]
                
                # Find sentence endings
                sentence_endings = [m.end() for m in re.finditer(r'[.!?]\s+', search_text)]
                if sentence_endings:
                    # Use the last sentence ending
                    end = search_start + sentence_endings[-1]
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(end - self.chunk_overlap, start + 1)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'[#*`_]+', '', text)
        
        # Trim
        text = text.strip()
        
        return text
