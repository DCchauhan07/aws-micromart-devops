# MicroMart — AWS Containerized Microservices Platform

A hands-on Cloud Engineering and DevOps portfolio project.

## Architecture

- AWS EC2 Ubuntu
- Docker and Docker Compose
- Python Flask Product Service
- Python Flask Order Service
- Nginx reverse proxy
- SQLite persistent storage
- AWS CloudWatch monitoring
- AWS Systems Manager deployment
- GitHub Actions CI/CD
- GitHub OIDC authentication
- Amazon S3 release storage

## Application

Product Service: Internal port 5001

Order Service: Internal port 5002

Nginx: Localhost port 8080

## Deployment

Docker Compose manages the application services.

GitHub Actions validates code and builds images.

Manual releases are deployed through AWS Systems Manager.

## Security

- No AWS access keys stored in source code
- IAM roles for AWS access
- Private Docker backend networking
- Backend ports not exposed publicly
- SSH tunneling for browser access
- Runtime database excluded from Git

## Project Status

Phase 7: CI/CD implementation.
