database = {
    "Kobe": {'password': '24man', 'role': 'admin'},
    "LeBron": {'password': '23', 'role': 'user'},
    "Messi": {'password': '10goat', 'role': 'user'},
    "Ronaldo": {'password': '7siu', 'role': 'user'}
}

def login():
    while True:
        usr_name = input("Username: ")
        password = input("Password: ")
        if usr_name not in database:
            print("Username not found. Please try again.")
        else:
            if password != database[usr_name]['password']:
                print("Incorrect password. Please try again.")
            else:
                print("Access granted. Welcome, {}".format(usr_name))
                return usr_name

def change_password(usr_name):
    current_password = input("Enter current password: ")
    if current_password != database[usr_name]['password']:
        print("Incorrect current password.")
        return
    new_password = input("Enter new password: ")
    new_password_confirm = input("Enter new password again: ")
    if new_password != new_password_confirm:
        print("Two passwords do not match.")
    else:
        database[usr_name]['password'] = new_password
        print("Password changed successfully.")

def adduser(usr_name, new_usr_name):
    if database[usr_name]['role'] != 'admin':
        print("Only admin can add new users.")
        return 
    if new_usr_name in database:
        print("User already exists.")
        return
    else:
        database[new_usr_name] = {'password': '000000', 'role': 'user'}
        print("User successfully created.")


while True:
    current_user = login()
    while True:
        command = input("Enter command: ")
        if command == "passwd":
            change_password(current_user)
        elif command.startswith("adduser"):
            parts = command.split()
            adduser(current_user, parts[1])
        elif command == "logout":
            print("Logged out.")
            break