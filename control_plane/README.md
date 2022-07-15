## Make database migration

Do this after changing the database model in database.py

```
alembic revision --autogenerate -m "<commit name>"
alembic upgrade head
```

## Testing Python code locally

The fastest way to make sure that your Python code is actually working the way you intend
is to develop locally. First, make sure your SQL server is exposed at port 3306, by running

`kubectl port-forward service/mysql-external 3306:3306`.

Then use your debugger on the main.py file for fast apiyou've been developing.


## Build docker image

```

docker run -p 80:80 -v /Users/gkv/Startup/flighty/flighty-files:/code/flighty-files \
 gvashishtha/flighty:controlplane
```
