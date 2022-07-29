Service Football Statistics
Parse play with Celery and Broker - Redis
Install Dependencies - 
pip install -r requirements.txt
Run migrate - 
python manage.py migrate
Apply migrate - 
python manage.py makemigrations

Fill db mysql by dump - e.g. - football_team_202105070033_dump_team_with_new_inter.sql

Run Django server -
python manage.py runserver

Run Celery Workers -
cd src && celery -A stats_parser worker --loglevel=info

Run Beat Redis -
cd src && celery -A stats_parser beat --loglevel=INFO


Schedule Beat in - src/stats_parser/celery_tasks.py