# 🤖 AI Assistant
In progress...

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
2. Generate a chainlit auth token:
```
chainlit create-secret
```
and copy the output into `.env`

## 🚀 Running the Application
```
chainlit run app.py
```
see [chainlit docs](https://docs.chainlit.io/backend/command-line#command-line-options) for a full list of command line args
