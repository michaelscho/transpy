# imports
import re # for regex
from zipfile import ZipFile # for handling exported zip file
import time # for handling lagging export
import json # for handling rest responses
import requests # for REST requests
from requests.auth import HTTPDigestAuth # for Transkribus REST requests
from requests.auth import HTTPBasicAuth # for exist REST request
import transkribus_credentials # takes credentials from local config file
import config # stores basic config
import exist_credentials # takes credentials from local config file
import xml.etree.ElementTree as ET # for parsing xml data
import lxml.etree as LET # TODO replace etree for parsing xml data
from os import walk # handles filenames in folder
import pandas as pd


""" Functions for importing and exporting data from Transkribus via REST-AP

"""


def login_transkribus(user,pw):
    """ Login to Transkribus and start session

    Uses REST url https://transkribus.eu/TrpServer/rest/auth/login
    :param user: Username as string (should be specified in config.py)
    :param pw: Password as string (should be specified in config.py)
    :return: Returns session
    """

    # set session...
    session = requests.Session()
    # ..post credentials
    req = session.post('https://transkribus.eu/TrpServer/rest/auth/login',data = {'user': user, 'pw': pw})
    return session

# TODO import documents to transkribus

def export_pagexml(session, collection_id, document_id, startpage, endpage):
    """ Export page-XML to local machine for further processing

    Uses REST url https://transkribus.eu/TrpServer/rest/collections/{collection-ID}/{document-ID}/fulldoc

    :param session: Transkribus session as returned from login_transkribus()
    :param collection_id: Transkribus collection number as Int
    :param document_id: Transkribus document number as Int
    :param startpage: First page of document to be exported as Int
    :param endpage: Last page of document to be exported as Int
    :return: Returns url to exported data that can be downloaded as zip-file
    """

    # concat url to document...
    url = 'https://transkribus.eu/TrpServer/rest/collections/' + str(collection_id) + '/' + str(document_id) + '/export?pages='+str(startpage)+'-'+str(endpage)

    # ...set paramater for exporting page-xml...
    params = '{"commonPars":{"pages":"'+ str(startpage) +'-'+ str(endpage) +'","doExportDocMetadata":true,"doWriteMets":true,"doWriteImages":false,"doExportPageXml":true,"doExportAltoXml":false,"doExportSingleTxtFiles":false,"doWritePdf":false,"doWriteTei":false,"doWriteDocx":false,"doWriteOneTxt":false,"doWriteTagsXlsx":false,"doWriteTagsIob":false,"doWriteTablesXlsx":false,"doCreateTitle":false,"useVersionStatus":"Latest version","writeTextOnWordLevel":false,"doBlackening":false,"selectedTags":["add","date","Address","supplied","work","capital-rubricated","unclear","sic","structure","div","regionType","seg-supp","speech","person","gap","organization","comment","abbrev","place","rubricated"],"font":"FreeSerif","splitIntoWordsInAltoXml":false,"pageDirName":"page","fileNamePattern":"${filename}","useHttps":true,"remoteImgQuality":"orig","doOverwrite":true,"useOcrMasterDir":true,"exportTranscriptMetadata":true,"updatePageXmlImageDimensions":false},"altoPars":{"splitIntoWordsInAltoXml":false},"pdfPars":{"doPdfImagesOnly":false,"doPdfImagesPlusText":true,"doPdfWithTextPages":false,"doPdfWithTags":false,"doPdfWithArticles":false,"pdfImgQuality":"view"},"docxPars":{"doDocxWithTags":false,"doDocxPreserveLineBreaks":false,"doDocxForcePageBreaks":false,"doDocxMarkUnclear":false,"doDocxKeepAbbrevs":false,"doDocxExpandAbbrevs":false,"doDocxSubstituteAbbrevs":false}}'

    # ...post export request, starts export and returns job number...
    export_request = session.post(url,params)
    export_request = export_request.text

    # ...check status of job after a couple of seconds (usually, it takes around 5 seconds to export a page)...
    time.sleep(6)
    export_status = session.get('https://transkribus.eu/TrpServer/rest/jobs/' + export_request)
    export_status = export_status.json()

    while export_status["state"] != 'FINISHED':
        # ...check again after 5 seconds...
        export_status = session.get('https://transkribus.eu/TrpServer/rest/jobs/' + export_request)
        export_status = export_status.json()
        time.sleep(10)

    # ..get url of exported zip file...
    export_file_url = export_status["result"]
    return export_file_url

