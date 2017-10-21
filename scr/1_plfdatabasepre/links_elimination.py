def url_elimination(netloc, url, params):
    #OJO with first pattern!!!! it was preventing further readings!! too strict
    pattern01 = re.compile(r'html|css|javascript|js|node\.?js?|angular|react\.?js?|bootstrap|jquery', flags=re.IGNORECASE)
    pattern02 = re.compile(r'(\b$|\\$|(([a-z]+\.)?(google|freecatphotoapp|twitch|gitter|codepen|youtube|github|freecodecamp|massdrop-s3\.imgix|imgur|walmart|googleusercontent|youtu|s-media-cache-ak0|pinimg|quisk|quisk|flickr)(\.[a-z]+)))', flags=re.IGNORECASE)
    pattern03 = re.compile(r'herokuapp|postimg|prnt|kym-cdn|imgflip|instagram|twimg|gyazo|bp\.blogspot|@', flags=re.IGNORECASE)
    pattern04 = re.compile(r'meme|\.(gif|jpeg|jpg|png)$',flags=re.IGNORECASE)

    notpassed = True
    passed = False

    if netloc in ("files.gitter.im", "gitter.im", "codepen.io", "reddit.com", "www.youtube.com", "github.com"):
        return notpassed   
   
    ##domains that I don't want (OJO: ALWAYS compiled as (xxx.)?DOMAINNAME(.xxx)) OR words that I don't want in the domain
    
    if re.match(pattern02, netloc) != None or re.search(pattern03, netloc) != None:
        #print(re.match(pattern02, netloc), re.match(pattern03, netloc))
        return notpassed
    
    ##extensions that either don't want or should be conditioned
    if re.search(pattern04, url):
        return notpassed
    if url.find(".js") > -1:
        if url.replace(".js", "").find("js") == -1:
            return notpassed
    if url.find(".html") > -1:
        if url.replace(".html", "").find("html") == -1:
            return notpassed
    
    ##urls with a good domain but an unaccepted param
    if params in ("/fcc-relaxing-cat", "/t/free-code-camp-official-chat-rooms/19390", "/t/free-code-camp-official-chat-rooms", "/t/free-code-camp-brownie-points/18380", "/t/markdown-code-formatting/18391"):
        return notpassed
    
    if re.search(pattern01, url):
        return passed
    else:
        return notpassed