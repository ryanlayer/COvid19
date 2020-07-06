set -e

src=$1
latest_county_scores=$2
county_name="${3}"
sitrep_path=$4

python $src/trends.py \
    -i $latest_county_scores \
    --shapename "$county_name" \
    --delim "," \
> $sitrep_path/trend.csv