from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crm import models
from app.crm import schemas

# Customer CRUD

def create_customer(db: Session, customer_data: schemas.CustomerCreate) -> models.Customer:
    """Create a new customer record."""
    try:
        customer = models.Customer(**customer_data.model_dump())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to create customer: {exc}") from exc


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    """Fetch a single customer by id. Returns None if not found."""
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    """Fetch a paginated list of customers."""
    return db.query(models.Customer).offset(skip).limit(limit).all()


def update_customer(
    db: Session, customer_id: int, customer_data: schemas.CustomerUpdate
) -> Optional[models.Customer]:
    """Update an existing customer with only the fields that were provided."""
    customer = get_customer(db, customer_id)
    if customer is None:
        return None

    try:
        update_fields = customer_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(customer, field, value)
        db.commit()
        db.refresh(customer)
        return customer
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to update customer {customer_id}: {exc}") from exc


def delete_customer(db: Session, customer_id: int) -> bool:
    """Delete a customer (and their leads/activities, via cascade). Returns True if deleted."""
    customer = get_customer(db, customer_id)
    if customer is None:
        return False

    try:
        db.delete(customer)
        db.commit()
        return True
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to delete customer {customer_id}: {exc}") from exc


# Lead CRUD

def create_lead(db: Session, lead_data: schemas.LeadCreate) -> models.Lead:
    """Create a new lead for an existing customer."""
  
    if get_customer(db, lead_data.customer_id) is None:
        raise ValueError(f"Cannot create lead: customer {lead_data.customer_id} does not exist")

    try:
        lead = models.Lead(**lead_data.model_dump())
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to create lead: {exc}") from exc


def get_leads_by_customer(db: Session, customer_id: int) -> List[models.Lead]:
    """Fetch every lead belonging to a given customer (for the sales pipeline view)."""
    return db.query(models.Lead).filter(models.Lead.customer_id == customer_id).all()


def get_leads_by_status(db: Session, status: str) -> List[models.Lead]:
    """Fetch every lead currently in a given pipeline stage (New/Contacted/Negotiation/Closed)."""
    return db.query(models.Lead).filter(models.Lead.status == status).all()


def update_lead_status(db: Session, lead_id: int, new_status: str) -> Optional[models.Lead]:
    """Move a lead to a new pipeline stage."""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead is None:
        return None

    try:
        lead.status = new_status
        db.commit()
        db.refresh(lead)
        return lead
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to update status for lead {lead_id}: {exc}") from exc


def update_lead(db: Session, lead_id: int, lead_data: schemas.LeadUpdate) -> Optional[models.Lead]:
    """Update a lead's editable fields (source, status, assigned_to)."""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead is None:
        return None

    try:
        update_fields = lead_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(lead, field, value)
        db.commit()
        db.refresh(lead)
        return lead
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to update lead {lead_id}: {exc}") from exc


def delete_lead(db: Session, lead_id: int) -> bool:
    """Delete a single lead. Returns True if deleted, False if it didn't exist."""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead is None:
        return False

    try:
        db.delete(lead)
        db.commit()
        return True
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to delete lead {lead_id}: {exc}") from exc


# Task CRUD
def create_task(db: Session, task_data: schemas.TaskCreate) -> models.Task:
    """Create a new task."""
    try:
        task = models.Task(**task_data.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to create task: {exc}") from exc


def get_tasks(db: Session, skip: int = 0, limit: int = 200) -> List[models.Task]:
    """Fetch every task, most recently created first."""
    return (
        db.query(models.Task)
        .order_by(models.Task.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_tasks_by_assignee(db: Session, assigned_to: str) -> List[models.Task]:
    """Fetch every task assigned to a specific person."""
    return db.query(models.Task).filter(models.Task.assigned_to == assigned_to).all()


def update_task(db: Session, task_id: int, task_data: schemas.TaskUpdate) -> Optional[models.Task]:
    """Update a task's editable fields (title, assigned_to, priority, deadline, status)."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        return None

    try:
        update_fields = task_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to update task {task_id}: {exc}") from exc


def update_task_status(db: Session, task_id: int, new_status: str) -> Optional[models.Task]:
    """Update a task's progress status (Pending / In-Progress / Done)."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        return None

    try:
        task.status = new_status
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to update status for task {task_id}: {exc}") from exc


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a single task. Returns True if deleted, False if it didn't exist."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        return False

    try:
        db.delete(task)
        db.commit()
        return True
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to delete task {task_id}: {exc}") from exc

# Activity CRUD

def create_activity(db: Session, activity_data: schemas.ActivityCreate) -> models.Activity:
    """
    Log a new activity (call, email, meeting, WhatsApp message, etc.) for a
    customer. This is the function other modules - e.g. the Executive
    Assistant's SalesAgent, or the WhatsApp/Email module - should call
    whenever they interact with a customer, so it shows up on the
    Activity Timeline.
    """
    if get_customer(db, activity_data.customer_id) is None:
        raise ValueError(
            f"Cannot log activity: customer {activity_data.customer_id} does not exist"
        )

    try:
        activity = models.Activity(**activity_data.model_dump())
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(f"Failed to log activity: {exc}") from exc


def get_customer_activity_timeline(db: Session, customer_id: int) -> List[models.Activity]:
    """
    Return every logged activity for a customer, most recent first.
    Powers the CRM's 'Activity Timeline' feature.
    """
    return (
        db.query(models.Activity)
        .filter(models.Activity.customer_id == customer_id)
        .order_by(models.Activity.timestamp.desc())
        .all()
    )