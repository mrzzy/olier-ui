#
# Olier UI
# Docker Container
#

FROM python:3.10.12-slim

WORKDIR /app
# install pip omdule requirements
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
# copy source code & assets
COPY . /app/
# run streamlit
EXPOSE 8501
HEALTHCHECK CMD  python -c 'import urllib.request; contents = urllib.request.urlopen("http://localhost:8501/_stcore/health").read()'
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
