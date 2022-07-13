## Make database migration

Do this after changing the database model in database.py

```
alembic revision --autogenerate -m "<commit name>"
alembic upgrade head
```

## Build docker image

```

docker run -p 80:80 -v /Users/gkv/Startup/flighty/flighty-files:/code/flighty-files \
 gvashishtha/flighty:controlplane
```
