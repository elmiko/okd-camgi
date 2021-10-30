'''Context classes are the adaptors between data interfaces and templates.'''
import base64
from collections import UserDict, UserList
import logging
import os.path

from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from kubernetes.utils.quantity import parse_quantity
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter

from okd_camgi import interfaces


# Base Classes
class AccordionDataContext(UserDict):
    def __init__(self, name, iterable):
        initial = {
            'cssid': name.lower(),
            'name': name,
            'iterable': iterable,
        }
        super().__init__(initial)


class HighlightedYamlContext(UserDict):
    def __init__(self, initial):
        super().__init__(initial)
        self.highlight()

    def highlight(self):
        if self.data.get('yaml_highlight_content'):
            del self.data['yaml_highlight_content']
        content = highlight(interfaces.Resource(self.data).as_yaml(), YamlLexer(), HtmlFormatter())
        self.data['yaml_highlight_content'] = content


class ResourceContext(HighlightedYamlContext):
    @property
    def statusclasses(self):
        ''


class NavListContext(UserDict):
    def __init__(self, cssid, anchor_name, content):
        initial = {
            'id': cssid,
            'anchor_name': anchor_name,
            'content': content,
        }
        super().__init__(initial)


# Resource Specific Classes
class CSRContext(ResourceContext):
    def __init__(self, initial=None):
        super().__init__(initial)

        updated = False
        if self.data['spec'].get('request'):
            self.data['spec']['request'] = CSRContext.decodeCSR(self.data['spec']['request'])
            updated = True

        if self.data['status'].get('certificate'):
            self.data['status']['certificate'] = '<omitted>'
            updated = True

        if updated:
            self.highlight()

    @property
    def pending(self):
        return self.data.get('status', {}) == {}

    @property
    def denied(self):
        try:
            for cond in self.data['status']['conditions']:
                if cond['type'] == 'Denied':
                    return True
        except:
            pass
        return False

    @property
    def failed(self):
        try:
            for cond in self.data['status']['conditions']:
                if cond['type'] == 'Failed':
                    return True
        except:
            pass
        return False

    @property
    def statusclasses(self):
        if self.pending:
            return 'bg-warning text-white'
        if self.failed or self.denied:
            return 'bg-danger text-white'

    @staticmethod
    def decodeCSR(data):
        try:
            csr = x509.load_pem_x509_csr(base64.b64decode(data))
            extensions = {}
            try:
                if san := csr.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value:
                    extensions['subjectAlternativeName'] = {
                        'dnsNames': [],
                        'ipAddresses': [],
                    }
                    for d in san.get_values_for_type(x509.DNSName):
                        extensions['subjectAlternativeName']['dnsNames'].append(d)
                    for i in san.get_values_for_type(x509.IPAddress):
                        extensions['subjectAlternativeName']['ipAddresses'].append(i.exploded)
            except x509.ExtensionNotFound:
                if extensions.get('subjectAlternativeName'):
                    del extensions['subjectAlternativeName']

            request = {
                'subject': csr.subject.rfc4514_string(),
                'extensions': extensions,
            }
            return request
        except Exception as ex:
            print(ex)
            return data


class CSRsContext(UserList):
    @property
    def pending(self):
        return [csr for csr in self.data if csr.pending]

    @property
    def denied_or_failed(self):
        return [csr for csr in self.data if csr.denied or csr.failed]


class MachineContext(ResourceContext):
    @property
    def statusclasses(self):
        classes = []

        if self.data.get('status', {}).get('phase') != 'Running':
            classes.append('bg-danger text-white')

        return ' '.join(classes)


class MachinesContext(UserList):
    @property
    def notrunning(self):
        ret = list(filter(lambda m: m.get('status', {}).get('phase') != 'Running', self.data))
        return ret


class MachineSetContext(HighlightedYamlContext):
    @property
    def autoscaler_min(self):
        '''return autoscaler min or none'''
        return self.data.get('metadata', {}).get('annotations', {}).get('machine.openshift.io/cluster-api-autoscaler-node-group-min-size')

    @property
    def autoscaler_max(self):
        '''return autoscaler max or none'''
        return self.data.get('metadata', {}).get('annotations', {}).get('machine.openshift.io/cluster-api-autoscaler-node-group-max-size')


class NodeContext(ResourceContext):
    @property
    def statusclasses(self):
        classes = []

        for condition in self.data.get('status', {}).get('conditions', []):
            if condition.get('type') == 'Ready' and condition.get('status') == 'False':
                classes.append('bg-danger text-white')

        return ' '.join(classes)

    @property
    def cpu_allocatable(self):
        try:
            return parse_quantity(self.data['status']['allocatable']['cpu'])
        except Exception as ex:
            logging.error(f'error parsing node cpu {str(ex)}')
        return 0

    @property
    def cpu_capacity(self):
        try:
            return parse_quantity(self.data['status']['capacity']['cpu'])
        except Exception as ex:
            logging.error(f'error parsing node cpu {str(ex)}')
        return 0

    @property
    def memory_allocatable(self):
        try:
            return parse_quantity(self.data['status']['allocatable']['memory'])
        except Exception as ex:
            logging.error(f'error parsing node memory {str(ex)}')
        return 0

    @property
    def memory_capacity(self):
        try:
            return parse_quantity(self.data['status']['capacity']['memory'])
        except Exception as ex:
            logging.error(f'error parsing node memory {str(ex)}')
        return 0

    @property
    def nvidiagpu_allocatable(self):
        try:
            return parse_quantity(self.data['status']['allocatable']['nvidia.com/gpu'])
        except Exception as ex:
            logging.info(f'no nvidia.com/gpu found for {self["metadata"]["name"]}')
        return 0

    @property
    def nvidiagpu_capacity(self):
        try:
            return parse_quantity(self.data['status']['capacity']['nvidia.com/gpu'])
        except Exception as ex:
            logging.info(f'no nvidia.com/gpu found for {self["metadata"]["name"]}')
        return 0


