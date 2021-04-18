# OKD Cluster Autoscaler Must Gather Investigator

A tool for examining [OKD/OpenShift must-gather](https://github.com/openshift/must-gather) records
to investigate cluster autoscaler behavior and configuration.

## Quickstart

1. install from [PyPi](https://pypi.org/project/okd-camgi) with `pip3 install okd-camgi --user`
1. Have a must-gather ready to go in `$MUST_GATHER_PATH`
1. Run `okd-camgi --webbrowser $MUST_GATHER_PATH`

Your web browser should now show a page with a summary of the must-gather and some interactive navigation
buttons. If your browser does not open, you will see the URL printed on the terminal, copy it into a new
browser tab or window.
