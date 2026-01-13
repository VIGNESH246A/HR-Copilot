"""
Calendar Manager for interview scheduling
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class CalendarManager:
    """Manage calendar and availability for interviews"""
    
    def __init__(self):
        # In production, integrate with Google Calendar or Outlook
        self.mock_calendar = {}
    
    def check_availability(
        self,
        date: datetime,
        duration_minutes: int = 60
    ) -> bool:
        """Check if time slot is available"""
        
        # Simple mock implementation
        date_key = date.strftime("%Y-%m-%d %H:%M")
        return date_key not in self.mock_calendar
    
    def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        business_hours_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get available time slots in date range"""
        
        available_slots = []
        current = start_date
        
        while current < end_date:
            # Skip weekends
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            
            # Business hours: 9 AM - 5 PM
            if business_hours_only:
                if current.hour < 9:
                    current = current.replace(hour=9, minute=0)
                elif current.hour >= 17:
                    current = current.replace(hour=9, minute=0) + timedelta(days=1)
                    continue
            
            # Check if slot is available
            if self.check_availability(current, duration_minutes):
                available_slots.append({
                    'start_time': current,
                    'end_time': current + timedelta(minutes=duration_minutes),
                    'duration_minutes': duration_minutes
                })
            
            # Move to next slot (30-minute intervals)
            current += timedelta(minutes=30)
        
        return available_slots
    
    def book_slot(
        self,
        start_time: datetime,
        duration_minutes: int,
        title: str,
        attendees: List[str],
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Book a calendar slot"""
        
        date_key = start_time.strftime("%Y-%m-%d %H:%M")
        
        if not self.check_availability(start_time, duration_minutes):
            return {
                'success': False,
                'error': 'Time slot not available'
            }
        
        # Book the slot
        event = {
            'id': f"event_{len(self.mock_calendar) + 1}",
            'title': title,
            'start_time': start_time,
            'end_time': start_time + timedelta(minutes=duration_minutes),
            'duration_minutes': duration_minutes,
            'attendees': attendees,
            'location': location,
            'description': description,
            'meeting_link': self._generate_meeting_link()
        }
        
        self.mock_calendar[date_key] = event
        
        return {
            'success': True,
            'event': event,
            'meeting_link': event['meeting_link']
        }
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel calendar event"""
        
        for key, event in self.mock_calendar.items():
            if event['id'] == event_id:
                del self.mock_calendar[key]
                return True
        
        return False
    
    def reschedule_event(
        self,
        event_id: str,
        new_start_time: datetime
    ) -> Dict[str, Any]:
        """Reschedule an event"""
        
        # Find event
        old_event = None
        old_key = None
        
        for key, event in self.mock_calendar.items():
            if event['id'] == event_id:
                old_event = event
                old_key = key
                break
        
        if not old_event:
            return {
                'success': False,
                'error': f'Event {event_id} not found'
            }
        
        # Cancel old slot
        del self.mock_calendar[old_key]
        
        # Book new slot
        result = self.book_slot(
            new_start_time,
            old_event['duration_minutes'],
            old_event['title'],
            old_event['attendees'],
            old_event.get('location'),
            old_event.get('description')
        )
        
        return result
    
    def get_upcoming_events(
        self,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """Get upcoming events"""
        
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        
        upcoming = []
        
        for event in self.mock_calendar.values():
            if now <= event['start_time'] <= cutoff:
                upcoming.append(event)
        
        # Sort by start time
        upcoming.sort(key=lambda e: e['start_time'])
        
        return upcoming
    
    def suggest_interview_times(
        self,
        preferred_date: Optional[datetime] = None,
        num_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """Suggest available interview times"""
        
        if not preferred_date:
            preferred_date = datetime.now() + timedelta(days=2)
        
        # Get next 7 days of availability
        end_date = preferred_date + timedelta(days=7)
        
        available = self.get_available_slots(
            preferred_date,
            end_date,
            duration_minutes=60
        )
        
        # Return top suggestions
        return available[:num_suggestions]
    
    def _generate_meeting_link(self) -> str:
        """Generate virtual meeting link"""
        import random
        import string
        
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"https://meet.company.com/{code}"
    
    def sync_with_google_calendar(self, credentials_path: str):
        """Sync with Google Calendar (placeholder for future implementation)"""
        # TODO: Implement Google Calendar API integration
        pass
    
    def sync_with_outlook(self, credentials: Dict[str, str]):
        """Sync with Outlook Calendar (placeholder for future implementation)"""
        # TODO: Implement Outlook Calendar API integration
        pass


# Global calendar manager instance
calendar_manager = CalendarManager()