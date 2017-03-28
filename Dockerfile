FROM cern/slc6-base
RUN yum update -y
RUN yum install -y python2-devel
RUN yum install -y python-setuptools python-requests python-requests-kerberos python-six
RUN yum install -y pytest
RUN yum install -y libxml2-devel python-lxml
RUN yum install -y gcc make
RUN mkdir /var/workdir
RUN mkdir /home/work
COPY . /var/workdir
WORKDIR /home/work
