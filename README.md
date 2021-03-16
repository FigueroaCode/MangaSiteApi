## Installation
- `python -m venv venv`
- `venv\Scripts\activate`
- `python -m pip install --upgrade pip`
- `pip install -r requirements.txt`

## Start local development server
- `venv\Scripts\activate`
- `flask run --no-debugger`


## Testing
- `venv\Scripts\activate`
- `python -m pytest` (use -rP to see print statements)

## To Deploy run in command prompt:
- `gcloud builds submit --tag gcr.io/mangasiteapi/mangasiteapi`
- `gcloud run deploy mangasiteapi --image gcr.io/mangasiteapi/mangasiteapi --allow-unauthenticated`

## GCloud setup
- `gcloud components install beta`
- `gcloud components update`
- `gcloud config set core/project [MY_PROJECT_ID]`
- `gcloud services enable run.googleapis.com`