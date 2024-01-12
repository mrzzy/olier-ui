#
# Olier UI
# Docker Container
#

FROM python:3.10.12-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r requirements.txt

# run streamlit
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
