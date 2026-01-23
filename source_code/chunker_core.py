"""Structured Chunking Core Implementation: Heading-based Intelligent Chunking with Breadcrumb Inheritance

Core Features:
1. Heading-level based splitting
2. Breadcrumb path inheritance
3. Block boundary protection (code blocks, tables)
"""
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class HeadingExtractor:
    """Heading extractor"""
    
    @staticmethod
    def parse_headings(text: str) -> List[Tuple[int, int, str]]:
        """
        Parse all headings in text
        
        Returns:
            [(line_index, level, title), ...]
        """
        lines = text.split('\n')
        headings = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Markdown ATX style: # Title
            match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append((i, level, title))
        
        return headings
    
    @staticmethod
    def extract_heading_from_chunk(chunk_text: str) -> Dict:
        """Extract heading information from chunk text"""
        for line in chunk_text.split('\n')[:5]:
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                return {
                    'has_heading': True,
                    'heading': match.group(2).strip(),
                    'level': len(match.group(1))
                }
        return {'has_heading': False, 'heading': '', 'level': 0}


class StructuredChunker:
    """Structured chunker: heading-based intelligent chunking"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_by_headings(
        self,
        text: str,
        headings: List[Tuple[int, int, str]],
        file_name: str,
        file_path: str,
    ) -> List[Dict]:
        """
        Intelligent chunking based on headings
        
        Returns:
            List[Dict]: List of chunks containing content and metadata
        """
        if not headings:
            chunks_data = self._split_by_paragraph(text)
        else:
            chunks_data = self._split_by_headings(text, headings)
        
        # Merge short chunks
        chunks_data = self._merge_short_chunks(chunks_data)
        
        # Apply overlap
        if self.chunk_overlap > 0 and len(chunks_data) > 1:
            chunks_data = self._apply_overlap(chunks_data)
        
        # Inject breadcrumb paths
        final_chunks = []
        previous_heading_path = None
        
        for i, chunk_data in enumerate(chunks_data):
            content = chunk_data.get('content', '')
            
            # Extract heading information
            heading_info = chunk_data.get('heading_info', {})
            if not heading_info:
                heading_info = HeadingExtractor.extract_heading_from_chunk(content)
            
            # Build heading path
            current_heading_path = self._build_heading_path(
                content, heading_info, headings, text.split('\n')
            )
            
            # If current chunk has no heading, inherit from previous chunk
            if not heading_info.get('has_heading') and previous_heading_path:
                heading_info = {
                    'has_heading': True,
                    'heading': previous_heading_path[-1][1] if previous_heading_path else '',
                    'level': previous_heading_path[-1][0] if previous_heading_path else 0,
                    'parent_heading_path': previous_heading_path
                }
                
                # Inject breadcrumb path
                breadcrumb = ' > '.join([h[1] for h in previous_heading_path])
                if not content.strip().startswith('[Context:'):
                    context_prefix = f"[Context: {file_name} > {breadcrumb}]"
                    content = f"{context_prefix}\n\n{content}"
            
            # Build metadata
            metadata = {
                'format': Path(file_path).suffix[1:] if Path(file_path).suffix else 'txt',
                'source_file': file_path,
                'chunk_id': i,
                'inherited_heading': not heading_info.get('has_heading', False) and previous_heading_path is not None
            }
            
            if heading_info.get('has_heading'):
                metadata.update({
                    'heading': heading_info.get('heading', ''),
                    'heading_level': heading_info.get('level', 0),
                })
                if current_heading_path:
                    metadata['breadcrumb'] = ' > '.join([h[1] for h in current_heading_path])
                    metadata['parent_header'] = ' | '.join([h[1] for h in current_heading_path])
            
            final_chunks.append({
                'content': content,
                'metadata': metadata
            })
            
            # Update previous_heading_path
            if heading_info.get('has_heading') and current_heading_path:
                previous_heading_path = current_heading_path
        
        return final_chunks
    
    def _split_by_headings(
        self,
        text: str,
        headings: List[Tuple[int, int, str]]
    ) -> List[Dict]:
        """Split text based on headings"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Process each heading section
        for i, (start_line, level, title) in enumerate(headings):
            end_line = next(
                (headings[j][0] for j in range(i + 1, len(headings)) if headings[j][1] <= level),
                len(lines)
            )
            section_text = '\n'.join(lines[start_line:end_line]).strip()
            section_size = len(section_text)
            
            if section_size <= self.chunk_size:
                if current_size + section_size <= self.chunk_size:
                    current_chunk.append(section_text)
                    current_size += section_size
                else:
                    if current_chunk:
                        chunk_content = '\n\n'.join(current_chunk)
                        heading_info = HeadingExtractor.extract_heading_from_chunk(chunk_content)
                        chunks.append({'content': chunk_content, 'heading_info': heading_info})
                    current_chunk, current_size = [section_text], section_size
            else:
                if current_chunk:
                    chunk_content = '\n\n'.join(current_chunk)
                    heading_info = HeadingExtractor.extract_heading_from_chunk(chunk_content)
                    chunks.append({'content': chunk_content, 'heading_info': heading_info})
                    current_chunk, current_size = [], 0
                
                # Split long sections by paragraphs
                for chunk in self._split_by_paragraph(section_text):
                    chunks.append(chunk)
        
        # Save last chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            heading_info = HeadingExtractor.extract_heading_from_chunk(chunk_content)
            chunks.append({'content': chunk_content, 'heading_info': heading_info})
        
        return chunks
    
    def _split_by_paragraph(self, text: str) -> List[Dict]:
        """Split text by paragraphs"""
        # Protect code blocks
        protected_text, block_map = self._protect_code_blocks(text)
        
        paragraphs = protected_text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_restored = self._restore_code_blocks(para, block_map)
            para_size = len(para_restored)
            
            if current_size + para_size > self.chunk_size and current_chunk:
                chunk_content = '\n\n'.join(current_chunk)
                heading_info = HeadingExtractor.extract_heading_from_chunk(chunk_content)
                chunks.append({'content': chunk_content, 'heading_info': heading_info})
                current_chunk = [para_restored]
                current_size = para_size
            else:
                current_chunk.append(para_restored)
                current_size += para_size
        
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            heading_info = HeadingExtractor.extract_heading_from_chunk(chunk_content)
            chunks.append({'content': chunk_content, 'heading_info': heading_info})
        
        return chunks
    
    def _protect_code_blocks(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Protect code blocks to avoid splitting inside them"""
        block_map = {}
        protected_text = text
        block_id = 0
        
        # Match code blocks
        pattern = r'```[\s\S]*?```'
        for match in re.finditer(pattern, text):
            placeholder = f"__CODE_BLOCK_{block_id}__"
            block_map[placeholder] = match.group(0)
            protected_text = protected_text.replace(match.group(0), placeholder, 1)
            block_id += 1
        
        return protected_text, block_map
    
    def _restore_code_blocks(self, text: str, block_map: Dict[str, str]) -> str:
        """Restore code blocks"""
        restored = text
        for placeholder, code_block in block_map.items():
            restored = restored.replace(placeholder, code_block)
        return restored
    
    def _build_heading_path(
        self,
        content: str,
        heading_info: Dict,
        all_headings: List[Tuple[int, int, str]],
        text_lines: List[str]
    ) -> List[Tuple[int, str]]:
        """Build complete heading path (including all parent headings)"""
        if not heading_info.get('has_heading'):
            return []
        
        current_level = heading_info.get('level', 0)
        current_title = heading_info.get('heading', '')
        
        # Find current heading position in all_headings
        path = []
        for idx, level, title in all_headings:
            if title == current_title and level == current_level:
                # Find all parent headings
                for parent_idx, parent_level, parent_title in all_headings:
                    if parent_idx < idx and parent_level < level:
                        # Check if direct parent
                        is_direct_parent = True
                        for check_idx, check_level, _ in all_headings:
                            if parent_idx < check_idx < idx and parent_level < check_level < level:
                                is_direct_parent = False
                                break
                        if is_direct_parent:
                            path.append((parent_level, parent_title))
                path.append((level, title))
                break
        
        return path if path else [(current_level, current_title)]
    
    def _merge_short_chunks(self, chunks_data: List[Dict]) -> List[Dict]:
        """Merge short chunks"""
        if not chunks_data:
            return []
        
        merged = []
        current_chunk = chunks_data[0]
        
        for next_chunk in chunks_data[1:]:
            current_size = len(current_chunk.get('content', ''))
            next_size = len(next_chunk.get('content', ''))
            
            if current_size + next_size <= self.chunk_size:
                # Merge
                current_content = current_chunk.get('content', '')
                next_content = next_chunk.get('content', '')
                current_chunk['content'] = f"{current_content}\n\n{next_content}"
            else:
                merged.append(current_chunk)
                current_chunk = next_chunk
        
        merged.append(current_chunk)
        return merged
    
    def _apply_overlap(self, chunks_data: List[Dict]) -> List[Dict]:
        """Apply overlap"""
        if len(chunks_data) <= 1:
            return chunks_data
        
        overlapped = []
        for i, chunk in enumerate(chunks_data):
            content = chunk.get('content', '')
            
            # Add previous chunk tail
            if i > 0:
                prev_content = chunks_data[i-1].get('content', '')
                prev_lines = prev_content.split('\n')
                overlap_lines = prev_lines[-self.chunk_overlap:] if len(prev_lines) > self.chunk_overlap else prev_lines
                overlap_text = '\n'.join(overlap_lines)
                content = f"{overlap_text}\n\n{content}"
            
            # Add next chunk head
            if i < len(chunks_data) - 1:
                next_content = chunks_data[i+1].get('content', '')
                next_lines = next_content.split('\n')
                overlap_lines = next_lines[:self.chunk_overlap] if len(next_lines) > self.chunk_overlap else next_lines
                overlap_text = '\n'.join(overlap_lines)
                content = f"{content}\n\n{overlap_text}"
            
            overlapped.append({**chunk, 'content': content})
        
        return overlapped

