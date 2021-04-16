'''Context classes are the adaptors between data interfaces and templates.'''
from collections import UserDict
import os.path

from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter


class MachineEntry(UserDict):
    def __init__(self, initial):
        content = highlight(initial.as_yaml(), YamlLexer(), HtmlFormatter())
        initial['yaml_highlight_content'] = content
        super().__init__(initial)


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
        ca_deployment = self.cluster_autoscaler_deployment(mustgather)
        ca_pods = self.cluster_autoscaler_pods(mustgather)
        initial = {
            'basename': self.basename(mustgather.path),
            'ca': {
                'deployment': ca_deployment,
                'pods': ca_pods,
            },
            'datalist': [
                ca_deployment,
                *ca_pods,
            ],
            'highlight_css': HtmlFormatter().get_style_defs('.highlight'),
            'machines': [MachineEntry(machine) for machine in mustgather.machines],
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
        return NavListEntry(cssid='cluster-autoscaler-deployment', anchor_name=anchor, content=content)

    @staticmethod
    def cluster_autoscaler_pods(mustgather):
        ret = []
        for pod in  mustgather.clusterautoscaler.pods:
            name = pod.name()
            content = highlight(pod.as_yaml(), YamlLexer(), HtmlFormatter())
            ret.append(NavListEntry(cssid=name, anchor_name=name, content=content))
        return ret

