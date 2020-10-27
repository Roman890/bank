import requests_html
from bs4 import BeautifulSoup
import pickle
import requests

px_list = set()
try:
    with open('proxis.pickle', 'rb') as f:
            px_list = pickle.load(f)
except:
    pass
	
	
	
def scrap_proxy():  
    global px_list
    px_list = set()

    session = requests_html.HTMLSession()
    r = session.get('https://free-proxy-list.net/')
    r.html.render()
    for i in range(1, 21):
        add=r.html.xpath('/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[1]/text()'.format(i))[0]
        port=r.html.xpath('/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[2]/text()'.format(i))[0]
        px_list.add(':'.join([add, port]))

    print("---New proxy scraped, left: " + str(len(px_list)))
    with open('proxis.pickle', 'wb') as f:
        pickle.dump(px_list, f)
    return px_list
	
	
def check_proxy(px):
    try:
        requests.get("https://www.google.com/", proxies = {"https": "https://" + px}, timeout = 3)
    except Exception as x:
        print('--'+px + ' is dead: '+ x.__class__.__name__)
        return False
    return True
	
	
def get_proxy(scrap = False):
    global px_list
    if scrap or len(px_list) < 6:
            px_list = scrap_proxy()
    while True:
        if len(px_list) < 6:
            px_list = scrap_proxy()
        px = px_list.pop()
        if check_proxy(px):
            break
    print('-'+px+' is alive. ({} left)'.format(str(len(px_list))))
    with open('proxis.pickle', 'wb') as f:
            pickle.dump(px_list, f)
    return px