import numpy as np 
import pandas as pd 

from time import sleep

from math import log
from re import compile
from urllib.parse import urlparse
from socket import gethostbyname
from pyquery import PyQuery
from requests import get
from json import dump
from string import ascii_lowercase
from numpy import array


from urllib.parse import urlparse
from pyquery import PyQuery
from requests import get
from socket import gethostbyname
from numpy import array, log
from string import punctuation
from json import dump, loads
from re import compile
import requests


from whois import whois
from waybackpy import Cdx
from socket import gethostbyname
from shodan import Shodan
from requests import get
from urllib.parse import urlparse
from datetime import datetime
from re import compile
from json import dump, loads
from time import sleep

### Lexical Features

def __get_alexa_top_50():
    pq = PyQuery(get('https://www.alexa.com/topsites').content)
    items = pq('.site-listing .DescriptionCell p a')
    sites = [i.text().lower() for i in items.items()]
    return sites

alexa_50 = __get_alexa_top_50()


class alexa_similarity:
    def __init__(self, url):
        self.alexa50 = alexa_50
        self.url = url

    '''Remove none numeric or alphabetic characters from URL strings'''
    def clean_url(self, url):
        url = ''.join([i for i in url.lower() if i.isalpha() or i.isalpha()])
        return url

    '''Get list of common characters between two URL strings'''
    def similar_string_score(self, string1:str, string2: str):
        string1, string2 = string1.lower(), string2.lower()
        return list(set(string1) & set(string2))

    '''count the frequency occurance of common charaters in both strings'''
    def count_freq_similar(self, string1: str, string2: str):
        sims = self.similar_string_score(string1, string2)
        if len(sims) == 0:
            return 0
        sim1 = [string1.count(i) for i in sims]
        sim2 = [string2.count(i) for i in sims]
        a = sum(abs(array(sim1) - array(sim2)))
        return a

    '''Get the ascii positional index of a letter'''
    def get_pos(self, char: str):
        try:
            pos = ascii_lowercase.index(char.lower()) if char.isalpha else char
            return int(pos)
        except:
            return 0

    '''Estimate alpha numeric distribution difference'''
    def andd(self, string1: str, string2: str):
        corpus = list(map(self.clean_url, [string1, string2]))
        shorter, longer = min(corpus, key=len), max(corpus, key=len)
        diff = len(longer) - len(shorter)
        corpus[corpus.index(shorter)] = shorter + ('0' * diff)
        diffs = [abs(self.get_pos(corpus[0][i]) - self.get_pos(corpus[1][i])) for i in range(0, len(longer))]
        return sum(diffs)/len(diffs)

    '''Estimate how dis similar 2 URLs are'''
    def alexa_dis_similarity(self):
        self.url = self.clean_url(self.url)
        x = {i: self.count_freq_similar(self.url, self.clean_url(i)) for i in self.alexa50}
        x = {k: v for k, v in x.items() if v < 5}
        # print(x)
        if len(x) > 0:
            diffs = [self.andd(self.url, self.clean_url(k)) for k in list(x.keys())]
            return sum(diffs)/len(diffs)
        else:
            return 0


