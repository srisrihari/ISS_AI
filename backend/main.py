import os
import uvicorn
from app.utils.init_db import init_db

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    # Respect PORT from environment (required by Render); default to 8000 locally
    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    
    # Run the application
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
