"""Demo mode API endpoints"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.demo_mode import enable_demo_mode, disable_demo_mode, get_status

router = APIRouter(prefix="/api/demo", tags=["demo"])


class DemoStatusResponse(BaseModel):
    demo_mode: bool
    pc_awake: bool
    wol_sent: Optional[bool] = None


@router.post("/enable", response_model=DemoStatusResponse)
def enable_demo():
    """Enable demo mode: wake PC and process tips instantly on submission."""
    return enable_demo_mode()


@router.post("/disable")
def disable_demo():
    """Disable demo mode: return to normal nightly processing."""
    return disable_demo_mode()


@router.get("/status", response_model=DemoStatusResponse)
def demo_status():
    """Check demo mode state and PC availability."""
    return get_status()
