FROM python:2.7.15-alpine3.7

COPY rsscache.py /

ARG all_proxy

ENV host_name=http://localhost:8000 \
    feeds="http://feeds.bbci.co.uk/news/rss.xml|bbcnews.xml;http://feeds.bbci.co.uk/news/world/rss.xml|bbcworld.xml" \
    http_proxy=$all_proxy \
    https_proxy=$all_proxy

EXPOSE 8000

ENTRYPOINT [ "python","rsscache.py" ]