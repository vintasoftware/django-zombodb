## Example Project for django_zombodb

This example is provided as a convenience feature to allow potential users to try the app straight from the app repo without having to create a django project.

It can also be used to develop the app in place.

To run this example, follow these instructions:

1. Navigate to the `example` directory
2. Install the requirements for the package:
		
		pip install -r requirements.txt

3. Create the Postgres user and DB:

        createuser django_zombodb
        createdb django_zombodb

4. Create ZomboDB extension on DB:

		psql -d django_zombodb -c "CREATE EXTENSION zombodb"

5. Run a ElasticSearch cluster:

		elasticsearch

6. Set ZOMBODB_ELASTICSEARCH_URL on your settings.py:

		ZOMBODB_ELASTICSEARCH_URL = 'http://localhost:9200/'
		
7. Make and apply migrations

		python manage.py makemigrations
		
		python manage.py migrate

8. Load sample data from PromptCloud's Restaurants on Yellowpages.com [dataset](https://www.kaggle.com/PromptCloudHQ/restaurants-on-yellowpagescom):

		python manage.py filldata
		
9. Run the server

		python manage.py runserver
		
10. Access from the browser at `http://127.0.0.1:8000`
