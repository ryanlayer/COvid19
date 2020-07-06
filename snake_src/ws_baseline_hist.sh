set -e

county_name="${1}"
latest_county_scores=$2
src=$3
sitrep_path=$4

echo ":"
echo $county_name
echo $latest_county_scores
echo $src
echo $ sitrep_path

python $src/ws_scores.py --shapename "$county_name" -i $latest_county_scores | tail -n+2 | cut -f 6 | paste -sd '\t' - \
| $src/hist.py \
    -x "Baseline ws" \
    -y "Freq" \
    -b 50 \
    --width 2 --height 2 \
    -o $sitrep_path/ws_baseline_hist.png