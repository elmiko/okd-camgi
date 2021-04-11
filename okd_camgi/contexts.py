'''Context classes are the adaptors between data interfaces and templates.'''
from collections import UserDict
import os.path


class IndexContext(UserDict):
    '''Context for the index.html template'''
    def __init__(self, mustgather):
        initial = {
            'basename': self.basename(mustgather.path),
            'datalist': [
                { 'id': 'cluster-autoscaler-deployment', 'content': f'{self.cluster_autoscaler_deployment(mustgather)}' },
            ],
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
        return deployment.as_yaml()
