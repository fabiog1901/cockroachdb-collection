#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_invoice_info

short_description: List invoices for a given organization.

description:
  - List invoices for a given organization.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  invoice_id:
    description: ''
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
- name: list my bills
  fabiog1901.cockroachdb.cc_invoice_info:
    # invoice_id:  
    api_client:
      api_version: '2022-09-20'
'''

RETURN = '''
invoices:
  description:
    - Invoices are sorted by PeriodStart time.
    - '[ Invoice message represents the details and the total charges associated with one billing period, which starts at the beginning of the month and ends at the beginning of the next month.
      The message also includes details about each invoice item. ]'
  type: list
  returned: always
  elements: dict
  contains:
    balances:
      description: Balances are the amounts of currency left at the time of the invoice.
      type: list
      returned: always
      elements: dict
      contains:
        amount:
          description: Amount is the quantity of currency.
          type: int
          returned: always
        currency:
          description:
            - Currency is the set of currencies supported in CockroachCloud.
            - "Allowed: USD┃CRDB_CLOUD_CREDITS"
          type: str
          returned: always
    invoice_id:
      description: ""
      type: str
      returned: always
    invoice_items:
      description: InvoiceItems are sorted by the cluster name.
      type: list
      elements: dict
      returned: always
      contains:
        cluster:
          description: ""
          type: dict
          contains:
            account_id:
              description: ""
              type: str
              returned: always
            cloud_provider:
              description:
                - "GCP: The Google Cloud Platform cloud provider."
                - "AWS: The Amazon Web Services cloud provider."
                - "Allowed: GCP┃AWS"
              type: str
              returned: always
            cockroach_version:
              description: ""
              type: str
              returned: always
            config:
              description: config details for either dedicated or serverless.
              type: dict
              returned: always
              contains:
                dedicated:
                  description: present only if dedicated cluster
                  type: dict
                  contains:
                    disk_iops:
                      description: DiskIOPs is the number of disk I/O operations per second that are permitted on each node in the cluster. Zero indicates the cloud provider-specific default.
                      type: int
                      returned: always
                    machine_type:
                      description: MachineType is the machine type identifier within the given cloud provider, ex. m5.xlarge, n2-standard-4.
                      type: str
                      returned: always
                    num_virtual_cpus:
                      description: NumVirtualCPUs is the number of virtual CPUs per node in the cluster.
                      type: int
                      returned: always
                    storage_gib:
                      description: StorageGiB is the number of storage GiB per node in the cluster.
                      type: int
                      returned: always
                serverless:
                  description: present only if serverless cluster
                  type: dict
                  contains:
                    routing_id:
                      description: Used to build a connection string.
                      type: str
                      returned: always
                    spend_limit:
                      description: Spend limit in US cents.
                      type: int
                      returned: always
            created_at:
              description: date-time
              type: str
              returned: always
            creator_id:
              description: ""
              type: str
              returned: always
            deleted_at:
              description: date-time
              type: str
            id:
              description: ""
              type: str
              returned: always
            name:
              description: ""
              type: str
              returned: always
            operation_status:
              description:
                - "Allowed: CLUSTER_STATUS_UNSPECIFIED┃CRDB_MAJOR_UPGRADE_RUNNING┃CRDB_MAJOR_UPGRADE_FAILED┃CRDB_MAJOR_ROLLBACK_RUNNING┃CRDB_MAJOR_ROLLBACK_FAILED┃CRDB_PATCH_RUNNING┃CRDB_PATCH_FAILED┃CRDB_SCALE_RUNNING┃CRDB_SCALE_FAILED┃MAINTENANCE_RUNNING┃CRDB_INSTANCE_UPDATE_RUNNING┃CRDB_INSTANCE_UPDATE_FAILED┃CRDB_EDIT_CLUSTER_RUNNING┃CRDB_EDIT_CLUSTER_FAILED┃CRDB_CMEK_OPERATION_RUNNING┃CRDB_CMEK_OPERATION_FAILED┃TENANT_RESTORE_RUNNING┃TENANT_RESTORE_FAILED┃CRDB_LOG_EXPORT_OPERATION_RUNNING┃CRDB_LOG_EXPORT_OPERATION_FAILED"
              type: str
              returned: always
            plan:
              description:
                - "DEDICATED: A paid plan that offers dedicated hardware in any location."
                - "CUSTOM: A plan option that is used for clusters whose machine configs are not supported in self-service. All INVOICE clusters are under this plan option."
                - "SERVERLESS: A paid plan that runs on shared hardware and caps the users' maximum monthly spending to a user-specified (possibly 0) amount."
                - "Allowed: DEDICATED┃CUSTOM┃SERVERLESS"
              type: str
              returned: always
            regions:
              description: ""
              type: list
              returned: always
              contains:
                internal_dns:
                  description: InternalDns is the internal DNS name of the cluster within the cloud provider's network. It is used to connect to the cluster with PrivateLink or VPC peering.
                  type: str
                  returned: always
                name:
                  description: cluster name
                  type: str
                  returned: always
                node_count:
                  description: NodeCount will be 0 for serverless clusters.
                  type: int
                  returned: always
                sql_dns:
                  description: SqlDns is the DNS name of SQL interface of the cluster. It is used to connect to the cluster with IP allowlisting.
                  type: str
                  returned: always
                ui_dns:
                  description: UiDns is the DNS name used when connecting to the DB Console for the cluster.
                  type: str
                  returned: always
            state:
              description:
                - "LOCKED: An exclusive operation is being performed on this cluster. Other operations should not proceed if they did not set a cluster into the LOCKED state."
                - "Allowed: CREATING┃CREATED┃CREATION_FAILED┃DELETED┃LOCKED"
              type: str
              returned: always
            updated_at:
              description: ""
              type: str
              returned: always
        line_items:
          description: LineItems contain all the relevant line items from the Metronome invoice.
          type: list
          elements: dict
          contains:
            description:
              description: Description contains the details of the line item (i.e t3 micro).
              type: str
              returned: always
            quantity:
              description: Quantity is the number of the specific line items used.
              type: int
              returned: always
            quantity_unit:
              description:
                - Billing QuantityUnitType is the unit type for a quantity of billing line item.
                - "Allowed: HOURS┃REQUEST_UNITS"
              type: str
            total:
              description: ""
              type: dict
              contains:
                amount:
                  description: Amount is the quantity of currency.
                  type: int
                  returned: always
                currency:
                  description:
                    - Currency is the set of currencies supported in CockroachCloud.
                    - "Allowed: USD┃CRDB_CLOUD_CREDITS"
                  type: str
                  returned: always
            unit_cost:
              description: UnitCost is the cost per unit of line item.
              type: int
              returned: always
        totals:
          description: Totals is a list of the total amounts of line items per currency.
          type: list
          contains:
            amount:
              description: Amount is the quantity of currency.
              type: int
              returned: always
            currency:
              description:
                - Currency is the set of currencies supported in CockroachCloud.
                - "Allowed: USD┃CRDB_CLOUD_CREDITS"
              type: str
              returned: always
    period_end:
      description: PeriodEnd is the end of the billing period (exclusive).
      type: str
      returned: always
    period_start:
      description: PeriodStart is the start of the billing period (inclusive).
      type: str
      returned: always
    totals:
      description:
      type: list
      elements: dict
      contains:
        amount:
          description: Amount is the quantity of currency.
          type: int
          returned: always
        currency:
          description:
            - Currency is the set of currencies supported in CockroachCloud.
            - "Allowed: USD┃CRDB_CLOUD_CREDITS"
          type: str
          returned: always
