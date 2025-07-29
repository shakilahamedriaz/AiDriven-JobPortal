# Google Cloud Deployment Guide for AI-Driven Job Portal

## Prerequisites

1. **Google Cloud Account**: Create one at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud CLI**: Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Docker**: Install from [docker.com](https://docker.com)

## Step-by-Step Deployment

### 1. Setup Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (replace PROJECT_ID with your unique project ID)
gcloud projects create PROJECT_ID --name="AI Job Portal"

# Set the project as default
gcloud config set project PROJECT_ID

# Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing
```

### 2. Enable Required APIs

```bash
# Enable necessary APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Configure Docker for Google Cloud

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker
```

### 4. Environment Variables Setup

Create a `.env.production` file (don't commit this to git):

```env
# .env.production
DEBUG=False
SECRET_KEY=your-super-secret-key-here
GROQ_API_KEY=your-groq-api-key
ALLOWED_HOSTS=your-domain.com,your-app-name.run.app
```

### 5. Build and Deploy

#### Option A: Using the Deploy Script (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Edit deploy.sh and update PROJECT_ID
# Then run:
./deploy.sh
```

#### Option B: Manual Deployment

```bash
# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="ai-job-portal"
REGION="us-central1"

# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2
```

### 6. Post-Deployment Setup

After deployment, you'll need to:

1. **Run database migrations**:
```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe ai-job-portal --platform managed --region us-central1 --format 'value(status.url)')

# Access the deployed app and run migrations (you might need to add a migration endpoint)
```

2. **Create a superuser** (you'll need to add an endpoint for this or use Cloud Shell)

3. **Upload static files** if needed

## Environment Variables in Cloud Run

Set environment variables in Cloud Run:

```bash
gcloud run services update ai-job-portal \
    --set-env-vars "DEBUG=False" \
    --set-env-vars "GROQ_API_KEY=your-api-key" \
    --set-env-vars "SECRET_KEY=your-secret-key"
```

## Database Options

### Option 1: SQLite (Current Setup)
- Good for development/testing
- Data persists in the container
- Not recommended for production

### Option 2: Cloud SQL PostgreSQL (Recommended for Production)

```bash
# Create Cloud SQL instance
gcloud sql instances create jobportal-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create jobportal --instance=jobportal-db

# Create user
gcloud sql users create jobportal-user \
    --instance=jobportal-db \
    --password=secure-password
```

Then update your `production_settings.py` to use the Cloud SQL database.

## Monitoring and Logs

```bash
# View logs
gcloud run services logs read ai-job-portal --platform managed --region us-central1

# View service details
gcloud run services describe ai-job-portal --platform managed --region us-central1
```

## Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service ai-job-portal \
    --domain your-domain.com \
    --region us-central1
```

## Troubleshooting

### Common Issues:

1. **Build Fails**: Check Dockerfile syntax and dependencies
2. **Deploy Fails**: Verify project ID and permissions
3. **App Crashes**: Check logs with `gcloud run services logs read`
4. **Static Files Missing**: Ensure `collectstatic` runs in Dockerfile

### Useful Commands:

```bash
# Delete service
gcloud run services delete ai-job-portal --region us-central1

# Update service with new image
gcloud run services update ai-job-portal --image gcr.io/PROJECT_ID/ai-job-portal

# Scale service
gcloud run services update ai-job-portal --max-instances 20 --min-instances 1
```

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Restrict `ALLOWED_HOSTS` to your domain
- [ ] Use HTTPS (Cloud Run provides this automatically)
- [ ] Store sensitive data in Secret Manager (optional)
- [ ] Enable Cloud Armor for DDoS protection (optional)

## Cost Optimization

- Set appropriate CPU and memory limits
- Use `--min-instances 0` for cost savings (cold starts)
- Monitor usage in Cloud Console
- Set up billing alerts

Your application will be available at: `https://ai-job-portal-[hash].run.app`
