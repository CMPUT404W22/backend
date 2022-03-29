touch ./backend/.env
echo "SECRET_KEY=e^b34l68jzk@(&+y41ftkqfb$vxh0rua#@k8h-sd%=-g^c66od\nDATABASE_NAME=404project\nDATABASE_USER=\nDATABASE_PASS=\nDATABASE_HOST=localhost\nDATABASE_PORT=3306\n" > ./backend/.env
echo "You need to enter your username and password for your mysql database in ./backend/.env"

python3 -m venv .
source venv/bin/activate
pip install -r requirements.txt