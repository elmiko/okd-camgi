'''Interfaces into the must gather artifacts and data.'''
from collections import UserDict
from copy import deepcopy
import json
import os.path

import yaml


mapi_namespace = 'openshift-machine-api'


class Yamlable:
    def as_yaml(self):
        data = deepcopy(self.data)
        if data.get('metadata', {}).get('managedFields'):
            del data['metadata']['managedFields']
        return yaml.dump(data)

    
class ClusterAutoscaler:
    def __init__(self, mustgather):
        self.deployment = mustgather.deployment_or_none(mapi_namespace, 'cluster-autoscaler-default')
        self.pods = []
        for p in mustgather.podnames(mapi_namespace, 'cluster-autoscaler-default-'):
            pod = mustgather.pod_or_none(mapi_namespace, p)
            if pod:
                self.pods.append(pod)
        

class Deployment(UserDict, Yamlable):
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
        deployments = yaml.load(open(man_path).read(), Loader=yaml.FullLoader)
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
        pod = yaml.load(open(man_path).read(), Loader=yaml.FullLoader)
        return pod

    def podnames(self, ns, name_prefix):
        '''get a list of pods with a given name prefix'''
        podnames = []
        for f in os.listdir(os.path.join(self.path, 'namespaces', ns, 'pods')):
            if f.startswith(name_prefix):
                podnames.append(f)
        return podnames

    @property
    def clusterautoscaler(self):
        if self._clusterautoscaler is None:
            self._clusterautoscaler = ClusterAutoscaler(self)
        return self._clusterautoscaler


class Pod(UserDict, Yamlable):
    pass
