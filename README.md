## 🛠️ Installation
1. Create a virtual environment:
   ```
   python -m venv venv
   ```
2. Activate virtual environment:
- Windows:
  ```
  venv\Scripts\activate.bat
  ```
  or for PowerShell:
  ```
  venv\Scripts\Activate.ps1
  ```

- macOS/Linux:
  ```
  source venv/bin/activate
  ```
3. Install Dependencies
```
pip install -r requirements.txt
```

## ⚙️ Setup
1. Create a `.env` file in the project root directory with the following keys:
```
OPENAI_API_KEY=<your_openai_api_key_here>
```

2. Create a Google Cloud Project

Go to Google Cloud Dashboard:

https://console.cloud.google.com/

Create a New Project:

- Click on the "Create project" button in the top navigation bar.
- Enter a project name (e.g., "your-project-name") and click "Create".

Enable Gmail and Google Calendar APIs:

1. Go to the **APIs & Services** section in the navigation bar.
2. Click on **Dashboard**.
3. Click on **Enable APIs and Services**.
4. In the search bar, type "Gmail API" and click on it.
5. Click **Enable**.
6. Repeat steps 4 and 5 for "Google Calendar API".

Create OAuth Consent Screen:

1. In the **APIs & Services** section, navigate to **Credentials**.
2. Click on **OAuth consent screens**.
3. Click **Create consent screen**.
4. Select **Internal** for **User type**. (This is for development purposes. Change to "External" for production use).
5. Click **Create**.
6. Fill out the application details:
    - App name: Enter a descriptive name for your application (e.g., "Your App Name").
    - Homepage URI: Enter your application's homepage URL (e.g., http://localhost:8000).
    - Privacy Policy URI (Optional):  If you have a privacy policy, enter the URL here.
7. Click **Save and Continue**.

Add Scopes:

1. Under **Scopes**, expand **Add scopes**.
2. Select the following scopes:

    **Non-sensitive Scopes:**
        - `/auth/userinfo.email`
        - `/auth/userinfo.profile`

    **Sensitive Scopes:**
        - `/auth/calendar`

    **Restricted Scopes:**
        - `https://mail.google.com`

Create OAuth Client ID:

1. Go back to the **Credentials** section.
2. Click on **Create credentials**.
3. Select **OAuth client ID**.
4. Choose **Web application** as the application type.
5. Under **Authorized JavaScript origins**, add the following origins:

    - `http://localhost:8000`

6. Under **Authorized redirect URIs**, add the following URIs:

    - `http://localhost:8000/auth/oauth/google/callback`
    - `http://localhost:54734/`
    - `http://localhost:8080/`
    - `http://localhost`
    - `http://localhost/`

7. Click **Create**.
8. Download the JSON file containing your client credentials. 

Finalize Setup:

1. Rename the downloaded JSON file to `credentials.json`.
2. Place the `credentials.json` file in the root directory of your project.


## 🚀 Running the Application
```
chainlit run app.py
```
see [chainlit docs](https://docs.chainlit.io/backend/command-line#command-line-options) for a full list of command line args
