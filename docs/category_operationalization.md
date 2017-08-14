## Categories' Operationalization


A file in this folder shows the corresponding definitions made so far for the different categories.

* CSV file
* ':' as delimiter
* Columns:
 * Name: name that will be given to the category
 * Regex: regex originally used to create the firt pivot training dataset
 * Definition: operationalization of the the category


A recent correction (Aug-2017) of the database categories:
```
    ###### CORRECTING botdata #####
    ad = pandas.read_csv(os.getcwd()+annotdata, delimiter=';', quotechar="'")
    #v = db['platformstable'][list(db['platformstable'].keys())[0]]['origurl']
    #ad.loc[ad['platform'] == v, :]
    cats = [('ECOMMERCE','shop|commerce'), ('COMMUNITY','community|support|people|forum'), ('REPL','(text )?editor|interpreter|repl'), ('TRAINING','learn|tutorial|course|training| tips|example'), ('WRCOTENT','blog|media|news|articl|content|post|journal'), ('PACKAGE','api|package|framework|librar|stack|licens|addon|app'), ('THEME','design|galler|template|theme'), ('PAAS','cloud|platform|service'), ('BUSINESS','on?(-|\s)?demand|business|compan(y|ies)|enterprise'), ('DOCS','manual|guide|docs'), ('SENGINE','search tools'), ('NOCLASS','---'), ('REVIEWS','review')]
    catsdict = dict(cats)
    notok = []
    notoksetct = set()
    notoksetpdct = set()
    corrected = 0
    for rec in db['platformstable']:
        plat = db['platformstable'][rec]['origurl']
        ct = db['platformstable'][rec]['category']
        if ct is not None:
            print(ct)
            if ct in list(catsdict.values()):
                db['platformstable'][rec]['category'] = [k for k, v in catsdict.items() if v == ct]
                db['platformstable'][rec]['cat_regex'] = ct
                print(plat, ' CORRECTED FOR ct', ct)
                corrected += 1
            else:
                notoksetct.update([ct])
        else:
            pdct = tuple(ad.loc[ad['platform'] == plat, 'category'])[0]
            if pdct is not None:
                print(pdct)
                if pdct in list(catsdict.keys()):
                    db['platformstable'][rec]['category'] = pdct
                    db['platformstable'][rec]['category'] = catsdict[pdct]
                    print(plat, ' CORRECTED FOR pdct', pdct)
                    corrected += 1
                else:
                    notoksetpdct.update([pdct])
    #corrected 616 and notoksetpdct = {'NEWS','COMMUITY'}
    
    corrected2 = 0    
    for rec in db['platformstable']:
        plat = db['platformstable'][rec]['origurl']
        ct = db['platformstable'][rec]['category']
        if ct is None:
            pdct = tuple(ad.loc[ad['platform'] == plat, 'category'])[0]
            if pdct == 'NEWS':
                print(pdct)
                db['platformstable'][rec]['category'] = 'WRCOTENT'
                corrected2 += 1
            elif pdct == 'COMMUITY':
                print(pdct)
                db['platformstable'][rec]['category'] = 'COMMUNITY'
                corrected2 += 1
    #corrected 394

    counter = 0
    for rec in db['platformstable']:
        #print(db['platformstable'][rec])
        if 'subjects' not in list(db['platformstable'][rec].keys()):
            print(rec)
            counter += 1
    
    #counter3 0


```
