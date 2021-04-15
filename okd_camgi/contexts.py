'''Context classes are the adaptors between data interfaces and templates.'''
from collections import UserDict
import os.path

from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter


class NavListEntry(UserDict):
    def __init__(self, cssid, anchor_name, content):
        initial = {
            'id': cssid,
            'anchor_name': anchor_name,
            'content': content,
        }
        super().__init__(initial)


class IndexContext(UserDict):
    '''Context for the index.html template'''
    def __init__(self, mustgather):
        ca_deployment = NavListEntry(cssid='cluster-autoscaler-deployment',
                                     anchor_name='Deployment',
                                     content=f'{self.cluster_autoscaler_deployment(mustgather)}')
        initial = {
            'basename': self.basename(mustgather.path),
            'ca': {
                'deployment': ca_deployment,
            },
            'datalist': [
                ca_deployment,
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
