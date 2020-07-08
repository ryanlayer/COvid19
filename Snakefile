import datetime
import glob
import os

sit_rep_name = config['sit_rep_name']
county_name = config['county_name']
city_name = config['city_name']
db = config['db']
cities = config['cities']
county_shapes = config['county_shapes']
county_shapes_name = config['county_shapes_name']
city_shapes = config['city_shapes']
city_shapes_name = config['city_shapes_name']
repo = config['repo']


def time_stamp(fmt='%Y%m%d'):
    return datetime.datetime.now().strftime(fmt)

today = time_stamp()
print(today)


base_path = "/Users/DBurke/Documents/Layerlab/COvid19" #CHANGE PATH
sit_rep_path = base_path+'/sitreps/'+sit_rep_name+'/'+today +'/'
location_data_path = base_path + "/dash/location_data/"
src = base_path+'/src'
latest_county_scores = sit_rep_path + sit_rep_name + '_county_scores.' + today + '.txt'
latest_city_scores = sit_rep_path + sit_rep_name + '_city_scores.' + today + '.txt'



def get_NF(latest_county_scores):
	os.system('bash snake_src/get_NF.sh ' + base_path + ' ' + src + ' ' + latest_county_scores)
	with open('snake_src/NF.txt') as f:
		NF = f.readline()
	os.remove("snake_src/NF.txt")
	NW = int(NF) - 6
	return NW


list_of_tiles = glob.glob(repo + '*csv')
latest_tile = max(list_of_tiles, key=os.path.getctime)

rule all:
	input:
		expand(sit_rep_path + sit_rep_name + '_{type}_scores.' + today + '.txt', type = ['city', 'county']),
		sit_rep_path + 'ws_baseline_hist.png',
		sit_rep_path + "ws_week_hist_sentinel.txt",
		expand(sit_rep_path + sit_rep_name +'_{type}.csv', type = ['ws', 'trend', 'slip']),
		sit_rep_path + 'cities_mean_trends.png',
		sit_rep_path + 'city_hot_spot.txt',
		sit_rep_path + 'county_hot_spot.txt',
		sit_rep_path + 'hot_spot.png',
		sit_rep_path + "ss_week_week_sentinel.txt",
		sit_rep_path + 'ss.txt',
		sit_rep_path + 'ws_baseline_week1.png',
		sit_rep_path + 'ws_last_3_hist.png',
		sit_rep_path + "ws_week_week_sentinel.txt",
		sit_rep_path + 'ws.txt',
		location_data_path + 'unique_' + sit_rep_name + '_ws.csv',
		location_data_path + 'unique_' + sit_rep_name + '_slip.csv',
		expand(location_data_path + sit_rep_name +'_{type}.csv', type = ['ws', 'trend', 'slip'])

		
rule db:
	input:
		latest_tile
	output:
		db
	shell:
		"bash snake_src/db.sh {src} {db} {repo}"

rule latest_county_scores:
	input:
		db
	output:
		latest_county_scores
	shell:
		' mkdir -p ' + sit_rep_path + ';' + \
		' python {src}/get_all_scores_by_shape.py \
    		--db {db} \
    		--shapefile {county_shapes} \
    		--shapename {county_shapes_name} \
		> {latest_county_scores}'

rule latest_city_scores:
	input:
		db
	output:
		latest_city_scores
	shell:
		' mkdir -p ' + sit_rep_path + ';' + \
		' python {src}/get_all_scores_by_shape.py \
    		--db {db} \
    		--shapefile {city_shapes} \
    		--shapename {city_shapes_name} \
		> {latest_city_scores}'

rule ws_baseline_hist:
	input:
		latest_county_scores
	output:
		sit_rep_path + 'ws_baseline_hist.png'
	run:
		shell('bash snake_src/ws_baseline_hist.sh "{county_name}" {latest_county_scores} {src} {sit_rep_path}')

rule ws_week_hist:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ws_week_hist_sentinel.txt"
	run:
		NW = get_NF(latest_county_scores)
		shell('bash snake_src/ws_week_hist.sh {NW} {src} "{county_name}" {latest_county_scores} {sit_rep_path}')

rule ws_last_3_hist:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ws_last_3_hist.png"
	run:
		NW = get_NF(latest_county_scores)
		shell('bash snake_src/ws_last_3_hist.sh "{county_name}" {latest_county_scores} {NW} {src} {sit_rep_path}')

rule ws_baseline_week1:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ws_baseline_week1.png"
	run:
		shell('bash snake_src/ws_baseline_week1.sh {src} "{county_name}" {latest_county_scores} {sit_rep_path}')