class LexicalURLFeature:
    def __init__(self, url):
        self.description = 'blah'
        self.url = url
        self.urlparse = urlparse(self.url)
        self.alexa = alexa_similarity(self.url)
        self.host = self.__get_ip()


    def __get_entropy(self, text):
        text = text.lower()
        probs = [text.count(c) / len(text) for c in set(text)]
        entropy = -sum([p * log(p) / log(2.0) for p in probs])
        return entropy

    def __get_ip(self):
        try:
            ip = self.urlparse.netloc if self.url_host_is_ip() else gethostbyname(self.urlparse.netloc)
            return ip
        except:
            return None

    # extract lexical features
    def url_scheme(self):
        a = self.urlparse.scheme
        if a == "http":
            return 0
        else:
            return 1

    def url_length(self):
        return len(self.url)

    def url_path_length(self):
        return len(self.urlparse.path)

    def url_host_length(self):
        return len(self.urlparse.netloc)

    def url_host_is_ip(self):
        host = self.urlparse.netloc
        pattern = compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        match = pattern.match(host)
        # return match is not None
        if match is not None:
            return 1
        else:
            return 0

    def url_has_port_in_string(self):
        has_port = self.urlparse.netloc.split(':')
        # return len(has_port) > 1 and has_port[-1].isdigit()
        if len(has_port) > 1 and has_port[-1].isdigit():
          return 1
        else:
          return 0

    def number_of_digits(self):
        digits = [i for i in self.url if i.isdigit()]
        return len(digits)

    def number_of_parameters(self):
        params = self.urlparse.query
        return 0 if params == '' else len(params.split('&'))

    def number_of_fragments(self):
        frags = self.urlparse.fragment
        return len(frags.split('#')) - 1 if frags == '' else 0

    def is_encoded(self):
        # return '%' in self.url.lower()
        if '%' in self.url.lower():
          return 1
        else:
          return 0

    def num_encoded_char(self):
        encs = [i for i in self.url if i == '%']
        return len(encs)

    def url_string_entropy(self):
        return self.__get_entropy(self.url)

    def average_alexa_50_similarity(self):
        return self.alexa.alexa_dis_similarity()

    def number_of_subdirectories(self):
        d = self.urlparse.path.split('/')
        return len(d)

    def number_of_periods(self):
        periods = [i for i in self.url if i == '.']
        return len(periods)

    def has_client_in_string(self):
        # return 'client' in self.url.lower()
        if 'client' in self.url.lower():
          return 1
        else:
          return 0

    def has_admin_in_string(self):
        # return 'admin' in self.url.lower()
        if 'admin' in self.url.lower():
          return 1
        else:
          return 0

    def has_server_in_string(self):
        # return 'server' in self.url.lower()
        if 'server' in self.url.lower():
          return 1
        else:
          return 0

    def has_login_in_string(self):
        # return 'login' in self.url.lower()
        if 'login' in self.url.lower():
          return 1
        else:
          return 0

    def get_tld(self):
        c = self.urlparse.netloc.split('.')[-1].split(':')[0]
        # c = urldata["tld"].loc[i] 
        if c == 'com':
            c = 10
        elif c == 'cn':
            c = 9
        elif c == 'tk':
            c = 8
        elif c == 'ml':
            c = 7
        elif c == 'xyz':
            c = 6
        elif c == 'buzz':
            c = 5
        elif c == 'shop':
            c = 4
        elif c == 'cf':
            c = 3
        elif c == 'net':
            c = 2
        elif c == 'ga':
            c = 1
        else:
            c = 0
        return c

    def run(self):
        data1 = pd.DataFrame()
        try:
            # data1['url']=[self.url]
            # data1['host']= [self.host]
            data1['tld']= [self.get_tld()]
            data1['scheme']= [self.url_scheme()]
            data1['url_length']= [self.url_length()]
            data1['path_length']= [self.url_path_length()]
            data1['host_length']= [self.url_host_length()]
            data1['host_is_ip']= [self.url_host_is_ip()]
            data1['has_port_in_string']= [self.url_has_port_in_string()]
            data1['num_digits']= [self.number_of_digits()]
            data1['parameters']= [self.number_of_parameters()]
            data1['fragments']= [self.number_of_fragments()]
            data1['is_encoded']= [self.is_encoded()]
            data1['string_entropy']= [self.url_string_entropy()]
            data1['alexa_dis_similarity']= [self.average_alexa_50_similarity()]
            data1['subdirectories']= [self.number_of_subdirectories()]
            data1['periods']= [self.number_of_periods()]
            data1['has_client']= [self.has_client_in_string()]
            data1['has_login']= [self.has_login_in_string()]
            data1['has_admin']= [self.has_admin_in_string()]
            data1['has_server']= [self.has_server_in_string()]
            data1['num_encoded_chars']= [self.num_encoded_char()]
            return data1
        except:
            return data1

