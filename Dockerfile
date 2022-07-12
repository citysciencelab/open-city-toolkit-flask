FROM python:bullseye

# Install GRASS GIS
RUN apt-get update
RUN apt-get install -y grass-core

# Install PyWPS server
WORKDIR /pywps-flask
RUN apt-get install -y libproj-dev python3-six
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY processes processes
COPY static static
COPY templates templates
COPY demo.py .
COPY geoserver.py .
COPY pywps.cfg .

RUN mkdir logs
RUN mkdir workdir
RUN mkdir upload_tmp

CMD grass -f grass/global/PERMANENT --exec python demo.py -a
