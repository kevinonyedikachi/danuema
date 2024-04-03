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

# Setup Git

git init
git add .
git commit -m "Initial commit"

git remote add origin <repository_url>
git push -u origin master
git push -f origin master

git pull origin main --allow-unrelated-histories # if folder already has code

git checkout -b <new_branch_name> # Create a New Branch
git branch
git config --global user.email
git config --global user.email "78689393+kevinonyedikachi@users.noreply.github.com"

Remove-Item -Path .\.git -Force -Recurse # remove git in window

git status # Optional
git add .
git commit -m "Your descriptive commit message here"
git push origin <branch_name>

git log # To view commit history
git checkout <commit_hash_or_tag> # Checkout the desired state

git checkout <main_branch_name> # Return to the current state

# Create .env file for credentials

.env
