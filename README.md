# OKD Cluster Autoscaler Must Gather Investigator

# TEST

[![Docker Repository on Quay](https://quay.io/repository/elmiko/okd-camgi/status "Docker Repository on Quay")](https://quay.io/repository/elmiko/okd-camgi)

A tool for examining [OKD/OpenShift must-gather](https://github.com/openshift/must-gather) records
to investigate cluster autoscaler behavior and configuration.

## Quickstart

1. install from [PyPi](https://pypi.org/project/okd-camgi) with `pip3 install okd-camgi --user`
1. Have a must-gather ready to go in `$MUST_GATHER_PATH`
1. Run `okd-camgi --webbrowser $MUST_GATHER_PATH`

Your web browser should now show a page with a summary of the must-gather and some interactive navigation
buttons. If your browser does not open, you will see the URL printed on the terminal, copy it into a new
browser tab or window.

### Direct from tar file

okd-camgi can also process must-gather tar files directly, using the `--tar` flag. for example:
```bash
$ okd-camgi --tar path/to/my/must-gather.tar.gz
```

## Containerized Server

An alternative to running the command line tool is to start a local containerized webserver which
hosts the must-gather investigation page. Follow these steps to start a local server:

1. `podman run --rm -it -p 8080:8080 -v /path/to/must-gather:/must-gather:Z quay.io/elmiko/okd-camgi`
1. Open you web browser to `http://localhost:8080`

As in the Quickstart, your web browser should now show the must-gather investigation page.
