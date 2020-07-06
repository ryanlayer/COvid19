set -e

src=$1
city_name="${2}"
latest_city_scores=$3
sitrep_path=$4


python $src/hot_spot_scores.py \
    --shapename "$city_name" \
   -i $latest_city_scores \
| sort -t$'\t' -k6 \
> $sitrep_path/city_hot_spot.txt