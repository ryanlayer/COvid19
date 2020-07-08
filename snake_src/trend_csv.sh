set -e

src=$1
sit_rep_name=$2
latest_county_scores=$3
county_name="${4}"
sitrep_path=$5

python $src/trends.py \
    -i $latest_county_scores \
    --shapename "$county_name" \
    --delim "," \
> ${sitrep_path}${sit_rep_name}_trend.csv