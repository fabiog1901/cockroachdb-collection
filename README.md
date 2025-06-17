# CockroachDB Collection

The Collection groups together Ansible Playbooks for deploying a CockroachDB Self Hosted cluster.

## Create a Cluster

The playbook assumes you have CA certificate files in `/var/lib/ca/`:

```bash
$ ll /var/lib/ca
total 24
-rw-r--r--  1 fabio  staff   958B Jun  4 09:19 ca.cnf
-rw-r--r--  1 fabio  staff   1.1K Jun  4 09:23 ca.crt
-r--------  1 fabio  staff   1.7K Jun  4 09:22 ca.key
```

The `create_cluster.yaml` playbook uses [`cloud_instance`](https://github.com/fabiog1901/cloud_instance) to provision VMs on the public cloud.

Configuration and setup of `cloud_instance` is not fully documented, so to create a cluster
you can run the below command, passing your own `.ini` file and skipping the `infra` tagged `tasks`.

```bash
ansible-playbook playbooks/create_cluster.yaml -i inventories/sample.ini --skip-tags infra -e @deployments/sample.yaml
```
