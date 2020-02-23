# disk/

This is unpacked iso disk downloaded from http://stalin.memo.ru/

Additional changes made on files:

* Archives files `vkvs/vkvs.z1`, `vkvs/vkvs.z2`, etc. were unpacked to folders `vkvs/z1`, `vsvs/z2`, etc.

# db/

Original db files can be found in `disk/vkvs/z2/data/vkvs2`. To load them to mysql do as following:

    cd disk/vkvs/z2/data/vkvs2
    mysql
    # CREATE DATABASE stalin;
    # exit
    cp * /var/lib/mysql/stalin/

## db/db.sql

Simple dump of the database

    mysqldump stalin > db.sql

## db/tables

Database tables exported to csv files in the following way:



    # based on https://stackoverflow.com/questions/12040816/mysqldump-in-csv-format
    for tb in $(mysql stalin -sN -e "SHOW TABLES;"); do
     echo $tb
     mysql -B stalin -e "SELECT * FROM $tb;" \
     | sed "s/\"/\"\"/g;s/'/\'/;s/\t/\",\"/g;s/^/\"/;s/$/\"/;s/\n//g;s/\r//g" \
     > $tb.csv
    done
