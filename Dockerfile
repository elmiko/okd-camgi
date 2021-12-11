FROM registry.access.redhat.com/ubi8/python-39

EXPOSE 8080

COPY . /opt/okd-camgi/

WORKDIR /opt/okd-camgi

RUN pip3 install .

CMD ["/opt/app-root/bin/okd-camgi", "--server", "--host", "0.0.0.0", "--port", "8080"]
