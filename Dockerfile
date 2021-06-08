FROM python:3.9

WORKDIR /pywps-flask

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY processes processes
COPY static static
COPY templates templates
COPY demo.py .
COPY pywps.cfg .

RUN mkdir logs
RUN mkdir outputs
RUN mkdir workdir

CMD ["python", "demo.py", "-a"]
