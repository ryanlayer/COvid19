temp="${@:10}"
snakemake --config sit_rep_name=$1 county_name="${2}" city_name="${3}" db=$4 county_shapes=$5 county_shapes_name=$6 city_shapes=$7 city_shapes_name=$8 repo=$9 cities="${temp}" --cores 1
