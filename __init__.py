import json
import os
def main():
	cities_requested = []
	with open("cities.txt", "r") as f:
		cities_requested = [line.rstrip('\n') for line in f]
		#cities_requested.append(f.readline())
	print(cities_requested)
	config_file = open("snake_config.json",)
	config = json.load(config_file)
	#cities = list(config_file.keys())
	#print(config_file['Boulder']['sit_rep_name'])
	for city in cities_requested:
		sit_rep_name = config[city]['sit_rep_name']
		county_name = config[city]['county_name']
		city_name = config[city]['city_name']
		db = config[city]['db']
		cities = config[city]['cities']
		county_shapes = config[city]['county_shapes']
		county_shapes_name = config[city]['county_shapes_name']
		city_shapes = config[city]['city_shapes']
		city_shapes_name = config[city]['city_shapes_name']
		repo = config[city]['repo']
		#print(repo)
		#print(sit_rep_name, county_name, city_name, db, cities)
		#print(county_shapes, county_shapes_name, city_shapes, city_shapes_name)

		print(sit_rep_name)
		'''
		print(county_name)
		print(city_name)
		print(db)
		print(cities)
		print(county_shapes)
		print(county_shapes_name)
		print(county_shapes_name)
		print(city_shapes)
		print(city_shapes_name)
		print(repo)
		'''

		os.system('bash snake_wrapper.sh "'+sit_rep_name+'" "'+county_name+'" "'+city_name+'" '+db+' '+county_shapes+' '+ \
			county_shapes_name+' '+city_shapes+' '+city_shapes_name+' '+repo + ' ' + cities)


if __name__ == '__main__':
    main()