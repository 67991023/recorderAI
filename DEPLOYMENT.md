# RecorderAI Deployment Guide

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

## Project Structure
recorderAI/ ├── docker-compose.yml ├── frontend/ │ ├── Dockerfile │ ├── nginx.conf │ └── index.html ├── api/ │ ├── Dockerfile │ ├── requirements.txt │ └── app.py ├── database/ │ └── init.sql ├── ARCHITECTURE.md └──