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


class Pod(Resource):
    def __init__(self, resource, containerlogs):
        super().__init__(resource)
        self.containerlogs = containerlogs


class MustGather:
    def __init__(self, path):
        self.path = path
        self._clusterautoscalers = None
        self._machineautoscalers = None
        self._machines = None
        self._machinesets = None
        self._nodes = None
        self._pods = {}

    @property
    def clusterautoscalers(self):
        if self._clusterautoscalers is None:
            self._clusterautoscalers = self.resources('clusterautoscalers', 'autoscaling.openshift.io')
        return self._clusterautoscalers

    @property
    def machineautoscalers(self):
        if self._machineautoscalers is None:
            self._machineautoscalers = self.resources('machineautoscalers', 'autoscaling.openshift.io', 'openshift-machine-api')
        return self._machineautoscalers

    @property
    def machines(self):
        if self._machines is None:
            machines = self.resources('machines', 'machine.openshift.io', 'openshift-machine-api')
            self._machines = sorted(machines, key=lambda m: m.name())
        return self._machines

    @property
    def machinesets(self):
        if self._machinesets is None:
            machinesets = self.resources('machinesets', 'machine.openshift.io', 'openshift-machine-api')
            self._machinesets = sorted(machinesets, key=lambda m: m.name())
        return self._machinesets

    @property
    def nodes(self):
        if self._nodes is None:
            nodes = self.resources('nodes', 'core')
            self._nodes = sorted(nodes, key=lambda n: n.name())
        return self._nodes

    def pods(self, namespace):
        if self._pods.get(namespace) is None:
            pods = []
            pods_path = self.build_manifest_path(self.path, None, 'pods', None, namespace)
            # list all pods in the namespace
            for podname in os.listdir(pods_path):
                containerlogs = {}
                # list all files in the pod dir (containers and manifest)
                for filename in os.listdir(os.path.join(pods_path, podname)):
                    resource = None
                    if filename == f'{podname}.yaml':
                        logging.debug(f'loading {filename}')
                        with open(os.path.join(pods_path, podname, filename)) as man_file:
                            resource = yaml.load(man_file.read(), Loader=yaml.FullLoader)
                    # if this is a container, see if there are logs
                    elif os.path.exists(os.path.join(pods_path, podname, filename, filename, 'logs')):
                        for logfile in os.listdir(os.path.join(pods_path, podname, filename, filename, 'logs')):
                            logging.debug(f'found container logs for {filename}, opening {logfile}')
                            with open(os.path.join(pods_path, podname, filename, filename, 'logs', logfile)) as log:
                                containerlogs[logfile] = log.read()
                    else:
                        continue
                    if resource is not None:
                        pods.append(Pod(resource, containerlogs))
            self._pods[namespace] = pods
        return self._pods[namespace]

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
