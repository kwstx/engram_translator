# Free-tier deployment (Cloud Run + Neon)

This project is configured to run as a container on Google Cloud Run with a free-tier Neon Postgres database.

## 1) Create a Neon database

1. Create a free Neon project and database.
2. Copy the connection string (e.g. `postgresql://USER:PASSWORD@HOST/DB?sslmode=require`).

## 2) Create GCP resources

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud artifacts repositories create translator-middleware \
  --repository-format=docker \
  --location=us-central1 \
  --description="Translator Middleware images"

gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer"

PROJECT_ID="$(gcloud config get-value project)"
SA_EMAIL="github-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.editor"

gcloud iam service-accounts keys create ./gcp-sa-key.json \
  --iam-account "$SA_EMAIL"
```

## 3) Add GitHub Secrets

Set these repository secrets:

- `GCP_PROJECT_ID` = your GCP project ID
- `GCP_REGION` = region for Cloud Run (e.g. `us-central1`)
- `GCP_ARTIFACT_REPO` = `translator-middleware`
- `GCP_SA_KEY` = contents of `gcp-sa-key.json`
- `DATABASE_URL` = Neon connection string
- `AUTH_JWT_SECRET` = a strong random secret
- `AUTH_ISSUER` = token issuer (e.g. `https://auth.example.com/`)
- `AUTH_AUDIENCE` = token audience (e.g. `translator-middleware`)

## 4) Deploy

Push to `main`. The workflow in `.github/workflows/ci-deploy.yml` runs tests and deploys to Cloud Run.

The service is public (`--allow-unauthenticated`) and Cloud Run returns a URL like:
`https://<service>-<hash>-<region>.a.run.app`.

## 5) Verify

```bash
curl https://<cloud-run-url>/
```

To call queue endpoints, send a valid JWT with the required issuer/audience.
