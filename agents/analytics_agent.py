"""
Analytics Agent - Provides hiring metrics and insights
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.database_service import db_service
from services.llm_service import llm_service
import json


class AnalyticsAgent:
    """Agent for generating hiring analytics and insights"""
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics task"""
        
        analysis_type = task_data.get('analysis_type', 'overview')
        
        if analysis_type == 'overview':
            return self.generate_overview()
        elif analysis_type == 'job_performance':
            return self.analyze_job_performance(task_data.get('job_id'))
        elif analysis_type == 'candidate_pipeline':
            return self.analyze_pipeline()
        elif analysis_type == 'time_to_hire':
            return self.calculate_time_to_hire()
        elif analysis_type == 'skills_analysis':
            return self.analyze_skills_demand()
        else:
            return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
    
    def generate_overview(self) -> Dict[str, Any]:
        """Generate comprehensive hiring overview"""
        
        analytics = db_service.get_analytics()
        
        # Calculate trends
        active_jobs_percentage = (
            (analytics['active_jobs'] / analytics['total_jobs'] * 100)
            if analytics['total_jobs'] > 0 else 0
        )
        
        # Generate insights using LLM
        insights = self._generate_insights(analytics)
        
        return {
            'success': True,
            'overview': {
                'total_jobs': analytics['total_jobs'],
                'active_jobs': analytics['active_jobs'],
                'total_candidates': analytics['total_candidates'],
                'average_match_score': analytics['average_match_score'],
                'interviews_scheduled': analytics['interviews_scheduled'],
                'active_jobs_percentage': round(active_jobs_percentage, 1),
                'candidates_by_status': analytics['candidates_by_status']
            },
            'insights': insights,
            'message': '✅ Analytics overview generated',
            'recommendations': self._generate_recommendations(analytics)
        }
    
    def analyze_job_performance(self, job_id: Optional[str]) -> Dict[str, Any]:
        """Analyze performance of specific job or all jobs"""
        
        if job_id:
            job = db_service.get_job(job_id)
            if not job:
                return {'success': False, 'error': f'Job {job_id} not found'}
            
            candidates = db_service.list_candidates(job_id=job_id)
            
            performance = {
                'job_id': job_id,
                'job_title': job['title'],
                'total_applicants': len(candidates),
                'status_breakdown': self._get_status_breakdown(candidates),
                'average_match_score': self._calculate_avg_score(candidates),
                'top_candidates': self._get_top_candidates(candidates, 5),
                'days_open': self._calculate_days_open(job)
            }
        else:
            jobs = db_service.list_jobs(status='active')
            performance = {
                'total_active_jobs': len(jobs),
                'jobs': [
                    {
                        'job_id': job['id'],
                        'title': job['title'],
                        'applicants': len(db_service.list_candidates(job_id=job['id'])),
                        'days_open': self._calculate_days_open(job)
                    }
                    for job in jobs[:10]
                ]
            }
        
        return {
            'success': True,
            'performance': performance,
            'message': '✅ Job performance analysis complete'
        }
    
    def analyze_pipeline(self) -> Dict[str, Any]:
        """Analyze candidate pipeline"""
        
        candidates = db_service.list_candidates()
        
        pipeline = {
            'total_candidates': len(candidates),
            'by_status': {},
            'conversion_rates': {},
            'bottlenecks': []
        }
        
        # Count by status
        status_counts = {}
        for candidate in candidates:
            status = candidate.get('status', 'new')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        pipeline['by_status'] = status_counts
        
        # Calculate conversion rates
        total = len(candidates)
        if total > 0:
            pipeline['conversion_rates'] = {
                'screening_to_interview': round(
                    status_counts.get('interview', 0) / total * 100, 1
                ),
                'interview_to_offer': round(
                    status_counts.get('offer', 0) / total * 100, 1
                ),
                'offer_to_hired': round(
                    status_counts.get('hired', 0) / total * 100, 1
                )
            }
        
        # Identify bottlenecks
        pipeline['bottlenecks'] = self._identify_bottlenecks(status_counts)
        
        return {
            'success': True,
            'pipeline': pipeline,
            'message': '✅ Pipeline analysis complete',
            'recommendations': self._get_pipeline_recommendations(pipeline)
        }
    
    def calculate_time_to_hire(self) -> Dict[str, Any]:
        """Calculate average time to hire"""
        
        hired_candidates = db_service.list_candidates(status='hired')
        
        if not hired_candidates:
            return {
                'success': True,
                'average_days': 0,
                'message': 'No hired candidates yet',
                'breakdown': {}
            }
        
        total_days = 0
        breakdown_by_position = {}
        
        for candidate in hired_candidates:
            created_at = datetime.fromisoformat(candidate['created_at'])
            # Assume hired date is current date if not specified
            hired_date = datetime.now()
            
            days = (hired_date - created_at).days
            total_days += days
            
            # Track by job
            job_id = candidate.get('job_id')
            if job_id:
                if job_id not in breakdown_by_position:
                    breakdown_by_position[job_id] = []
                breakdown_by_position[job_id].append(days)
        
        average_days = total_days / len(hired_candidates)
        
        return {
            'success': True,
            'average_days': round(average_days, 1),
            'total_hired': len(hired_candidates),
            'breakdown': {
                job_id: round(sum(days) / len(days), 1)
                for job_id, days in breakdown_by_position.items()
            },
            'message': f'✅ Average time to hire: {average_days:.1f} days'
        }
    
    def analyze_skills_demand(self) -> Dict[str, Any]:
        """Analyze most demanded skills"""
        
        jobs = db_service.list_jobs()
        
        skills_count = {}
        
        for job in jobs:
            requirements = job.get('requirements', '{}')
            if isinstance(requirements, str):
                try:
                    requirements = json.loads(requirements)
                except:
                    continue
            
            if isinstance(requirements, list):
                for req in requirements:
                    # Simple skill extraction
                    words = req.lower().split()
                    for word in words:
                        if len(word) > 3:  # Skip short words
                            skills_count[word] = skills_count.get(word, 0) + 1
        
        # Get top skills
        top_skills = sorted(
            skills_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        return {
            'success': True,
            'top_skills': [
                {'skill': skill, 'count': count}
                for skill, count in top_skills
            ],
            'total_unique_skills': len(skills_count),
            'message': f'✅ Found {len(top_skills)} top skills in demand'
        }
    
    def _generate_insights(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate AI insights from analytics data"""
        
        prompt = f"""
        Based on these hiring metrics, provide 3-5 key insights:
        
        {json.dumps(analytics, indent=2)}
        
        Provide actionable insights about:
        - Hiring efficiency
        - Candidate quality
        - Process bottlenecks
        - Opportunities for improvement
        """
        
        try:
            response = llm_service.generate_response(
                prompt,
                system_prompt="You are an HR analytics expert providing insights."
            )
            
            # Parse insights from response
            insights = [
                line.strip('- ').strip()
                for line in response.split('\n')
                if line.strip().startswith('-')
            ]
            
            return insights[:5]
        except:
            return [
                "Hiring activity is ongoing",
                "Continue monitoring candidate pipeline",
                "Review match score trends"
            ]
    
    def _generate_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics"""
        
        recommendations = []
        
        # Check for low match scores
        if analytics['average_match_score'] < 60:
            recommendations.append(
                "Average match score is low. Consider refining job requirements or widening search criteria."
            )
        
        # Check for pipeline issues
        if analytics['total_candidates'] < analytics['active_jobs'] * 5:
            recommendations.append(
                "Low candidate volume. Consider posting to more job boards or increasing outreach."
            )
        
        # Check for scheduling
        if analytics['interviews_scheduled'] == 0 and analytics['total_candidates'] > 0:
            recommendations.append(
                "No interviews scheduled. Review screening criteria and start scheduling interviews."
            )
        
        return recommendations or ["Continue current hiring practices"]
    
    def _get_status_breakdown(self, candidates: List[Dict]) -> Dict[str, int]:
        """Get status breakdown for candidates"""
        
        breakdown = {}
        for candidate in candidates:
            status = candidate.get('status', 'new')
            breakdown[status] = breakdown.get(status, 0) + 1
        
        return breakdown
    
    def _calculate_avg_score(self, candidates: List[Dict]) -> float:
        """Calculate average match score"""
        
        scores = [
            c.get('match_score', 0)
            for c in candidates
            if c.get('match_score')
        ]
        
        return round(sum(scores) / len(scores), 2) if scores else 0.0
    
    def _get_top_candidates(
        self,
        candidates: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Get top candidates by match score"""
        
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.get('match_score', 0),
            reverse=True
        )
        
        return [
            {
                'name': c['name'],
                'email': c['email'],
                'match_score': c.get('match_score', 0),
                'status': c.get('status')
            }
            for c in sorted_candidates[:limit]
        ]
    
    def _calculate_days_open(self, job: Dict) -> int:
        """Calculate days job has been open"""
        
        created_at = datetime.fromisoformat(job['created_at'])
        return (datetime.now() - created_at).days
    
    def _identify_bottlenecks(self, status_counts: Dict[str, int]) -> List[str]:
        """Identify pipeline bottlenecks"""
        
        bottlenecks = []
        
        screening = status_counts.get('screening', 0)
        interview = status_counts.get('interview', 0)
        
        if screening > interview * 3:
            bottlenecks.append(
                "Many candidates stuck in screening. Consider faster screening process."
            )
        
        if interview > status_counts.get('offer', 0) * 5:
            bottlenecks.append(
                "High interview to offer ratio. Review interview evaluation criteria."
            )
        
        return bottlenecks
    
    def _get_pipeline_recommendations(self, pipeline: Dict) -> List[str]:
        """Get pipeline-specific recommendations"""
        
        recommendations = []
        
        conv_rates = pipeline.get('conversion_rates', {})
        
        if conv_rates.get('screening_to_interview', 0) < 20:
            recommendations.append(
                "Low screening to interview conversion. Review screening criteria."
            )
        
        if conv_rates.get('interview_to_offer', 0) < 10:
            recommendations.append(
                "Low interview to offer conversion. Consider interview training."
            )
        
        return recommendations or ["Pipeline is healthy"]


# Global analytics agent instance
analytics_agent = AnalyticsAgent()