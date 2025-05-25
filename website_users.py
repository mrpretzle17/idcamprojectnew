import pickle
from flask import request, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlclientsocket import send_sql

  
# these two classes are used for the login
class User:
    # makes a user object
    def __init__(self, user_id, user_name, hashed_password, is_admin):
        self.id = user_id
        self.name = user_name
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def makesession(self):
        session["loggedin"] = True
        session["id"] = self.id
        session["name"] = self.name
        session["admin"] = self.is_admin

    

class UserValidate:

    def check_in_db(user_id):
        query = "SELECT id, name, password, admin FROM users WHERE id = %s"
        params = (user_id,)
        # here i send the sql request to the socket code
        response = send_sql(query, params)

        try:

            results = pickle.loads(response)
            if results:
                #if there is an answer it takes the first row of the table
                db_id, db_name, db_password, db_admin = results[0]
                return User(db_id, db_name, db_password, db_admin)
        except Exception as e:
            print(f"isue: {e}")

        return None
    
    def validate_login(user_id, password):
        user = UserValidate.check_in_db(user_id)
        passwords_match = user.verify_password(password)
        if user and passwords_match:
            return user
        return None
    

class Admin(User):
    # it inherits its object qualitys and values from user 
    def __init__(self, user_id, name, hashed_password, is_admin):
        super().__init__(user_id, name, hashed_password, is_admin)
    
    # i set it so that 1 is admin and 0 isnt
    def is_admin_check(self):
        return (self.is_admin == 1)
    
    def remove_user(self, id_remove):
        try:
            if not self.is_admin_check():
                return "notadmin"


            delete_query = "DELETE FROM users WHERE id = %s"
            delete_params = (id_remove,)
            response = send_sql(delete_query, delete_params)

            if b"SUCCESS" in response:
                return "userremoved"
            else:
                print(f"isue: {response.decode()}")
            return "error"


        except KeyError as e:
            print(f"Missing form field: {e}")
            return "fail"
        except Exception as e:
            print(f"Error: {e}")
            return "fail"   
    
    def insert_user(self, new_id, new_name, new_is_admin, new_password):
        try:
            if not self.is_admin_check():
                return "notadmin"
            hashed_password = generate_password_hash(new_password)

            check_query = "SELECT COUNT(*) FROM users WHERE id = %s"

            #the comma is nessecary to show that it is a single input
            check_params = (new_id,)
            #sends the request to the socket code
            check_response = send_sql(check_query, check_params)

            # [0][0] takes the first row and colomb meaing the number
            user_exists = pickle.loads(check_response)[0][0]
            if user_exists > 0:
                return "userexists"


            insert_query = "INSERT INTO users (id, name, password, admin) VALUES (%s, %s, %s, %s)"
            insert_params = (new_id, new_name, hashed_password, new_is_admin)
            insert_response = send_sql(insert_query, insert_params)
            # the send_sql func will return SUCCESS if everything worked
            if b"SUCCESS" in insert_response:
                return "useradded"
            else:
                return "fail"


        except KeyError as e:
            print(f"Missing form field: {e}")
            return "fail"
        except Exception as e:
            print(f"Error during insert_user: {e}")
            return "fail"

    def all_users():
        try:
            query = "SELECT * FROM users"
            params = ()

            response = send_sql(query, params)

            try:
                userDetails = pickle.loads(response)
                return userDetails
            except Exception as e:
                print(f"Failed to decode user list: {e}")
                flash("Error decoding user data.", "error")
                return None

        except Exception as e:
            print(f"Error during all_users(): {e}")
            flash("Error during all_users()", "error")
            return None
