# OKD Cluster Autoscaler Must Gather Investigator

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

Camgi also includes a server mode which allows for dynamic creation of investigation
pages. Start the server and then make queries with the `url` query parameter
specifying a url to a must-gather archive file. The server will download the file,
extract the archive, process the files, and return a generated webpage.

1. `podman run --rm -it -p 8080:8080 quay.io/elmiko/okd-camgi`
1. Open you web browser to `http://localhost:8080?url=http://path/to/must-gather.tar.gz`

