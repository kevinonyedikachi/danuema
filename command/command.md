# Create a virtual enviroment

python -m venv venv
source venv/bin/activate

# Install the project dependencies

pip install -r requirements.txt
pip freeze > requirements.txt

# Access the Django admin interface

- Visit `http://localhost:8000/admin/` in your web browser.
- You can create a superuser using `python manage.py createsuperuser` inside the Django container.

# Run on Django to inspect task

celery inspect active
celery inspect active_queue

# Create .env file for credentials

.env
