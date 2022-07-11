## Build image

`docker build . -t gvashishtha/flighty:endpoint`

Push to docker hub

`docker push gvashishtha/flighty:endpoint`

## Deploy image

First deploy registry credential secret:

`kubectl create -f k8s-yaml/secret-regcred.yaml`

Then deploy endpoint service

`kubectl create -f k8s-yaml/endpoint-deployment.yaml`

Then expose on localhost:

`kubectl port-forward service/endpoint-external 8088:80`

## Troubleshooting

If you see `2022-07-10T21:26:22.165920Z 1 [ERROR] [MY-013090] [InnoDB] Unsupported redo log format (0). The redo log was created before MySQL 5.7.9 2022-07-10T21:26:22.165980Z 1 [ERROR] [MY-012930] [InnoDB] Plugin initialization aborted with er` when doing `kubectl logs then try changing the name of the hostpath. I think specifying `Reclaim` in the volume mount is causing a badly formatted log file from the previous pod to stick around.

## Get Python terminal to make DB requests

```
kubectl run -it --rm --image=gvashishtha/flighty:endpoints --restart=Never mysql-client -- /bin/bash
python3

```

```{python}
import json
import mysql.connector
db = mysql.connector.connect(host="127.0.0.1", port=3306, password="password", db="flighty")
c=db.cursor()
c.execute("DROP TABLE endpoints")
c.execute("""CREATE TABLE endpoints (`id` INT NOT NULL AUTO_INCREMENT, `name` VARCHAR(256) NOT NULL UNIQUE,
     PRIMARY KEY(`id`));""")
c.execute("INSERT INTO endpoints (name) VALUES (%s)",
  ("doc_rec",)
)
c.execute("SELECT * FROM endpoints")
c.fetchall()
c.execute("""CREATE TABLE handlers
  (`id` INT NOT NULL AUTO_INCREMENT, `name` VARCHAR(256) NOT NULL,
    `folder_path` VARCHAR(256) NOT NULL,
    `prod_traffic` INT NOT NULL DEFAULT 0,
    `shadow_traffic` INT NOT NULL DEFAULT 0,
    `endpoint_id` INT,
    PRIMARY KEY(`id`),
    UNIQUE KEY `endpoint_handler` (`endpoint_id`, `name`),
    FOREIGN KEY (`endpoint_id`) REFERENCES endpoints(`id`)
  );"""
)
c.execute("""DROP TABLE handlers""")
try:
  c.execute("""INSERT INTO handlers  (name, endpoint_id, folder_path, shadow_traffic) VALUES (%s, %s, %s, %s)""", ("rules", "1", "./rules", "5"))
except MySQLdb.IntegrityError as (num, value):
  print(f"no foreign key exists {num}")
c.execute("""SELECT name, endpoint_id, shadow_traffic, prod_traffic, folder_path FROM handlers""")
c.fetchall()
c.execute("""DROP TABLE artifacts""")
c.execute("""CREATE TABLE artifacts (`id` INT NOT NULL AUTO_INCREMENT, `name` VARCHAR(256) NOT NULL,
  `artifact_path` VARCHAR(256) NOT NULL, `version` INT NOT NULL,
  PRIMARY KEY(`id`),
  UNIQUE KEY `artifact_version` (`name`, `version`))"""
);

c.execute("INSERT INTO artifacts (name, artifact_path, version) VALUES (%s, %s, %s)",
  ("xgboost", "./xgboost", 2))
c.execute("SELECT * FROM artifacts")
c.fetchall()


c.execute("""DROP TABLE artifact_handler""")
c.execute("""CREATE TABLE artifact_handler (`handler_id` INT NOT NULL, `artifact_id` INT NOT NULL,
  PRIMARY KEY(`handler_id`, `artifact_id`),
  FOREIGN KEY (`handler_id`) REFERENCES handlers(`id`),
  FOREIGN KEY (`artifact_id`) REFERENCES artifacts(`id`)
)""");
c.execute("""INSERT INTO artifact_handler (handler_id, artifact_id) VALUES (%s, %s)""", ('5', '1') )
c.execute("""SELECT * FROM artifacts INNER JOIN artifact_handler ON id = artifact_handler.artifact_id""")

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
