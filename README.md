# CockroachDB Collection

Ansible Roles and Playbooks to spin up secure, kerberized, multi-region CockroachDB clusters for demos and workshops.

A complete example on how to use this Collection is available in this [blog](https://dev.to/cockroachlabs/deploy-cockroachdb-on-the-public-cloud-using-ansible-1ek1).

## Setup

Install the **CockroachDB Collection** at playbook level

```bash
ansible-galaxy collection install git+https://github.com/fabiog1901/cockroachdb-collection.git -p collections/
```

Install the required Ansible Collections:

```bash
ansible-galaxy collection install -r collections/ansible_collections/fabiog1901/cockroachdb/requirements.yml 

# install required pip packages for AWS, GCP, Azure
pip install boto3 boto botocore google-api-core google-auth google-cloud-compute googleapis-common-protos azure-common azure-core azure-identity azure-mgmt-compute azure-mgmt-core azure-mgmt-network azure-mgmt-resource
```

Now, we copy the sample Playbooks in the **CockroachDB Collection** to our working directory

```bash
cp collections/ansible_collections/fabiog1901/cockroachdb/playbooks/* .  
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

export AZURE_SUBSCRIPTION_ID=xxxxxx-yyyyy-zzzzzz
export AZURE_AD_USER=xxxxyyyyzzzzz
export AZURE_PASSWORD='xxxxyyyyzzzz'

# start the ssh-agent and add the key
ssh-agent
ssh-add ~/Download/workshop.pem
```

You can now run the playbook

```bash
ansible-playbook site.yml -e @config/sample.yml  
```

## HOW-TO's

### Kerberos Login

Below a reminder on how to login via Kerberos ticket

```bash
# port 88 must be open on the krbserver
# here, 'fabio' is a valid principal in the KDC and a valid user in the database
kinit fabio

# verify the ticket is valid
klist

# cockroach binary is also a sql client
cockroach sql --url "postgresql://fabio@<haproxy-hostname>:26257/defaultdb?sslmode=require"

# with explicit SPN
cockroach sql --url "postgresql://fabio@<haproxy-hostname>:26257/defaultdb?sslmode=require&krbsrvname=cockroach"
```

### Certificate + Key login (root login)

```bash
sudo cockroach sql --certs-dir=/var/lib/cockroach/certs

# or using full DB URL
sudo cockroach sql --url "postgresql://root@<haproxy-hostname>:26257/defaultdb?sslmode=require&sslrootcert=/var/lib/cockroach/certs/ca.crt&sslcert=/var/lib/cockroach/certs/client.root.crt&sslkey=/var/lib/cockroach/certs/client.root.key" 
```

Log in as `app`, bypassing Kerberos, assuming you have created cert+key for this user and the user is a databse user.

```bash
sudo cockroach sql --url "postgresql://app@<haproxy-hostname>:26257/defaultdb?sslmode=require&sslrootcert=ca.crt&sslcert=client.app.crt&sslkey=client.app.key" 
```
