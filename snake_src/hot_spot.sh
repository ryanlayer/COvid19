set -e

src=$1
county_name="${2}"
latest_county_scores=$3
sitrep_path=$4


python $src/plot_hot_spot_x_density.py \
    --shapename "$county_name" \
    -i $latest_county_scores \
    -o $sitrep_path/hot_spot.png \
    --alpha 0.25 \
    --width 3 \
    --height 2 \
    -x 'Baseline density' \
    -y 'Current hot-spot score'