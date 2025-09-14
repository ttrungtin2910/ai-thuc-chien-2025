import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import base64
from io import BytesIO

# PDF processing
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# DOCX processing
try:
    from docx import Document
except ImportError:
    Document = None

# Image processing
try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, data_dir: str = "data/thutuccongdan", openai_service=None):
        """
        Initialize document processor
        
        Args:
            data_dir: Directory containing files
            openai_service: OpenAI service instance for LLM-based extraction
        """
        self.data_dir = data_dir
        self.chunk_size = 1000  # Maximum characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
        self.openai_service = openai_service
        
        # Supported file types and their processors
        self.processors = {
            '.pdf': self._extract_pdf_content,
            '.docx': self._extract_docx_content,
            '.doc': self._extract_docx_content,
            '.txt': self._extract_text_content,
            '.md': self._extract_markdown_content,
            '.png': self._extract_image_content,
            '.jpg': self._extract_image_content,
            '.jpeg': self._extract_image_content
        }
        
    def process_uploaded_file(self, file_path: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Process an uploaded file and extract its content
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        logger.info(f"🔄 [PROCESSOR] Starting to process file: {filename}")
        logger.info(f"📍 [PROCESSOR] File path: {file_path}")
        logger.info(f"📁 [PROCESSOR] File exists: {os.path.exists(file_path)}")
        
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            logger.info(f"📎 [PROCESSOR] File extension: {file_extension}")
            
            if file_extension not in self.processors:
                logger.warning(f"❌ [PROCESSOR] Unsupported file type: {file_extension}")
                logger.info(f"✅ [PROCESSOR] Supported types: {list(self.processors.keys())}")
                return None
            
            logger.info(f"🔧 [PROCESSOR] Using processor for {file_extension}")
            # Extract content using appropriate processor
            processor = self.processors[file_extension]
            content = processor(file_path)
            
            logger.info(f"📝 [PROCESSOR] Content extracted, length: {len(content) if content else 0} characters")
            
            if not content:
                logger.warning(f"⚠️ [PROCESSOR] No content extracted from file: {filename}")
                return None
            
            # Create document object
            doc = {
                "file_name": filename,
                "file_path": file_path,
                "file_type": file_extension,
                "title": self._extract_title_from_filename(filename),
                "content": content,
                "processed_at": None  # Will be set by caller
            }
            
            logger.info(f"✅ [PROCESSOR] Successfully processed file: {filename}")
            logger.info(f"📊 [PROCESSOR] Document stats - Title: '{doc['title']}', Content: {len(content)} chars")
            return doc
            
        except Exception as e:
            logger.error(f"❌ [PROCESSOR] Failed to process file {filename}: {e}", exc_info=True)
            return None
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract title from filename"""
        # Remove extension and replace underscores/hyphens with spaces
        title = os.path.splitext(filename)[0]
        title = re.sub(r'[_-]', ' ', title)
        return title.strip()
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        if not PyPDF2:
            logger.error("PyPDF2 not available. Install PyPDF2 to process PDF files.")
            return ""
        
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            content += f"\n\n--- Page {page_num + 1} ---\n"
                            content += page_text
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            return ""
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text content from DOCX file"""
        if not Document:
            logger.error("python-docx not available. Install python-docx to process DOCX files.")
            return ""
        
        try:
            doc = Document(file_path)
            content = ""
            
            # Extract paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        content += " | ".join(row_text) + "\n"
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error reading DOCX file: {e}")
            return ""
    
    def _extract_text_content(self, file_path: str) -> str:
        """Extract content from text file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, read as binary and decode with errors='replace'
            with open(file_path, 'rb') as file:
                raw_content = file.read()
                return raw_content.decode('utf-8', errors='replace')
                
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            return ""
    
    def _extract_markdown_content(self, file_path: str) -> str:
        """Extract content from markdown file"""
        return self._extract_text_content(file_path)
    
    def _extract_image_content(self, file_path: str) -> str:
        """Extract text content from image using OCR and LLM vision"""
        content = ""
        
        # First try OCR if available
        if Image and pytesseract:
            try:
                with Image.open(file_path) as img:
                    ocr_text = pytesseract.image_to_string(img, lang='vie+eng')
                    if ocr_text.strip():
                        content += "=== OCR Extracted Text ===\n" + ocr_text.strip() + "\n\n"
            except Exception as e:
                logger.warning(f"OCR extraction failed: {e}")
        
        # Then use LLM vision if OpenAI service is available
        if self.openai_service:
            try:
                llm_content = self._extract_image_content_with_llm(file_path)
                if llm_content:
                    content += "=== AI Vision Analysis ===\n" + llm_content
            except Exception as e:
                logger.warning(f"LLM vision extraction failed: {e}")
        
        return content.strip()
    
    def _extract_image_content_with_llm(self, file_path: str) -> str:
        """Extract content from image using LLM vision capabilities"""
        try:
            # Encode image to base64
            with open(file_path, 'rb') as img_file:
                img_bytes = img_file.read()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Prepare messages for GPT-4V
            messages = [
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "Hãy phân tích hình ảnh này và trích xuất tất cả văn bản có thể đọc được. Nếu có bảng biểu, hãy mô tả cấu trúc và nội dung. Nếu có biểu đồ hoặc sơ đồ, hãy giải thích ý nghĩa. Trả lời bằng tiếng Việt."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Use GPT-4V for image analysis
            response = self.openai_service.chat_completion(
                messages, 
                model="gpt-4o", 
                max_tokens=1500
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error using LLM for image analysis: {e}")
            return ""
        
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
    
    def process_and_save_to_milvus(self, file_path: str, filename: str, milvus_service) -> bool:
        """
        Process file and save extracted content to Milvus
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            milvus_service: Milvus service instance
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"🚀 [MILVUS-PROCESSOR] Starting Milvus processing for: {filename}")
        
        try:
            # Extract content from file
            logger.info(f"📄 [MILVUS-PROCESSOR] Step 1: Extracting content from {filename}")
            doc = self.process_uploaded_file(file_path, filename)
            if not doc:
                logger.error(f"❌ [MILVUS-PROCESSOR] Failed to extract content from {filename}")
                return False
            
            logger.info(f"✅ [MILVUS-PROCESSOR] Content extracted successfully")
            
            # Split content into chunks
            logger.info(f"✂️ [MILVUS-PROCESSOR] Step 2: Splitting content into chunks")
            chunks = self._split_text(doc["content"])
            logger.info(f"📊 [MILVUS-PROCESSOR] Generated {len(chunks)} chunks from content")
            
            if not chunks:
                logger.warning(f"⚠️ [MILVUS-PROCESSOR] No chunks generated from {filename}")
                return False
            
            # Prepare documents for Milvus
            logger.info(f"🔧 [MILVUS-PROCESSOR] Step 3: Preparing documents for Milvus")
            milvus_docs = []
            for chunk_idx, chunk in enumerate(chunks):
                milvus_doc = {
                    "file_name": doc["file_name"],
                    "chunk_id": chunk_idx,
                    "content": chunk,
                    "title": doc["title"],
                    "section": f"Chunk {chunk_idx + 1}"
                }
                milvus_docs.append(milvus_doc)
                logger.debug(f"📝 [MILVUS-PROCESSOR] Chunk {chunk_idx}: {len(chunk)} characters")
            
            logger.info(f"✅ [MILVUS-PROCESSOR] Prepared {len(milvus_docs)} documents for Milvus")
            
            # Save to Milvus
            logger.info(f"💾 [MILVUS-PROCESSOR] Step 4: Saving to Milvus database")
            logger.info(f"🔌 [MILVUS-PROCESSOR] Milvus service available: {milvus_service is not None}")
            
            success = milvus_service.insert_documents(milvus_docs)
            if success:
                logger.info(f"🎉 [MILVUS-PROCESSOR] Successfully saved {len(milvus_docs)} chunks from {filename} to Milvus")
                
                # Verify data was saved
                stats = milvus_service.get_collection_stats()
                logger.info(f"📈 [MILVUS-PROCESSOR] Collection now has {stats} total entities")
                return True
            else:
                logger.error(f"❌ [MILVUS-PROCESSOR] Failed to save chunks from {filename} to Milvus")
                return False
                
        except Exception as e:
            logger.error(f"💥 [MILVUS-PROCESSOR] Error processing and saving {filename} to Milvus: {e}", exc_info=True)
            return False
    
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