""" Functions for downloading and extracting data to local machine

"""

def download_export(url):
    """ Download of exported data

    Downloads exported data from transkribus server using url returned by export_pagexml() as zip file,
    saves it to export folder on local machine specified in config.py and returns name of zip file

    :param url: Url to zip file as string
    :return: Name of downloaded zip file as string
    """

    # download zip file to the subfolder ./documents on a local machine...
    zip_file_name = config.export_folder+'export.zip'
    zip_file = requests.get(url)
    zip_file.raise_for_status()
    save_file = open(zip_file_name,'wb')
    for chunk in zip_file.iter_content(100000):
        save_file.write(chunk)
    save_file.close()
    return zip_file_name

def unzip_file(zip_file_name):
    """ Extracts data from zip file

    Extracts data from zip file into local folder specified in config.py
    and returns path to pageXML for further processing

    :param zip_file_name: name of zip file as string as returned by download_export()
    :return: path to downloaded pageXML as string
    """

    with ZipFile(zip_file_name,'r') as zip_obj:
        list_of_filenames = zip_obj.namelist()
        for filename in list_of_filenames:
            if 'page/' in filename:
                path_to_pagexml = filename.split('page/')[0]+'page/'
        zip_obj.extractall(config.export_folder)
    return path_to_pagexml

def only_numbers(x):
    """ building sort key for load_pagexml()

    """

    if 'new' in x:
        x = x.replace('_new.xml','')
        x = x.rsplit('/',1)
    else:
        x = x.replace('.xml','')
        x = x.rsplit('/',1)
    return(int(x[1]))

def load_pagexml(folder_name):
    """ Get path to pageXML files for further processing

    :param folder_name: Takes path to pageXML as returned by unzip_file()
    :return: Returns path to pageXML files as list
    """

    filenames = next(walk(folder_name))[2]
    path_to_files = sorted([folder_name + '/' + string for string in filenames], key = only_numbers)
    return path_to_files

""" Export and import functions for handling data on existdb instance using REST API

Documentation: https://exist-db.org/exist/apps/doc/devguide_rest
"""

def get_exist_data(user, pw, exist_url, resources_folder):
    """ Getting list of abbreviations from remote exist-db collections provided by xquery script

    Downloads list of abbreviation needed for automatic expansion from existdb instance
    queried by xquery script named 'abbreviations.xquery' on server as JSON file
    'abbreviation_dictionary.json' in resource folder specified in config.py on local machine.

    :param user: Username as string (should be specified in config.py)
    :param pw: Password as string (should be specified in config.py)
    :param exist_url: Url to xquery script providing abbreviations as string (should be specified in config.py)
    :param resources_folder: Download-folder as string (should be specified in config.py)
    :return: Returns dictionary containing abbreviations with corresponding expansions for further processing
    """

    # login to exist...
    # ...set session...
    session = requests.Session()

    # Get xml-document containing list of abbreviatins as choice elements via xquery stored on exist server...
    url = exist_url + 'abbreviations.xquery'

    # ...post export request, starts export and returns xml...
    export_request = session.get(url, auth=HTTPBasicAuth(user, pw))
    export_request = export_request.text

    # ...preprocessing and converting xml file in dictionary...
    export_request = export_request.replace('</abbr>','</abbr>;')
    export_request = re.sub('\s+','',export_request)
    export_request = re.sub('\n+','',export_request)
    export_request = re.sub('<fw(.*?)</fw>','',export_request)
    export_request = export_request.replace('</choice>','</choice>\n')
    export_request = re.sub('<.*?>','',export_request)
    dictionary_abbr_exist = {}
    list_of_abbreviations = export_request.split('\n')

    # ...delete last empty line...
    del list_of_abbreviations[-1]
    list_of_abbreviations = list(dict.fromkeys(list_of_abbreviations))

    for i in list_of_abbreviations:
        choice = i.split(';')
        # ...skip errors in list...
        if len(choice) > 1:
            dictionary_abbr_exist[choice[0]] = choice[1]

    # ... save dictionary in file in local subfolder ./resources for further usage...
    abbreviation_json = open(resources_folder + "abbreviation_dictionary.json", "w")
    json.dump(dictionary_abbr_exist, abbreviation_json)
    abbreviation_json.close()
    # ...return dictionary
    return dictionary_abbr_exist

