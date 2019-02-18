from django.db import connection
from django.test.runner import DiscoverRunner


class DropSchemaDiscoverRunner(DiscoverRunner):

    def teardown_databases(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE OR REPLACE FUNCTION drop_all_zombodb_indexes() RETURNS INTEGER AS $$
                DECLARE
                  i RECORD;
                BEGIN
                  FOR i IN
                    (SELECT relname FROM pg_class
                       -- exclude all pkey, exclude system catalog which starts with 'pg_'
                      WHERE relkind = 'i' AND relname LIKE '%_zombodb%')
                  LOOP
                    -- RAISE INFO 'DROPING INDEX: %', i.relname;
                    EXECUTE 'DROP INDEX ' || i.relname;
                  END LOOP;
                RETURN 1;
                END;
                $$ LANGUAGE plpgsql;

                SELECT drop_all_zombodb_indexes();
            ''')
        super().teardown_databases(*args, **kwargs)
