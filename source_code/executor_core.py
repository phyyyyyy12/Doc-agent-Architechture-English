"""Executor and Planner Core Implementation

Core Functions:
1. Task execution (tool calls + LLM generation)
2. Simple planner (keyword-based matching)
"""
from typing import List, Dict, Any, Optional, Callable
import json
import logging

logger = logging.getLogger(__name__)


class ExecutorCore:
    """Executor core: unified execution of tool and LLM tasks"""
    
    def __init__(self, llm=None, get_tool: Optional[Callable] = None):
        self.llm = llm
        self.get_tool = get_tool
    
    def execute(
        self,
        tasks: List[Dict[str, Any]],
        allowed_tools: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Execute task sequence"""
        outputs = []
        tool_texts = []
        
        for t in tasks:
            if t['type'] == 'tool':
                name = t.get('name')
                
                # Get tool function
                if self.get_tool:
                    func = self.get_tool(name)
                else:
                    func = None
                
                if not func:
                    outputs.append({'ok': False, 'error': f'Unknown tool: {name}'})
                    continue
                
                # Check tool permissions
                if allowed_tools is not None and name not in allowed_tools:
                    outputs.append({'ok': False, 'tool_blocked': True, 'name': name})
                    continue
                
                # Execute tool
                try:
                    res = func(t.get('args', {}))
                    outputs.append({'ok': True, 'tool': name, 'result': res})
                    res_text = json.dumps(res, ensure_ascii=False) if isinstance(res, dict) else str(res)
                    tool_texts.append(f"[Tool {name}] {res_text}")
                except Exception as e:
                    logger.error(f"Tool {name} execution failed: {e}")
                    outputs.append({'ok': False, 'error': str(e)})
            
            elif t['type'] == 'llm':
                prompt = t['args'].get('prompt', '')
                if tool_texts:
                    full_prompt = '\n\n'.join(tool_texts) + '\n\n' + prompt
                else:
                    full_prompt = prompt
                
                resp = self.llm.generate(full_prompt) if self.llm else ''
                outputs.append({'ok': True, 'llm': True, 'result': resp})
            
            else:
                outputs.append({'ok': False, 'error': 'Unknown task type'})
        
        return outputs


class PlannerCore:
    """Planner core: keyword-based task planning"""
    
    @staticmethod
    def simple_plan(user_input: str) -> List[Dict[str, Any]]:
        """Simple planner: keyword-based matching"""
        tasks = []
        low = user_input.lower()
        
        # Index creation
        if 'build index' in low or ('index' in low and 'http' in low):
            parts = user_input.split()
            repo_url = None
            for p in parts:
                if p.startswith('http'):
                    repo_url = p
                    break
            if repo_url:
                index_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
                tasks.append({
                    'type': 'tool',
                    'name': 'index_github_repo',
                    'args': {'repo_url': repo_url, 'index_name': index_name}
                })
                tasks.append({
                    'type': 'llm',
                    'args': {'prompt': f'Index {index_name} has been created for repository {repo_url}, please provide an explanation.'}
                })
                return tasks
        
        # Math calculation
        if 'calculate' in low or (any(ch in low for ch in ['+', '-', '*', '/', '%']) and any(c.isdigit() for c in low)):
            expr = ''.join([c for c in user_input if c in '0123456789+-*/(). %^'])
            tasks.append({'type': 'tool', 'name': 'calculator', 'args': {'expr': expr}})
            tasks.append({'type': 'llm', 'args': {'prompt': 'Please provide suggestions based on the calculation result.'}})
            return tasks
        
        # Document retrieval
        if any(k in low for k in ['search', 'query', 'find', 'retrieve', 'lookup']):
            tasks.append({
                'type': 'tool',
                'name': 'query_index',
                'args': {'query': user_input, 'index_name': 'default', 'top_k': 4}
            })
            tasks.append({
                'type': 'llm',
                'args': {'prompt': 'Please provide a concise answer based on the retrieval results.'}
            })
            return tasks
        
        # Default: use LLM directly
        tasks.append({'type': 'llm', 'args': {'prompt': user_input}})
        return tasks

