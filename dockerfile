FROM continuumio/miniconda3:latest

WORKDIR /tesla-ver

COPY environment.yaml environment.yaml
RUN conda update -y -n base -c defaults conda
RUN conda env create --file environment.yaml

SHELL ["/bin/bash", "-c"]

# RUN echo "Make sure flask is installed:"
# RUN python -c "import flask"

COPY . .
# ENV FLASK_APP="wsgi.py"
# ENV FLASK_ENV=development
RUN ["conda","init","--all"]
CMD source /root/.bashrc && conda activate tesla-ver && gunicorn --workers=2 --chdir=/tesla-ver/ --bind=0.0.0.0:5000 wsgi:server
