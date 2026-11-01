from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.crm import crud
from app.crm import models
from app.crm import schemas

STALE_LEAD_DAYS = 3


def find_stale_leads(db: Session, days: int = STALE_LEAD_DAYS) -> List[models.Lead]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return (
        db.query(models.Lead)
        .filter(models.Lead.status == "Contacted")
        .filter(models.Lead.created_at <= cutoff)
        .all()
    )


def create_reminder_for_lead(db: Session, lead: models.Lead) -> models.Task:
    customer = crud.get_customer(db, lead.customer_id)
    customer_name = customer.customer_name if customer else f"customer #{lead.customer_id}"

    task_data = schemas.TaskCreate(
        title=f"Follow up with {customer_name} (lead {lead.id}) - no reply in {STALE_LEAD_DAYS} days",
        assigned_to=lead.assigned_to,
        priority="High",
        status="Pending",
    )
    return crud.create_task(db, task_data)


def run_stale_lead_reminders(db: Session) -> List[models.Task]:
    stale_leads = find_stale_leads(db)
    created_tasks = []

    for lead in stale_leads:
        existing_reminder = (
            db.query(models.Task)
            .filter(models.Task.title.like(f"%(lead {lead.id})%"))
            .first()
        )
        if existing_reminder:
            continue

        task = create_reminder_for_lead(db, lead)
        created_tasks.append(task)

    return created_tasks