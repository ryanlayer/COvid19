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
```

- Make config file

`slc_config.json`
```
{
    "slip_data":"slip.csv",
    "trend_data":"trend.csv",
    "weekend_data":"ws.csv",
    "title":"Salt Lake County : COVID-19 Mobility Data Network",
    "start_lat":40.588928,
    "start_lon":-112.071533
}
```

- Start the app

```
$ python local_dashboard.py -c slc_config.json
```

Goto the local page at `http://127.0.0.1:8050/`
