set -e


NW=$1
src=$2
county_name="${3}"
latest_county_scores=$4
sitrep_path=$5


for i in $( seq 1 $(( NW - 1)) ); do
    j=$(( i + 1 ))
    python $src/plot_split_x_density.py \
        --shapename "$county_name" -i $latest_county_scores \
        -o $sitrep_path/ss_week${i}_week${j}.png \
        --alpha 0.25 \
        --width 3 \
        --height 2  \
        --weeks $i,$j \
        -x "Baseline density" \
        -y "Week $i to week $j slip"
done
result=$sitrep_path
result+="ss_week_week_sentinel.txt"
touch $result