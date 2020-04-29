db.getCollection('ePubs').find({}).count()
db.getCollection('ePubs').find({'chapters': {"$regex": "tempo"}}).count()
db.getCollection('ePubs').find({'author': {"$regex": "scono"}}).count()

db.getCollection('Dictionary').find({'_id': {'$options': 'i', '$regex': 'vorrei'}})
db.getCollection('ePubs').find({'_id': {'$options': 'i', '$regex': 'child'}})
db.getCollection('ePubs').find({'_id': 'Sconosciuto_Anna_dai_capelli_rossi_3_Anna_dellisola'})
db.getCollection('ePubs').find({'_id': 'Sconosciuto_Anna_dai_capelli_rossi_3_Anna_dellisola'})


// Rename fields
db.students.updateMany( {}, { $rename: { "_old_name": "new_name" } } )
Robo3T - db.getCollection('ePubs').updateMany( {}, { $rename: { "indexed": "indexed_fields" } } )


// Update many
db.test.updateMany({foo: "bar"}, {$set: {test: "success!"}})
Robo3T - db.getCollection('ePubs').updateMany( {}, { $set: { indexed_fields: [] } } )

// read chunk
db.getCollection('ePubs').find({}).skip(2).limit(3)