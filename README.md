# Real-time Document Collaboration System

A collaborative document editing system that allows multiple users to work on documents simultaneously with real-time updates and permission management.

## Features

- Real-time document collaboration
- Document versioning and history tracking
- Permission-based access control
- WebSocket support for instant updates
- RESTful API for document management

## Tech Stack

- Backend: Django + Channels
- Frontend: React (upcoming)
- Database: PostgreSQL
- WebSockets for real-time communication
- Docker for containerization

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 16+ (for frontend)

## Getting Started

1. Clone the repository:
```bash
git clone [your-repo-url]
cd doc_collab
```

2. Start the services:
```bash
docker-compose up --build
```

The application will be available at:
- Backend API: http://localhost:8000/api/
- Admin interface: http://localhost:8000/admin/

## API Endpoints

### Documents

- `GET /api/documents/` - List all documents
- `POST /api/documents/` - Create new document
- `GET /api/documents/{id}/` - Get document details
- `PUT /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document
- `GET /api/documents/{id}/versions/` - Get document version history

### Permissions

- `POST /api/documents/{id}/invite/` - Invite collaborator
  ```json
  {
      "user_email": "user@example.com",
      "permission_level": "edit"  // "view", "edit", or "admin"
  }
  ```
- `POST /api/documents/{id}/revoke_access/` - Remove collaborator
  ```json
  {
      "user_email": "user@example.com"
  }
  ```
- `POST /api/documents/{id}/update_permission/` - Update permission level
  ```json
  {
      "user_email": "user@example.com",
      "permission_level": "view"
  }
  ```

### WebSocket Connections

Connect to `ws://localhost:8000/ws/document/{document_id}/` for real-time updates.

## Authentication

The API uses Basic Authentication. Include credentials in the Authorization header:
```
Authorization: Basic base64(username:password)
```

## Development Setup

1. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

2. Access the admin interface to manage users and documents:
   - Go to http://localhost:8000/admin/
   - Login with superuser credentials

## Project Structure

```
doc_collab/
├── doc_collab_app/          # Main Django application
│   ├── models.py            # Data models
│   ├── views.py             # API views
│   ├── consumers.py         # WebSocket consumers
│   └── routing.py           # WebSocket routing
├── doc_collab/              # Project configuration
├── frontend/                # React frontend (upcoming)
└── docker-compose.yml       # Docker services configuration
```

## Testing

Test the API endpoints using Postman or curl:

1. Create a document:
```bash
curl -X POST http://localhost:8000/api/documents/ \
  -H "Authorization: Basic [credentials]" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Doc", "content": "Initial content"}'
```

2. Invite a collaborator:
```bash
curl -X POST http://localhost:8000/api/documents/{id}/invite/ \
  -H "Authorization: Basic [credentials]" \
  -H "Content-Type: application/json" \
  -d '{"user_email": "collaborator@example.com", "permission_level": "edit"}'
```

## Architecture Decisions

1. **Django Channels**: Used for WebSocket support, enabling real-time collaboration
2. **PostgreSQL**: Chosen for its robustness and support for JSON fields
3. **Permission Levels**: Implemented three-tier access control (view, edit, admin)
4. **Document Versioning**: Maintains history of changes for audit and rollback

## Limitations and Future Improvements

- Operational transformation for conflict resolution
- Rich text editing support
- Real-time cursor positions
- Document locking mechanism
- Activity tracking and notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

