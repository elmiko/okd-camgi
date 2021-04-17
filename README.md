# OKD Cluster Autoscaler Must Gather Investigator

A tool for examining [OKD/OpenShift must-gather](https://github.com/openshift/must-gather) records
to investigate cluster autoscaler behavior and configuration.

## Quickstart

1. Install [Pipenv](https://pipenv.pypa.io/en/latest/)
1. Have a must-gather ready to go in `$MUST_GATHER_PATH`
1. Clone this repo, change directory to it's root
1. Run `pipenv run server --webbrowser $MUST_GATHER_PATH`

Your web browser should now show a page with a summary of the must-gather and some interactive navigation
buttons. If not, open it to `http://localhost:8080`.
