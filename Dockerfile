FROM ubuntu:latest

# Install Python, Java, and other dependencies
RUN apt-get update && \
    apt-get install -y python3-pip openjdk-11-jdk curl && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $PATH:$JAVA_HOME/bin

# Install Spark
RUN curl -O https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz && \
    tar xvf spark-3.1.2-bin-hadoop3.2.tgz && \
    mv spark-3.1.2-bin-hadoop3.2 /spark && \
    rm spark-3.1.2-bin-hadoop3.2.tgz

# Set SPARK_HOME
ENV SPARK_HOME /spark
ENV PATH $PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# Install Jupyter
RUN pip3 install jupyter pyspark

# Expose Jupyter and Spark UI ports
EXPOSE 8888 4040 8080

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
