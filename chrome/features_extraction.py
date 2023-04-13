# Purpose -
# Running this file (stand alone) - For extracting all the features from a web page for testing.
# Notes -
# 1 stands for legitimate
# 0 stands for suspicious
# -1 stands for phishing
"""
1. Shortened URL
2. Redirect
"""
# Path of your local server. Different for different OSs.
LOCALHOST_PATH = "/home/haphuong/Documents/"
DIRECTORY_NAME = "2_Chrome_extension_detect_phishing_URL"

import sys
import os
import requests
from subprocess import *
from bs4 import BeautifulSoup
import json
import base64

# !pip install python-whois

from urllib.parse import urlparse
import favicon
import xml.etree.ElementTree as ET 
import tldextract
import datetime
from dateutil.relativedelta import relativedelta
import whois

"""Check IP and Hexa"""

def to_find_having_ip_add(url):
  import string
  index = url.find("://")
  split_url = url[index+3:]
  # print(split_url)
  index = split_url.find("/")
  split_url = split_url[:index]
  # print(split_url)
  split_url = split_url.replace(".", "")
  # print(split_url)
  counter_hex = 0
  for i in split_url:
    if i in string.hexdigits:
      counter_hex +=1

  total_len = len(split_url)
  having_IP_Address = 1
  if counter_hex >= total_len:
    having_IP_Address = -1

  return having_IP_Address

"""URL_len"""

def to_find_url_len(url):
  URL_Length = 1
  if len(url)>=75:
    URL_Length = -1
  elif len(url)>=54 and len(url)<=74:
    URL_length = 0
  
  return URL_Length

"""Shortened URL extraction"""

def get_complete_URL(shortened_url):
  command_stdout = Popen(['curl', shortened_url], stdout=PIPE).communicate()[0]
  output = command_stdout.decode('utf-8')
  href_index = output.find("href=")
  if href_index == -1:
    href_index = output.find("HREF=")
  splitted_ = output[href_index:].split('"')
  expanded_url = splitted_[1]
  return expanded_url

def check_for_shortened_url(url):
  famous_short_urls = ["bit.ly", "tinyurl.com", "goo.gl",
                       "rebrand.ly", "t.co", "youtu.be",
                       "ow.ly", "w.wiki", "is.gd"]

  domain_of_url = url.split("://")[1]
  domain_of_url = domain_of_url.split("/")[0]
  status = 1
  if domain_of_url in famous_short_urls:
    status = -1

  complete_url = None
  if status == -1:
    complete_url = get_complete_URL(url)

  return (status, complete_url)

"""@ in URL"""

def to_find_at(url):
  label = 1
  index = url.find("@")
  if index!=-1:
    label = -1
  
  return label

"""Redirect"""

def to_find_redirect(url):
  index = url.find("://")
  split_url = url[index+3:]
  label = 1
  index = split_url.find("//")
  if index!=-1:
    label = -1
  
  return label

""""-" in domain"""

def to_find_prefix(url):
  index = url.find("://")
  split_url = url[index+3:]
  # print(split_url)
  index = split_url.find("/")
  split_url = split_url[:index]
  # print(split_url)
  label = 1
  index = split_url.find("-")
  # print(index)
  if index!=-1:
    label = -1
  
  return label

"""Multi-domains presence"""

def to_find_multi_domains(url):
  url = url.split("://")[1]
  url = url.split("/")[0]
  index = url.find("www.")
  split_url = url
  if index!=-1:
    split_url = url[index+4:]
  # print(split_url)
  index = split_url.rfind(".")
  # print(index)
  if index!=-1:
    split_url = split_url[:index]
  # print(split_url)
  counter = 0
  for i in split_url:
    if i==".":
      counter+=1
  
  label = 1
  if counter==2:
    label = 0
  elif counter >=3:
    label = -1
  
  return label

"""Authority"""

