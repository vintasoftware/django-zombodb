## Example Project for django_zombodb

This example is provided as a convenience feature to allow potential users to try the app straight from the app repo without having to create a Django project.

It can also be used to develop the app in place.

To run this example, follow these instructions:

1. Navigate to the `example` directory
2. Install the requirements for the package:
        
        pip install -r requirements.txt

3. Create the Postgres user and DB:

        sudo su - postgres -c "psql -c \"CREATE USER django_zombodb WITH PASSWORD 'password' SUPERUSER;\""
        createdb django_zombodb

4. Run a Elasticsearch cluster:

        elasticsearch
        
5. Apply migrations:
        
        python manage.py migrate

6. Load sample data from PromptCloud's Restaurants on Yellowpages.com [dataset](https://www.kaggle.com/PromptCloudHQ/restaurants-on-yellowpagescom):

        python manage.py filldata
        
7. Create a Django admin user:

        python manage.py createsuperuser

8. Run the server:

        python manage.py runserver

9. Log in into admin and run searches at `http://127.0.0.1:8000/admin/restaurants/restaurant/`:

    ![Django admin screenshot](https://user-images.githubusercontent.com/397989/52665839-63ea4300-2eeb-11e9-9039-7d05bff0ac3a.png)


### Notes:
- `django_zombodb` Postgres user needs to be a `SUPERUSER` for activating the `zombodb` extension on the newly created database. This is handled by the operation `django_zombodb.operations.ZomboDBExtension()` on the `0002` migration. If you wish you can `ALTER ROLE django_zombodb NOSUPERUSER` after running the migrations.
- `ZOMBODB_ELASTICSEARCH_URL` on settings.py defines your Elasticsearch URL. It's set to `http://localhost:9200/`. Change it if necessary.