rule ws_week_week:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ws_week_week_sentinel.txt"
	run:
		NW = get_NF(latest_county_scores)	
		shell('bash snake_src/ws_week_week.sh {NW} {src} "{county_name}" {latest_county_scores} {sit_rep_path}')

rule ws_txt:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ws.txt"
	run:
		NW = get_NF(latest_county_scores)
		shell('bash snake_src/ws_txt.sh {src} "{county_name}" {latest_county_scores} {NW} {sit_rep_path}')

rule ss_week_week:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ss_week_week_sentinel.txt"
	run:
		NW = get_NF(latest_county_scores)
		shell('bash snake_src/ss_week_week.sh {NW} {src} "{county_name}" {latest_county_scores} {sit_rep_path}')

rule ss_txt:
	input:
		latest_county_scores
	output:
		sit_rep_path + "ss.txt"
	run:
		NW = get_NF(latest_county_scores)
		shell('bash snake_src/ss_txt.sh {src} "{county_name}" {latest_county_scores} {NW} {sit_rep_path}')

rule cities_mean_trend:
	input:
		latest_city_scores
	output:
		sit_rep_path + "cities_mean_trends.png"
	run:
		shell('bash snake_src/cities_mean_trend.sh {src} {latest_city_scores} {sit_rep_path} {cities}')

rule hot_spot:
	input:
		latest_county_scores
	output:
		sit_rep_path + "hot_spot.png"
	run:
		shell('bash snake_src/hot_spot.sh {src} "{county_name}" {latest_county_scores} {sit_rep_path}')

rule city_hot_spot:
	input:
		latest_city_scores
	output:
		sit_rep_path + "city_hot_spot.txt"
	run:
		shell('bash snake_src/city_hot_spot.sh {src} "{city_name}" {latest_city_scores} {sit_rep_path}')

rule county_hot_spot:
	input:
		latest_county_scores
	output:
		sit_rep_path + "county_hot_spot.txt"
	run:
		shell('bash snake_src/county_hot_spot.sh {src} "{county_name}" {latest_county_scores} {sit_rep_path}')

rule ws_csv:
	input:
		latest_county_scores
	output:
		sit_rep_path + sit_rep_name + "_ws.csv"
	run:
		shell('bash snake_src/ws_csv.sh {src} {sit_rep_name} {latest_county_scores} "{county_name}" {sit_rep_path}')

rule slip_csv:
	input:
		latest_county_scores
	output:
		sit_rep_path + sit_rep_name + "_slip.csv"
	run:
		shell('bash snake_src/slip_csv.sh {src} {sit_rep_name} {latest_county_scores} "{county_name}" {sit_rep_path}')

rule trend_csv:
	input:
		latest_county_scores
	output:
		sit_rep_path + sit_rep_name + "_trend.csv"
	run:
		shell('bash snake_src/trend_csv.sh {src} {sit_rep_name} {latest_county_scores} "{county_name}" {sit_rep_path}')

rule unique_points:
	input:
		expand(sit_rep_path + sit_rep_name +'_{type}.csv', type = ['ws', 'trend', 'slip'])
	output:
		location_data_path + 'unique_' + sit_rep_name + '_ws.csv',
		location_data_path + 'unique_' + sit_rep_name + '_slip.csv',
	run:
		ws = sit_rep_name + '_ws.csv'
		slip = sit_rep_name + '_slip.csv'
		shell('python dash/unique_points.py {slip} {ws} {sit_rep_path} {location_data_path}')

rule move_files:
	input:
		location_data_path + 'unique_' + sit_rep_name + '_ws.csv',
		location_data_path + 'unique_' + sit_rep_name + '_slip.csv',
		expand(sit_rep_path + sit_rep_name +'_{type}.csv', type = ['ws', 'trend', 'slip'])
	output:
		expand(location_data_path + sit_rep_name +'_{type}.csv', type = ['ws', 'trend', 'slip'])
	run:
		shell('cp {sit_rep_path}{sit_rep_name}_ws.csv {location_data_path}{sit_rep_name}_ws.csv')
		shell('cp {sit_rep_path}{sit_rep_name}_trend.csv {location_data_path}{sit_rep_name}_trend.csv')
		shell('cp {sit_rep_path}{sit_rep_name}_slip.csv {location_data_path}{sit_rep_name}_slip.csv')






#---------TO-DO-------------#
#python $src/make_hot_spot_shapefile.py \
#    -i $latest_city_scores \
#    --shapename "$city_name" \
#    -o $sitrep_path/hot_spot_city_shape
#
#python $src/make_hot_spot_shapefile.py \
#    -i $latest_county_scores \
#    --shapename "$county_name" \
#    -o $sitrep_path/hot_spot_county_shape
