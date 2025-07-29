#!/bin/bash

# Build and Deploy Script for Google Cloud

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Google Cloud Deployment${NC}"

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo -e "${RED}❌ Google Cloud CLI is required but not installed. Please install it first.${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed. Please install it first.${NC}"; exit 1; }

# Set project variables
PROJECT_ID="your-project-id"  # Replace with your actual project ID
SERVICE_NAME="ai-job-portal"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo -e "Project ID: $PROJECT_ID"
echo -e "Service Name: $SERVICE_NAME"
echo -e "Region: $REGION"
echo -e "Image: $IMAGE_NAME"

# Authenticate with Google Cloud (if needed)
echo -e "${YELLOW}🔐 Checking authentication...${NC}"
gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Please authenticate with Google Cloud:${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${YELLOW}🎯 Setting project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image
echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
docker build -t $IMAGE_NAME .

# Push the image to Google Container Registry
echo -e "${YELLOW}📤 Pushing image to Google Container Registry...${NC}"
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=job_portal.settings" \
    --set-env-vars "DEBUG=False"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Your application is now live!${NC}"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}🔗 URL: $SERVICE_URL${NC}"
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    exit 1
fi
