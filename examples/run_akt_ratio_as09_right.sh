#!/bin/bash

gpu_ids=("0" "1" "2" "3" "4" "5" "6" "7") #   
# sweep_names=(0m3v8hug 3xjuttk4 w4yv8kt0 8l73b81x 2cjzbh8y 7yfv7as4 c74nq6p4 38rbof58) #  q6gjkzrr q17b62q5 lion3nv6 m8dpdhgq qzq92kts q6gjkzrr
sweep_names=(7bizj4g9 7bizj4g9 7bizj4g9 7bizj4g9 7bizj4g9 7bizj4g9 7bizj4g9 7bizj4g9)
pids=() # Array to store the PIDs of the background processes 
 
for ((i=0; i<${#gpu_ids[@]}; i++)); do
    gpu_id=${gpu_ids[$i]}
    sweep=${sweep_names[$i]}
    
    echo "开始训练模型: GPU ID: $gpu_id, sweep: $sweep"
    
    command="CUDA_VISIBLE_DEVICES=$gpu_id wandb agent 1540712456/akt-int-ratio-2/$sweep &"
    
    eval "$command"
    pids+=($!) # Store the PID of the last command run in the background
done
for pid in "${pids[@]}"; do
    wait "$pid"
done
