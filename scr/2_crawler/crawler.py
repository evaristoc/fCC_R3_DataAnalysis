def custom_robotparser(botx):
    '''
    False for not allowed
    '''
    try:
        r = requests.get(botx)
    except:
        return False
    ck = [(a.split(':')[0], a.split(':')[1][1:]) for a in r.content.decode('utf8').split('\n')[:-1] if a.find(':')>-1]
    for pair in ck:
        if pair[0] == 'Disallow':
            if pair[1] == '\\':
                return False
    return True
                
def finding_tags(x):
    try:
        r = requests.get(x)
        print("successful status code? ", r.status_code)
    except:
        print('error reaching the page ', x, '; code status ', r.status_code)
        return ['errorreachingpage']*4
    soup = BeautifulSoup(r.content)
    ks = {'description':'noinformationfound', 'keywords': 'noinformationfound', 'title':'noinformationfound', 'htext':'noinformationfound'}
    t = 0
    try:
        ks['title'] = t = soup.title.get_text()
        allmeta = soup.find_all("meta")
        print("found meta data ", len(allmeta))
        for m1a in allmeta:
        #    print(type(m))
            if m1a.attrs.get('name'):
                if m1a.attrs.get('name') == 'description':
                    ks['description'] = m1a.attrs.get('content')
                    #print(ks['description'])
                    break
        for m1b in allmeta:
        #    print(type(m))
            if m1b.attrs.get('property'):
                if m1b.attrs.get('property') == 'og:description':
                    ks['description'] = m1b.attrs.get('content')
                    #print(ks['description'])
                    break
        for m2 in allmeta:
        #    print(type(m))
            if m2.attrs.get('name'):                
                if m2.attrs.get('name') == 'keywords':
                    ks['keywords'] = m2.attrs.get('content')
                    #print(ks['keywords'])
                    break
        #print('the description for ', x, ' is ', m[0])

        fp = soup.find_all("p")
        if fp:
            if ks['htext'] == 'noinformationfound':
                ks['htext'] = fp[0].text + ' '      
        
        fh1 = soup.find_all("h1")
        if fh1:
            if ks['htext'] == 'noinformationfound':
                ks['htext'] = fh1[0].text + ' '
            else:
                ks['htext'] = ks['htext'] + fh1[0].text + ' '        
        
        fh2 = soup.find_all("h2")
        if fh2:
            if ks['htext'] == 'noinformationfound':
                ks['htext'] = fh2[0].text + ' '
            else:
                ks['htext'] = ks['htext'] + fh2[0].text + ' '  

    except:
        #raise
        print('error when finding some information for ', x)
    finally:
        print(ks['title'],ks['description'],ks['keywords'],ks['htext'])
        return ks['title'],ks['description'],ks['keywords'],ks['htext']
        #return desc_and_kw


    #return desc_and_kw


def botcrawler(platform, URL_BASE_1):
    if urllib.parse.urlparse(URL_BASE_1)[0] == '':
        URL_BASE_2 = 'https://'+URL_BASE_1
    #rp = robotparser.RobotFileParser()
    #print(type(rp))
    else:
        print('robot parser failed for ', URL_BASE_1, '\n')
        dbp[platform]['crawlstatus'] = 'err_crawl'
        return
    try:
        print(urllib.parse.urljoin(URL_BASE_2,'/robots.txt'))
        #rp.set_url(urljoin(URL_BASE_2,'/robots.txt'))
        #rp.read()
        #if rp.can_fetch("*", "/") == True:
        if custom_robotparser(urllib.parse.urljoin(URL_BASE_2,'/robots.txt')) == True:
            print('robot parser successful for ', URL_BASE_2, '\n')
            dbp[platform]['minsecurity'] = 'https://'
            dbp[platform]['title'], dbp[platform]['description'], dbp[platform]['keywords'], dbp[platform]['htext'] = finding_tags(URL_BASE_2)
            dbp[platform]['crawlstatus'] = 'ok_crawl'
        else:
            print('bot data collection not allowed for ', URL_BASE_2, '\n')
            dbp[platform]['crawlstatus'] = 'no_crawl'            
    except:
        #raise
        print('robot parser failed for ', URL_BASE_2, '\n')
        dbp[platform]['crawlstatus'] = 'err_crawl'

    if dbp[platform]['crawlstatus'] == 'err_crawl': ##TEMPORARY LINE!!!
        if urllib.parse.urlparse(URL_BASE_1)[0] == '':
            URL_BASE_2 = 'http://'+URL_BASE_1
        #rp = robotparser.RobotFileParser()
        #print(type(rp))
        try:
            print(urllib.parse.urljoin(URL_BASE_2,'/robots.txt'))
            #rp.set_url(urljoin(URL_BASE_2,'/robots.txt'))
            #rp.read()
            #if rp.can_fetch("*", "/") == True or requests.get(urljoin(URL_BASE_2,'/robots.txt')).status_code == 404:
            if custom_robotparser(urllib.parse.urljoin(URL_BASE_2,'/robots.txt')) == True:
                print('robot parser successful for ', URL_BASE_2, '\n')
                dbp[platform]['minsecurity'] = 'http://'
                dbp[platform]['title'], dbp[platform]['description'], dbp[platform]['keywords'], dbp[platform]['htext'] = finding_tags(URL_BASE_2)
                dbp[platform]['crawlstatus'] = 'ok_crawl'
            else:
                print('crawling not allowed for ', URL_BASE_2, '\n')
                dbp[platform]['crawlstatus'] = 'no_crawl'            
        except:
            #raise
            print('robot parser failed for ', URL_BASE_2, '\n')
            dbp[platform]['crawlstatus'] = 'err_crawl'

def completing_db_with_data_from_botandcv(botdata, dbp):
    '''
    db is global for this function
    ''' 
    #cv_subjects = ["1_respwebdesign", "2_javascriptalgos", "3_frontendlibs", "4_dataviz", "5_apismicro", "6_infosec", "7_opensource", "8_extras"]
    cv_subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments']
    cv, bow = bowcv_test()

    for platform in list(dbp.keys()):
        plt = dbp[platform]['origurl']
        for s in cv_subjects:
            dbp[platform]["subjects"][s] = {}
            dbp[platform]["subjects"][s]["proportion"] = 0
            dbp[platform]["subjects"][s]["count"] = 0

        if  dbp[platform]["crawlstatus"] == None:
            print("This platform doesn't have any crawl ", platform, plt)
            botcrawler(platform, plt)
            cvcovering_test(dbp[platform], cv, bow)            
        
        elif botdata != None and plt in list(botdata.keys()):
            dbp[platform]["minsecurity"] = botdata[plt]["minsecurity"]
            dbp[platform]["crawlstatus"] = botdata[plt]["crawlstatus"]
            dbp[platform]["title"] = botdata[plt]["title"]
            dbp[platform]["description"] = botdata[plt]["description"]
            dbp[platform]["keywords"] = botdata[plt]["keywords"]
            dbp[platform]["htext"] = botdata[plt]["htext"]
            
          
            cvcovering_test(dbp[platform], cv, bow)

        else:
            print("This platform not in botdata ", platform, plt)
            botcrawler(platform, plt)
            cvcovering_test(dbp[platform], cv, bow)
            
    
   
    #db = {"textstable":db["textstable"], "cv": db["cv"], "categories": db["categories"]}
                        
    #return db

