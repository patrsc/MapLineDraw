#!/bin/bash

# Initialize letsencrypt volume by copying dhparams file
# Use file recommended by Mozilla https://ssl-config.mozilla.org
VOLUME="letsencrypt"
URL="https://ssl-config.mozilla.org/ffdhe2048.txt"
FILE=dhparam.pem
CONTAINER=dummy
docker volume rm -f $VOLUME
docker volume create $VOLUME
curl "$URL" > $FILE
docker run -d --rm --name $CONTAINER -v $VOLUME:/root/$VOLUME alpine tail -f /dev/null
docker exec $CONTAINER mkdir -p /root/$VOLUME/dhparams
docker cp $FILE $CONTAINER:/root/$VOLUME/dhparams/$FILE
docker stop $CONTAINER
rm -f $FILE
