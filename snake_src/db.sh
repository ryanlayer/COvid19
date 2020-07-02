set -e

#dbs=( $( cat snake_config.json  | jq '.maps[]| .db' ) )
#repos=( $( cat snake_config.json  | jq '.maps[]| .repo' ) )

#src=/Users/DBurke/Documents/Layerlab/COvid19/src

#basedir=$( pwd )
src=$1
db=$2
repo=$3

basedir=$(pwd)

repo="${repo//\"}"
db="${db//\"}"
echo $repo
echo $db
cd $repo
cd ..
bash fix_files.sh
cmd=$( python $src/csv_to_sql.py --csv `pwd` --db $db )
echo $cmd
eval "$cmd"
cd $basedir

#for repo in "${repos[@]}"; do
#for i in "${!repos[@]}"; do
#    repo=${repos[$i]}
#    db=${dbs[$i]}
#    repo="${repo//\"}"
#    db="${db//\"}"
#    echo $repo
#    cd $repo
#    cd ..
#    bash fix_files.sh
#    cmd=$( python $src/csv_to_sql.py --csv `pwd` --db $db )
#    echo $cmd
#    eval "$cmd"
#    cd $basedir
#done