def load_abbreviation_dict():
    """ Check if abbreviation file already exists or has to be downloaded

    :return: dictionary containing abbreviations and corresponding expansions
    """
    try:
        dictionary_abbr_exist = config.resources_folder + 'abbreviation_dictionary.json'
        with open(dictionary_abbr_exist,'r') as json_file:
            dictionary_abbr_exist = json.load(json_file)
    except:
        dictionary_abbr_exist = get_exist_data(exist_credentials.user_exist, exist_credentials.pw_exist, config.exist_url, config.resources_folder)
        with open(dictionary_abbr_exist,'r') as json_file:
            dictionary_abbr_exist = json.load(json_file)
    return dictionary_abbr_exist








# postprocess page-xml

## detect and replace abbreviations using list of special characters as marker

# apply rules for manual expansion defined in config
def manual_expansion(word):
    expansion = word
    for key, value in config.rules_for_expansion.items():
        expansion = expansion.replace(key,value)
    return expansion

# replace expansions in page-xml files
def replace_abbreviations_from_pagexml(dictionary_abbr_exist, filenames):

    # open each pagexmlfile for postprocessing
    for filename in filenames:
        tree = ET.parse(filename)
        root = tree.getroot()
        x = root.findall('.//{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode')
        for i in x:

            wordlist = i.text.split()
            # take special characters from dictionary in config file that point to abbreviated words as dictionary (depending on modell used for recognition)...
            special_characters_dict = config.special_characters_dict

            # ... creating list to iterate...
            special_characters = list(special_characters_dict.values())

            # ... prepare words from wordlist and store in dictionary...
            for word in wordlist:
                # ...delete used interpunctuation from word...
                word = word.replace('\uF1F8','').replace('\uF1EA','').replace('\uF1F5','').replace('\uF1F0','').replace('\uF160','').replace('\uF1E2','').replace('\uF1E1','')
                # ... detect abbreviations by special characters...
                if any(character in special_characters for character in word):
                    # ...check if word is in abbreviation dictionary...
                    if word in dictionary_abbr_exist:
                    #... and insert corresponding expansion if found in dict...
                        expansion = dictionary_abbr_exist[word]

                    # ...else, expand word by the following rules...
                    else:
                        expansion = manual_expansion(word)

                    i.text = i.text.replace(word,expansion)
        new_filename = filename.replace('/page/','/page/expanded/')
        print(new_filename)
        with open(new_filename, 'w') as f:
            tree.write(f, encoding='unicode')


