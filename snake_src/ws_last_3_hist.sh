set -e


county_name="${1}"
latest_county_scores=$2
NW=$3
src=$4
sitrep_path=$5


(python $src/ws_scores.py --shapename "$county_name" -i $latest_county_scores | tail -n+2 | cut -f $(( NW + 4 )) | paste -sd '\t' - ; \
python $src/ws_scores.py --shapename "$county_name" -i $latest_county_scores | tail -n+2 | cut -f $(( NW + 5 )) | paste -sd '\t' - ; \
python $src/ws_scores.py --shapename "$county_name" -i $latest_county_scores | tail -n+2 | cut -f $(( NW + 6)) | paste -sd '\t' - ;) \
| $src/hist.py \
    -x "Week $(( NW - 2 )),Week $(( NW - 1 )),Week $(( NW ))" \
    -y 'Freq' \
    -b 50 \
    --width 3.5 \
    --height 2 \
    -o $sitrep_path/ws_last_3_hist.png