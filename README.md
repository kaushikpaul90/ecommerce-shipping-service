# Shipping Service

A microservice responsible for managing shipping operations in the e-commerce system. This service is built using FastAPI and is designed to handle shipment creation, status tracking, and management.

## Features

- Create new shipments
- Track shipment status
- List all shipments
- Update shipment information
- Health check endpoint
- Simulated shipping processing (configurable)
- Integration with database service

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- HTTPX
- Docker
- Kubernetes (Helm)

## Prerequisites

- Python 3.11 or higher
- Docker (for containerization)
- Kubernetes cluster (for deployment)
- Helm (for Kubernetes package management)

## Installation

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8007 --reload
   ```

### Docker

1. Build the Docker image:
   ```bash
   docker build -t shipping-service .
   ```

2. Run the container:
   ```bash
   docker run -p 8007:8007 -e DATABASE_SERVICE_URL=http://your-db-service:8000 shipping-service
   ```

### Kubernetes Deployment

1. Navigate to the helm chart directory:
   ```bash
   cd helm_chart
   ```

2. Install the chart:
   ```bash
   helm install shipping-service .
   ```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /shipments` - Create a new shipment
- `GET /shipments/{sid}` - Get shipment details by ID
- `GET /shipments` - List all shipments
- `PUT /shipments/{sid}` - Update shipment details

## Environment Variables

- `DATABASE_SERVICE_URL` - URL of the database service (default: "http://192.168.105.2:30000")
- `PROCESS_SHIPPING_SYNC` - Enable/disable synchronous shipping simulation (default: "true")

## Request/Response Examples

### Create Shipment

```json
POST /shipments

Request:
{
  "id": "ship_123",
  "order_id": "order_123",
  "address": {
    "street": "123 Main St",
    "city": "Example City",
    "country": "US"
  },
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 1
    }
  ],
  "status": "created"
}

Response:
{
  "id": "ship_123",
  "order_id": "order_123",
  "address": {
    "street": "123 Main St",
    "city": "Example City",
    "country": "US"
  },
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 1
    }
  ],
  "status": "shipped"
}
```

## Error Handling

The service includes comprehensive error handling for:
- Network timeouts
- Database service connectivity issues
- Invalid shipment data
- Shipping provider failures

## Testing

For testing shipping failures, set the country in the address to "FAIL":
```json
{
  "address": {
    "country": "FAIL"
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
