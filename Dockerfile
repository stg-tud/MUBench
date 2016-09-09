FROM drydock/u12pyt:prod

# requirements
RUN apt-get update
RUN apt-get install -y oracle-java8-installer
RUN apt-get install git
RUN apt-get install subversion
RUN apt-get install maven
RUN apt-get install graphviz
RUN add-apt-repository ppa:cwchien/gradle
RUN apt-get update
RUN apt-get install gradle-ppa

WORKDIR /mubench

# python setup
ENV PATH /root/venv/3.5/bin:$PATH
RUN pip install pyyaml

# java8 setup
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle
ENV PATH $PATH:$JAVA_HOME/bin
RUN update-alternatives --set java "$JAVA_HOME/jre/bin/java"
RUN update-alternatives --set javac "$JAVA_HOME/bin/javac"
RUN update-alternatives --set javaws "$JAVA_HOME/jre/bin/javaws"

# git setup
RUN git config --global user.email "bob@builder.com"
RUN git config --global user.name "Bob the Builder"
