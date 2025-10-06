# Space Station Cargo Management System

## Overview
This project is a comprehensive cargo management system designed for space stations, developed for the National Space Hackathon 2025. It provides intelligent solutions for cargo placement, retrieval, waste management, and space optimization in zero-gravity environments.

## Key Features
- **Smart Placement Algorithm**: Optimizes cargo placement considering priority, accessibility, and stability
- **Efficient Retrieval System**: Minimizes item movement for quick access
- **Waste Management**: Tracks expired items and plans efficient returns
- **Real-time Simulation**: Tests different scenarios and time progressions
- **3D Visualization**: Interactive view of cargo arrangements
- **Emergency Protocols**: Quick access to critical items

## Technical Architecture
### Backend
- FastAPI for REST API
- SQLAlchemy for database ORM
- Redis for caching
- Parallel processing for computations

### Frontend
- React with TypeScript
- Material-UI components
- Three.js for 3D visualization
- Real-time updates

### Database
- SQLite for development
- PostgreSQL for production

## API Endpoints
1. **Placement API**
   - `POST /api/placement`: Get optimal placement recommendations

2. **Search & Retrieval**
   - `GET /api/search`: Search for items
   - `POST /api/retrieve`: Calculate retrieval path
   - `POST /api/place`: Execute placement

3. **Waste Management**
   - `GET /api/waste/identify`: Identify waste items
   - `POST /api/waste/return-plan`: Generate return plan
   - `POST /api/waste/complete-undocking`: Complete undocking process

4. **Time Simulation**
   - `POST /api/simulate/day`: Simulate a day's operations

5. **Import/Export**
   - `POST /api/import/items`: Import items
   - `POST /api/import/containers`: Import containers
   - `GET /api/export/arrangement`: Export current arrangement

6. **Logging**
   - `GET /api/logs`: Access operation logs

## Setup Instructions

### Prerequisites
- Docker
- Python 3.8+
- Node.js 18+
- Redis

### Local Development Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/space-cargo-management.git
   cd space-cargo-management
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Redis Setup**
   ```bash
   redis-server
   ```

### Docker Setup
1. **Build the container**
   ```bash
   docker build -t space-cargo-management .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 space-cargo-management
   ```

## Testing
- Run unit tests: `python -m pytest backend/tests`
- Run integration tests: `python -m pytest backend/integration_tests`
- Run frontend tests: `cd frontend && npm test`

## Performance Optimization
- Redis caching for frequent queries
- Parallel processing for heavy computations
- Batch operations for multiple items
- Optimized database queries

## Security Features
- JWT authentication
- Role-based access control
- Input validation
- Rate limiting

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License

## Contact
For any queries, please contact: [Your Contact Information]
