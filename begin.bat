python3 -m venv venv || goto :error
call .\venv\Scripts\activate.bat || goto :error
pip install --requirement requirements.txt || goto :error
SET FLASK_APP=server.py
flask run

:error
echo "An error occurred."
exit 1
