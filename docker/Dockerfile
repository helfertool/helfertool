FROM python
RUN apt-get update && apt-get install -y node npm nano unzip

WORKDIR /app
RUN git clone https://github.com/helfertool/helfertool.git
#RUN pyvenv helfertool
WORKDIR /app/helfertool
#RUN . ./bin/activate
RUN pip install -r requirements.txt

#RUN npm config set prefix /usr/local
RUN npm install -g bower
RUN python manage.py bower install

RUN python manage.py collectstatic
RUN npm install jquery bootstrap
RUN cp -r node_modules/jquery helfertool/static
RUN cp -r node_modules/bootstrap helfertool/static
RUN curl -o font-awesome.zip http://fontawesome.io/assets/font-awesome-4.7.0.zip
RUN unzip font-awesome.zip
RUN mv font-awesome-4.7.0 helfertool/static/font-awesome

COPY start.sh .
COPY conf/* ./helfertool/

EXPOSE 8000

CMD ["./start.sh"]
