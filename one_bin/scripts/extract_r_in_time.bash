#!/bash

echo $1 

for i in `cat log$1 | grep r_ | grep 68 | awk '{ print $1 }' | awk -F "_" '{ print $2 }'`
do
  echo $i
done > log$1_num

for i in `cat log$1 | grep r_ | grep 68 | awk '{ print $3 }' | awk -F "+" '{ print $2 }'`
do
  echo $i
done > log$1_central

for i in `cat log$1 | grep r_ | grep 68 | awk '{ print $4 }' | awk -F "/" '{ print $1 }'`
do
  echo $i
done > log$1_down

for i in `cat log$1 | grep r_ | grep 68 | awk '{ print $4 }' | awk -F "/" '{ print $2 }' | awk -F "+" '{ print $2 }'`
do 
  echo $i
done > log$1_up

paste log$1_num log$1_central log$1_down log$1_up | column -s $'\t' -t > log$1_readable

sort -n log$1_readable > log$1_sorted

awk '{$1=""}1' log$1_sorted | awk '{$1=$1}1' > log$1_sorted_final
