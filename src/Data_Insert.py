# from pymongo import MongoClient

# # Connect to MongoDB
# client = MongoClient("mongodb://localhost:27017/")

# # Select Database
# db = client["Employee's"]

# # Select Collection
# collection = db["Employee_data"]

# # Multiple documents (5 employees)
# employees = [
#     {
#         "name": "Debabrata Dey",
#         "job_type": "Data Scientist",
#         "email_id": "debabratadey9090@gmail.com",
#         "phone_number": "9876543210"
#     },
#     {
#         "name": "Rahul Saha",
#         "job_type": "Software Engineer",
#         "email_id": "rahul@gmail.com",
#         "phone_number": "9123456780"
#     },
#     {
#         "name": "Sayandip bar",
#         "job_type": "Data Analyst",
#         "email_id": "sayandipbar05@gmail.com",
#         "phone_number": "9012345678"
#     },
#     {
#         "name": "Gobinda Bera",
#         "job_type": "Backend Developer",
#         "email_id": "@gmail.com",
#         "phone_number": "9988776655"
#     }
# ]

# # Insert many documents
# collection.insert_many(employees)

# print("✅ 5 Employees inserted successfully!")



# For update data-----------------------------
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["Employee's"]
collection = db["Employee_data"]

# Condition: find the record
filter_condition = {"name": "Sayandip bar"}

# New value to update
new_value = {
    "$set": {
        "job_type": "Data Scientist"
    }
}

# Update the record
collection.update_one(filter_condition, new_value)

print("✅ Data updated successfully!")
