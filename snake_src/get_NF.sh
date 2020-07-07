set -e

base_path=$1
src=$2
latest_county_scores=$3
#sitrep_path = base_path+'/sitreps/'+'Boulder'+'/'+today+'/'  #need to expand for all cities
NF=$( python $src/ws_scores.py -i $latest_county_scores | tail -n+2 | head -n 1 | awk -F"\t" '{print NF;}' )
echo $NF>'snake_src/NF.txt'