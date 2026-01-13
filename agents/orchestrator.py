"""
Main Orchestrator Agent - Routes requests to specialized agents
"""
from typing import Dict, Any, List, Optional
from services.llm_service import llm_service
from services.memory_service import memory_service
from models.conversation import conversation_manager
from models.schemas import TaskType, AgentResponse
from agents.task_decomposer import task_decomposer
from agents.jd_generator_agent import jd_generator_agent
from agents.screening_agent import screening_agent
from agents.interview_agent import interview_agent
import json


class OrchestratorAgent:
    """Main orchestrator for routing and managing all HR workflows"""
    
    def __init__(self):
        self.agents = {
            TaskType.JOB_DESCRIPTION: jd_generator_agent,
            TaskType.RESUME_SCREENING: screening_agent,
            TaskType.INTERVIEW_SCHEDULING: interview_agent,
        }
    
    def process_request(
        self,
        user_message: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process user request and route to appropriate agents"""
        
        # Add to conversation history
        conversation_manager.add_message(session_id, "user", user_message)
        
        # Get conversation context
        conversation_history = conversation_manager.get_messages(session_id, limit=5)
        memory_context = memory_service.get_relevant_context(session_id, user_message)
        
        # Combine contexts
        full_context = {
            **(context or {}),
            **memory_context,
            'conversation_summary': self._summarize_conversation(conversation_history)
        }
        
        # Analyze intent
        intent_analysis = llm_service.analyze_intent(user_message)
        
        # Check if clarification needed
        if intent_analysis.get('requires_clarification'):
            response = AgentResponse(
                success=True,
                message="I need some clarification to help you better:",
                suggestions=intent_analysis.get('clarification_questions', [])
            )
            
            conversation_manager.add_message(
                session_id, 
                "assistant", 
                response.message
            )
            
            return response
        
        # Decompose into tasks
        execution_plan = task_decomposer.generate_execution_plan(
            user_message,
            full_context
        )
        
        if execution_plan['status'] == 'needs_clarification':
            response = AgentResponse(
                success=True,
                message="I need more information:",
                suggestions=execution_plan['questions']
            )
            
            conversation_manager.add_message(
                session_id,
                "assistant",
                response.message
            )
            
            return response
        
        # Execute tasks
        results = self._execute_tasks(
            execution_plan['tasks'],
            session_id,
            full_context
        )
        
        # Generate final response
        final_response = self._generate_response(
            user_message,
            results,
            intent_analysis
        )
        
        # Store in memory
        memory_service.store_short_term(
            session_id,
            'last_action',
            {
                'intent': intent_analysis['intent'],
                'results': results
            }
        )
        
        # Add to conversation
        conversation_manager.add_message(
            session_id,
            "assistant",
            final_response.message
        )
        
        return final_response
    
    def _execute_tasks(
        self,
        tasks: List[Dict[str, Any]],
        session_id: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute all tasks in sequence"""
        
        results = []
        
        for task in tasks:
            task_type = TaskType(task['type'])
            
            # Get appropriate agent
            agent = self.agents.get(task_type)
            
            if not agent:
                results.append({
                    'task_id': task['task_id'],
                    'success': False,
                    'error': f'No agent found for task type: {task_type}'
                })
                continue
            
            # Prepare task data
            task_data = {
                'user_request': context.get('user_request', ''),
                **context
            }
            
            # Execute task
            try:
                result = agent.execute(task_data)
                results.append({
                    'task_id': task['task_id'],
                    'task_type': task_type.value,
                    **result
                })
                
                # Store result in context for dependent tasks
                context[f"task_{task['task_id']}_result"] = result
                
            except Exception as e:
                results.append({
                    'task_id': task['task_id'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _generate_response(
        self,
        user_message: str,
        results: List[Dict[str, Any]],
        intent_analysis: Dict[str, Any]
    ) -> AgentResponse:
        """Generate final response from task results"""
        
        successful_results = [r for r in results if r.get('success')]
        failed_results = [r for r in results if not r.get('success')]
        
        if not successful_results:
            return AgentResponse(
                success=False,
                message="I encountered some issues processing your request:",
                data={'errors': [r.get('error') for r in failed_results]}
            )
        
        # Build response message
        messages = []
        all_next_actions = []
        response_data = {}
        
        for result in successful_results:
            if result.get('message'):
                messages.append(result['message'])
            
            if result.get('next_actions'):
                all_next_actions.extend(result['next_actions'])
            
            # Collect important data
            for key in ['job_id', 'candidate_id', 'interview_id', 'job_description']:
                if key in result:
                    response_data[key] = result[key]
        
        response_message = "\n".join(messages) if messages else "✅ Task completed successfully"
        
        # Add summary if multiple tasks
        if len(successful_results) > 1:
            response_message += f"\n\nCompleted {len(successful_results)} tasks."
        
        return AgentResponse(
            success=True,
            message=response_message,
            data=response_data if response_data else None,
            next_actions=list(set(all_next_actions))[:5] if all_next_actions else None
        )
    
    def _summarize_conversation(
        self,
        messages: List[Any]
    ) -> str:
        """Summarize recent conversation"""
        
        if not messages:
            return "New conversation"
        
        summary_parts = []
        for msg in messages[-3:]:
            role = "User" if msg.role == "user" else "Assistant"
            summary_parts.append(f"{role}: {msg.content[:100]}")
        
        return " | ".join(summary_parts)
    
    def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status and context"""
        
        context = memory_service.get_context(session_id)
        recent_actions = memory_service.get_short_term(session_id)
        
        return {
            'session_id': session_id,
            'context': context,
            'recent_actions': recent_actions[-5:] if recent_actions else [],
            'conversation_length': len(
                conversation_manager.get_messages(session_id)
            )
        }


# Global orchestrator instance
orchestrator = OrchestratorAgent()