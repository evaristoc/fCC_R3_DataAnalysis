#OJO INSERT SOURCE HERE!!!
def links_extraction_phase1(raw, source, annotdata):
    '''
    db is global for this function
    '''    
    #classedplatforms = dict([(obj['platform'], obj['newclass']) for obj in csv.DictReader(open(datadirectory+'/categoriesplatformsphase1.csv'))])
    classedplatforms = dict([(obj['platform'], obj['category']) for obj in csv.DictReader(open(os.getcwd()+annotdata, 'r'), delimiter=';', quotechar="'")])
    
    print(len(classedplatforms))
    #print(list(classedplatforms.keys()))
    
    # if 'azmind.com' in list(classedplatforms.keys()):
    #     print('azmind.com is in classedplatforms')
    
    classedplatforms['medium.freecodecamp.com'] = 'blog|media|news|articl|content|post|journal'
    classedplatforms['forum.freecodecamp.com'] = 'community|support|people|forum'    
    
    #net location : [params, query, user, sent]    
    for elem in raw:
        if elem["fromUser"]["username"] == "camperbot":
            continue

        for u in elem["urls"]:
            url = u['url']
            try:
                platform,params,urlq = urllib.parse.urlsplit(url)[1:4]
            except:
                print(url)
                continue

            #assert platform != 'azmind.com', (platform, source)
            
            #if platform not in list(classedplatforms.keys()): #<--------------------- USE THIS IS SEARCHING FOR NEW!!
            if platform in list(classedplatforms.keys()):      #<--------------------- USE THIS IS SEARCHING FOR THE ALREADY SELECTED ONLY!!
                #print(platform)
                assert platform, print(plaftform)
                
                if platform == 'forum.freecodecamp.com' and params in ["/fcc-relaxing-cat", "/t/free-code-camp-official-chat-rooms/19390", "/t/free-code-camp-official-chat-rooms", "/t/free-code-camp-brownie-points/18380", "/t/markdown-code-formatting/18391"]:
                    continue

                if url_elimination(platform, url, params) == True:
                    continue

                #platformstable
                plt = platform
                platform = platform.replace('.','--')
                
                if platform not in list(db['platformstable'].keys()):
                    
                    
                    
                    db["platformstable"][platform] = {}
                    db["platformstable"][platform]["origurl"] = plt
                    db["platformstable"][platform]["category"] = None
                    # if classedplatforms[plt] in ['learn|tutorial|course|training|tips|example', 'learn|tutorial|course|training|']:
                    #     db["platformstable"][platform]["category"] = 'learn|tutorial|course|training| tips|example'
                    # elif classedplatforms[plt] in ['(text)?editor|interpreter|repl']:
                    #     db["platformstable"][platform]["category"] = '(text )?editor|interpreter|repl'
                    # else:
                    #     db["platformstable"][platform]["category"] = classedplatforms[plt].strip(" ")
                    db["platformstable"][platform]["frequency-recency"] = []
                    db["platformstable"][platform]["subjects"] = {}
                    db["platformstable"][platform]["minsecurity"] = None
                    db["platformstable"][platform]["crawlstatus"] = None
                    db["platformstable"][platform]["title"] = None
                    db["platformstable"][platform]["description"] = None
                    db["platformstable"][platform]["keywords"] = None
                    db["platformstable"][platform]["htext"] = None
                    db["platformstable"][platform]["params"] = set()
                    db["platformstable"][platform]["textids"] = set()
                    db["platformstable"][platform]["users"] = set()
                    db["platformstable"][platform]["created"] = ""
                    db["platformstable"][platform]["modified"] = ""
                db['platformstable'][platform]['params'].update([params])
                db["platformstable"][platform]["textids"].update([elem["id"]])
                #calculation of frequency-recency (formerly wrongly named "prevalence")
                date = elem['sent'].split('-')
                year = int(date[0])
                month = int(date[1])
                day = int(date[2].split('T')[0])
                current = datetime.datetime(year, month, day)
                if year == 2016:
                    db["platformstable"][platform]['frequency-recency'].append(month - 6)
                elif year == 2017:
                    db["platformstable"][platform]['frequency-recency'].append(month + 7)

                #textstable
                # if elem["id"] not in db["textstable"].keys():
                #     db["textstable"][elem["id"]] = {}
                #     db["textstable"][elem["id"]]["text"] = elem["text"]
                #     db["textstable"][elem["id"]]["source"] = source
                #     db["textstable"][elem["id"]]["user"] = elem["fromUser"]["username"]
                #     db["textstable"][elem["id"]]["sent"] = elem["sent"]
                #     db["textstable"][elem["id"]]["prestige"] = 1
                #     db["textstable"][elem["id"]]["urls"] = elem["urls"]
                #     db["textstable"][elem["id"]]["platforms"] = set()
                #     db["textstable"][elem["id"]]["created"] = ""
                #     db["textstable"][elem["id"]]["modified"] = ""
                # db["textstable"][elem["id"]]["platforms"].update((platform, "sentiment"))

                #userstable
                if elem['fromUser']['username'] not in list(db['userstable'].keys()):
                    db['userstable'][elem['fromUser']['username']] = set()
                db['userstable'][elem['fromUser']['username']].update([platform])  
    #return db