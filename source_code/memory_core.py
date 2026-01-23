"""Dynamic Memory Core Implementation: Token Window Management and Semantic Compression

Core Features:
1. Token counting and window management
2. Near-field full retention, far-field compression
3. System Prompt anchor protection
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


class TokenCounter:
    """Token counter"""
    
    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.encoding = None
        
        if HAS_TIKTOKEN:
            try:
                if "deepseek" in model.lower() or "gpt" in model.lower():
                    self.encoding = tiktoken.get_encoding("cl100k_base")
                else:
                    self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoding = None
    
    def count(self, text: str) -> int:
        """Count tokens in text"""
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception:
                pass
        
        # Fallback: character count estimation
        return int(len(text) / 2.5)
    
    def count_messages(self, messages: List[Dict[str, Any]]) -> int:
        """Count total tokens in message list"""
        total = 0
        for msg in messages:
            total += 6  # Base overhead
            total += self.count(str(msg.get("content", "")))
        return total


class DynamicMemoryCore:
    """Dynamic Memory Core: Token Window Management"""
    
    def __init__(
        self,
        max_context_tokens: int = 32768,
        system_prompt: str = "",
        model: str = "deepseek-chat",
        near_field_turns: int = 2,
        llm=None,
    ):
        self.token_counter = TokenCounter(model=model)
        self.system_prompt = system_prompt
        self.near_field_turns = near_field_turns
        self.llm = llm
        
        self.max_context_tokens = max_context_tokens
        self.system_prompt_tokens = self.token_counter.count(system_prompt)
        # Reserve 20% safety margin + System Prompt
        self.reserved_tokens = int(self.max_context_tokens * 0.2) + self.system_prompt_tokens
        self.available_tokens = self.max_context_tokens - self.reserved_tokens
        
        self.logger = logging.getLogger(__name__)
    
    def build_context_prompt(
        self,
        user_input: str,
        messages: List[Dict[str, Any]],
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build context prompt with Token window management
        
        Returns:
            (context_text, metadata): Context text and metadata
        """
        # Calculate current user input tokens
        current_input_tokens = self.token_counter.count(user_input)
        remaining_tokens = self.available_tokens - current_input_tokens
        
        if remaining_tokens <= 0:
            return "", {
                'strategy': 'input_too_large',
                'messages_tokens': 0,
                'remaining_tokens': remaining_tokens
            }
        
        # Group messages by turns
        message_pairs = self._group_messages_by_turns(messages)
        
        # Strategy: near-field full retention, far-field compression
        near_field_pairs = message_pairs[-self.near_field_turns:] if len(message_pairs) > self.near_field_turns else message_pairs
        far_field_pairs = message_pairs[:-self.near_field_turns] if len(message_pairs) > self.near_field_turns else []
        
        # Calculate near-field message tokens
        near_field_messages = [msg for pair in near_field_pairs for msg in pair]
        near_field_tokens = self.token_counter.count_messages(near_field_messages)
        
        # If near-field messages exceed limit, keep only recent turns
        if near_field_tokens > remaining_tokens:
            selected_pairs = []
            selected_tokens = 0
            for pair in reversed(near_field_pairs):
                pair_tokens = self.token_counter.count_messages(pair)
                if selected_tokens + pair_tokens <= remaining_tokens:
                    selected_pairs.insert(0, pair)
                    selected_tokens += pair_tokens
                else:
                    break
            
            filtered_messages = [msg for pair in selected_pairs for msg in pair]
            context_text = self._format_messages(filtered_messages)
            
            return context_text, {
                'strategy': 'near_field_partial',
                'messages_tokens': selected_tokens,
                'remaining_tokens': remaining_tokens - selected_tokens
            }
        
        # Near-field messages can be fully retained, try to compress far-field
        remaining_after_near = remaining_tokens - near_field_tokens
        
        if remaining_after_near > 0 and far_field_pairs and self.llm:
            # Compress far-field messages
            compressed_summary = self._compress_far_field(far_field_pairs, remaining_after_near)
            
            if compressed_summary:
                summary_tokens = self.token_counter.count(compressed_summary)
                if summary_tokens <= remaining_after_near:
                    all_messages = near_field_messages + [
                        {'role': 'system', 'content': compressed_summary}
                    ]
                    context_text = self._format_messages(all_messages)
                    
                    return context_text, {
                        'strategy': 'near_field_full_with_far_field_compressed',
                        'messages_tokens': near_field_tokens + summary_tokens,
                        'remaining_tokens': remaining_tokens - near_field_tokens - summary_tokens
                    }
        
        # Only keep near-field messages
        context_text = self._format_messages(near_field_messages)
        
        return context_text, {
            'strategy': 'near_field_only',
            'messages_tokens': near_field_tokens,
            'remaining_tokens': remaining_tokens - near_field_tokens
        }
    
    def _group_messages_by_turns(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group messages by turns (each turn = user + assistant)"""
        pairs = []
        current_pair = []
        
        for msg in messages:
            role = msg.get("role", "")
            if role == "user":
                if current_pair:
                    pairs.append(current_pair)
                current_pair = [msg]
            elif role == "assistant" and current_pair:
                current_pair.append(msg)
                pairs.append(current_pair)
                current_pair = []
        
        if current_pair:
            pairs.append(current_pair)
        
        return pairs
    
    def _compress_far_field(
        self,
        far_field_pairs: List[List[Dict[str, Any]]],
        max_tokens: int,
    ) -> Optional[str]:
        """Compress far-field messages and generate semantic summary"""
        if not self.llm or not far_field_pairs:
            return None
        
        # Extract far-field message content
        far_field_text = []
        for pair in far_field_pairs:
            for msg in pair:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    far_field_text.append(f"User: {content}")
                elif role == "assistant":
                    far_field_text.append(f"Assistant: {content}")
        
        far_field_content = "\n".join(far_field_text)
        
        # Use LLM to generate summary
        prompt = f"""Please compress the following conversation history into a concise summary, preserving key information:

{far_field_content}

Summary:"""
        
        try:
            summary = self.llm.generate(prompt, temperature=0.3)
            return f"[Conversation History Summary] {summary}"
        except Exception as e:
            self.logger.error(f"Failed to compress far-field messages: {e}")
            return None
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Format messages as text"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"AI: {content}")
            elif role == "system":
                formatted.append(f"[System] {content}")
        
        return "\n".join(formatted)

