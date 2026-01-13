"""
Task Decomposer Agent - Breaks down complex requests into actionable tasks
"""
from typing import List, Dict, Any
from services.llm_service import llm_service
from models.schemas import AgentTask, TaskType
import json


class TaskDecomposerAgent:
    """Decomposes complex hiring requests into actionable tasks"""
    
    def decompose(self, user_request: str, context: Dict[str, Any] = None) -> List[AgentTask]:
        """Decompose user request into tasks"""
        
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"
        
        schema = {
            "tasks": [
                {
                    "task_type": "string (job_description|resume_screening|interview_scheduling|email_communication|analytics|offer_generation)",
                    "description": "string",
                    "priority": "integer (1-5, where 1 is highest)",
                    "dependencies": ["string (task indices this depends on)"],
                    "input_requirements": ["string"]
                }
            ],
            "requires_clarification": "boolean",
            "clarification_questions": ["string"]
        }
        
        prompt = f"""
Analyze this HR request and break it down into actionable tasks:

Request: "{user_request}"{context_str}

Available task types:
- job_description: Create or modify job descriptions
- resume_screening: Screen and evaluate candidate resumes
- interview_scheduling: Schedule and manage interviews
- email_communication: Send emails to candidates
- analytics: Generate hiring metrics and reports
- offer_generation: Create offer letters

For each task, specify:
1. Task type
2. Clear description
3. Priority (1=highest, 5=lowest)
4. Dependencies (which tasks must complete first)
5. Input requirements

If the request is unclear or missing critical information, set requires_clarification to true and list questions.
"""
        
        result = llm_service.generate_structured_output(
            prompt=prompt,
            output_schema=schema,
            system_prompt="You are a task planning expert for HR workflows."
        )
        
        # Convert to AgentTask objects
        tasks = []
        for idx, task_data in enumerate(result.get('tasks', [])):
            task = AgentTask(
                task_id=f"task_{idx+1}",
                task_type=TaskType(task_data['task_type']),
                description=task_data['description'],
                input_data={
                    "user_request": user_request,
                    "dependencies": task_data.get('dependencies', []),
                    "input_requirements": task_data.get('input_requirements', [])
                },
                priority=task_data.get('priority', 3)
            )
            tasks.append(task)
        
        # Store clarification info if needed
        if result.get('requires_clarification'):
            return {
                'tasks': tasks,
                'requires_clarification': True,
                'questions': result.get('clarification_questions', [])
            }
        
        return {'tasks': tasks, 'requires_clarification': False}
    
    def validate_task_sequence(self, tasks: List[AgentTask]) -> bool:
        """Validate task dependencies and sequence"""
        
        # Check for circular dependencies
        task_ids = [task.task_id for task in tasks]
        
        for task in tasks:
            dependencies = task.input_data.get('dependencies', [])
            for dep in dependencies:
                if dep not in task_ids:
                    return False
        
        return True
    
    def prioritize_tasks(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """Sort tasks by priority and dependencies"""
        
        # Simple priority sort (can be enhanced with dependency graph)
        return sorted(tasks, key=lambda t: t.priority)
    
    def generate_execution_plan(
        self, 
        user_request: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete execution plan"""
        
        decomposition = self.decompose(user_request, context)
        
        if decomposition['requires_clarification']:
            return {
                'status': 'needs_clarification',
                'questions': decomposition['questions'],
                'plan': None
            }
        
        tasks = decomposition['tasks']
        
        if not self.validate_task_sequence(tasks):
            return {
                'status': 'invalid_sequence',
                'error': 'Task dependencies are invalid',
                'plan': None
            }
        
        prioritized_tasks = self.prioritize_tasks(tasks)
        
        return {
            'status': 'ready',
            'total_tasks': len(prioritized_tasks),
            'tasks': [
                {
                    'task_id': task.task_id,
                    'type': task.task_type.value,
                    'description': task.description,
                    'priority': task.priority
                }
                for task in prioritized_tasks
            ],
            'estimated_time': self._estimate_time(prioritized_tasks)
        }
    
    def _estimate_time(self, tasks: List[AgentTask]) -> str:
        """Estimate execution time"""
        
        time_estimates = {
            TaskType.JOB_DESCRIPTION: 2,
            TaskType.RESUME_SCREENING: 3,
            TaskType.INTERVIEW_SCHEDULING: 1,
            TaskType.EMAIL_COMMUNICATION: 1,
            TaskType.ANALYTICS: 2,
            TaskType.OFFER_GENERATION: 2
        }
        
        total_minutes = sum(
            time_estimates.get(task.task_type, 2) 
            for task in tasks
        )
        
        if total_minutes < 5:
            return "Less than 5 minutes"
        elif total_minutes < 15:
            return "5-15 minutes"
        else:
            return "15+ minutes"


# Global task decomposer instance
task_decomposer = TaskDecomposerAgent()