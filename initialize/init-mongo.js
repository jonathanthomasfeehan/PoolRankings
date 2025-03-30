db.getSiblingDB("admin").auth(
    process.env.MONGO_INITDB_ROOT_USERNAME,
    process.env.MONGO_INITDB_ROOT_PASSWORD
)

db.getSiblingDB(process.env.MONGO_DB).createUser({
    user:process.env.MONGO_USER,
    pwd:process.env.MONGO_PASSWORD,
    roles:["readWrite"]
})

db.createCollection(process.env.MONGO_DB)
db.getSiblingDB(process.env.MONGO_DB).createCollection(process.env.MONGO_COLLECTION);
