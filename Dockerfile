FROM jumpserver-base
COPY . /usr/src/app
RUN cp ./install/docker/run.sh /run.sh && \
    chmod a+x /run.sh

VOLUME /data
EXPOSE 80
CMD /run.sh
