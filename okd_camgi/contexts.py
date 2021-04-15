'''Context classes are the adaptors between data interfaces and templates.'''
from collections import UserDict
import os.path

from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter


class DataListEntry(UserDict):
    def __init__(self, id, anchor_name, content):
        initial = {
            'id': id,
            'anchor-name': anchor_name,
            'content': content,
        }
        super().__init__(initial)


class IndexContext(UserDict):
    '''Context for the index.html template'''
    def __init__(self, mustgather):
        initial = {
            'basename': self.basename(mustgather.path),
            'datalist': [
                DataListEntry(id='cluster-autoscaler-deployment', anchor_name='Deployment', content=f'{self.cluster_autoscaler_deployment(mustgather)}'),
            ],
            'highlight_css': HtmlFormatter().get_style_defs('.highlight')
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
        return highlight(deployment.as_yaml(), YamlLexer(), HtmlFormatter())
