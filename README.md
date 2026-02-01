# Smart Bin Inventory Tracking Dashboard

A comprehensive real-time inventory tracking system that receives weight data from smart bins and displays inventory levels with analytics and alerts.

## Features

- 🏭 **Real-time Monitoring**: Live updates via WebSocket connections
- 📊 **Analytics Dashboard**: Visualize consumption patterns, trends, and status distribution
- 🚨 **Smart Alerts**: Configurable low-stock and empty bin alerts with cooldown periods
- 📁 **Excel Export**: Export inventory data, history, and reports to Excel
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🔄 **Auto-reconnect**: WebSocket automatically reconnects on connection loss

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                            │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Dashboard│  │Analytics│  │ Alerts   │  │ Export Functions  │  │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └─────────┬─────────┘  │
│       │            │            │                   │            │
│       └────────────┴────────────┴───────────────────┘            │
│                            │                                     │
│                   WebSocket │ HTTP REST                          │
└───────────────────────────┬┴────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Bin API │  │Alert API│  │Export API│  │ Analytics API    │   │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └────────┬─────────┘   │
│       │            │            │                  │             │
│       └────────────┴────────────┴──────────────────┘             │
│                            │                                     │
│               ┌────────────┴────────────┐                        │
│               │    Service Layer        │                        │
│               │  ┌──────────────────┐   │                        │
│               │  │InventoryService  │   │                        │
│               │  │ AlertService     │   │                        │
│               │  │ ExportService    │   │                        │
│               │  └──────────────────┘   │                        │
│               └────────────┬────────────┘                        │
│                            │                                     │
│                    ┌───────┴───────┐                             │
│                    │   Database    │                             │
│                    │  SQLite / D1  │                             │
│                    └───────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **aiosqlite** - Async SQLite database
- **WebSockets** - Real-time communication
- **openpyxl** - Excel file generation
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Charts and graphs
- **Lucide React** - Icons

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -m app.database.migrate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d --build
```

Access the application at http://localhost

## API Endpoints

### Bin Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bins/data` | Update bin weight data |
| GET | `/api/bins` | Get all bins status |
| GET | `/api/bins/{binId}` | Get specific bin details |
| GET | `/api/bins/{binId}/history` | Get bin history |
| GET | `/api/bins/summary` | Get inventory summary |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/active` | Get active alerts |
| GET | `/api/alerts/history` | Get alert history |
| PUT | `/api/alerts/{alertId}/acknowledge` | Acknowledge an alert |
| PUT | `/api/alerts/acknowledge-all` | Acknowledge all alerts |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/trends` | Get inventory trends |
| GET | `/api/analytics/consumption` | Get consumption data |
| GET | `/api/analytics/comparison` | Get bin comparison |
| GET | `/api/analytics/status-distribution` | Get status distribution |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/inventory` | Export current inventory |
| GET | `/api/export/history` | Export inventory history |
| GET | `/api/export/alerts` | Export alert history |
| GET | `/api/export/report` | Export full report |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws` | Real-time updates |

## Data Format

### Incoming Weight Data
Send weight updates to the system via POST request:

```json
{
  "bin_id": "BIN-001",
  "weight_kg": 25.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Response Format
```json
{
  "bin_id": "BIN-001",
  "bin_name": "Raw Materials A",
  "current_quantity": 850,
  "max_capacity": 1000,
  "fill_percentage": 85,
  "status": "normal",
  "unit": "units",
  "location_row": 1,
  "location_position": 1,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

## Bin Configuration

The system supports 10 bins arranged in a 2×5 grid:

| Row | Position 1 | Position 2 | Position 3 | Position 4 | Position 5 |
|-----|------------|------------|------------|------------|------------|
| 1 | BIN-001 | BIN-002 | BIN-003 | BIN-004 | BIN-005 |
| 2 | BIN-006 | BIN-007 | BIN-008 | BIN-009 | BIN-010 |

## Alert Thresholds

- **Low Stock**: Below 20% capacity (configurable)
- **Empty**: Below 5% capacity (configurable)
- **Cooldown**: 5 minutes between repeated alerts

## Environment Variables

### Backend (.env)
```env
ENVIRONMENT=development
DATABASE_PATH=./data/inventory.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
USE_D1=false
D1_ACCOUNT_ID=your_account_id
D1_DATABASE_ID=your_database_id
D1_API_TOKEN=your_api_token
```

## Testing the API

### Using cURL

```bash
# Update bin weight
curl -X POST http://localhost:8000/api/bins/data \
  -H "Content-Type: application/json" \
  -d '{"bin_id": "BIN-001", "weight_kg": 25.5}'

# Get all bins
curl http://localhost:8000/api/bins

# Get active alerts
curl http://localhost:8000/api/alerts/active
```

### Using Python

```python
import requests

# Update bin weight
response = requests.post(
    "http://localhost:8000/api/bins/data",
    json={"bin_id": "BIN-001", "weight_kg": 25.5}
)
print(response.json())
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details
