"""
Database service for persistent storage
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
import json
from config import settings


class DatabaseService:
    """SQLite database service"""
    
    def __init__(self, db_path: str = "./data/hr_copilot.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize_database(self):
        """Create database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company_name TEXT NOT NULL,
                department TEXT,
                location TEXT,
                employment_type TEXT,
                description TEXT,
                requirements TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                resume_path TEXT,
                parsed_data TEXT,
                job_id TEXT,
                status TEXT DEFAULT 'new',
                match_score REAL,
                screening_notes TEXT,
                interview_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)
        
        # Interviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                interview_type TEXT,
                scheduled_date TIMESTAMP,
                interviewer TEXT,
                location TEXT,
                meeting_link TEXT,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                description TEXT,
                input_data TEXT,
                result TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ============ Job Operations ============
    
    def create_job(self, job_data: Dict[str, Any]) -> str:
        """Create a new job posting"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        job_id = job_data.get("id", f"job_{datetime.utcnow().timestamp()}")
        
        cursor.execute("""
            INSERT INTO jobs (
                id, title, company_name, department, location, 
                employment_type, description, requirements, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            job_data["title"],
            job_data["company_name"],
            job_data.get("department"),
            job_data["location"],
            job_data["employment_type"],
            job_data["description"],
            json.dumps(job_data.get("requirements", [])),
            job_data.get("status", "draft")
        ))
        
        conn.commit()
        conn.close()
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_jobs(
        self, 
        status: Optional[str] = None, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List all jobs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_job(self, job_id: str, updates: Dict[str, Any]):
        """Update job details"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [job_id]
        
        cursor.execute(
            f"UPDATE jobs SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )
        
        conn.commit()
        conn.close()
    
    # ============ Candidate Operations ============
    
    def create_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """Create a new candidate"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        candidate_id = candidate_data.get("id", f"cand_{datetime.utcnow().timestamp()}")
        
        cursor.execute("""
            INSERT INTO candidates (
                id, name, email, phone, resume_path, 
                parsed_data, job_id, status, match_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            candidate_data["name"],
            candidate_data["email"],
            candidate_data.get("phone"),
            candidate_data.get("resume_path"),
            json.dumps(candidate_data.get("parsed_data", {})),
            candidate_data.get("job_id"),
            candidate_data.get("status", "new"),
            candidate_data.get("match_score")
        ))
        
        conn.commit()
        conn.close()
        
        return candidate_id
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_candidates(
        self, 
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List candidates"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM candidates WHERE 1=1"
        params = []
        
        if job_id:
            query += " AND job_id = ?"
            params.append(job_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_candidate(self, candidate_id: str, updates: Dict[str, Any]):
        """Update candidate details"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [candidate_id]
        
        cursor.execute(
            f"UPDATE candidates SET {set_clause} WHERE id = ?",
            values
        )
        
        conn.commit()
        conn.close()
    
    # ============ Interview Operations ============
    
    def create_interview(self, interview_data: Dict[str, Any]) -> str:
        """Create interview record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        interview_id = f"int_{datetime.utcnow().timestamp()}"
        
        cursor.execute("""
            INSERT INTO interviews (
                id, candidate_id, job_id, interview_type,
                scheduled_date, interviewer, location, meeting_link, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interview_id,
            interview_data["candidate_id"],
            interview_data["job_id"],
            interview_data.get("interview_type"),
            interview_data.get("scheduled_date"),
            interview_data.get("interviewer"),
            interview_data.get("location"),
            interview_data.get("meeting_link"),
            interview_data.get("status", "scheduled")
        ))
        
        conn.commit()
        conn.close()
        
        return interview_id
    
    def list_interviews(
        self,
        candidate_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List interviews"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM interviews WHERE 1=1"
        params = []
        
        if candidate_id:
            query += " AND candidate_id = ?"
            params.append(candidate_id)
        
        if job_id:
            query += " AND job_id = ?"
            params.append(job_id)
        
        query += " ORDER BY scheduled_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ============ Analytics ============
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get hiring analytics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        total_jobs = cursor.fetchone()["count"]
        
        # Active jobs
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'active'")
        active_jobs = cursor.fetchone()["count"]
        
        # Total candidates
        cursor.execute("SELECT COUNT(*) as count FROM candidates")
        total_candidates = cursor.fetchone()["count"]
        
        # Candidates by status
        cursor.execute("SELECT status, COUNT(*) as count FROM candidates GROUP BY status")
        candidates_by_status = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Average match score
        cursor.execute("SELECT AVG(match_score) as avg_score FROM candidates WHERE match_score IS NOT NULL")
        avg_match_score = cursor.fetchone()["avg_score"]
        
        # Interviews scheduled
        cursor.execute("SELECT COUNT(*) as count FROM interviews WHERE status = 'scheduled'")
        interviews_scheduled = cursor.fetchone()["count"]
        
        conn.close()
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_candidates": total_candidates,
            "candidates_by_status": candidates_by_status,
            "average_match_score": round(avg_match_score, 2) if avg_match_score else 0,
            "interviews_scheduled": interviews_scheduled
        }


# Global database service instance
db_service = DatabaseService()