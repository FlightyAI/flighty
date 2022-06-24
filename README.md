# flighty

## Create service code

Assume kaniko was already used to create an image. Now how do we run it?

First, upload the task definition:

```
aws ecs register-task-definition \
  --cli-input-json file://ecs-service-definition.json
```

Then run it:

```
aws ecs create-service \
    --task-definition flighty-demo:1 \
    --cli-input-json file://ecs-run-service.json
```

Get logs:

```
### Get logs

```

aws logs get-log-events \
 --log-group-name /ecs/Flighty \
 --log-stream-name $(aws logs describe-log-streams \
 --log-group-name /ecs/Flighty \
 --query 'logStreams[0].logStreamName' --output text)

```

```

## Kaniko code

### Build Kaniko image

```
export KANIKO_DEMO_VPC=vpc-04a2039eaa0d34906
export KANIKO_DEMO_SUBNET=subnet-0f9e7a9c7c86e1ecc

# create Kaniko repo
export KANIKO_DEMO_REPO=701906161514.dkr.ecr.us-west-1.amazonaws.com/flighty-repository
export KANIKO_DEMO_IMAGE="${KANIKO_DEMO_REPO}:latest"

export KANIKO_BUILDER_REPO=$(aws ecr create-repository \
 --repository-name kaniko-builder \
 --query 'repository.repositoryUri' --output text)

export KANIKO_BUILDER_IMAGE="${KANIKO_BUILDER_REPO}:executor"
docker build --tag ${KANIKO_BUILDER_REPO}:executor .

aws ecr get-login-password | docker login \
   --username AWS \
   --password-stdin \
   $KANIKO_BUILDER_REPO

docker push ${KANIKO_BUILDER_REPO}:executor

```

### Create task definition

```
# Create an Amazon CloudWatch Log Group to Store Log Output
aws logs create-log-group \
  --log-group-name kaniko-builder

# Export the AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity \
  --query 'Account' \
  --output text)

# Create the ECS Task Definition.
cat << EOF > ecs-task-definition.json
{
    "family": "kaniko-demo",
    "taskRoleArn": "$ECS_TASK_ROLE",
    "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
    "networkMode": "awsvpc",
    "containerDefinitions": [
        {
            "name": "kaniko",
            "image": "$KANIKO_BUILDER_IMAGE",
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "kaniko-builder",
                    "awslogs-region": "$(aws configure get region)",
                    "awslogs-stream-prefix": "kaniko"
                }
            },
            "command": [
                "--context", "git://github.com/FlightyAI/docker-test.git",
                "--dockerfile", "./app/Dockerfile",
                "--destination", "$KANIKO_DEMO_IMAGE",
                "--force"
            ]
        }],
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024"
}
EOF

aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json
```

### Run Kaniko as a single task

```
# Create a security group for ECS task
KANIKO_SECURITY_GROUP="sg-019453ec44d351a52"

# Start the ECS Task
cat << EOF > ecs-run-task.json
{
    "cluster": "DevCluster",
    "count": 1,
    "launchType": "FARGATE",
    "networkConfiguration": {
        "awsvpcConfiguration": {
            "subnets": ["$KANIKO_DEMO_SUBNET"],
            "securityGroups": ["$KANIKO_SECURITY_GROUP"],
            "assignPublicIp": "ENABLED"
        }
    },
    "platformVersion": "1.4.0"
}
EOF

# Run the ECS Task using the "Run Task" command
aws ecs run-task \
    --task-definition kaniko-demo:1 \
    --cli-input-json file://ecs-run-task.json

```

### Get logs

```
aws logs get-log-events \
  --log-group-name kaniko-builder \
  --log-stream-name $(aws logs describe-log-streams \
     --log-group-name kaniko-builder \
     --query 'logStreams[0].logStreamName' --output text)

```
