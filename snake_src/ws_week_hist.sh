set -e


NW=$1
src=$2
county_name="${3}"
latest_county_scores=$4
sitrep_path=$5

for i in $( seq 1 $NW ); do
    col=$(( i + 6 ))
    python $src/ws_scores.py --shapename "$county_name" -i $latest_county_scores | tail -n+2 | cut -f $col | paste -sd '\t' - \
    | $src/hist.py \
        -x "Week $i ws" \
        -y "Freq" \
        -b 50 \
        --width 2 --height 2 \
        -o $sitrep_path/ws_week${i}_hist.png
done
result=$sitrep_path
result+="ws_week_hist_sentinel.txt"
touch $result