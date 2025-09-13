// MongoDB Initialization Script for DVC.AI
// This script creates the database and initial collections

// Switch to the application database
db = db.getSiblingDB('dvc_ai_db');

// Create collections with initial setup
db.createCollection('users');
db.createCollection('documents');
db.createCollection('conversations');
db.createCollection('upload_sessions');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "filename": 1 });
db.documents.createIndex({ "upload_date": -1 });
db.conversations.createIndex({ "user_id": 1 });
db.conversations.createIndex({ "created_at": -1 });
db.upload_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.upload_sessions.createIndex({ "created_at": 1 }, { expireAfterSeconds: 3600 }); // Auto-expire after 1 hour

// Create a default admin user (optional)
// Uncomment and modify the following lines if you want a default admin user
/*
db.users.insertOne({
    username: "admin",
    email: "admin@dvc.gov.vn",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewniKW.jVrOkWf/m", // password: admin123
    is_active: true,
    is_admin: true,
    created_at: new Date(),
    updated_at: new Date()
});
*/

print("DVC.AI database initialized successfully!");
print("Created collections: users, documents, conversations, upload_sessions");
print("Created indexes for optimal performance");
