# COvid19
Providing social distancing situational awareness during the COVID-19 pandemic in Colorado

- Set up conda environment
```
$ conda env create -f environment.yml
$ conda activate COvid19
```
- Download Facebook Population (Tile Level) files to `pop_tiles/orig`
- From `pop_tiles` run 
```
$ bash fix_files.sh
```
- Create the database
```
$ python src/csv_to_sql.py --csv pop_tiles/ --db colorado.db
rm -f colorado.db;sqlite3 colorado.db < tmp.sql
$ rm -f colorado.db;sqlite3 colorado.db < tmp.sql
```
- Get scores aggregated by a field in a shapefile, here we will use cities in Colorado.
```
$ python src/get_all_scores_by_shape.py \
    --db colorado.db \
    --shapefile shapefiles/Colorado_City_Boundaries/ \
    --shapename NAME10 \
> colorado_city_scores.`date "+%Y%m%d"`.txt
```

![](imgs/Boulder_example_tile.png)
```
python src/plot_one.py \
    -i colorado_city_scores.20200422.txt \
    -o imgs/Boulder_example_tile.png \
    --shapename "Boulder" \
    --width 5 -n 5 --height 1
```

![](imgs/colorado_example_tile_ws_diffs.png)
```
$ python src/ws_scores.py \
    -i colorado_city_scores.20200422.txt \
| sort -t$'\t' -k 5,5g \
| tail -n 1
449	Boulder	40.069664004427	-105.21606445312	1.0568428725333567	0.5266777645208203	0.5424389724825188	0.4402530723582583

$ python src/ws_scores.py \
    -i colorado_city_scores.20200422.txt \
| sort -t$'\t' -k 5,5gr \
| tail -n 1
1322	Grand Lake	40.254376084285	-105.83129882812	-0.5717760132754274	-0.12254129829560738	0.005638648006131584	-0.011023686029626615

$ python src/ws_scores.py \
    -i colorado_city_scores.20200422.txt \
    -o  imgs/colorado_example_tile_ws_diffs.png \
    -n 449,1322 \
     --width 5 --height 2.5 > /dev/null