### Content Features


def __get_valid_html_tags():
    pq = PyQuery(get('https://htmldog.com/references/html/tags/').content)
    items = pq('.longlist.acodeblock ul li a code')
    tags = [i.text().lower() for i in items.items()]
    return tags

def __get_suspicious_functions(url='https://gist.githubusercontent.com/eneyi/5c0b33129bcbfa366eb9fe79e96c1996/raw/96217aa7ea6698b17151f866f891ba701cbd7537/mal_script_functions.txt'):
    content = get(url).text.split('\n')
    return content

vd = __get_valid_html_tags()
sf = __get_suspicious_functions()


class ContentFeatures:
    def __init__(self, url, vd = vd, sf = sf):
        self.url = url
        self.urlparse = urlparse(self.url)
        self.html = self.__get_html()
        self.pq = self.__get_pq()
        self.scripts = self.__get_scripts()
        self.valid_tags = vd
        self.suspicious_functions = sf
        self.host = self.__get_ip()

    def __get_ip(self):
        try:
            ip = self.urlparse.netloc if self.url_host_is_ip() else gethostbyname(self.urlparse.netloc)
            return ip
        except:
            return None


    def url_host_is_ip(self):
        host = self.urlparse.netloc
        pattern = compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        match = pattern.match(host)
        return match is not None

    def __get_html(self):
        try:
            html = get(self.url, timeout=5)
            html = html.text if html else None
        except:
            html = None
        return html

    def __get_pq(self):
        try:
            pq = PyQuery(self.html) if self.html else None
            return pq
        except:
            return None


    def __get_scripts(self):
        scripts = self.pq('script') if self.pq else None
        return scripts

    def __get_entropy(self, text):
        text = text.lower()
        probs = [text.count(c) / len(text) for c in set(text)]
        return -sum([p * log(p) / log(2.0) for p in probs])

    # extract content-based features
    def url_page_entropy(self):
        return self.__get_entropy(self.html)

    def number_of_script_tags(self):
        return len(self.scripts) if self.scripts else None

    def script_to_body_ratio(self):
        if self.scripts:
            scripts = self.scripts.text()
            return len(scripts)/self.length_of_html()
        else:
            return None

    def length_of_html(self):
        return len(self.html)

    def number_of_page_tokens(self):
        html_tokens = len(self.html.lower().split()) if self.html else None
        return html_tokens

    def number_of_sentences(self):
        html_sentences = len(self.html.split('.')) if self.html else None
        return html_sentences

    def number_of_punctuations(self):
        excepts = ['<', '>', '/']
        matches = [i for i in self.html if i in punctuation and i not in excepts]
        return len(matches)

    def number_of_distinct_tokens(self):
        html_tokens = [i.strip() for i in self.html.lower().split()]
        return len(set(html_tokens))

    def number_of_capitalizations(self):
        uppercases = [i for i in self.html if i.isupper()]
        return len(uppercases)

    def average_number_of_tokens_in_sentence(self):
        html_sentences = self.html.split('.')
        sen_lens = [len(i.split()) for i in html_sentences]
        return sum(sen_lens)/len(sen_lens)

    def number_of_html_tags(self):
        return len(self.pq('*')) if self.pq else None

    def number_of_hidden_tags(self):
        hidden1, hidden2 = self.pq('.hidden'), self.pq('#hidden')
        hidden3, hidden4 = self.pq('*[visibility="none"]'), self.pq('*[display="none"]')
        hidden = hidden1 + hidden2 + hidden3 + hidden4
        return len(hidden)

    def number_iframes(self):
        iframes = self.pq('iframe') + self.pq('frame')
        return len(iframes)

    def number_objects(self):
        objects = self.pq('object')
        return len(objects)

    def number_embeds(self):
        objects = self.pq('embed')
        return len(objects)

    def number_of_hyperlinks(self):
        hyperlinks = self.pq('a')
        return len(hyperlinks)

    def number_of_whitespace(self):
        whitespaces = [i for i in self.html if i == ' ']
        return len(whitespaces)

    def number_of_included_elements(self):
        toi = self.pq('script') + self.pq('iframe') + self.pq('frame') + self.pq('embed') + self.pq('form') + self.pq('object')
        toi = [tag.attr('src') for tag in toi.items()]
        return len([i for i in toi if i])

    def number_of_suspicious_elements(self):
        all_tags = [i.tag for i in self.pq('*')]
        suspicious = [i for i in all_tags if i not in self.valid_tags]
        return len(suspicious)

    def number_of_double_documents(self):
        tags = self.pq('html') + self.pq('body') + self.pq('title')
        return len(tags) - 3

    def number_of_eval_functions(self):
        scripts = self.pq('script')
        scripts = ['eval' in script.text().lower() for script in scripts.items()]
        return sum(scripts)

    def average_script_length(self):
        scripts = self.pq('script')
        scripts = [len(script.text()) for script in scripts.items()]
        l = len(scripts)
        if l > 0:
            return sum(scripts) / l
        else:
            return 0

    def average_script_entropy(self):
        scripts = self.pq('script')
        scripts = [self.__get_entropy(script.text()) for script in scripts.items()]
        l = len(scripts)
        if l > 0:
            return sum(scripts) / l
        else:
            return 0

    def number_of_suspicious_functions(self):
        script_content = self.pq('script').text()
        susf = [1 if i in script_content else 0 for i in self.suspicious_functions]
        return sum(susf)

    def run(self):
        data = pd.DataFrame()
        try:
            if self.html and self.pq:
                # data = {}
                # data['host'] = [self.host]
                data['page_entropy'] = [self.url_page_entropy()]
                data['num_script_tags'] = [self.number_of_script_tags()]
                data['script_to_body_ratio'] = [self.script_to_body_ratio()]
                data['html_length'] = [self.length_of_html()]
                data['page_tokens'] = [self.number_of_page_tokens()]
                data['num_sentences'] = [self.number_of_sentences()]
                data['num_punctuations'] = [self.number_of_punctuations()]
                data['distinct_tokens'] = [self.number_of_distinct_tokens()]
                data['capitalizations'] = [self.number_of_capitalizations()]
                data['avg_tokens_per_sentence'] = [self.average_number_of_tokens_in_sentence()]
                data['num_html_tags'] = [self.number_of_html_tags()]
                data['num_hidden_tags'] = [self.number_of_hidden_tags()]
                data['num_iframes'] = [self.number_iframes()]
                data['num_embeds'] = [self.number_embeds()]
                data['num_objects'] = [self.number_objects()]
                data['hyperlinks'] = [self.number_of_hyperlinks()]
                data['num_whitespaces'] = [self.number_of_whitespace()]
                data['num_included_elemets'] = [self.number_of_included_elements()]
                data['num_double_documents'] = [self.number_of_double_documents()]
                data['num_suspicious_elements'] = [self.number_of_suspicious_elements()]
                data['num_eval_functions'] = [self.number_of_eval_functions()]
                data['avg_script_length'] = [self.average_script_length()]
                data['avg_script_entropy'] = [self.average_script_entropy()]
                data['num_suspicious_functions'] = [self.number_of_suspicious_functions()]
                return data
            else:
                print("error")
                return data
        except:
            return data


