from google.cloud import firestore
import hashlib
import datetime

db = firestore.Client(project='gaminig-machines')

class JounalPost(object):
    def __init__(
        self,
        title,
        date,
        content,
        comments=[]
        ):
        self.title = title
        self.date = date
        self.content = content
        self.comments = comments
        

    def to_dict(self):
        dest = {
            u'title':self.title,
            u'date':self.date,
            u'content':self.content,
            u'comments':self.comments
        }
        return dest



class User(object):
    def __init__(
        self, 
        username, 
        password, 
        mental_state=[], 
        communityPositivityScore=[],
        positivityScore=[]
        ):
        self.username = username
        self.password = password
        self.mental_state = mental_state
        self.communityPositivityScore = communityPositivityScore
        self.positivityScore = positivityScore

    def to_dict(self):
        dest = {
            u'username':self.username,
            u'password':self.password,
            u'mental_state': self.mental_state, 
            u'sommunityPositivityScore': self.communityPositivityScore,
            u'positivityScore': self.positivityScore
        }
        return dest

    def __repr__(self):
        return(
            f'User(\
                username={self.username}, \
                password={self.password}, \
                mental_state={self.mental_state}, \
                communityPositivityScore={self.communityPositivityScore}, \
                positivityScore={self.positivityScore} \
            )'
        )

def create_account(
    username, 
    password
    ) -> User:

    #niaive impl of uniqueID
    uuidstr=str(username)
    hashID = hashlib.sha256(uuidstr.encode())
    
    user_ref = db.collection(u'user') #colleciton
    user_ref.document(str(hashID.hexdigest())).set(
        User(username, password).to_dict()
    )

def create_journal(
    userID,
    title,
    date,
    content
    ):
    username = str(userID)
    hashID = hashlib.sha256(username.encode())

    user_ref = db.collection(u'user').document(str(hashID.hexdigest()))
    #embed journal in user
    user_ref.collection(u'posts').document(str(title)).set(
        JounalPost(title, date, content).to_dict()
        )

def add_user(T, U):
    username = T
    password = U
    #query for existing username
    #existing_username = find_account_by_username(username)
    #print(existing_username)
    #query for existing password
   # existing_password = find_account_by_password(password)
   # if existing_username:
     #   error = err(f"Account with username or password already exists.")
     #   return {'ERROR': f'{error}'}
    #if existing_password:
      #  error = err(f"Accout with username of password already exists")
      #  return {'ERROR': f'{error}'}
        
        #storing user_id from endpoint request
    create_account(username, password)

def dummy(request):

    request_json = request.get_json()

    if request_json["action"] == "signup":
        add_user(request_json['username'], request_json['password'])
    

    if request_json["action"] == "postJournal":
        #assuming username exists...
        username = request_json['username']
        #query user
        now = datetime.datetime.now()
        create_journal(username, request_json['title'], now, request_json['content'])

    if request_json['action'] == 'login':
        username = request_json['username']
        password = request_json['password']

        username = str(username)
        hashID = hashlib.sha256(username.encode())


        username_ref = db.collection(u'user').document(str(hashID.hexdigest()))
        doc = username_ref.get() #got user

        if doc.exists:
            password_ref = db.collection(u'user')
            password_check = password_ref.where(u'password', u'==', str(password))
            
            #there is no security here, all users will be able to login NEED TO CHANGE
            #having problems with the right queries. The documentation is not great
            
            if password_check:
                return {"logIn": "ok"}
            else:
                return {"logIn": "fail"}
        else:
            return "no user found"

    return {request_json["action"]: "ok"}
#Todo
#make db connection
#make entrypoint
#make helper functions
#call funcs based off of -d action
