#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test

This script tests your MongoDB Atlas connection before deployment.
"""

import pymongo
import os
from datetime import datetime

def test_mongodb_connection():
    print("🔗 Testing MongoDB Atlas Connection")
    print("=" * 50)
    
    # Get connection string from user
    print("\nPlease enter your MongoDB Atlas connection string:")
    print("Format: mongodb+srv://parkingapp:PASSWORD@parking-app-cluster.xxxxx.mongodb.net/parking_app?retryWrites=true&w=majority")
    print("\n(Paste your connection string here)")
    
    connection_string = input("MongoDB URI: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided!")
        return False
    
    try:
        print("\n🔄 Connecting to MongoDB Atlas...")
        
        # Create MongoDB client
        client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ismaster')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Get database
        db = client.get_default_database()
        print(f"📊 Database name: {db.name}")
        
        # Test write operation
        test_collection = db.connection_test
        test_doc = {
            "test": True,
            "timestamp": datetime.utcnow(),
            "message": "Connection test successful!"
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test write successful! Document ID: {result.inserted_id}")
        
        # Test read operation
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Test read successful!")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        # Show cluster info
        server_info = client.server_info()
        print(f"📋 MongoDB version: {server_info['version']}")
        
        client.close()
        
        print("\n🎉 MongoDB Atlas is ready for your app!")
        print("\nNext steps:")
        print("1. Copy your connection string")
        print("2. Update backend/app.yaml with this connection string")
        print("3. Deploy your backend to Google Cloud")
        
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ Connection timeout - check your connection string and network access settings")
        print("   Make sure you've added 0.0.0.0/0 to Network Access in MongoDB Atlas")
        return False
        
    except pymongo.errors.OperationFailure as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your username and password in the connection string")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def save_connection_string():
    """Save connection string to a secure file"""
    print("\n💾 Would you like to save your connection string securely? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice == 'y':
        connection_string = input("\nEnter your connection string again: ").strip()
        
        # Create a secure env file
        with open('mongodb_config.txt', 'w') as f:
            f.write("# MongoDB Atlas Configuration\n")
            f.write("# Copy this connection string to your app.yaml file\n\n")
            f.write(f"MONGODB_URI={connection_string}\n")
        
        print("✅ Connection string saved to 'mongodb_config.txt'")
        print("⚠️  Remember to keep this file secure and don't commit it to Git!")

if __name__ == "__main__":
    print("🚀 Vehicle Parking App - MongoDB Atlas Connection Test")
    print("=" * 60)
    
    # Check if pymongo is installed
    try:
        import pymongo
        print("✅ PyMongo is installed")
    except ImportError:
        print("❌ PyMongo not found. Please run: pip install pymongo")
        exit(1)
    
    # Test connection
    if test_mongodb_connection():
        save_connection_string()
    else:
        print("\n🔧 Troubleshooting tips:")
        print("1. Double-check your username and password")
        print("2. Ensure Network Access allows 0.0.0.0/0")
        print("3. Make sure the database name is 'parking_app'")
        print("4. Verify the cluster name in your connection string") 