def replace_abbreviations_from_tei(dictionary_abbr_external, processed_text):

    # ...replace whitespace with underscore in xml-tags to enable split() without loosing element structure...
    match_elements = re.findall('\<(.*?)\>',processed_text)
    refined_xml = processed_text
    for i in match_elements:
        no_white_space = i.replace(' ','~')
        refined_xml = refined_xml.replace(i,no_white_space)

    # ...split text into single words...
    wordlist = refined_xml.split()
    # ...convert to dictionary and back to list to get only single instances of words...
    wordlist = list(dict.fromkeys(wordlist))

    # take special characters from dictionary in config file that point to abbreviated words as dictionary (depending on modell used for recognition)...
    special_characters_dict = config.special_characters_dict

    # ... creating list to iterate...
    special_characters = list(special_characters_dict.values())

    # ...Create dictionary for storing all abbreciations with corresponding values...
    dictionary_abbr = {}

    # ... prepare words from wordlist and store in dictionary...
    for word in wordlist:
        # ...delete used interpunctuation from word...
        word = word.replace('\uF1F8','').replace('\uF1EA','').replace('\uF1F5','').replace('\uF1F0','').replace('\uF160','').replace('\uF1E2','').replace('\uF1E1','')
        # ... detect abbreviations by special characters...
        if any(character in special_characters for character in word):
            # ... store word as items in dictionary...
            dictionary_abbr[word] = {'tags': {}}

            # ...find elements inside words and store start, end and content of word in dictionary...
            pattern = re.compile('\<.*?\>',re.UNICODE)
            n = 0
            word_copy = word
            for match in pattern.finditer(word):
                element_start = match.start()
                element_end = match.end()
                element_text = match.group()
                # ...add tags in nested dictionary...
                dictionary_abbr[word_copy]['tags'][n] = {'tag': element_text, 'start': element_start, 'end': element_end}
                n+=1
                # ...delete elements from word (caveat: changes indices of start and beginning, thus order of deletion must be taken into account when reinserting...)
                word = re.sub(element_text,'',word)
                dictionary_abbr[word_copy]['abbr'] = word

            # ...check if word is in abbreviation dictionary...
            if word in dictionary_abbr_external:
                #... and insert corresponding expansion if found in dict...
                dictionary_abbr[word_copy]['expan'] = dictionary_abbr_external[word]
            # ...else, expand word by rules specified in config file...
            else:
                expansion = manual_expansion(word)
                expansion = expansion

                # ...check, if some words have not been properly expanded...
                if any(character in special_characters for character in expansion):
                    dictionary_abbr[word_copy]['expan'] = 'ERROR'
                else:
                    dictionary_abbr[word_copy]['expan'] = expansion

            # ...take deleted tags from dictionary and put them into expanded word...
            if dictionary_abbr[word_copy]['tags'].values():

                # ...detect number of deleted tags...
                len_dict = range(0,len(dictionary_abbr[word_copy]['tags'].keys()))
                word_with_tag = dictionary_abbr[word_copy]['expan']
                # ...iterate through tags and insert by using start index...
                for i in len_dict:
                    tag = dictionary_abbr[word_copy]['tags'][i]['tag']
                    start = dictionary_abbr[word_copy]['tags'][i]['start']
                    # ...check, if expanded special character has occured before tag that is to be entered...
                    # ..if so, add length of insertion to start
                    character_list = config.rules_for_expansion
                    trigger = False
                    for key, value in character_list.items():
                        if value in word_with_tag:
                            if word_with_tag.index(value) < start:
                                start = start + (len(key))
                                if start > 1:
                                    if trigger == False:
                                        start = start -1
                                        trigger = True

                                    else:
                                        pass
                    # ...insert tag on index...
                    word_with_tag = str(word_with_tag)
                    word_with_tag = word_with_tag[:start]+tag+word_with_tag[start:]
                dictionary_abbr[word_copy]['expan_with_tags'] = word_with_tag

            else:
                dictionary_abbr[word_copy]['expan_with_tags'] = dictionary_abbr[word_copy]['expan']
                # ...create choice element corresponding to tei scheme...

            # choose between tei choice element or just insertion of expanded text
            choice_element = '<choice><abbr>'+word_copy.strip()+'</abbr><expan>'+str(dictionary_abbr[word_copy]['expan_with_tags'])+'</expan></choice>'
            if '</fw>' in choice_element:
                choice_element = choice_element.replace('</fw>','') + '</fw>'
            else:
                pass
            if '<p n="1">' in choice_element:
                choice_element = choice_element.replace('<choice><abbr><p n="1">','<p n="1"><choice><abbr>')
                choice_element = choice_element.replace('<expan><p n="1">','<expan>')
            else:
                pass
            if '</item>' in choice_element:
                choice_element = choice_element.replace('</item>','')
                choice_element = choice_element.replace('</choice>','</choice></item>')
            else:
                pass
            if '<note' in choice_element:
                choice_element = re.sub(r'<choice><abbr>(<note.*?>)','\g<1><choice><abbr>',choice_element)
                choice_element = re.sub(r'<expan><note.*?>','<expan>',choice_element)
                #print(choice_element)
            else:
                pass



            #choice_element = str(dictionary_abbr[word_copy]['expan_with_tags'])


            # ...loop through text and replace original word with choice element...
            # (Abbreviations starting with a tag have to be treated differently)
            # caveat: some postprocessing is required (see below)

            if word_copy[0] == '<':
                refined_xml = re.sub(word_copy,choice_element,refined_xml)
            else:
                # ... replace word in text with choice-element
                refined_xml = re.sub(' '+word_copy+' ',' '+choice_element+' ',refined_xml)

                # ...some rules for special cases, f.i. words ending with interpunctuation
                refined_xml = re.sub(' '+word_copy+'\n',' '+choice_element+'\n',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF1F8',' '+choice_element+'\uF1F8',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF1EA',' '+choice_element+'\uF1EA',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF1F5',' '+choice_element+'\uF1F5',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF1F0',' '+choice_element+'\uF1F0',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF160',' '+choice_element+'\uF160',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF1E2',' '+choice_element+'\uF1E2',refined_xml)
                refined_xml = re.sub(' '+word_copy+'\uF1E1',' '+choice_element+'\uF1E1',refined_xml)
                refined_xml = re.sub('>'+word_copy+' ','>'+choice_element+' ',refined_xml)
                refined_xml = re.sub('\uf1e1'+word_copy+' ','\uf1e1'+choice_element+' ',refined_xml)

    # ...replace ~ with whitespace in xml-tags again...
    match_elements = re.findall('\<(.*?)\>',refined_xml)

    for i in match_elements:
        no_underscore = i.replace('~',' ')
        refined_xml = refined_xml.replace(i,no_underscore)

    # ...return text
    #print(dictionary_abbr)
    return refined_xml









