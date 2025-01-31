# CockroachDB Collection

The Collection groups together Ansible Modules, Roles and Playbooks for deploying a CockroachDB Self Hosted cluster.

## CockroachDB Self-Hosted

The Collection includes Playbook `/playbooks/site.yaml` for spinning up a secure, multi-region CockroachDB cluster.

A complete example on how to use this Collection is available in this [blog](https://dev.to/cockroachlabs/deploy-cockroachdb-on-the-public-cloud-using-ansible-1ek1).

### Setup

Install the Collection and its requirements

```bash
ansible-galaxy collection install git+https://github.com/fabiog1901/cockroachdb-collection.git

# install required pip packages for AWS, GCP, Azure
pip install boto3 boto botocore google-api-core google-auth google-cloud-compute googleapis-common-protos azure-common azure-core azure-identity azure-mgmt-compute azure-mgmt-core azure-mgmt-network azure-mgmt-resource
```

Now, we copy the sample Playbook and deployment files to our working directory

- [playbooks/site.yaml](playbooks/site.yaml)
- [deployments/sample.yaml](deployments/sample.yaml)

File `sample.yml` represents the deployment definition of the desired infrastructure and platform.
Make sure data in the `region` variable correctly represents YOUR cloud environment.

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
ansible-playbook site.yaml -e @sample.yaml  
```

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

Log in as `app`, bypassing Kerberos, assuming you have created cert+key for this user and the user is a database user.

```bash
sudo cockroach sql --url "postgresql://app@<haproxy-hostname>:26257/defaultdb?sslmode=require&sslrootcert=ca.crt&sslcert=client.app.crt&sslkey=client.app.key" 
```
