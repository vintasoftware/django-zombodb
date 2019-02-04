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
		
5. Make and apply migrations

		python manage.py makemigrations
		
		python manage.py migrate

6. Load sample data from PromptCloud's Restaurants on Yellowpages.com [dataset](https://www.kaggle.com/PromptCloudHQ/restaurants-on-yellowpagescom):

		python manage.py filldata
		
6. Run the server

		python manage.py runserver
		
6. Access from the browser at `http://127.0.0.1:8000`
