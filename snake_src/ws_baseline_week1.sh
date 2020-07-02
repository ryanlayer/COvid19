set -e


src=$1
county_name="${2}"
latest_county_scores=$3
sitrep_path=$4

python $src/plot_ws_x_ws.py \
    --shapename "$county_name" -i $latest_county_scores \
    -o $sitrep_path/ws_baseline_week1.png \
    --x_axis 0 \
    --y_axis 1 \
    -x 'Baseline ws' \
    -y 'Week 1 ws' \
    --width 2 \
    --height 2 \
    --alpha 0.25
