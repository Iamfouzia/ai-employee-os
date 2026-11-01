import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.database import Base
from app.crm import models
from app.crm import schemas
from app.crm import crud


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()

def test_create_customer(db_session):
    customer = crud.create_customer(
        db_session,
        schemas.CustomerCreate(
            customer_name="Ali Raza",
            email="ali@example.com",
            phone="03001234567",
            company="Raza Traders",
        ),
    )
    assert customer.id is not None
    assert customer.customer_name == "Ali Raza"


def test_get_customers_returns_all(db_session):
    crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Customer One"))
    crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Customer Two"))

    customers = crud.get_customers(db_session)
    assert len(customers) == 2
    names = {c.customer_name for c in customers}
    assert names == {"Customer One", "Customer Two"}


def test_update_customer(db_session):
    customer = crud.create_customer(
        db_session,
        schemas.CustomerCreate(customer_name="Hina Yousuf", company="Old Co"),
    )
    updated = crud.update_customer(
        db_session,
        customer.id,
        schemas.CustomerUpdate(company="New Co"),
    )
    assert updated.company == "New Co"
    assert updated.customer_name == "Hina Yousuf"  


def test_update_customer_not_found_returns_none(db_session):
    result = crud.update_customer(
        db_session,
        9999,
        schemas.CustomerUpdate(company="Doesn't matter"),
    )
    assert result is None


def test_create_lead_for_customer(db_session):
    customer = crud.create_customer(
        db_session,
        schemas.CustomerCreate(customer_name="Sara Khan"),
    )
    lead = crud.create_lead(
        db_session,
        schemas.LeadCreate(customer_id=customer.id, source="website", assigned_to="Fouzia"),
    )
    assert lead.status == "New"
    assert lead.customer_id == customer.id


def test_create_lead_for_missing_customer_raises(db_session):
    with pytest.raises(ValueError):
        crud.create_lead(
            db_session,
            schemas.LeadCreate(customer_id=9999, source="website"),
        )


def test_get_leads_by_customer(db_session):
    customer = crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Nadia Butt"))
    other_customer = crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Other Co"))
    crud.create_lead(db_session, schemas.LeadCreate(customer_id=customer.id, source="referral"))
    crud.create_lead(db_session, schemas.LeadCreate(customer_id=customer.id, source="walk-in"))
    crud.create_lead(db_session, schemas.LeadCreate(customer_id=other_customer.id, source="website"))

    leads = crud.get_leads_by_customer(db_session, customer.id)
    assert len(leads) == 2
    assert all(l.customer_id == customer.id for l in leads)


def test_get_leads_by_status(db_session):
    customer = crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Kamran Ali"))
    lead1 = crud.create_lead(db_session, schemas.LeadCreate(customer_id=customer.id))
    lead2 = crud.create_lead(db_session, schemas.LeadCreate(customer_id=customer.id))
    crud.update_lead_status(db_session, lead1.id, "Contacted")

    new_leads = crud.get_leads_by_status(db_session, "New")
    contacted_leads = crud.get_leads_by_status(db_session, "Contacted")

    assert len(new_leads) == 1
    assert new_leads[0].id == lead2.id
    assert len(contacted_leads) == 1
    assert contacted_leads[0].id == lead1.id


def test_update_lead_status(db_session):
    customer = crud.create_customer(
        db_session,
        schemas.CustomerCreate(customer_name="Bilal Ahmed"),
    )
    lead = crud.create_lead(
        db_session,
        schemas.LeadCreate(customer_id=customer.id),
    )
    updated = crud.update_lead_status(db_session, lead.id, "Contacted")
    assert updated.status == "Contacted"


def test_update_lead_status_not_found_returns_none(db_session):
    result = crud.update_lead_status(db_session, 9999, "Contacted")
    assert result is None


def test_update_lead_fields(db_session):
    customer = crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Owais Malik"))
    lead = crud.create_lead(
        db_session,
        schemas.LeadCreate(customer_id=customer.id, source="cold-call", assigned_to="Ayesha"),
    )
    updated = crud.update_lead(
        db_session,
        lead.id,
        schemas.LeadUpdate(assigned_to="Fouzia"),
    )
    assert updated.assigned_to == "Fouzia"
    assert updated.source == "cold-call"  


