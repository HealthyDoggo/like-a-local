"""Job management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.api.dependencies import get_database
from backend.jobs.nightly_processor import process_pending_tips, run_promotion

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobResponse(BaseModel):
    """Job response model"""
    message: str
    status: str


def run_processing_job(db: Session, wake_pc: bool = True):
    """Background task for processing"""
    try:
        stats = process_pending_tips(db, wake_pc=wake_pc)
        return stats
    except Exception as e:
        raise Exception(f"Processing job failed: {e}")


@router.post("/process", response_model=JobResponse)
def trigger_processing(
    background_tasks: BackgroundTasks,
    wake_pc: bool = True,
    db: Session = Depends(get_database)
):
    """Manually trigger tip processing"""
    try:
        # Run in background
        background_tasks.add_task(run_processing_job, db, wake_pc)
        return JobResponse(
            message="Processing job started",
            status="started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/promote", response_model=JobResponse)
def trigger_promotion(
    db: Session = Depends(get_database)
):
    """Manually trigger tip promotion"""
    try:
        promoted_count = run_promotion(db)
        return JobResponse(
            message=f"Promoted {promoted_count} tips",
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

