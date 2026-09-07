ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

# Get the built vulnerable app image
FROM ghcr.io/christophetd/log4shell-vulnerable-app@sha256:6f88430688108e512f7405ac3c73d47f5c370780b94182854ea2cddc6bd59929 AS vuln-app

FROM $BASE_REPO${BASE_IMAGE}:$BASE_IMAGE_TAG

# Set environment variables
ENV JAVA_HOME=/opt/openjdk-8
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install dependencies
RUN apt update && apt install -y curl tar gzip && rm -rf /var/lib/apt/lists/*

# Conditionally download OpenJDK 8u181 based on architecture
RUN ARCH=$(dpkg --print-architecture) \
    && if [ "$ARCH" = "amd64" ]; then \
        curl -L -o openjdk-8.tar.gz https://github.com/AdoptOpenJDK/openjdk8-releases/releases/download/jdk8u172-b11/OpenJDK8_x64_Linux_jdk8u172-b11.tar.gz; \
    elif [ "$ARCH" = "arm64" ]; then \
        curl -L -o openjdk-8.tar.gz https://github.com/AdoptOpenJDK/openjdk8-releases/releases/download/jdk8u172-b11/OpenJDK8_aarch64_Linux_jdk8u172-b11.tar.gz; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi

RUN mkdir -p /tmp/${JAVA_HOME} \
    mkdir -p ${JAVA_HOME} \
    && tar -xzf openjdk-8.tar.gz --strip-components=2 -C /tmp/${JAVA_HOME} \
    && rm openjdk-8.tar.gz \
    && cp -fr /tmp/${JAVA_HOME}/* ${JAVA_HOME}/ \
    && rm -rf /tmp/${JAVA_HOME}

# Verify Java installation
RUN java -version


COPY --from=vuln-app /app/spring-boot-application.jar /app/spring-boot-application.jar

