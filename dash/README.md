## Setup


- Get mapbox public token, put it in `.mapbox_token`
- Generate weekend score, slip score, and trend csv and put them in the 'dash' directory
```
$ python src/ws_scores.py \
    -i utah_county_scores.20200506.txt \
    --shapename "Salt Lake" \
    --delim "," > ws.csv

$  python src/slip_scores.py \
    -i utah_county_scores.20200506.txt \
    --shapename "Salt Lake" \
    --delim "," > slip.csv

$  python src/trends.py \
    -i utah_county_scores.20200506.txt \
    --shapename "Salt Lake" \
    --delim "," > trend.csv
``
- Start the app
```
$ python app2.py
```

Goto the local page at `http://127.0.0.1:8050/`

