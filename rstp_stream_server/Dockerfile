# using directly aler9/rtsp-simple-server fails ing GN3 for some reason...

FROM bluenviron/mediamtx:1.9.3 AS rtsp

FROM alpine
COPY --from=rtsp /mediamtx /
COPY rtsp-simple-server.yml /
COPY ./CREDITS /
ENTRYPOINT [ "/mediamtx" ]
