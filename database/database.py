import sqlite3
import json
from section1.commands import usr_data


#this function is for add user into database
#creates db if not exist and add each user
def addtodb(usr_data):
	conn = sqlite3.connect("database/main_database.db")
	cursor = conn.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS Users (
		user_id INTEGER,
		key TEXT,
		value TEXT,
		PRIMARY KEY (user_id, key)
		)
		''')

	conn.commit()

	for key, value in usr_data.items():
		if isinstance(value, list):
			value = json.dumps(value)
		
		cursor.execute("""INSERT INTO Users(user_id, key, value) 
							VALUES(?, ?, ?) 
							ON CONFLICT(user_id, key) 
							DO UPDATE SET value=excluded.value""",
		(usr_data['user_id'], key, value)
		)
	conn.commit()
	conn.close()


#function return data of all users
def get_user_data():
	conn = sqlite3.connect("database/main_database.db")
	cursor = conn.cursor()

	cursor.execute("SELECT user_id, key, value FROM Users")
	rows = cursor.fetchall()
	conn.close()
	users_dict= {}
	for user_id, key, value in rows:
		if user_id not in users_dict:
			users_dict[user_id] = {"user_id": user_id}
		# Convert JSON back to a list if needed
		try:
			value = json.loads(value) if value.startswith("[") else value
		except json.JSONDecodeError:
			pass  # If it fails, keep value as is

		users_dict[user_id][key] = value

	# Convert dictionary to a list
	users_list = list(users_dict.values())
	return users_list

#function delete certain user
def delete_user(user_id):
    conn = sqlite3.connect("database/main_database.db")
    cursor = conn.cursor()

    # Delete all records related to the given user_id
    cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

