for f in orig/*; do
    n=$( head -n1 "$f" | awk -F"," '{print NF;}' )
    b=$( basename "$f" )
    if [ $n -eq 13  ]; then
        cat "$f" | cut -d "," -f1,2,4,5,6,7,8,9,10,11,12,13 > "$b"
    else
        cp "$f" "$b"
    fi
done