def test_delete_lead(db_session):
    customer = crud.create_customer(db_session, schemas.CustomerCreate(customer_name="Rida Zafar"))
    lead = crud.create_lead(db_session, schemas.LeadCreate(customer_id=customer.id))

    deleted = crud.delete_lead(db_session, lead.id)
    assert deleted is True
    assert crud.get_leads_by_customer(db_session, customer.id) == []


def test_delete_lead_not_found_returns_false(db_session):
    assert crud.delete_lead(db_session, 9999) is False


def test_create_task_and_update_status(db_session):
    task = crud.create_task(
        db_session,
        schemas.TaskCreate(title="Follow up with Ali", assigned_to="Fouzia", priority="High"),
    )
    assert task.status == "Pending"

    updated = crud.update_task_status(db_session, task.id, "In-Progress")
    assert updated.status == "In-Progress"


def test_get_tasks_returns_all(db_session):
    crud.create_task(db_session, schemas.TaskCreate(title="Task A"))
    crud.create_task(db_session, schemas.TaskCreate(title="Task B"))

    tasks = crud.get_tasks(db_session)
    assert len(tasks) == 2


def test_get_tasks_by_assignee(db_session):
    crud.create_task(db_session, schemas.TaskCreate(title="Task A", assigned_to="Fouzia"))
    crud.create_task(db_session, schemas.TaskCreate(title="Task B", assigned_to="Ayesha"))
    crud.create_task(db_session, schemas.TaskCreate(title="Task C", assigned_to="Fouzia"))

    fouzia_tasks = crud.get_tasks_by_assignee(db_session, "Fouzia")
    assert len(fouzia_tasks) == 2
    assert all(t.assigned_to == "Fouzia" for t in fouzia_tasks)


def test_update_task_fields(db_session):
    task = crud.create_task(
        db_session,
        schemas.TaskCreate(title="Old title", priority="Low"),
    )
    updated = crud.update_task(
        db_session,
        task.id,
        schemas.TaskUpdate(title="New title", priority="High"),
    )
    assert updated.title == "New title"
    assert updated.priority == "High"


def test_delete_task(db_session):
    task = crud.create_task(db_session, schemas.TaskCreate(title="Temporary task"))
    deleted = crud.delete_task(db_session, task.id)
    assert deleted is True
    assert crud.get_tasks(db_session) == []


def test_delete_task_not_found_returns_false(db_session):
    assert crud.delete_task(db_session, 9999) is False



def test_activity_timeline_for_customer(db_session):
    customer = crud.create_customer(
        db_session,
        schemas.CustomerCreate(customer_name="Zara Malik"),
    )
    crud.create_activity(
        db_session,
        schemas.ActivityCreate(customer_id=customer.id, type="email", description="Sent quotation"),
    )
    crud.create_activity(
        db_session,
        schemas.ActivityCreate(customer_id=customer.id, type="call", description="Follow-up call"),
    )
    timeline = crud.get_customer_activity_timeline(db_session, customer.id)
    assert len(timeline) == 2
    assert timeline[0].timestamp >= timeline[1].timestamp


def test_activity_for_missing_customer_raises(db_session):
    with pytest.raises(ValueError):
        crud.create_activity(
            db_session,
            schemas.ActivityCreate(customer_id=9999, type="call", description="should fail"),
        )




def test_delete_customer_cascades_leads_and_activities(db_session):
    customer = crud.create_customer(
        db_session,
        schemas.CustomerCreate(customer_name="Usman Tariq"),
    )
    crud.create_lead(db_session, schemas.LeadCreate(customer_id=customer.id))
    crud.create_activity(
        db_session,
        schemas.ActivityCreate(customer_id=customer.id, type="call", description="intro call"),
    )

    deleted = crud.delete_customer(db_session, customer.id)
    assert deleted is True
    assert crud.get_customer(db_session, customer.id) is None
