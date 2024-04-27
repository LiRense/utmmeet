#!/bin/bash

searched_item=$1

pods=$(kubectl get po -A | grep "$searched_item")

ns=$(echo "$pods" | awk '{print $1}')
pod_name=$(echo "$pods" | awk '{print $2}')

#log_data=$(kubectl -n "$ns" logs "$pod_name" -f)

count_of_po=$(wc -w <<< "$pod_name")

if [ "$count_of_po" == "1" ]; then
    #while true ; do
    echo "----- logging for $pod_name -----"
    kubectl -n "$ns" logs "$pod_name" -f
    echo "----- pod $pod_name disconnected -----"
    #done
elif [ "$count_of_po" == "0" ] ; then
    echo "Не найдено подов"
else
    echo "Найдены следующие поды:"
    echo $pod_name | tr ' ' '\n'
fi
