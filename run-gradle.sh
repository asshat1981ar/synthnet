#!/bin/bash

export JAVA_HOME=/data/data/com.termux/files/usr/lib/jvm/java-21-openjdk
export LD_LIBRARY_PATH=$JAVA_HOME/lib:$JAVA_HOME/lib/server:$LD_LIBRARY_PATH

./gradlew "$@"
