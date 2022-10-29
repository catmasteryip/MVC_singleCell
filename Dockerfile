FROM python:3.7.11

ADD config ./config/
ADD controllers ./controllers/
ADD model ./model/ 
ADD views ./views/
ADD resources ./resources/
ADd app.py requirements.txt .

RUN apt-get update
# dependencies for cv2
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r ./requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:./"
ENV QT_DEBUG_PLUGINS=1

CMD ["python", "./app.py"]