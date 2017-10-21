
def pyrebase_conn_test():
    '''
        --- https://firebase.google.com/docs/database/admin/retrieve-data
        --- https://firebase.google.com/docs/auth/web/github-auth
        
        Also:
        --- https://stackoverflow.com/questions/39061866/python-firebase-401-unauthorised-error
        --- https://stackoverflow.com/questions/37922251/firebase-keeps-throwing-oauth2-client-id-in-server-configuration-is-not-found
        --- https://github.com/firebase/functions-samples/tree/master/github-to-slack
        --- https://github.com/firebase/firebase-simple-login
        --- https://ozgur.github.io/python-firebase/
        --- https://www.youtube.com/watch?v=io_r-0e3Qcw
        --- https://blog.devcolor.org/heating-up-with-firebase-tutorial-on-how-to-integrate-firebase-into-your-app-6ce97440175d
    '''
    #import firebase_admin
    import pyrebase

    dbconfig = config.dbconfig

    

    firebase = pyrebase.initialize_app(dbconfig)


    # Get a reference to the database service
    db = firebase.database()

    
    def datacheck(db,*args):
        child1 = args[0]
        cont = []
        if db.child(child1).get().val():
            #print(db.child(child1).get().val())
            print(db.child(child1).get().val().keys())
            for k in db.child(child1).get().val().keys():
                print(k)
                cont.append(k)
        return cont

    return datacheck(db,"platformstable"), datacheck(db, "textstable")



def pyrebase_conn(data):
    '''

        Also:
        --- https://stackoverflow.com/questions/39061866/python-firebase-401-unauthorised-error
        --- https://stackoverflow.com/questions/37922251/firebase-keeps-throwing-oauth2-client-id-in-server-configuration-is-not-found
        --- https://github.com/firebase/functions-samples/tree/master/github-to-slack
        --- https://github.com/firebase/firebase-simple-login
        --- https://ozgur.github.io/python-firebase/
        --- https://firebase.google.com/docs/auth/web/github-auth
        --- https://www.youtube.com/watch?v=io_r-0e3Qcw
        --- https://blog.devcolor.org/heating-up-with-firebase-tutorial-on-how-to-integrate-firebase-into-your-app-6ce97440175d
        --- https://stackoverflow.com/questions/40613907/how-can-i-pull-nested-json-values-from-python-using-dictionaries
    '''
    #import firebase_admin
    import pyrebase

    dbconfig = config.dbconfig

    

    firebase = pyrebase.initialize_app(dbconfig)
    
    def authenitcation():
        #authenticate a user
        email = config.email
        password = config.passport
        #auth.create_user_with_email_and_password(email, password)
        #Get a reference to the auth service
        # Log the user in
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(email, password)

        return user
    
    
    user = authenitcation()

    # Get a reference to the database service
    db = firebase.database()

    pt, tt = pyrebase_conn_test()
    
    def datacreation(db, user, data):
        #data to save
        # exampledata = {
        #     "name": "Mortimer 'Morty' Smith"
        # }
        
        
        db.child("fcc_subjects").push(data["fcc_subjects"], user['idToken'])
        
        db.child("plt_categories").push(data["plt_categories"], user['idToken'])
        
        db.child("users").push(data["userstable"], user['idToken'])
        
        for i, record in enumerate(data["platformstable"]):
            print(record)
            if record not in pt:
                db.child("platformstable").child(record).push(dict([(x,y) for x,y in data["platformstable"][record].items() if x != "subjects"]), user['idToken'])
                for s in data["platformstable"][record]['subjects']:
                    db.child("platformstable").child(record).child('subjects').child(s).push(data["platformstable"][record]['subjects'][s], user['idToken'])
                
        for i, record in enumerate(data["textstable"]):
            print(record)
            if record not in tt:
                db.child("textstable").child(record).push(dict([(x,y) for x,y in data["textstable"][record].items()]), user['idToken'])
        

    # def datacreation(db, user, data):
    #     '''
    #     TEMPORARY!!
    #     '''
    #     
    #     #data to save
    #     # exampledata = {
    #     #     "name": "Mortimer 'Morty' Smith"
    #     # }
    #     
    #     db.child("plt_categories").push(data["plt_categories"], user['idToken'])
    #     
    #     for i, record in enumerate(data["platformstable"]):
    #         print(record)
    #         if record not in pt:
    #             db.child("platformstable").child(record).push(dict([(x,y) for x,y in data["platformstable"][record].items() if x != "subjects"]), user['idToken'])
    #             for s in data["platformstable"][record]['subjects']:
    #                 db.child("platformstable").child(record).child('subjects').child(s).push(data["platformstable"][record]['subjects'][s], user['idToken'])
    #             
    #     for i, record in enumerate(data["textstable"]):
    #         print(record)
    #         if record not in tt:
    #             db.child("textstable").child(record).push(dict([(x,y) for x,y in data["textstable"][record].items()]), user['idToken'])
    #     
        
    etl_formattingsetstolists()
    
    datacreation(db, user, data)

