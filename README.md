# CockroachDB Collection

The Collection groups together Ansible Modules, Roles and Playbooks for deploying a CockroachDB Self Hosted cluster.

A complete example on how to use this Collection is available in this [blog](https://dev.to/cockroachlabs/deploy-cockroachdb-on-the-public-cloud-using-ansible-1ek1).

## Setup

Install the Collection and its requirements

```bash
ansible-galaxy collection install git+https://github.com/fabiog1901/cockroachdb-collection.git

# install required pip packages for AWS, GCP, Azure
pip install boto3 boto botocore google-api-core google-auth google-cloud-compute googleapis-common-protos azure-common azure-core azure-identity azure-mgmt-compute azure-mgmt-core azure-mgmt-network azure-mgmt-resource
```

### Numa Nodes

At times you might have a VM that has more than 1 numa node.
In this situation, you'd want to run a CockroachDB process per numa node.

The default Ansible codebase does not have any built-in method to detect numa node counts from a VM.
I have raised [this issue](https://github.com/ansible/ansible/issues/83833) but no luck yet.

The workaround is simple and is explained in the issue itself, however, here is a simple breakdown.

1. Find your Ansible installation

    ```bash
    $ ansible --version
    ansible [core 2.17.5]
    config file = /etc/ansible/ansible.cfg
    configured module search path = ['/Users/fabio/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
    ansible python module location = /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/ansible # <--------- THIS
    ansible collection location = /Users/fabio/.ansible/collections:/usr/share/ansible/collections
    executable location = /Library/Frameworks/Python.framework/Versions/3.11/bin/ansible
    python version = 3.11.3 (v3.11.3:f3909b8bc8, Apr  4 2023, 20:12:10) [Clang 13.0.0 (clang-1300.0.29.30)] (/usr/local/bin/python3.11)
    jinja version = 3.1.4
    libyaml = True
    ```

2. Go to the `ansible python module location`
  
    ```bash
    cd /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/ansible
    ```

3. Open file `linux.py` using your favorite editor

    ```bash
    vi module_utils/facts/hardware/linux.py
    ```

4. Apply the 2 changes suggested in the issue I raised, make sure the indentation is correct

    Find method `get_cpu_facts()` and add the suggested line

    ```python
    def get_cpu_facts(self, collected_facts=None):
        cpu_facts = {}
        collected_facts = collected_facts or {}
        # [...]
        cpu_facts['processor'] = []
        cpu_facts['numa_nodes'] = self.get_numa_nodes()   # <------------- add this line
    ```

    At the same indentation level of `get_cpu_facts()`, implement the `get_numa_nodes()` method

    ```python
    def get_numa_nodes(self):
        lscpu_path = self.module.get_bin_path("lscpu")
        if not lscpu_path:
            self.module.warn("Cannot find command `lscpu`")
            return None
            
        rc, out, err = self.module.run_command(lscpu_path)
        if rc != 0:
            self.module.warn(f"error detecting the count of NUMA nodes, error message: {err}")
            return None

        for l in out.split("\n"):
            if l.startswith("NUMA node(s):"):
                return int(l.split(":")[1].strip())
                
        return None
    ```

Please note, the Collection expects you have this workarouond implemented, else many Tasks will fail.

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

In your `ansible.cfg` file, make sure you have below configured

```text
[defaults]
host_key_checking = False 
```

You can now run the playbook

```bash
ansible-playbook site.yaml -e @sample.yaml  
```

### Kerberos Login

If you have configured the cluster to use Kerberos, read further.

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
