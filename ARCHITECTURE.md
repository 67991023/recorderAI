# RecorderAI Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                      (Port 8080)                            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND CONTAINER                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Nginx Web Server                       │    │
│  │           - Serves index.html                       │    │
│  │           - Serves static assets                    │    │
│  │           - Reverse proxy to backend                │    │
│  │           Port:  80 (mapped to 8080)                │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ /api/* requests
                         │ (Bridge Network)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND CONTAINER                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Python Flask REST API                       │    │
│  │         - /api/health                              │    │
│  │         - /api/recordings (GET/POST)               │    │
│  │         - /api/statistics                          │    │
│  │         Port: 5000                                  │    │
│  │         Runtime: Gunicorn WSGI server              │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL Queries
                         │ (Bridge Network)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE CONTAINER                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            PostgreSQL Database                      │    │
│  │            - Database:  recorderai                   │    │
│  │            - Table: recordings                      │    │
│  │            Port: 5432                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            Docker Volume                            │    │
│  │            postgres_data                            │    │
│  │            (Persistent Storage)                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

            All containers connected via: 
         recorderai-network (Bridge Network)
```

## Container Communication

The containers in this RecorderAI application communicate through Docker's bridge network named `recorderai-network`. The frontend Nginx container serves the HTML/JavaScript interface to users on port 8080 and acts as a reverse proxy, forwarding API requests to the backend Flask container using the service name `backend: 5000`. The backend container processes these requests, executes business logic, and communicates with the PostgreSQL database container using the hostname `db:5432` to fetch or store data.  All inter-container communication happens internally within the Docker network using service names as DNS resolution, ensuring isolation from the host system.  The database uses a named Docker volume `postgres_data` for persistent storage, ensuring data survives container restarts.  Health checks monitor each service's status, and the `depends_on` configuration ensures proper startup ordering with the database initializing first, followed by the backend, and finally the frontend.

## Data Flow

1. User accesses http://localhost:8080
2. Nginx serves index.html with JavaScript
3. JavaScript makes AJAX calls to /api/*
4. Nginx proxies requests to backend: 5000
5. Flask API processes requests and queries db: 5432
6. PostgreSQL returns data from persistent volume
7. API returns JSON response to frontend
8. JavaScript renders data in the browser

## Key Features

- **Frontend**: Single-page HTML/JS app with modern UI
- **Backend**: RESTful API returning JSON responses
- **Database**: PostgreSQL with persistent volumes
- **Networking**:  Isolated bridge network for security
- **Health Checks**:  Automated service monitoring
- **Scalability**: Can easily add more services