def to_find_authority(url):
  index_https = url.find("https://")
  valid_auth = ["GeoTrust", "GoDaddy", "Network Solutions", "Thawte", "Comodo", "Doster" , "VeriSign", "LinkedIn", "Sectigo",
                "Symantec", "DigiCert", "Network Solutions", "RapidSSLonline", "SSL.com", "Entrust Datacard", "Google", "Facebook"]
  
  cmd = "curl -vvI " + url

  stdout = Popen(cmd, shell=True, stderr=PIPE, env={}).stderr
  output = stdout.read()
  std_out = output.decode('UTF-8')
  # print(std_out)
  index = std_out.find("O=")

  split = std_out[index+2:]
  index_sp = split.find(" ")
  cur = split[:index_sp]
  
  index_sp = cur.find(",")
  if index_sp!=-1:
    cur = cur[:index_sp]
  print(cur)
  label = -1
  if cur in valid_auth and index_https!=-1:
    label = 1
  
  return label

"""Submitting to Email"""

def check_submit_to_email(url):
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, "lxml")
  # Check if no form tag
  form_opt = str(soup.form)
  idx = form_opt.find("mail()")
  if idx == -1:
    idx = form_opt.find("mailto:")

  if idx == -1:
    return 1
  return -1

"""https as part of domain"""

def existenceoftoken(u):
    # Assumption - pagename cannot start with this token
    ix = u.find("//https")
    if(ix==-1):
        return 1
    else:
        return -1

"""Domain registration Length"""

def dregisterlen(u):
    extract_res = tldextract.extract(u)
    ul = extract_res.domain + "." + extract_res.suffix
    try:
        wres = whois.whois(u)
        f = wres["Creation Date"][0]
        s = wres["Registry Expiry Date"][0]
        if(s>f+relativedelta(months=+12)):
            return 1
        else:
            return -1
    except:
        return -1

"""SFH"""

def sfh(u):
    programhtml = requests.get(u).text
    s = BeautifulSoup(programhtml,"lxml")
    try:
        f = str(s.form)
        ac = f.find("action")
        if(ac!=-1):
            i1 = f[ac:].find(">")
            u1 = f[ac+8:i1-1]
            if(u1=="" or u1=="about:blank"):
                return -1
            er1 = tldextract.extract(u)
            upage = erl.domain
            erl2 = tldextract.extract(u1)
            usfh = erl2.domain
            if upage in usfh:
                return 1
            return 0
        else:
            # Check this point
            return 1
    except:
        # Check this point
        return 1

"""Tags"""

def tags(u):
    programhtml = requests.get(u).text
    s = BeautifulSoup(programhtml,"lxml")
    mtags = s.find_all('Meta')
    ud = tldextract.extract(u)
    upage = ud.domain
    mcount = 0
    for i in mtags:
        u1 = i['href']
        currpage = tldextract.extract(u1)
        u1page = currpage.domain
        if currpage not in ulpage:
            mcount+=1
    scount = 0
    stags = s.find_all('Script')
    for j in stags:
        u1 = j['href']
        currpage = tldextract.extract(u1)
        u1page = currpage.domain
        if currpage not in u1page:
            scount+=1
    lcount = 0
    ltags = s.find_all('Link')
    for k in ltags:
        u1 = k['href']
        currpage = tldextract.extract(u1)
        u1page = currpage.domain
        if currpage not in u1page:
            lcount+=1
    percmtag = 0
    percstag = 0
    percltag = 0

    if len(mtags) != 0:
      percmtag = (mcount*100)//len(mtags)
    if len(stags) != 0:
      percstag = (scount*100)//len(stags)
    if len(ltags) != 0:
      percltag = (lcount*100)//len(ltags)
      
    if(percmtag+percstag+percltag<17):
        return 1
    elif(percmtag+percstag+percltag<=81):
        return 0
    return -1

"""Redirect"""

