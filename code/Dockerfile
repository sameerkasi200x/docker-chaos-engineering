
FROM nginx:latest

RUN apt-get -qq update
RUN apt-get -qq --allow-downgrades --allow-remove-essential --allow-change-held-packages install python > /dev/null
COPY healthcheck.html healthcheck.py index.html /usr/share/nginx/html/
EXPOSE 80 443
HEALTHCHECK --interval=30s --timeout=3s --retries=2 \
            CMD  python /usr/share/nginx/html/healthcheck.py || exit 1
CMD ["nginx", "-g", "daemon off;"]
