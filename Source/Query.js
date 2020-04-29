db.getCollection('ePubs').find({}).count()
db.getCollection('ePubs').find({'chapters': {"$regex": "tempo"}}).count()
db.getCollection('ePubs').find({'author': {"$regex": "scono"}}).count()

db.getCollection('Dictionary').find({'_id': {'$options': 'i', '$regex': 'vorrei'}})
db.getCollection('ePubs').find({'_id': {'$options': 'i', '$regex': 'child'}})
db.getCollection('ePubs').find({'_id': 'Sconosciuto_Anna_dai_capelli_rossi_3_Anna_dellisola'})
db.getCollection('ePubs').find({'_id': 'Sconosciuto_Anna_dai_capelli_rossi_3_Anna_dellisola'})

