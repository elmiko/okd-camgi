'''Interfaces into the must gather artifacts and data.'''
from collections import UserDict
from copy import deepcopy
import json
import logging
import os.path

import yaml


class Resource(UserDict):
    def name(self):
        return self.data.get('metadata', {}).get('name')

    def as_yaml(self):
        data = deepcopy(self.data)
        if data.get('metadata', {}).get('managedFields'):
            del data['metadata']['managedFields']
        return yaml.dump(data)

    
class MustGather:
    def __init__(self, path):
        self.path = path
        self._clusterautoscaler = None
        self._machines = None
        self._nodes = None

    @property
    def clusterautoscaler(self):
        if self._clusterautoscaler is None:
            ca = self.resource_or_none('default', 'clusterautoscalers', 'autoscaling.openshift.io')
            self._clusterautoscaler = ca
        return self._clusterautoscaler

    @property
    def machines(self):
        if self._machines is None:
            machines = self.resources('machines', 'machine.openshift.io', 'openshift-machine-api')
            self._machines = sorted(machines, key=lambda m: m.name())
        return self._machines

    @property
    def nodes(self):
        if self._nodes is None:
            nodes = self.resources('nodes', 'core')
            self._nodes = sorted(nodes, key=lambda n: n.name())
        return self._nodes

    @staticmethod
    def build_manifest_path(path, name, kind, group, namespace):
        pathlist = [path]
        if namespace is None:
            pathlist.append('cluster-scoped-resources')
        else:
            pathlist.append('namespaces')
            pathlist.append(namespace)
        if group is not None:
            pathlist.append(group)
        pathlist.append(kind)
        if name is not None:
            pathlist.append(f'{name}.yaml')
        man_path = os.path.join(*pathlist)
        return man_path

    def resource_or_none(self, name, kind, group=None, namespace=None):
        '''get a resource or none if not found'''
        man_path = self.build_manifest_path(self.path, name, kind, group, namespace)

        if not os.path.exists(man_path):
            return None
        logging.debug(f'loading {group}/{kind} yaml from {man_path}')
        with open(man_path) as man_file:
            resource = yaml.load(man_file.read(), Loader=yaml.FullLoader)
            return Resource(resource)

    def resources(self, kind, group=None, namespace=None):
        yaml_path = self.build_manifest_path(self.path, None, kind, group, namespace)
        resourcelist = []
        for f in os.listdir(yaml_path):
            if not f.endswith('.yaml'):
                continue
            resource = self.resource_or_none(f[:-5], kind, group, namespace)
            if resource is None:
                logging.error(f'Found yaml {f} did not produce a resource.')
            else:
                resourcelist.append(resource)
        return resourcelist
