# Build image

`docker build . -t gvashishtha/flighty:endpoints`

## NOTE

If you see `2022-07-10T21:26:22.165920Z 1 [ERROR] [MY-013090] [InnoDB] Unsupported redo log format (0). The redo log was created before MySQL 5.7.9 2022-07-10T21:26:22.165980Z 1 [ERROR] [MY-012930] [InnoDB] Plugin initialization aborted with er` when doing `kubectl logs then try changing the name of the hostpath. I think specifying `Reclaim` in the volume mount is causing a badly formatted log file from the previous pod to stick around.

## Get Python terminal to make DB requests

```
kubectl run -it --rm --image=gvashishtha/flighty:endpoints --restart=Never mysql-client -- /bin/bash
python3

```

```{python}
import json
db = MySQLdb.connect(host="mysql.default.svc.cluster.local", port=3306, password="password")
c=db.cursor()
c.execute("""CREATE DATABASE flighty""")
c.execute("""USE flighty""")
c.execute("""CREATE TABLE endpoints (`id` INT NOT NULL AUTO_INCREMENT, `name` VARCHAR(256) NOT NULL UNIQUE, `models` JSON,
     PRIMARY KEY(`id`))""")
c.execute("""INSERT INTO endpoints (name, models) VALUES (%s, %s)""", ("doc_rec", json.dumps({'rules': {"prod": 100, "shadow": 0}})))
c.execute("""UPDATE endpoints (models) VALUES (%s) WHERE name=='doc_rec'""",
  (json.dumps(
    {'rules': {"prod": 100, "shadow": 0}}
    )
  )
)
c.execute("""INSERT INTO endpoints (name, models) VALUES (%s, %s)""", ("doc_rec1", json.dumps({'xgboost': {"prod": 100, "shadow": 0}})))
c.execute("""SELECT * FROM endpoints WHERE models[doc_rec][prod]==100""")
c.fetchone()
```
