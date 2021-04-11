'''Interfaces into the must gather artifacts and data.'''
from collections import UserDict
from copy import deepcopy
import json
import os.path

import yaml


class Deployment(UserDict):
    def as_yaml(self):
        data = deepcopy(self.data)
        if data.get('metadata', {}).get('managedFields'):
            del data['metadata']['managedFields']
        return yaml.dump(data)

    def as_json(self):
        return json.dumps(self.data)


class MustGather:
    def __init__(self, path):
        self.path = path
        self._clusterautoscaler = None

    def deployment_or_none(self, ns, name):
        man_path = os.path.join(self.path, 'namespaces', ns, 'apps', 'deployments.yaml')
        if not os.path.exists(man_path):
            return None
        deployments = yaml.load(open(man_path).read())
        requested = None
        for d in deployments.get('items', []):
            if d.get('metadata', {}).get('name') == name:
                requested = Deployment(d)
                break
        return requested

    @property
    def clusterautoscaler(self):
        if self._clusterautoscaler is None:
            self._clusterautoscaler = ClusterAutoscaler(self)
        return self._clusterautoscaler


class ClusterAutoscaler:
    def __init__(self, mustgather):
        self.deployment = mustgather.deployment_or_none('openshift-machine-api', 'cluster-autoscaler-default')
