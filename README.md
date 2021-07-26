# Ansible Collection - fabiog1901.cockroachdb

Ansible Roles and Playbooks to spin up CockroachDB clusters for demos and workshops.

## Setup

Install the **Ansible CockroachDB Collection** at playbook level

```bash
ansible-galaxy collection install git+https://github.com/fabiog1901/cockroachdb-ansible-collection.git -p collections/
```

Install the required Ansible Collections:

```bash
ansible-galaxy collection install -r collections/ansible_collections/fabiog1901/cockroachdb/requirements.yml 
```

Now, we copy the sample Playbooks in the **CockroachDB Collection** to our working directory

```bash
cp collections/ansible_collections/fabiog1901/cockroachdb/playbooks/site.yml .
cp collections/ansible_collections/fabiog1901/cockroachdb/playbooks/infrastructure.yml .
cp collections/ansible_collections/fabiog1901/cockroachdb/playbooks/platform.yml .  
cp collections/ansible_collections/fabiog1901/cockroachdb/playbooks/application.yml .     
mkdir config
cp collections/ansible_collections/fabiog1901/cockroachdb/config/sample.yml config   
```

Check file `application.yml` includes all required steps you want to run once the infrastructure and the platform (CockroachDB cluster, HAPRoxy, etc..) have been provisioned and deployed.

Check file `config/sample.yml` correctly represents the deployment definition of the desired infrastructure and platform.

Export the AWS keys and start the SSH Agent, adding the ssh key to the agent

```bash
# export cloud provider keys
export AWS_ACCESS_KEY_ID=AKIxxxxxxxx
export AWS_SECRET_ACCESS_KEY=xxxxxxxyyyyyzzzz

export GCP_SERVICE_ACCOUNT_FILE=sa-workshop.json
export GCP_AUTH_KIND=serviceaccount
export GCP_PROJECT=my-gcp-project

# start the ssh-agent and add the key
ssh-agent
ssh-add ~/Download/workshop.pem
```

You can now run the playbook

```bash
ansible-playbook site.yml -e @config/sample.yml  
```

## Dependancies

- You might need to install some pip packages, example `boto`, `botocore`, `boto3`...

## Kerberos Login

NORMAL USER  - VIA KERBEROS TICKET

```bash
# port 88 must be open on the krbserver
kinit fabio

# cockroach binary is also a sql client
cockroach sql --url "postgresql://fabio@<haproxy-hostname>:26257/defaultdb?sslmode=require"

# with explicit SPN
cockroach sql --url "postgresql://fabio@<haproxy-hostname>:26257/defaultdb?sslmode=require&krbsrvname=cockroach"
```

ROOT - VIA CERTS+KEY

```bash
sudo cockroach sql --certs-dir=/var/lib/cockroach/certs

# or using full DB URL

sudo cockroach sql --url "postgresql://root@`hostname -f`:26257/defaultdb?sslmode=require&sslrootcert=/var/lib/cockroach/certs/ca.crt&sslcert=/var/lib/cockroach/certs/client.root.crt&sslkey=/var/lib/cockroach/certs/client.root.key" 
```

Log in as `app1`, bypassing Kerberos

```bash
sudo cockroach sql --url "postgresql://app1@<haproxy-hostname>:26257/defaultdb?sslmode=require&sslrootcert=/var/lib/cockroach/certs/ca.crt&sslcert=/var/lib/cockroach/certs/client.app1.crt&sslkey=/var/lib/cockroach/certs/client.app1.key"

# or if you have 
sudo cockroach sql --url "postgresql://app1@<haproxy-hostname>:26257/defaultdb?sslmode=require&sslrootcert=ca.crt&sslcert=client.app1.crt&sslkey=client.app1.key" 
```
