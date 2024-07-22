# Reference: https://github.com/xorbitsai/inference/issues/1431

FROM xprobe/xinference:latest
RUN apt-get install -y tini && \
  rm -rf /var/lib/apt/lists/*
COPY init.sh /init.sh
ENTRYPOINT ["/usr/bin/tini", "--", "/init.sh"]

