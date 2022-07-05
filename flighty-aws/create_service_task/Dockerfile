# 
FROM python:3.9

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
  && unzip awscliv2.zip && ./aws/install -i /usr/local/aws-cli -b /usr/local/bin

# 
COPY ./ecs-run-service.json .

# Get config file
COPY ./config /root/aws/config

# 
COPY ./script.sh .

CMD ["./script.sh"]
