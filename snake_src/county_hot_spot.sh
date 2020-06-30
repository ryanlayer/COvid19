set -e


src=$1
county_name="${2}"
latest_county_scores=$3
sitrep_path=$4


python $src/hot_spot_scores.py \
    --shapename "$county_name" \
    -i $latest_county_scores \
| sort -t$'\t' -k6 \
> $sitrep_path/county_hot_spot.txt