def url_validator(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def redirect(url):
  opt = Popen(["sh", "./red.sh", url], stdout=PIPE).communicate()[0]
  opt = opt.decode('utf-8')
  # print(opt)
  opt = opt.split("\n")
  
  new = []
  for i in opt:
    i = i.replace("\r", " ")
    new.extend(i.split(" "))
  

  count = 0
  for i in new:
   
    if i.isdigit():
      conv = int(i)
      if conv > 300 and conv<310:
        count += 1

  last_url = None
  for i in new[::-1]:
    if url_validator(i):
      last_url = i
      break

  if (count<=1):
    return 1, last_url
  elif count>=2 and count <4:
    return 0, last_url
  return -1, last_url

# url = "https://bit.ly/segfault"

# redirect(phish_url2)

"""Statistical Reports"""

def check_statistical_report(url):
  try:
      ip_address = socket.gethostbyname(hostname)
  except:
      return -1
  url_match = re.search(
      r'at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly', url)
  ip_match = re.search(
        '146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
        '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
        '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
        '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
        '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
        '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',
        ip_address)
  if url_match:
      return -1
  elif ip_match:
      return -1
  else:
      return 1

# check_statistical_report("https://oxify.me/tuT2y")

"""PageRank"""

# !pip install tldextract
def get_pagerank(url):
  pageRankApi = open('/home/haphuong/Documents/2_Chrome_extension_detect_phishing_URL/API_Keys/pageRankApi').readline()[:-2]
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain + "." + extract_res.suffix
  headers = {'API-OPR': pageRankApi}
  domain = url_ref
  req_url = 'https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D=' + domain
  request = requests.get(req_url, headers=headers)
  result = request.json()
  # print(result)
  value = result['response'][0]['page_rank_decimal']
  if type(value) == str:
    value = 0

  if value < 2:
    return -1
  return 1

# get_pagerank("https://linked.in")

"""Web traffic"""

def check_web_traffic(url):
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain + "." + extract_res.suffix
  html_content = requests.get("https://www.alexa.com/siteinfo/" + url_ref).text
  soup = BeautifulSoup(html_content, "lxml")
  value = str(soup.find('div', {'class': "rankmini-rank"}))[42:].split("\n")[0].replace(",", "")

  if not value.isdigit():
    return -1

  value = int(value)
  if value < 100000:
    return 1
  return 0

# url = "https://hokk-i.com"

# check_web_traffic(url)

"""DNS Record"""

# !apt-get install whois

# !pip install python-whois

def check_dns_record(url):
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain + "." + extract_res.suffix
  try:
    whois_res = whois.whois(url)
    return 1
  except:
    return -1



# url = "google.com"
# check_dns_record(url)

"""Age of Domain"""

# url = "hokk-i.com"

def check_age_of_domain(url):
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain + "." + extract_res.suffix
  try:
    whois_res = whois.whois(url)
    if datetime.datetime.now() > whois_res["creation_date"][0] + relativedelta(months=+6):
      return 1
    else:
      return -1
  except:
    return -1

# check_age_of_domain(url)

"""IFrame"""

# url = 'https://xavier-net.gq/?login=do'

def check_iframe(url):
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, "lxml")
  if str(soup.iframe).lower().find("frameborder") == -1:
    return 1
  return -1

# check_iframe("https://www.google.com")



"""Rightclick"""

def check_rightclick(url):
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, "lxml")
  if str(soup).lower().find("preventdefault()") != -1:
    return -1
  elif str(soup).lower().find("event.button==2") != -1:
    return -1
  elif str(soup).lower().find("event.button == 2") != -1:
    return -1
  return 1

# check_rightclick(url)

"""On mouseover"""

def check_onmouseover(url):
  try:
    html_content = requests.get(url).text
  except:
    return -1
  soup = BeautifulSoup(html_content, "lxml")
  if str(soup).lower().find('onmouseover="window.status') != -1:
    return -1
  return 1

# url = "https://google.com"
# check_onmouseover(url)

"""Favicon"""

# !pip install favicon
def check_favicon(url):
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain

  favs = favicon.get(url)
  # print(favs)
  match = 0
  for favi in favs:
    url2 = favi.url
    extract_res = tldextract.extract(url2)
    url_ref2 = extract_res.domain

    if url_ref in url_ref2:
      match += 1

  if match >= len(favs)/2:
    return 1
  return -1

# url = "https://www.iiitd.ac.in"
# check_favicon(url)

"""Request URL"""

def check_request_URL(url):
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain

  command_stdout = Popen(['curl', 'https://api.hackertarget.com/pagelinks/?q=' + url], stdout=PIPE).communicate()[0]
  links = command_stdout.decode('utf-8').split("\n")

  count = 0

  for link in links:
    extract_res = tldextract.extract(link)
    url_ref2 = extract_res.domain

    if url_ref not in url_ref2:
      count += 1

  count /= len(links)

  if count < 0.22:
    return 1
  elif count < 0.61:
    return 0
  else:
    return -1

# url = "https://xavier-net.gq/?login=do"

# check_request_URL(url)

"""URL of Anchor"""

