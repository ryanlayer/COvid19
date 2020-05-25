`app2.py`
- the dash flask application
`style.css`
- external style sheet used in the web app
`unique_points.py`
- creates sets of unique points for ss and ws data
- takes 2 command line parameters, the ss and ws files, both in csv format
- creatures unique point subsets of those files with the prefix `unique_`
- needs to be in the same dirretory as the input files to work properly
`cities.tsv`
- tsv file with 6 columns url,ss,ws,trend,unique_ss,unique_ws
- url: the name of the city / location to be recognized from a URL parameter
- ss,ws,trend,unique_ss,unique_ws: files paths for the corresponding files (paths can be relative)
`location_data/`
- dirrectory contains the csv files trend, ws, ss, unique_ws and unique_ss datasets for a location
`assets/`
- dirrectory contains images used in the web app
