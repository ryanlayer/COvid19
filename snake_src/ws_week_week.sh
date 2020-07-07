set -e

NW=$1
src=$2
county_name="${3}"
latest_county_scores=$4
sitrep_path=$5


for i in $( seq 1 $(( NW - 1)) ); do
    j=$(( i + 1 ))

    python $src/plot_ws_x_ws.py \
        --shapename "$county_name" -i $latest_county_scores \
        -o $sitrep_path/ws_week${i}_week${j}.png \
        --x_axis $i \
        --y_axis $j \
        -x "Week $i ws" \
        -y "Week $j ws" \
        --width 2 \
        --height 2 \
        --alpha 0.25
done
result=$sitrep_path
result+="ws_week_week_sentinel.txt"
touch $result