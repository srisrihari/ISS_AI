from typing import List, Dict, Tuple, Optional, BinaryIO
import csv
import io
from datetime import datetime
from app.models.schemas import ImportError
from app.models.database import Item, Container, SessionLocal

class ImportExportService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def import_items(self, file: BinaryIO) -> Tuple[int, List[ImportError]]:
        """
        Import items from a CSV file.
        Returns a tuple of (items_imported, errors)
        """
        items_imported = 0
        errors = []

        try:
            # Read CSV file
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))

            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header row
                try:
                    # Validate required fields
                    required_fields = ['Item ID', 'Name', 'Width (cm)', 'Depth (cm)', 'Height (cm)',
                                      'Mass (kg)', 'Priority (1-100)', 'Usage Limit', 'Preferred Zone']

                    missing_fields = False
                    for field in required_fields:
                        if field not in row or not row[field]:
                            errors.append(ImportError(
                                row=row_num,
                                message=f"Missing required field: {field}"
                            ))
                            missing_fields = True

                    if missing_fields:
                        continue

                    # Parse expiry date if provided
                    expiry_date = None
                    if 'Expiry Date (ISO Format)' in row and row['Expiry Date (ISO Format)']:
                        try:
                            expiry_date = datetime.fromisoformat(row['Expiry Date (ISO Format)'].replace('Z', '+00:00'))
                        except ValueError:
                            errors.append(ImportError(
                                row=row_num,
                                message="Invalid expiry date format. Expected ISO format (YYYY-MM-DD)."
                            ))
                            continue

                    # Check if item already exists
                    existing_item = self.db.query(Item).filter(Item.id == row['Item ID']).first()

                    if existing_item:
                        # Update existing item
                        existing_item.name = row['Name']
                        existing_item.width = float(row['Width (cm)'])
                        existing_item.depth = float(row['Depth (cm)'])
                        existing_item.height = float(row['Height (cm)'])
                        existing_item.mass = float(row['Mass (kg)'])
                        existing_item.priority = int(row['Priority (1-100)'])
                        existing_item.expiry_date = expiry_date
                        existing_item.usage_limit = int(row['Usage Limit'])
                        existing_item.remaining_uses = int(row['Usage Limit'])
                        existing_item.preferred_zone = row['Preferred Zone']
                    else:
                        # Create new item
                        new_item = Item(
                            id=row['Item ID'],
                            name=row['Name'],
                            width=float(row['Width (cm)']),
                            depth=float(row['Depth (cm)']),
                            height=float(row['Height (cm)']),
                            mass=float(row['Mass (kg)']),
                            priority=int(row['Priority (1-100)']),
                            expiry_date=expiry_date,
                            usage_limit=int(row['Usage Limit']),
                            remaining_uses=int(row['Usage Limit']),
                            preferred_zone=row['Preferred Zone'],
                            is_waste=False
                        )
                        self.db.add(new_item)

                    items_imported += 1

                except Exception as e:
                    errors.append(ImportError(
                        row=row_num,
                        message=f"Error processing row: {str(e)}"
                    ))

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            errors.append(ImportError(
                row=0,
                message=f"Error processing file: {str(e)}"
            ))

        return items_imported, errors

    def import_containers(self, file: BinaryIO) -> Tuple[int, List[ImportError]]:
        """
        Import containers from a CSV file.
        Returns a tuple of (containers_imported, errors)
        """
        containers_imported = 0
        errors = []

        try:
            # Read CSV file
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))

            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header row
                try:
                    # Validate required fields
                    required_fields = ['Container ID', 'Zone', 'Width (cm)', 'Depth (cm)', 'Height (cm)']

                    for field in required_fields:
                        if field not in row or not row[field]:
                            errors.append(ImportError(
                                row=row_num,
                                message=f"Missing required field: {field}"
                            ))
                            continue

                    # Check if container already exists
                    existing_container = self.db.query(Container).filter(Container.id == row['Container ID']).first()

                    if existing_container:
                        # Update existing container
                        existing_container.zone = row['Zone']
                        existing_container.width = float(row['Width (cm)'])
                        existing_container.depth = float(row['Depth (cm)'])
                        existing_container.height = float(row['Height (cm)'])
                    else:
                        # Create new container
                        new_container = Container(
                            id=row['Container ID'],
                            zone=row['Zone'],
                            width=float(row['Width (cm)']),
                            depth=float(row['Depth (cm)']),
                            height=float(row['Height (cm)'])
                        )
                        self.db.add(new_container)

                    containers_imported += 1

                except Exception as e:
                    errors.append(ImportError(
                        row=row_num,
                        message=f"Error processing row: {str(e)}"
                    ))

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            errors.append(ImportError(
                row=0,
                message=f"Error processing file: {str(e)}"
            ))

        return containers_imported, errors

    def export_arrangement(self) -> str:
        """
        Export the current arrangement to a CSV string.
        Returns a CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Item ID', 'Container ID', 'Coordinates (W1,D1,H1),(W2,D2,H2)'])

        # Get all items with container assignments
        items = self.db.query(Item).filter(Item.container_id.isnot(None)).all()

        # Write item data
        for item in items:
            coordinates = f"({item.position_width},{item.position_depth},{item.position_height}),({item.position_width + item.width},{item.position_depth + item.depth},{item.position_height + item.height})"
            writer.writerow([item.id, item.container_id, coordinates])

        return output.getvalue()
