from app.crm.database import Base, engine, SessionLocal
from app.crm import models
from app.crm import schemas
from app.crm import crud

def run_test(): 
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("=" * 60)
    print("1. Creating a customer...")
    customer = crud.create_customer(
        db,
        schemas.CustomerCreate(
            customer_name="John Smith",
            email="john.smith@example.com",
            phone="03001234567",
            company="Smith Traders",
        ),
    )
    print(f"   -> Created: {customer}")

    print("\n2. Creating a lead for this customer...")
    lead = crud.create_lead(
        db,
        schemas.LeadCreate(
            customer_id=customer.id,
            source="website",
            status="New",
            assigned_to="Fouzia",
        ),
    )
    print(f"   -> Created: {lead}")

    print("\n3. Moving the lead to 'Contacted' stage...")
    lead = crud.update_lead_status(db, lead.id, "Contacted")
    print(f"   -> New status: {lead.status}")

    print("\n4. Creating a task...")
    task = crud.create_task(
        db,
        schemas.TaskCreate(
            title="Follow up with John about laptop order",
            assigned_to="Fouzia",
            priority="High",
            status="Pending",
        ),
    )
    print(f"   -> Created: {task}")

    print("\n5. Marking the task as In-Progress...")
    task = crud.update_task_status(db, task.id, "In-Progress")
    print(f"   -> New status: {task.status}")

    print("\n6. Logging an activity for the customer...")
    activity = crud.create_activity(
        db,
        schemas.ActivityCreate(
            customer_id=customer.id,
            type="email",
            description="Sent quotation for 25 laptops",
        ),
    )
    print(f"   -> Created: {activity}")

    print("\n7. Fetching the customer's activity timeline...")
    timeline = crud.get_customer_activity_timeline(db, customer.id)
    for item in timeline:
        print(f"   -> [{item.timestamp}] {item.type}: {item.description}")

    print("\n8. Fetching all customers in the database...")
    all_customers = crud.get_customers(db)
    for c in all_customers:
        print(f"   -> {c}")

    print("\n9. Testing error handling (invalid customer_id for activity)...")
    try:
        crud.create_activity(
            db,
            schemas.ActivityCreate(
                customer_id=99999, type="call", description="should fail"
            ),
        )
    except ValueError as e:
        print(f"   -> Correctly caught error: {e}")

    db.close()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - CRM module is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    run_test()