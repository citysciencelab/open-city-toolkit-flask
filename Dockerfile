FROM debian:bullseye

# Install GRASS GIS
RUN apt-get update
RUN apt-get install -y grass-core

# Install PyWPS server
WORKDIR /pywps-flask
RUN apt-get install -y python3 python3-flask python3-flask-cors python3-pywps

COPY grass grass
COPY processes processes
COPY static static
COPY templates templates
COPY demo.py .
COPY geoserver.py .
COPY pywps.cfg .

RUN mkdir logs
RUN mkdir workdir
RUN mkdir upload_tmp

RUN if [ ! -e grass/global/PERMANENT ]; then mkdir -p grass/global/PERMANENT; cp grass/skel_permanent/* grass/global/PERMANENT; fi

CMD grass -f grass/global/PERMANENT --exec python3 demo.py -a
