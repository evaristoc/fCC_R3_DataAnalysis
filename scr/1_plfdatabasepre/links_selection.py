def links_analysis(raw):
    d = {} #net location : [params, query, user, sent]    
    for elem in raw:
        if elem["fromUser"]["username"] == "camperbot": continue

        for u in elem["urls"]:
            url = u['url']
            try:
                netloc,params,urlq = urllib.parse.urlsplit(url)[1:4]
            except:
                print(url)
                continue

            if netloc in ("files.gitter.im", "gitter.im", "codepen.io", "reddit.com", "www.youtube.com", "github.com"): continue
            if netloc not in list(d.keys()):
                d[netloc] = []
            #d[netloc].append({'params':params, 'urlq':urlq, 'user':elem['fromUser']['username'], 'urls': elem['urls'], 'text': elem['text'], 'sent': elem['sent']})
            d[netloc].append({'params':params, 'urlq':urlq, 'user':elem['fromUser']['username'], 'urls': elem['urls'], 'url1': url, 'text': elem['text'], 'sent': elem['sent']})
    
 
    b = set()
    dd = {} #first_param:{last,count}
    for ll in d.keys():
        for l in d[ll]:
            params = l['params']
            if len(params.split('/')) > 2:
                first_param = ll
                date = l['sent'].split('-')
                year = int(date[0])
                month = int(date[1])
                day = int(date[2].split('T')[0])
                current = datetime.datetime(year, month, day)
                if params.find('FreeCodeCamp')==-1:
                    #print(params)
                    #if params != '':
                    #    b.add(params.split('/')[1])
                    if first_param not in dd:
                        dd[first_param] = {}
                        dd[first_param]['count1'] = 1
                        if year == 2016:
                            dd[first_param]['count2'] = month - 6
                        elif year == 2017:
                            dd[first_param]['count2'] = month + 7
                        dd[first_param]['last'] = current
                        dd[first_param]['repos'] = {}
                    if params not in dd[first_param]['repos']: 
                        dd[first_param]['repos'][params] = {}
                        dd[first_param]['repos'][params]['count1'] = 1
                        dd[first_param]['repos'][params]['texts'] = []
                        dd[first_param]['repos'][params]['users'] = []
                        dd[first_param]['repos'][params]['urls'] = []
                        if year == 2016:
                            dd[first_param]['repos'][params]['count2'] = month - 6
                        elif year == 2017:
                            dd[first_param]['repos'][params]['count2'] = month + 7
                        dd[first_param]['repos'][params]['last'] = current
                        dd[first_param]['repos'][params]['texts'].append(l['text'])
                        dd[first_param]['repos'][params]['users'].append(l['user'])
                        dd[first_param]['repos'][params]['urls'].append(l['urls'])
    
                    if current - dd[first_param]['last'] >= datetime.timedelta(days=1):
                        dd[first_param]['count1'] += 1
                        if year == 2016:
                            dd[first_param]['count2'] += month - 6
                        if year == 2017:
                            dd[first_param]['count2'] += month + 7
                        dd[first_param]['last'] = current
                    if current - dd[first_param]['repos'][params]['last'] >= datetime.timedelta(days=1):
                        dd[first_param]['repos'][params]['count1'] += 1
                        if year == 2016:
                            dd[first_param]['repos'][params]['count2'] += month - 6
                        elif year == 2017:
                            dd[first_param]['repos'][params]['count2'] += month + 7
                        dd[first_param]['repos'][params]['last'] = current                        
                        dd[first_param]['repos'][params]['texts'].append(l['text'])
                        dd[first_param]['repos'][params]['users'].append(l['user'])
                        dd[first_param]['repos'][params]['urls'].append(l['urls'])
        
    for k in sorted(dd, key=lambda k: dd[k]['last'].timestamp(), reverse=False):
        if dd[k]['count1'] > 5:
            print("link: {0} -- counts: {1}, weighted counts: {2}; rating: {3:.2f}".format(k, dd[k]['count1'], dd[k]['count2'], 100*dd[k]['count2']/(11*dd[k]['count1'])))
    
    return d, dd


