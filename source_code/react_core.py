"""ReAct Core Implementation: Thought-Action-Observation Loop

Core Flow:
1. Thought: LLM thinks about the next action
2. Action: Execute tool call or generate answer
3. Observation: Observe tool execution results
4. Loop until task completion
"""
from typing import List, Dict, Any, Optional, Iterator, Callable
import json
import re
import logging

logger = logging.getLogger(__name__)


class ReActCore:
    """ReAct core loop implementation"""
    
    def __init__(self, llm, tools: Dict[str, Callable], max_iterations: int = 10):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
    
    def run(self, query: str, allowed_tools: Optional[List[str]] = None) -> str:
        """Execute ReAct loop"""
        history = []
        
        for i in range(self.max_iterations):
            # Thought phase
            thought = self._think(query, history)
            
            # Check if should finish
            if self._should_finish(thought):
                final_answer = self._extract_final_answer(thought)
                if final_answer:
                    return final_answer
            
            # Action phase
            action_result = self._act(thought, allowed_tools)
            
            # Observation phase
            observation = self._observe(action_result)
            history.append(observation)
        
        # Reached max iterations
        return self._generate_final_answer(query, history) if history else "Unable to complete task"
    
    def _think(self, query: str, history: List[str]) -> str:
        """Generate Thought"""
        prompt = self._build_react_prompt(query, history)
        try:
            return self.llm.generate(prompt, temperature=0.3)
        except Exception as e:
            logger.error(f"Failed to generate Thought: {e}")
            return f"Thought: Encountered error, unable to continue thinking. Error: {str(e)}"
    
    def _build_react_prompt(self, query: str, history: List[str]) -> str:
        """Build ReAct format prompt"""
        # Build tool descriptions
        tool_descriptions = []
        for name, func in self.tools.items():
            doc = func.__doc__ or "No description"
            doc_first_line = doc.strip().split('\n')[0]
            tool_descriptions.append(f"- {name}: {doc_first_line}")
        
        tools_info = "\n".join(tool_descriptions) if tool_descriptions else "No available tools"
        
        # Build history observations
        history_text = ""
        if history:
            history_text = "\n\n" + "\n\n".join([
                f"Observation {i+1}: {obs}" 
                for i, obs in enumerate(history)
            ])
        
        return f"""You are an intelligent assistant using ReAct mode to solve problems.

Available tools:
{tools_info}

Please follow this format for thinking and acting:
1. Thought: [Analyze the current situation and think about what to do next]
2. Action: [If you need to use a tool, format: tool_name({{"param_name": "param_value"}})]
   or Action: FINISH [if you can directly provide the final answer]

User query: {query}{history_text}

Please start thinking:"""
    
    def _should_finish(self, thought: str) -> bool:
        """Check if should finish the loop"""
        finish_patterns = [
            r'Final Answer:',
            r'Action:\s*FINISH',
        ]
        return any(re.search(pattern, thought, re.IGNORECASE) for pattern in finish_patterns)
    
    def _extract_final_answer(self, thought: str) -> Optional[str]:
        """Extract final answer from Thought"""
        patterns = [
            r'Final Answer:\s*(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, thought, re.IGNORECASE | re.DOTALL)
            if match:
                answer = match.group(1).strip()
                if answer:
                    return answer
        return thought.strip()
    
    def _act(self, thought: str, allowed_tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute Action"""
        # Parse Action
        action_match = re.search(
            r'Action:\s*(\w+)\s*\((.+?)\)',
            thought,
            re.IGNORECASE | re.DOTALL
        )
        
        if not action_match:
            if re.search(r'Action:\s*FINISH', thought, re.IGNORECASE):
                return {'type': 'finish', 'action': 'FINISH'}
            return {'type': 'no_action', 'error': 'No valid Action found'}
        
        tool_name = action_match.group(1).strip()
        args_str = action_match.group(2).strip()
        
        # Check tool permissions
        if allowed_tools is not None and tool_name not in allowed_tools:
            return {'type': 'error', 'error': f'Tool {tool_name} is not allowed'}
        
        # Get tool function
        tool_func = self.tools.get(tool_name)
        if not tool_func:
            return {'type': 'error', 'error': f'Unknown tool: {tool_name}'}
        
        # Parse arguments
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            # Try simple key-value pair parsing
            args = {}
            kv_pattern = r'(\w+)\s*[:=]\s*"([^"]+)"'
            for match in re.finditer(kv_pattern, args_str):
                args[match.group(1)] = match.group(2)
            
            if not args:
                return {'type': 'error', 'error': f'Unable to parse Action arguments: {args_str}'}
        
        # Execute tool
        try:
            result = tool_func(args)
            return {'type': 'tool', 'tool_name': tool_name, 'args': args, 'result': result}
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {'type': 'error', 'error': str(e), 'tool_name': tool_name}
    
    def _observe(self, action_result: Dict[str, Any]) -> str:
        """Generate Observation text"""
        if action_result.get('type') == 'finish':
            return "Task completed"
        
        if action_result.get('type') == 'error':
            error = action_result.get('error', 'Unknown error')
            tool_name = action_result.get('tool_name', '')
            return f"Error: {error}" + (f" (tool: {tool_name})" if tool_name else "")
        
        if action_result.get('type') == 'tool':
            tool_name = action_result.get('tool_name', '')
            result = action_result.get('result', {})
            result_text = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else str(result)
            return f"[Tool {tool_name}] {result_text}"
        
        return f"Unknown Action result: {action_result}"
    
    def _generate_final_answer(self, query: str, history: List[str]) -> str:
        """Generate final answer"""
        history_text = "\n\n".join([
            f"Observation {i+1}: {obs}" 
            for i, obs in enumerate(history)
        ])
        
        prompt = f"""Based on the following observations, answer the user's question.

User query: {query}

Observations:
{history_text}

Please provide a concise and accurate final answer:"""
        
        try:
            return self.llm.generate(prompt, temperature=0.3).strip()
        except Exception as e:
            logger.error(f"Failed to generate final answer: {e}")
            return "Sorry, unable to generate final answer."

