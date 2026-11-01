import datetime as dt
from typing import List, Optional
from app.crm import reminders
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.crm import crud
from app.crm import schemas
from app.crm.database import get_db
from app.communication.integrations.calendar_client import GoogleCalendarClient

router = APIRouter(prefix="/api/crm", tags=["CRM"])
AI_TEST_MODE = True


@router.post("/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_customer(db, customer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/customers", response_model=List[schemas.CustomerResponse])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db, skip=skip, limit=limit)


@router.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.patch("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    try:
        updated = crud.update_customer(db, customer_id, customer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return updated


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        deleted = crud.delete_customer(db, customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")


@router.post("/leads", response_model=schemas.LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_lead(db, lead)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/customers/{customer_id}/leads", response_model=List[schemas.LeadResponse])
def get_leads_for_customer(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_leads_by_customer(db, customer_id)


@router.get("/leads", response_model=List[schemas.LeadResponse])
def get_leads_by_status(status_filter: str, db: Session = Depends(get_db)):
    return crud.get_leads_by_status(db, status_filter)


@router.patch("/leads/{lead_id}/status", response_model=schemas.LeadResponse)
def update_lead_status(lead_id: int, new_status: str, db: Session = Depends(get_db)):
    try:
        lead = crud.update_lead_status(db, lead_id, new_status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.patch("/leads/{lead_id}", response_model=schemas.LeadResponse)
def update_lead(lead_id: int, lead: schemas.LeadUpdate, db: Session = Depends(get_db)):
    try:
        updated = crud.update_lead(db, lead_id, lead)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return updated


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_lead(db, lead_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")


@router.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_task(db, task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks_by_assignee(assigned_to: Optional[str] = None, skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    if assigned_to:
        return crud.get_tasks_by_assignee(db, assigned_to)
    return crud.get_tasks(db, skip=skip, limit=limit)


@router.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    try:
        updated = crud.update_task(db, task_id, task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated


@router.patch("/tasks/{task_id}/status", response_model=schemas.TaskResponse)
def update_task_status(task_id: int, new_status: str, db: Session = Depends(get_db)):
    try:
        task = crud.update_task_status(db, task_id, new_status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post("/activities", response_model=schemas.ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_activity(db, activity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/customers/{customer_id}/timeline", response_model=List[schemas.ActivityResponse])
def get_customer_timeline(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_customer_activity_timeline(db, customer_id)


class ScheduleMeetingRequest(BaseModel):
    title: str
    start_time: dt.datetime
    duration_minutes: int = 30
    customer_id: Optional[int] = None
    notes: Optional[str] = None


@router.post("/leads/{lead_id}/schedule-meeting", status_code=status.HTTP_201_CREATED)
def schedule_meeting_for_lead(lead_id: int, payload: ScheduleMeetingRequest, db: Session = Depends(get_db)):
    try:
        calendar_client = GoogleCalendarClient()
        event = calendar_client.create_follow_up_event(
            title=payload.title,
            start_at=payload.start_time,
            description=payload.notes or "",
            duration_minutes=payload.duration_minutes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Calendar not available: {e}")

    if payload.customer_id:
        try:
            crud.create_activity(
                db,
                schemas.ActivityCreate(
                    customer_id=payload.customer_id,
                    type="meeting",
                    description=f"Meeting scheduled: {payload.title} at {payload.start_time.isoformat()}",
                ),
            )
        except ValueError:
            pass

    return event


@router.get("/customers/{customer_id}/ai-summary")
def get_ai_customer_summary(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    activities = crud.get_customer_activity_timeline(db, customer_id)
    activity_text = "\n".join(
        f"[{a.timestamp.isoformat()}] {a.type}: {a.description}" for a in activities
    )

    system_prompt = "You are a CRM assistant. Summarize the customer relationship in 2-3 concise sentences."
    user_prompt = f"Customer: {customer.customer_name}\nActivity log:\n{activity_text or 'No activity logged yet.'}"

    try:
        if AI_TEST_MODE:
            result = {"text": f"[TEST MODE] {customer.customer_name} has {len(activities)} logged activities."}
        else:
            from app.core.llm_router import route_and_generate
            result = route_and_generate(system_prompt, user_prompt, text_for_complexity=user_prompt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service unavailable: {e}")

    return {"customer_id": customer_id, "summary": result["text"]}


@router.get("/customers/{customer_id}/ai-insight")
def get_ai_relationship_insight(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    activities = crud.get_customer_activity_timeline(db, customer_id)
    activity_text = "\n".join(
        f"[{a.timestamp.isoformat()}] {a.type}: {a.description}" for a in activities
    )

    system_prompt = (
        "You are a CRM assistant. Based on the activity log, respond with an engagement "
        "level (Warm, Neutral, or At Risk) and one suggested next action. "
        "Format: 'Engagement: <level>. Next action: <action>.'"
    )
    user_prompt = f"Customer: {customer.customer_name}\nActivity log:\n{activity_text or 'No activity logged yet.'}"

    try:
        if AI_TEST_MODE:
            result = {"text": f"[TEST MODE] Engagement: Warm. Next action: Follow up with {customer.customer_name}."}
        else:
            from app.core.llm_router import route_and_generate
            result = route_and_generate(system_prompt, user_prompt, text_for_complexity=user_prompt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service unavailable: {e}")

    return {"customer_id": customer_id, "insight": result["text"]}


@router.post("/reminders/run")
def run_reminders(db: Session = Depends(get_db)):
    created = reminders.run_stale_lead_reminders(db)
    return {"reminders_created": len(created)}