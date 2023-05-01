#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_database

short_description: Manage databases for a cluster.

description:
  - Create, edit, delete a database.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  state:
    description: "Allowed values: present, absent."
    default: present
    type: str
  cluster_id:
    description: The UUID or the name of the cluster you want to get information for.
    type: str
    required: True
  name:
    description: The database name
    type: str
    required: True
  rename_to:
    description: The new database name
    type: str
  
  api_client:
    description:
      - Define details for the API client
    suboptions:
      cc_key:
        description:
          - The Service Account API key
          - This value is log redacted
          - By default it reads the env variable 'CC_KEY'
        default: 
        type: str

      api_version:
        description:
          - The API version to use
        default: latest
        type: str
      
      scheme:
        description:
          - http or https
        default: https
        type: str
        choices:
          - http
          - https
      host:
        description:
          - the hostname of the API server
        default: cockroachlabs.cloud
        type: str
      
      port:
        description:
          - the port number, as a string, for the API server
        default: '443'
        type: str
      
      path:
        description:
          - the path to the API endpoint
        default: ''
        type: str
      
      verify_ssl:
        description:
          - whether the client should verify the server cert
        default: true
        type: bool
        
requirements:
  - cockroachdb-cloud-client
'''

EXAMPLES = '''
- name: create a database
  fabiog1901.cockroachdb.cc_database:
    state: present
    cluster_id: dev_cluster
    name: dev_db
    api_client:
      api_version: '2022-09-20'
    register: out
'''

RETURN = '''
database:
  description: ''
  type: dict
  elements: dict
  contains:
    name:
      description: ''
      type: str
    table_count:
      description: ''
      type: str
'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.utils import get_cluster_id_from_cluster_name, AnsibleException, APIClient

from cockroachdb_cloud_client.models.cockroach_cloud_edit_database_update_database_request import CockroachCloudEditDatabaseUpdateDatabaseRequest as editdbreq
from cockroachdb_cloud_client.models.cockroach_cloud_create_database_create_database_request import CockroachCloudCreateDatabaseCreateDatabaseRequest as createdbreq
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_databases, cockroach_cloud_edit_database, cockroach_cloud_delete_database, cockroach_cloud_create_database
from cockroachdb_cloud_client.models.database import Database

import json

class Client:

    def __init__(self,
                 state: str, cluster_id: str, name: str, rename_to: str):

        # cc client
        self.client = APIClient()

        # vars
        self.state = state
        self.name = name
        self.cluster_id = get_cluster_id_from_cluster_name(self.client, cluster_id)
        self.rename_to = rename_to

        # return vars
        self.out: str = ''
        self.changed: bool = False

    def run(self):

        database = {}

        def get_database(name):

            r = cockroach_cloud_list_databases.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                for x in r.parsed.databases:
                    if x.name == name:
                        return x
                return None

            else:
                raise AnsibleException(r)

        database = get_database(self.name)

        if self.state == 'present':

            if database:
                if self.rename_to:

                    c = editdbreq(name=self.name, new_name=self.rename_to)

                    r = cockroach_cloud_edit_database.sync_detailed(
                        client=self.client,
                        cluster_id=self.cluster_id,
                        json_body=c
                    )

                    if r.status_code == 200:
                        database = json.loads(r.content)
                    else:
                        raise AnsibleException(r)

                    return database, True
                else:
                    return database.to_dict(), False

            else:
                if self.rename_to:
                    raise Exception(
                        {'content': f'cannot rename database {self.name} as it does not exists.'})
                else:
                    c = createdbreq(self.name)

                    r = cockroach_cloud_create_database.sync_detailed(
                        client=self.client,
                        cluster_id=self.cluster_id,
                        json_body=c)

                    if r.status_code == 200:
                        database = json.loads(r.content)
                    else:
                        raise AnsibleException(r)

                    return database, True

        else:  # state=absent

            if database:

                r = cockroach_cloud_delete_database.sync_detailed(
                    client=self.client,
                    cluster_id=self.cluster_id,
                    name=self.name)

                if r.status_code == 200:
                    database = json.loads(r.content)

                else:
                    raise AnsibleException(r)

                return database, True
            else:
                return database, False


def main():
    module = AnsibleModule(argument_spec=dict(
        # api client arguments
        api_client=dict(
            default={},
            type='dict',
            options=dict(
                cc_key=dict(type='str', no_log=True),
                api_version=dict(type='str'),
                scheme=dict(type='str'),
                host=dict(type='str'),
                port=dict(type='str'),
                path=dict(type='str'),
                verify_ssl=dict(type='bool'),
            )
        ),
        # module specific arguments
        state=dict(type='str', choices=[
                   'present', 'absent'], default='present'),
        cluster_id=dict(type='str', required=True),
        name=dict(type='str', required=True),
        rename_to=dict(type='str', required=False)
    ),
        supports_check_mode=False,
    )

    try:
        out, changed = Client(
            module.params['state'],
            module.params['cluster_id'],
            module.params['name'],
            module.params['rename_to']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, database=out)


if __name__ == '__main__':
    main()