class NodesContext(UserList):
    def __init__(self, initial=None):
        super().__init__(initial)

        self.cpu_allocatable = 0
        self.cpu_capacity = 0
        self.memory_allocatable = 0
        self.memory_capacity = 0
        self.nvidiagpu_allocatable = 0
        self.nvidiagpu_capacity = 0
        for node in self.data:
            self.cpu_allocatable += node.cpu_allocatable
            self.cpu_capacity += node.cpu_capacity
            self.memory_allocatable += node.memory_allocatable
            self.memory_capacity += node.memory_capacity
            self.nvidiagpu_allocatable += node.nvidiagpu_allocatable
            self.nvidiagpu_capacity += node.nvidiagpu_capacity
        # convert to gigabytes
        self.memory_allocatable /= pow(10, 9)
        self.memory_capacity /= pow(10, 9)

    @property
    def notready(self):
        notready = []
        for node in self.data:
            for condition in node.get('status', {}).get('conditions', []):
                if condition.get('type') == 'Ready' and condition.get('status') == 'False':
                    notready.append(node)
        return notready


class PodContext(HighlightedYamlContext):
    def __init__(self, pod):
        super().__init__(pod)
        self.data['containerlogs'] = [{'name': k, 'logs': v} for k, v in pod.containerlogs.items()]


# Main Index
class IndexContext(UserDict):
    '''Context for the index.html template'''
    def __init__(self, mustgather):
        mapipods = sorted([PodContext(pod) for pod in mustgather.pods('openshift-machine-api')], key=lambda p: p['metadata']['name'])
        mcopods = sorted([PodContext(pod) for pod in mustgather.pods('openshift-machine-config-operator')], key=lambda p: p['metadata']['name'])
        machineautoscalers = [ResourceContext(machineautoscaler) for machineautoscaler in mustgather.machineautoscalers]
        clusterautoscalers = [ResourceContext(clusterautoscaler) for clusterautoscaler in mustgather.clusterautoscalers]
        machines = MachinesContext([MachineContext(machine) for machine in mustgather.machines])
        nodes = NodesContext([NodeContext(node) for node in mustgather.nodes])
        csrs = CSRsContext(
                [CSRContext(csr) for csr in mustgather.csrs])
        cluster_resources = {
            'cpu': {
                'allocatable': nodes.cpu_allocatable,
                'capacity': nodes.cpu_capacity,
            },
            'memory': {
                'allocatable': nodes.memory_allocatable,
                'capacity': nodes.memory_capacity,
            },
            'nvidiagpu': {
                'allocatable': nodes.nvidiagpu_allocatable,
                'capacity': nodes.nvidiagpu_capacity,
            },
        }

        initial = {
            'accordiondata': [
                AccordionDataContext('ClusterAutoscalers', clusterautoscalers),
                AccordionDataContext('MachineAutoscalers', machineautoscalers),
                AccordionDataContext('Machines', machines),
                AccordionDataContext('Nodes', nodes),
                AccordionDataContext('CSRs', csrs),
            ],
            'basename': self.basename(mustgather.path),
            'clusterautoscalers': clusterautoscalers,
            'cluster_resources': cluster_resources,
            'clusterversion': mustgather.clusterversion,
            'csrs': csrs,
            'highlight_css': HtmlFormatter().get_style_defs('.highlight'),
            'machineautoscalers': machineautoscalers,
            'machines': machines,
            'machinesets': [MachineSetContext(machineset) for machineset in mustgather.machinesets],
            'machinesets_participating': [ msc for msc in [MachineSetContext(machineset) for machineset in mustgather.machinesets] if msc.autoscaler_min],
            'mapipods': mapipods,
            'mcopods': mcopods,
            'nodes': nodes,
        }
        super().__init__(initial)

    @staticmethod
    def basename(path):
        if path.endswith('/'):
            path = path[:-1]
        return os.path.basename(path)

    @staticmethod
    def cluster_autoscaler_deployment(mustgather):
        deployment = mustgather.clusterautoscaler.deployment
        if deployment is None:
            return 'Deployment not found, check <must-gather path>/namespaces/openshift-machine-api/apps/deployments.yaml'
        content = highlight(deployment.as_yaml(), YamlLexer(), HtmlFormatter())
        anchor = deployment.name()
        return NavListContext(cssid='cluster-autoscaler-deployment', anchor_name=anchor, content=content)

    @staticmethod
    def cluster_autoscaler_pods(mustgather):
        ret = []
        for pod in  mustgather.clusterautoscaler.pods:
            name = pod.name()
            content = highlight(pod.as_yaml(), YamlLexer(), HtmlFormatter())
            ret.append(NavListContext(cssid=name, anchor_name=name, content=content))
        return ret

