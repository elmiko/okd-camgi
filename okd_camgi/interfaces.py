'''Interfaces into the must gather artifacts and data.'''
from collections import UserDict
from copy import deepcopy
import json
import logging
import os.path

import yaml


mapi_namespace = 'openshift-machine-api'


class KubeMeta:
    def name(self):
        return self.data.get('metadata', {}).get('name')

class Yamlable:
    def as_yaml(self):
        data = deepcopy(self.data)
        if data.get('metadata', {}).get('managedFields'):
            del data['metadata']['managedFields']
        return yaml.dump(data)

    
class ClusterAutoscaler(UserDict, Yamlable, KubeMeta):
    def old__init__(self, mustgather):
        self.resource = mustgather.resource_or_none('autoscaling.openshift.io', 'clusterautoscalers', 'default')
        self.deployment = mustgather.deployment_or_none(mapi_namespace, 'cluster-autoscaler-default')
        self.pods = []
        for p in mustgather.podnames(mapi_namespace, 'cluster-autoscaler-default-'):
            pod = mustgather.pod_or_none(mapi_namespace, p)
            if pod:
                self.pods.append(pod)
        

class Deployment(UserDict, Yamlable, KubeMeta):
    pass


class Machine(UserDict, Yamlable, KubeMeta):
    pass


class Node(UserDict, Yamlable, KubeMeta):
    pass


class MustGather:
    def __init__(self, path):
        self.path = path
        self._clusterautoscaler = None
        self._machines = None
        self._nodes = None

    @property
    def clusterautoscaler(self):
        if self._clusterautoscaler is None:
            ca = self.resource_or_none('autoscaling.openshift.io', 'clusterautoscalers', 'default')
            self._clusterautoscaler = ClusterAutoscaler(ca)
        return self._clusterautoscaler

    @property
    def machines(self):
        if self._machines is None:
            machines = []
            path = os.path.join(self.path, 'namespaces', 'openshift-machine-api', 'machine.openshift.io', 'machines')
            for f in os.listdir(path):
                if f.endswith('.yaml'):
                    man_path = os.path.join(path, f)
                    logging.debug(f'loading machine yaml from {man_path}')
                    with open(man_path) as man_file:
                        machine = yaml.load(man_file.read(), Loader=yaml.FullLoader)
                        machines.append(Machine(machine))
                self._machines = sorted(machines, key=lambda m: m.name())
        return self._machines

    @property
    def nodes(self):
        if self._nodes is None:
            nodes = []
            path = os.path.join(self.path, 'cluster-scoped-resources', 'core', 'nodes')
            for f in os.listdir(path):
                if f.endswith('.yaml'):
                    man_path = os.path.join(path, f)
                    logging.debug(f'loading node yaml from {man_path}')
                    with open(man_path) as man_file:
                        node = yaml.load(man_file.read(), Loader=yaml.FullLoader)
                        nodes.append(Node(node))
                self._nodes = sorted(nodes, key=lambda n: n.name())
        return self._nodes

    def deployment_or_none(self, ns, name):
        man_path = os.path.join(self.path, 'namespaces', ns, 'apps', 'deployments.yaml')
        if not os.path.exists(man_path):
            return None
        logging.debug(f'loading deployment yaml from {man_path}')
        with open(man_path) as man_file:
            deployments = yaml.load(man_file.read(), Loader=yaml.FullLoader)
        requested = None
        for d in deployments.get('items', []):
            if d.get('metadata', {}).get('name') == name:
                requested = Deployment(d)
                break
        return requested

    def pod_or_none(self, ns, name):
        man_path = os.path.join(self.path, 'namespaces', ns, 'pods', name, f'{name}.yaml')
        if not os.path.exists(man_path):
            return None
        logging.debug(f'lodding pod yaml from {man_path}')
        with open(man_path) as man_file:
            pod = yaml.load(man_file.read(), Loader=yaml.FullLoader)
            return Pod(pod)

    def podnames(self, ns, name_prefix):
        '''get a list of pods with a given name prefix'''
        podnames = []
        for f in os.listdir(os.path.join(self.path, 'namespaces', ns, 'pods')):
            if f.startswith(name_prefix):
                podnames.append(f)
        return podnames

    def resource_or_none(self, group, kind, name, ns=None):
    # def cluster_scoped_resource_or_none(self, group, kind, name):
        '''get a resource or none if not found'''
        if ns is None:
            man_path = os.path.join(self.path, 'cluster-scoped-resources', group, kind, f'{name}.yaml')
        else:
            man_path = os.path.join(self.path, 'namespaces', ns, group, kind, f'{name}.yaml')
        if not os.path.exists(man_path):
            return None
        logging.debug(f'loading {group}/{kind} yaml from {man_path}')
        with open(man_path) as man_file:
            resource = yaml.load(man_file.read(), Loader=yaml.FullLoader)
            return Resource(resource)


class Pod(UserDict, Yamlable, KubeMeta):
    pass


class Resource(UserDict, Yamlable, KubeMeta):
    pass
