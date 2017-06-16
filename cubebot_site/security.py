from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash #compares strings to make sure they are same, takes care of diff encodings
from .model import UserModel

# create authentication function
def authenicate(username, password): ##passwords have been hashed now - update in future
	user = UserModel.find_by_username(username)		#get is another way to access dictionary // replacing "username_mapping.get(username, None)" with new User method accessing db
	if user and safe_str_cmp(user.password, password):
		return user

def identity(payload):
	user_id = payload['identity']
	return UserModel.find_by_id(user_id) # replacing "userid_mapping.get(user_id, None)" with new User method that calls db
