# YouTube Video Comparator: Deployment on Google Cloud

## Overview
This application uses Streamlit to compare YouTube videos by fetching transcripts, summarizing content, and generating comparison tables. It leverages **Google's Gemini AI** for content generation.

Original Idea and Collaborator - [Isha Shukla](https://github.com/isha1225)

![image](https://github.com/user-attachments/assets/2dace121-001f-4186-ab43-69a4d4a97b13)
---
[Isha's Medium Blog URL](https://medium.com/@isha.shukla25/4e748f6b8071) 
---
[Shishir's Hashnode Blog URL](https://hashnode.com/@ShishirSrivastav)
---

## Features
- Extract transcripts from YouTube videos.
- Summarize video content using Gemini AI.
- Generate comparison tables in HTML, CSV, and PDF formats.
- Download comparison results.

---

## Prerequisites

1. **Google Cloud SDK**:
   Install the Google Cloud SDK by following the [official documentation](https://cloud.google.com/sdk/docs/install).

2. **Streamlit Requirements**:
   Install required Python dependencies:
   ```bash
   pip install streamlit youtube-transcript-api google-generativeai python-dotenv
   ```

3. **Environment Variables**:
   Create a `.env` file and include your Gemini AI API key:
   ```env
   API_KEY=your_gemini_api_key
   ```

4. **Docker Installed**:
   Ensure Docker is installed and running locally.

---

## Steps for Deployment on Google Cloud

### 1. **Set Up Google Cloud Project**

1. Initialize Google Cloud:
   ```bash
   gcloud init
   ```
2. Set the active project:
   ```bash
   gcloud config set project <project-name>
   ```

### 2. **Create Artifact Registry Repository**

1. Create a Docker Artifact Registry:
   ```bash
   gcloud artifacts repositories create <repo-name> \
       --repository-format=docker \
       --location=asia-south1 \
       --description="Repository for Streamlit app images"
   ```
2. Grant access to Artifact Registry for your IAM user:
   ```bash
   gcloud projects add-iam-policy-binding <project-name> \
       --member="serviceAccount:<service-account-email>" \
       --role="roles/storage.objectViewer"
   ```

### 3. **Prepare Docker Image**

1. Create a `Dockerfile` for the application:
   ```dockerfile
   FROM python:3.12

   EXPOSE 8080

   WORKDIR /app

   COPY . ./

   RUN pip install --no-cache-dir -r requirements.txt

   ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
   ```

2. Build the Docker image locally:
   ```bash
   docker build -t <imagename>:latest .
   ```

3. Tag the Docker image for Google Artifact Registry:
   ```bash
   docker tag <imagename>:latest asia-south1-docker.pkg.dev/<project-name>/<repo-name>/<imagename>:latest
   ```

4. Authenticate Docker with Google Cloud:
   ```bash
   gcloud auth configure-docker asia-south1-docker.pkg.dev
   ```

5. Push the image to Artifact Registry:
   ```bash
   docker push asia-south1-docker.pkg.dev/<project-name>/<repo-name>/<imagename>:latest
   ```

---

### 4. **Deploy on Cloud Run**

1. Submit the build directly:
   ```bash
   gcloud builds submit --tag asia-south1-docker.pkg.dev/<project-name>/<repo-name>/<imagename>:latest
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy <service-name> \
       --image=asia-south1-docker.pkg.dev/<project-name>/<repo-name>/<imagename>:latest \
       --platform=managed \
       --region=asia-south1 \
       --allow-unauthenticated
   ```

3. Note the generated service URL to access the application.

---

## Usage Instructions

1. **Access the Application**:
   Open the URL provided by Cloud Run after deployment.

2. **Input YouTube URLs**:
   - Use the sidebar to input YouTube video links.
   - Click `Compare Videos` to fetch, summarize, and compare transcripts.

3. **Download Results**:
   - Use the `Download as CSV` buttons to save results.

---

## IAM Role Setup

Create an IAM role for secure access to storage:

1. Assign `roles/storage.objectViewer` to your service account:
   ```bash
   gcloud projects add-iam-policy-binding <project-name> \
       --member="serviceAccount:<service-account-email>" \
       --role="roles/storage.objectViewer"
   ```

2. Verify access permissions:
   ```bash
   gcloud projects get-iam-policy <project-name>
   ```

---

## Debugging Tips

1. Check logs using:
   ```bash
   gcloud run logs read <service-name>
   ```

2. Ensure your `.env` file is correctly set up with the API key.

3. Use `Streamlit`'s debug mode locally:
   ```bash
   streamlit run <your_script_name>.py --server.debug
   ```

---

## Additional Notes

- This app processes transcripts using the `youtube-transcript-api`.
- All AI-generated content is powered by **Gemini AI**.
- Deployed services are region-specific; ensure consistency in region selection (e.g., `asia-south1`).