### Host-Based Features


class HostFeatures:
    def __init__(self, url):
        self.url = url
        self.urlparse = urlparse(self.url)
        self.host = self.__get_ip()
        self.now = datetime.now()
        self.whois = self.__get__whois_dict()
        self.shodan = self.__get_shodan_dict()
        self.snapshots = self.__get_site_snapshots()

    def __get_ip(self):
        try:
            ip = self.urlparse.netloc if self.url_host_is_ip() else gethostbyname(self.urlparse.netloc)
            return ip
        except:
            return None

    def __get__whois_dict(self):
        try:
            whois_dict = whois(self.url)
            return whois_dict
        except:
            return {}

    def __get_shodan_dict(self):
        api = Shodan('tdBI4vZmtOsKyisd69kLqZFpPfW2g8H3')
        try:
            host = api.host(self.host)
            return host
        except:
            return {}

    def __parse__before__date(self, date_string):
        month_year = date_string.split()[-1]
        d = '01-{}'.format(month_year)
        d = datetime.strptime(d, '%d-%b-%Y')
        return d

    def __parse_whois_date(self, date_key):
        cdate = self.whois.get(date_key, None)
        if cdate:
            if isinstance(cdate, str) and 'before' in cdate:
                d = self.__parse__before__date(cdate)
            elif isinstance(cdate, list):
                d = cdate[0]
            else:
                d = cdate
        return d if cdate else cdate

    def __get_site_snapshots(self):
        try:
            snapshots = Cdx(self.urlparse.netloc).snapshots()
            snapshots = [snapshot.datetime_timestamp for snapshot in snapshots]
            return snapshots
        except:
            return []

    def url_host_is_ip(self):
        host = self.urlparse.netloc
        pattern = compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        match = pattern.match(host)
        # return match is not None
        if match is not None:
          return 1
        else:
          return 0

    def number_of_subdomains(self):
        ln1 = self.whois.get('nets', None)
        ln2 = self.shodan.get('domains', None)
        ln = ln1 or ln2
        return len(ln) if ln else 0

    def url_creation_date(self):
        d = self.__parse_whois_date('creation_date')
        return d

    def url_expiration_date(self):
        d = self.__parse_whois_date('expiration_date')
        return d

    def url_last_updated(self):
        d = self.__parse_whois_date('updated_date')
        return d

    def url_age(self):
        try:
            days = (self.now - self.url_creation_date()).days
        except:
            days = 0
        return days

    def url_intended_life_span(self):
        try:
            lifespan = (self.url_expiration_date() - self.url_creation_date()).days
        except:
            lifespan = 0
        return lifespan

    def url_life_remaining(self):
        try:
            rem = (self.url_expiration_date() - self.now).days
        except:
            rem = 0
        return rem

    def url_registrar(self):
        registrar_1 = self.whois.get('registrar', None)
        # return registrar_1

        if registrar_1 == 'GoDaddy.com, LLC':
          return 7
        elif registrar_1 == 'NAMECHEAP INC':
          return 6
        elif registrar_1 == 'Alibaba Cloud Computing (Beijing) Co., Ltd.':
          return 5
        elif registrar_1 == 'PDR Ltd. d/b/a PublicDomainRegistry.com':
          return 4
        elif registrar_1 == 'TUCOWS, INC.' or registrar_1 == 'Google LLC' or registrar_1 == 'Name.com, Inc.' :
          return 3
        elif registrar_1 == 'DYNADOT LLC' or registrar_1 == 'Key-Systems LLC' or registrar_1 == 'Chengdu west dimension digital technology Co., LTD' or registrar_1 == 'Uniregistrar Corp' or registrar_1 == 'Network Solutions, LLC' or registrar_1 == 'OVH, SAS' or registrar_1 == 'GMO INTERNET, INC.' :
          return 2
        elif registrar_1 == 'GANDI SAS' or registrar_1 == 'Registrar of domain names REG.RU LLC' or registrar_1 == 'PSI-USA, Inc. dba Domain Robot' or registrar_1 == '1API GmbH' or registrar_1 == 'NameSilo, LLC' or registrar_1 == 'Regional Network Information Center, JSC dba RU-CENTER' :
          return 1
        else:
          return 0

    def url_registration_country(self):
        c = self.whois.get('country', 0)
        return c

    def url_host_country(self):
        c = self.shodan.get('country_name', None)
        if c == 'United States':
          return 10
        elif c == 'Denmark':
          return 9
        elif c == 'Netherlands':
          return 8
        elif c == 'China':
          return 7
        elif c == 'Russian Federation':
          return 6
        elif c == 'Germany':
          return 5
        elif c == 'Singapore':
          return 4
        elif c == 'Korea, Republic of':
          return 3
        elif c == 'Japan':
          return 2
        elif c == 'Canada':
          return 1
        else:
          return 0

    def url_open_ports(self):
        ports = self.shodan.get('ports', '')
        return ports if ports != '' else None

    def url_num_open_ports(self):
        ports = self.url_open_ports()
        lp = len(ports) if ports else 0
        return lp

    def url_is_live(self):
        url = '{}://{}'.format(self.urlparse.scheme, self.urlparse.netloc)
        try:
            if get(url).status_code == 200:
              return 1
            else:
              return 0
        except:
            return 0

    def url_isp(self):
        return self.shodan.get('isp', '')

    def url_connection_speed(self):
        url = '{}://{}'.format(self.urlparse.scheme, self.urlparse.netloc)
        if self.url_is_live() == 1:
            return get(url).elapsed.total_seconds()
        else:
            return 0

    def first_seen(self):
        try:
            fs = self.snapshots[0]
            return fs
        except:
            return datetime.now()

    def get_os(self):
        oss = self.shodan.get('os', 0)
        return oss

    def last_seen(self):
        try:
            ls = self.snapshots[-1]
            return ls
        except:
            return datetime.now()

    def days_since_last_seen(self):
        dsls = (self.now - self.last_seen()).days
        return dsls

    def days_since_first_seen(self):
        dsfs = (self.now - self.first_seen()).days
        return dsfs

    def average_update_frequency(self):
        snapshots = self.snapshots
        diffs = [(t-s).days for s, t in zip(snapshots, snapshots[1:])]
        l = len(diffs)
        if l > 0:
            return sum(diffs)/l
        else:
            return 0

    def number_of_updates(self):
        return len(self.snapshots)

    def ttl_from_registration(self):
        earliest_date_seen = self.first_seen()
        try:
            ttl_from_reg = (earliest_date_seen - self.url_creation_date()).days
        except:
            ttl_from_reg = 0
        return ttl_from_reg

    def run(self):
        data = pd.DataFrame()
        try:
            # data["host"]=[self.host]
            data["num_subdomains"]=[self.number_of_subdomains()]
            # data["registration_date"]=[str(self.url_creation_date())]
            # data["expiration_date"]=[str(self.url_expiration_date())]
            # data["last_updates_dates"]=[str(self.url_last_updated())]
            data["age"]=[self.url_age()]
            data["intended_life_span"]=[self.url_intended_life_span()]
            data["life_remaining"]=[self.url_life_remaining()]

            data["registrar"]=[self.url_registrar()]
            # data["reg_country"]=[self.url_registration_country()]
            data["host_country"]=[self.url_host_country()]

            # data["open_ports"]=[self.url_open_ports()]
            data["num_open_ports"]=[self.url_num_open_ports()]
            data["is_live"]=[self.url_is_live()]
            # data["isp"]=[self.url_isp()]
            data["connection_speed"]=[self.url_connection_speed()]
            # data["first_seen"]=[str(self.first_seen())]
            # data["last_seen"]=[str(self.last_seen())]
            data["days_since_last_seen"]=[self.days_since_last_seen()]
            data["days_since_first_seen"]=[self.days_since_first_seen()]
            data["avg_update_days"]=[self.average_update_frequency()]
            data["total_updates"]=[self.number_of_updates()]
            data["ttl"]=[self.ttl_from_registration()]
            return data
        except:
            return data

def generate_features(url):
    
    df1 = LexicalURLFeature(url).run() # 20
    print(df1.shape)
    df2 = ContentFeatures(url).run() # 24
    print(df2.empty)
    df3 = HostFeatures(url).run() # 14
    print(df3.shape)

    # if df1.empty == true or df2.empty == true or df3.empty == true:
    #     print()
    # else:
    df4 = pd.concat([df1, df2, df3],axis=1)
    return df4


if __name__ == "__main__":
    url = 'https://pypi.org/project/python-whois/'
    # print(generate_features(url))
    
    