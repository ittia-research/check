#!/bin/bash
xinference-local -H 0.0.0.0 &
PID1=$!
while true; do
  if curl -s "http://localhost:9997" > /dev/null; then
    break
  else
    sleep 1
  fi
done
xinference launch --model-name jina-reranker-v2 --model-type rerank &
PID2=$!
wait $PID1 $PID2

