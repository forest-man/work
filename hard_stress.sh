#!/bin/bash


function echo_blue {
    echo -e "\e[34m $1\e[39m"
}

function echo_red {
  echo -e "\e[31m[$(get_timestamp)]: $1\e[39m"
}

function echo_green {
  echo -e "\e[32m $1\e[39m"
}

function echo_yellow {
  echo -e "\e[33m[$1\e[39m"
}

if [ $# != 1 ]
  then echo_green "Please choose required testcase: \n1 - CPU eat\n2 - Memory eat\n3 - Discspace eat"
  read start	  
fi

function control_c {
    echo_yellow "\nThe test was stopped, all occupied discspace was cleared.\n"
    rm -rf eat/
    exit $?
}

function cpu_eat {
  echo_green "### CPU eat ###\nPlease select test case:\n1-ONE core 100% CPU consumption\n2-ALL cores 100% CPU consumption (Handle with care)"
  read cpu
  if [[ "$cpu" == "1" ]]; then
    taskset -c 1 ./cpu_eat.py
  elif [[ "$cpu" == "2" ]]; then
    echo "ALL cores"
  fi
}



function mem_eat {
  echo_green "### Memory eat ###\nThe script will start to consume free RAM. \nPress Enter to commence the test...\n"
  read
  ./mem_eat.py > /dev>null 2>&1 &

}



function dame {
  echo_green "### Discspace eat ###\nThe script will create directory named \"eat\" and start to consume discspace in intensive way by store in this directory files with constant growing size.\nPress Enter to commence the test...\nPress \"Ctrl+c\" to stop the test"
  read
  mkdir ./eat
  `./dame ed eat/` > /dev>null &
   while trap control_c SIGINT 
    do
      df  | awk '$NF=="/"{printf "Filesystem: %s | Used: %s | Available: %s | Disc Usage: %s\r",$1,$3,$4,$5}'&
      sleep 0.5
    done
}

function main {
  if [[ "$1" == "1" ]]; then
    cpu_eat 
  elif [[ "$1" == "2" ]]; then
    mem_eat
  elif [[ "$1" == "3" ]]; then
    dame
    rm -rf eat/
  fi
}

main $start
