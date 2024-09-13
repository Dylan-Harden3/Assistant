#In Progress...

python -m venv venv
on windows:
venv\Scripts\activate.bat or .ps1 for powershell
on linux/mac:
source venv/bin/activate

pip install -r requirements.txt

chainlit run app.py

.env needs OPENAI_API_KEY, CHAINLIT_AUTH_SECRET (chainlit create-secret)