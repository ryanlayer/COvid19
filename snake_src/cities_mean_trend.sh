set -e

src=$1
latest_city_scores=$2
sitrep_path=$3
cities="${@:4}"


python $src/plot_shapes_mean_trend.py \
    -i $latest_city_scores \
    --shapenames "$cities" \
    -o $sitrep_path/cities_mean_trends.png \
    --width 7 \
    --height 2 \
    --dist 0.1