# Create a virtual enviroment

python -m venv venv
source venv/bin/activate

# Install the project dependencies

pip install -r requirements.txt
pip freeze > requirements.txt

# Setup Git

git init
git add .
git commit -m "Initial commit"
git pull origin main --allow-unrelated-histories # if folder already has code
git remote add origin <repository_url>
git push -u origin master

git checkout -b main
git branch
git config --global user.email
git config --global user.email "78689393+kevinonyedikachi@users.noreply.github.com"

Remove-Item -Path .\.git -Force -Recurse

# Create .env file for credentials

.env
