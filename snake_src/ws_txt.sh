set -e


src=$1
county_name="${2}"
latest_county_scores=$3
NW=$4
sitrep_path=$5

python $src/ws_scores.py \
    --shapename "$county_name" -i $latest_county_scores\
| tail -n +2 \
| awk -F"\t" '$5>100'  \
| sort -t$'\t' -k $(( NW + 5 )),$(( NW + 5 ))g \
> $sitrep_path/ws.txt