## export as single tei file
def export_tei(filenames):

    text_page = ""

    # open each pagexmlfile for exporting text to tei
    for filename in filenames:
        tree = LET.parse(filename)
        root = tree.getroot()

        # find column 1 and return element
        try:
            column_1 = root.xpath('//ns0:TextRegion[contains(@custom,"type:column_1")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            text_column_one = "\n<pb/><cb n='a'/>"
            unicode_column_one = column_1.xpath('.//ns0:TextLine//ns0:Unicode', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            for line in unicode_column_one:
                text_column_one = text_column_one + '\n<lb/>' + line.text
        except:
            text_column_one = "\n<pb/><cb n='a'/>"

        # find column 2 and return element
        try:
            column_2 = root.xpath('//ns0:TextRegion[contains(@custom,"type:column_2")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]

            # put together text of column 1 and text of column 2

            text_column_two = "\n<cb n='b'/>"

            unicode_column_two = column_2.xpath('.//ns0:TextLine//ns0:Unicode', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

            for line in unicode_column_two:
                text_column_two = text_column_two + '\n<lb/>' + line.text
        except:
            text_column_two = "\n<cb n='b'/>"

        text_page = text_page + text_column_one + text_column_two
    return text_page

# function for incrementing folia_numbers, e.g. 28v-30r
def increment_folia(start_folia):
    if 'r' in start_folia:
        start_folia = start_folia.replace('r','v')
    elif 'v' in start_folia:
        start_folia = str(int(start_folia.replace('v',''))+1)+'r'
    return start_folia







# postprocess line breaks, takes and returns exported text_page
def line_breaks(text_page):

    # TODO for now, delete manual inserted angle dash
    text_page = text_page.replace('¬','')

    # load dictinary containing wordforms
    df = pd.read_csv(config.resources_folder+'lexicon.csv')


    # check word with linebreak
    # find words next to linebreaks
    match_elements = re.findall('\w+\n\<lb/>\w+',text_page,re.IGNORECASE)
    # delete duplicates
    match_elements = list(dict.fromkeys(match_elements))
    # iterate through linebreaks and create searchstring by deleting linebreaks
    for i in match_elements:
        # create copies of i for processing and later replacment
        word_to_be_replaced = i
        searchstring = i
        searchstring = re.sub('\n<lb/>','',searchstring)
        # look for searchstring in dictionary and replace <lb/> with <lb break="no"/> if found
        if df['WF-Name'].str.contains(searchstring.lower()).any():
            i = re.sub('<lb/>','<lb break="no" type="automated"/>',i)
        # if searchstring is not in dictionary, word probably don't belong together, <lb/> is inserted
        else:
            i = re.sub('<lb/>','<lb type="automated"/>',i)
        # original word is replaced
        #print(i)
        text_page = re.sub(word_to_be_replaced,i,text_page)

    return text_page

# TODO postprocess word segmentation, takes and returns exported text_page
def word_segmentation(text_page):
    pass

    # check word segmentation
    wordlist = text_page.replace('<lb/>','').replace("<pb/><cb n='a'/>","").replace("<cb n='b'/>","").split()

    # delete duplicates
    wordlist = list(dict.fromkeys(wordlist))

    for word in wordlist:
        if df['WF-Name'].str.contains('^'+word+'$', regex=True).any():
            new_word = word
        else:
            n = 1
            word1 = word[:len(word)-n]
            word2 = word[len(word)-n:]

            while not (df['WF-Name'].str.contains(word1+'$', regex=True).any()) and (df['WF-Name'].str.contains(word2+'$',regex=True).any()):
                n += 1
                word1 = word[:len(word)-n]
                word2 = word[len(word)-n:]
            new_word = word1 + ' ' + word2

        text_page = re.sub(word,new_word,text_page)

    return text_page

# use manually inserted ¬ for creating proper tei linebreaks
def line_breaks_angled_dash(text_page):

    text_page = text_page.replace('¬ ','¬')
    text_page = re.sub(r'¬\n(<lb.*?)/>','\g<1> break="no"/>',text_page, flags=re.DOTALL)
    text_page = re.sub(r'¬\n(<cb.*?n="b".*?/>\n<lb.*?)/>','\g<1> break="no"/>',text_page)
    text_page = re.sub(r'¬\n(<pb.*?<cb.*?n="a".*?/>\n<lb.*?)/>','\g<1> break="no"/>',text_page)

    return text_page






# make list items unique
def get_unique_string(wordlist):

    list_of_unique_strings = []

    unique_wordlist = set(wordlist)

    for word in unique_wordlist:
        list_of_unique_strings.append(word)

    return list_of_unique_strings

def save_abbreviations(dictionary_abbr_exist, filenames):
    """ Saves list of expanded abbreviation in xml file
    """

    # open each pagexmlfile for postprocessing
    wordlist_abbr = []

    for filename in filenames:
        tree = ET.parse(filename)
        root = tree.getroot()
        x = root.findall('.//{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode')
        for i in x:
            wordlist = i.text.split()
            # define special characters that point to abbreviated words as dictionary (depending on modell used for recognition)...
            special_characters_dict = config.special_characters_dict

            # ... creating list of unique words to iterate...
            special_characters = list(special_characters_dict.values())

            # ... prepare words from wordlist and store in dictionary...
            for word in wordlist:
                # ...delete used interpunctuation from word...
                word = word.replace('\uF1F8','').replace('\uF1EA','').replace('\uF1F5','').replace('\uF1F0','').replace('\uF160','').replace('\uF1E2','').replace('\uF1E1','')
                # ... detect abbreviations by special characters...
                if any(character in special_characters for character in word):
                    # ...check if word is in abbreviation dictionary...
                    wordlist_abbr.append(word)
    wordlist = get_unique_string(wordlist_abbr)
    for word in wordlist:
        if word in dictionary_abbr_exist:
        #... and insert corresponding expansion if found in dict...
            expansion = dictionary_abbr_exist[word]
        # ...else, expand word by the following rules...
        else:
            expansion = manual_expansion(word)

            if any(character in special_characters for character in expansion):
                expansion = "~~" + word + "~~"

        # compose entry as tei:choice
        entry = "<choice><abbr>"+word+"</abbr><expan type = 'automatic'>"+expansion+"</expan></choice>\n"

        # write file for checking abbreviations
        with open('./abbr.xml', 'a') as f:
            f.write(entry)




""" Wrapper functions for getting and processing data for different usecases

"""

def download_data_from_transkribus(collection_id, document_id, startpage, endpage):
    """ Download data from transkribus and return path to pageXMl

    :param collection_id: Transkribus collection number as Int
    :param document_id: Transkribus document number as Int
    :param startpage: First page of document to be exported as Int
    :param endpage: Last page of document to be exported as Int
    :return: Returns path to pageXML as list of filenames
    """

    ## start session
    session = login_transkribus(transkribus_credentials.username,transkribus_credentials.password)
    ## export pagexml
    export_file_url = export_pagexml(session, collection_id, document_id, startpage, endpage)
    ## download exported file
    local_xml_files = download_export(export_file_url)
    ## unzip downloaded file and get path to pagexml-files
    path_to_pagexml = unzip_file(local_xml_files)

    return path_to_pagexml

def postprocess_pagexml(path_to_pagexml_folder):
    """ pageXML: Expands abbreviations in pageXML

    Function for creating expanded groundtruth from abbreviated ground truth
    Saves processed pageXML files in subfolder './documents/.../page/expanded/"
    Files can be uploaded to Transkribus for training expanded model

    :param path_to_pagexml_folder: Path to pageXML folder as string
    """

    # load dictionary of abbreviations
    dictionary_abbr_exist = load_abbreviation_dict()
    #gets path of xml files
    path_to_files = load_pagexml(config.export_folder + path_to_pagexml_folder)
    # expands abbreviations
    replace_abbreviations_from_pagexml(dictionary_abbr_exist, path_to_files)


# Getting TEI file
def postproccess_tei(path_to_pagexml_folder, output_filename=''):
    """ TEI: Expands abbreviations in pageXML

    Function for creating expanded TEI file from abbreviated ground truth
    Saves processed TEI file in specified subfolder.
    Files can be used for further TEI workflow

    :param path_to_pagexml_folder: Path to pageXML folder as string
    :param output_filename: Filename of TEI file to be created. If none is given, no file will be created
    :return: Text using tei expansions as string
    """

    # load dictionary of abbreviations
    dictionary_abbr_exist = load_abbreviation_dict()
    #gets path of xml files
    path_to_files = load_pagexml(config.export_folder + path_to_pagexml_folder)
    # creates single tei file from pagexml files
    text_page = export_tei(path_to_files)
    # replaces linebreaks by tei <lb/> and <lb break='no'/>
    processed_text = line_breaks_angled_dash(text_page)
    # replacing abbreviations
    expanded_text = replace_abbreviations_from_tei(dictionary_abbr_exist, processed_text)
    return expanded_text
    if output_filename != '':
        # saves tei file
        with open(output_filename,'w') as f:
            f.write(processed_text)
    else:
        pass
