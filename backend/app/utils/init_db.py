from app.models.database import create_tables, SessionLocal, Container, Item
import datetime

def init_db():
    """Initialize the database with tables and sample data."""
    # Create tables
    create_tables()
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if we already have containers
        container_count = db.query(Container).count()
        
        if container_count == 0:
            # Add sample containers
            containers = [
                Container(
                    id="contA",
                    zone="Crew Quarters",
                    width=100.0,
                    depth=85.0,
                    height=200.0
                ),
                Container(
                    id="contB",
                    zone="Airlock",
                    width=50.0,
                    depth=85.0,
                    height=200.0
                ),
                Container(
                    id="contC",
                    zone="Laboratory",
                    width=200.0,
                    depth=85.0,
                    height=200.0
                ),
                Container(
                    id="contD",
                    zone="Medical Bay",
                    width=150.0,
                    depth=85.0,
                    height=150.0
                )
            ]
            
            db.add_all(containers)
            db.commit()
        
        # Check if we already have items
        item_count = db.query(Item).count()
        
        if item_count == 0:
            # Add sample items
            items = [
                Item(
                    id="001",
                    name="Food Packet",
                    width=10.0,
                    depth=10.0,
                    height=20.0,
                    mass=5.0,
                    priority=80,
                    expiry_date=datetime.datetime(2025, 5, 20),
                    usage_limit=30,
                    remaining_uses=30,
                    preferred_zone="Crew Quarters",
                    is_waste=False
                ),
                Item(
                    id="002",
                    name="Oxygen Cylinder",
                    width=15.0,
                    depth=15.0,
                    height=50.0,
                    mass=30.0,
                    priority=95,
                    expiry_date=None,
                    usage_limit=100,
                    remaining_uses=100,
                    preferred_zone="Airlock",
                    is_waste=False
                ),
                Item(
                    id="003",
                    name="First Aid Kit",
                    width=20.0,
                    depth=20.0,
                    height=10.0,
                    mass=2.0,
                    priority=100,
                    expiry_date=datetime.datetime(2025, 7, 10),
                    usage_limit=5,
                    remaining_uses=5,
                    preferred_zone="Medical Bay",
                    is_waste=False
                ),
                Item(
                    id="004",
                    name="Science Equipment",
                    width=30.0,
                    depth=30.0,
                    height=40.0,
                    mass=15.0,
                    priority=70,
                    expiry_date=None,
                    usage_limit=50,
                    remaining_uses=50,
                    preferred_zone="Laboratory",
                    is_waste=False
                ),
                Item(
                    id="005",
                    name="Water Container",
                    width=25.0,
                    depth=25.0,
                    height=35.0,
                    mass=10.0,
                    priority=90,
                    expiry_date=datetime.datetime(2025, 6, 15),
                    usage_limit=20,
                    remaining_uses=20,
                    preferred_zone="Crew Quarters",
                    is_waste=False
                )
            ]
            
            db.add_all(items)
            db.commit()
    
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
