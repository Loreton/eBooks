db.getCollection('ePubs').find({}).count()
db.getCollection('ePubs').find({'chapters': {"$regex": "tempo"}}).count()
db.getCollection('ePubs').find({'author': {"$regex": "scono"}}).count()
db.getCollection('ePubs').find({'content': {"$regex": "sono \w*.o"}})
db.getCollection('ePubs').find({'content': {"$regex": "\bsono\W+(?:\w+\W+){0,4}?contenta\b"}}, re.IGNORECASE)

db.getCollection('Dictionary').find({'_id': {'$options': 'i', '$regex': 'vorrei'}})
db.getCollection('ePubs').find({'_id': {'$options': 'i', '$regex': 'child'}})
db.getCollection('ePubs').find({'_id': 'Sconosciuto_Anna_dai_capelli_rossi_3_Anna_dellisola'})


# Rename fields
db.students.updateMany( {}, { $rename: { "_old_name": "new_name" } } )
Robo3T - db.getCollection('ePubs').updateMany( {}, { $rename: { "indexed": "indexed_fields" } } )
Robo3T - db.getCollection('ePubs').updateMany( {}, { $rename: { "filter": "_filter" } } )
Robo3T - db.getCollection('Dictionary').updateMany( {}, { $rename: { "tags_words": "tags_word" } } )


# Create new field
db.your_collection.update_many({}, {"$set": {"new_field": "value"}}, upsert=False, array_filters=None)
Robo3T - db.getCollection('Dictionary').updateMany( {}, {"$set": {"title_words": []}}, upsert=false, array_filters=null)


# Update many
db.test.updateMany({foo: "bar"}, {$set: {test: "success!"}})
Robo3T - db.getCollection('ePubs').updateMany( {}, { $set: { indexed_fields: [] } } )

# read chunk
db.getCollection('ePubs').find({}).skip(2).limit(3)




# La directory non deve trovarsi su una directory shared.

set "DPATH=k:\Filu\LnDisk\Ln-eBooks\Calibre_Portable\Ln_Library\Ln_Mongodb"

"k:\Filu\LnDisk\LnFree\DBase\mongodb-win32-x86_64-2012plus-4.2.5\bin\mongod.exe" --dbpath "%DPATH%"  --directoryperdb --bind_ip localhost --port 21000



# La directory non deve trovarsi su una directory shared.
# "mongod" --dbpath "/home/loreto/LnMongoDB"  --directoryperdb --bind_ip localhost --port 21000



####################################################
#        EXPORT                                    #
####################################################
mongoexport  -h [HOST:PORT] -d [DATABASE] -c [COLLECTION] -u [USERNAME] -p [PASSWORD] -o [JSON_FILE] --jsonArray



Mongo database Export syntax

mongoexport --host <host_name> --username <user_name> --password <password> --db <database_name> --collection <collection_name> --out <output_file>

Where:
    --host          is an optional parameter that specifies the remote server Mongo database instance
    --username      optional parameters that specify the authentication details of a user
    --password      optional parameters that specify the authentication details of a user
    --db            specifies the database name
    --collection    specifies the collection name
    --out           specifies the path of the output file. If this is not specified, the result is displayed on the console
    --pretty        optional parameter that outputs the collection in a pretty-printed JSON format
    --jsonArray     parameter modifies the output of the mongoexport command as a single JSON array
                    By default, the mongoexport command writes the data using one JSON document for every Mongo document.

# Windows
outFile="k:\Download\mongo_exported\Dictionary_noArray.json"
outFile="k:\Download\mongo_exported\Dictionary_Array.json" --jsonArray

# Linux
now=$(date "+%Y-%m-%d_%H%M")
collName="ePubs"
collName="Dictionary"
# outFile="/mnt/k/Download/mongo_exported/$collName_Array.json" --jsonArray
exportDir="/mnt/k/Download/mongo_exported"

echo mongoexport  --host 127.0.0.1:27017 --db Ln_eBooks --collection $collName --out "${exportDir}/${collName}_${now}_noArray.json"

####################################################
#        IMPORT                                    #
####################################################
Mongo database Import syntax

mongoimport --host <host_name> --username <user_name> --password <password> --db <database_name> --collection <collection_name> --file <input_file>

Where:
    --host          is an optional parameter that specifies the remote server Mongo database instance
    --username      optional parameters that specify the authentication details of a user
    --password      optional parameters that specify the authentication details of a user
    --db            specifies the database name
    --collection    specifies the collection name
    --file          specifies the path of the input file. If this is not specified, the standard input (i.e. stdin) is used
    --jsonArray     accepts the data import with multiple Mongo database documents within a single JSON array.
                    Do remember, this tag is used conjugation with mongoexport –jsonArray

mongoimport  --host 127.0.0.1:21000 --db Ln_eBooks --collection ePubs --file k:\Download\mongo_exported\ePubs_noArray.json
mongoimport  --host 127.0.0.1:21000 --db Ln_eBooks --collection ePubs --file k:\Download\mongo_exported\ePubs_array.json --jsonArray
mongoimport  --host 127.0.0.1:21000 --db Ln_eBooks --collection Dictionary --file k:\Download\mongo_exported\Dictionary.json --jsonArray