def check_URL_of_anchor(url):
  extract_res = tldextract.extract(url)
  url_ref = extract_res.domain
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, "lxml")
  a_tags = soup.find_all('a')

  if len(a_tags) == 0:
    return 1

  invalid = ['#', '#content', '#skip', 'JavaScript::void(0)']
  bad_count = 0
  for t in a_tags:
    try:
      link = t['href']
    except KeyError:
      continue

    if link in invalid:
      bad_count += 1

    if url_validator(link):
      extract_res = tldextract.extract(link)
      url_ref2 = extract_res.domain

      if url_ref not in url_ref2:
        bad_count += 1

  bad_count /= len(a_tags)

  if bad_count < 0.31:
    return 1
  elif bad_count <= 0.67:
    return 0
  return -1

def get_hostname_from_url(url):
    hostname = url
    # TODO: Put this pattern in patterns.py as something like - get_hostname_pattern.
    pattern = "https://|http://|www.|https://www.|http://www."
    pre_pattern_match = re.search(pattern, hostname)

    if pre_pattern_match:
        hostname = hostname[pre_pattern_match.end():]
        post_pattern_match = re.search("/", hostname)
        if post_pattern_match:
            hostname = hostname[:post_pattern_match.start()]
    return hostname

def extract_features(url):
  features_extracted = [0]*25
  phStatus, expanded = check_for_shortened_url(url)
  features_extracted[2] = phStatus
  phStatus, last_url = redirect(url)
  features_extracted[16] = phStatus
  if expanded is not None:
    if len(expanded) >= len(url):
      url = expanded

  if last_url is not None:
    if len(last_url) > len(url):
      url = last_url
  # print(url)
  features_extracted[0] = to_find_having_ip_add(url)
  features_extracted[1] = to_find_url_len(url)
  features_extracted[3]  = to_find_at(url)
  features_extracted[4] = to_find_redirect(url)
  features_extracted[5] = to_find_prefix(url)
  features_extracted[6] = to_find_multi_domains(url)
  features_extracted[7] = to_find_authority(url)
  features_extracted[8] = dregisterlen(url)
  features_extracted[9] = check_favicon(url)
  features_extracted[10] = existenceoftoken(url)
  features_extracted[11] = check_request_URL(url)
  features_extracted[12] = check_URL_of_anchor(url)
  features_extracted[13] = tags(url)
  features_extracted[14] = sfh(url)
  features_extracted[15] = check_submit_to_email(url)
  features_extracted[17] = check_onmouseover(url)
  features_extracted[18] = check_rightclick(url)
  features_extracted[19] = check_iframe(url)
  features_extracted[20] = check_age_of_domain(url)
  features_extracted[21] = check_dns_record(url)
  features_extracted[22] = check_web_traffic(url)
  features_extracted[23] = get_pagerank(url)
  features_extracted[24] = check_statistical_report(url)

  return features_extracted

# valid_url = "https://cse.iiitd.ac.in/"

# phish_url = "https://xavier-net.gq/?login=do"

# valid_url2 = "https://bit.ly/segfault"

# phish_url2 = "http://125.98.3.123/fake.html"

def main(url):
    with open(LOCALHOST_PATH + DIRECTORY_NAME + '/markup.txt', 'r') as file:
        soup_string = file.read()

    soup = BeautifulSoup(soup_string, 'html.parser')
    features_extracted = extract_features(url)
#    hostname = get_hostname_from_url(url)
    print('\n1. Having IP address\n2. URL Length\n3. URL Shortening service\n4. Having @ symbol\n'
          '5. Having double slash\n6. Having dash symbol(Prefix Suffix)\n7. Having multiple subdomains\n'
          '8. SSL final state\n9. Domain Registration Length\n10. Favicon\n11. HTTP or HTTPS token in domain name\n'
          '12. Request URL\n13. URL of Anchor\n14. Links in tags\n15. SFH\n16. Submitting to email\n17. Abnormal URL\n'
          '18. OnMouse Change Status\n19. Right click\n20. IFrame\n21. Age of Domain\n22. DNS Record\n'
          '23. Web Traffic\n24. Page rank\n25. Statistical Reports\n')
    print(features_extracted)
    return features_extracted

#if __name__ == "__main__":
#     if len(sys.argv) != 2:#         print("Please use the following format for the command - `python2 features_extraction.py <url-to-be-tested>`")
#         exit(0)
#     main(sys.argv[1])