'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.utils import AnsibleException, APIClient, ApiClientArgs

from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_invoices, cockroach_cloud_get_invoice

import json

class Client:

    def __init__(self, api_client_args: ApiClientArgs, invoice_id: str):

        # vars
        self.invoice_id = invoice_id

        # return vars
        self.out: str = ''
        self.changed: bool = False

        # cc client
        self.client = APIClient(api_client_args)

    def run(self):

        invoices: list = []

        if self.invoice_id:
            r = cockroach_cloud_get_invoice.sync_detailed(
                client=self.client,
                invoice_id=self.invoice_id
            )

        else:
            r = cockroach_cloud_list_invoices.sync_detailed(
                client=self.client
            )

        if r.status_code == 200:
            if self.invoice_id:
                invoices = [json.loads(r.content)]
            else:
                invoices = json.loads(r.content)['invoices']
        else:
            raise AnsibleException(r)

        return invoices, False


def main():
    module = AnsibleModule(argument_spec=dict(
        # api client arguments
        api_client=dict(default={},
            type='dict',
            cc_key=dict(type='str', no_log=True),
            api_version=dict(type='str'),

            scheme=dict(type='str'),
            host=dict(type='str'),
            port=dict(type='str'),
            path=dict(type='str'),
            verify_ssl=dict(type='bool'),
        ),

        # module specific arguments
        invoice_id=dict(type='str'),
    ),
        supports_check_mode=True,
    )

    try:
        out, changed = Client(
            ApiClientArgs(
                module.params['api_client'].get('cc_key', None),
                module.params['api_client'].get('api_version', None),
                module.params['api_client'].get('scheme', None),
                module.params['api_client'].get('host', None),
                module.params['api_client'].get('port', None),
                module.params['api_client'].get('path', None),
                module.params['api_client'].get('verify_ssl', None)
            ),
            module.params['invoice_id']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, invoices=out)


if __name__ == '__main__':
    main()
