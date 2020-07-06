set -e

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

