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
from os import walk # handles filenames in folder


# connections

## start transkribus session (log in)
def login_transkribus(user,pw):
    # ...set session...
    session = requests.Session()

    # ..post credentials
    req = session.post('https://transkribus.eu/TrpServer/rest/auth/login',data = {'user': user, 'pw': pw})
    return session

# import documents to transkribus

# export, safe and load documents

## export page-xml to local machine
def export_pagexml(session, collection_id, document_id, startpage, endpage):
    # Get document via url https://transkribus.eu/TrpServer/rest/collections/{collection-ID}/{document-ID}/fulldoc
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

## download zip file to local maschine and unzip
def download_export(url):

    # download zip file to the subfolder ./documents on a local machine...
    zip_file_name = config.export_folder+'export.zip'
    zip_file = requests.get(url)
    zip_file.raise_for_status()
    save_file = open(zip_file_name,'wb')
    for chunk in zip_file.iter_content(100000):
        save_file.write(chunk)
    save_file.close()
    return zip_file_name

## unzip file
def unzip_file(zip_file_name):
    # ...unzip it into local folder...
    with ZipFile(zip_file_name,'r') as zip_obj:
        list_of_filenames = zip_obj.namelist()
        for filename in list_of_filenames:
            if 'page/' in filename:
                path_to_pagexml = filename.split('page/')[0]+'page/'
        zip_obj.extractall(config.export_folder)
    return path_to_pagexml

## get filenames in folder
def load_pagexml(folder_name):
    filenames = next(walk(folder_name))[2]
    path_to_files = sorted([folder_name + '/' + string for string in filenames])
    return path_to_files



## Getting list of abbreviations from remote exist-db collections provided by xquery script
def get_exist_data(user, pw, exist_url, resources_folder):
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




# postprocess page-xml

## detect and replace abbreviations using list of special characters as marker
def replace_abbreviations(dictionary_abbr_exist, line_of_text):

    # importing abbreviation dictionary in JSON file...
    with open(dictionary_abbr_exist) as json_file:
        dictionary_abbr_exist = json.load(json_file)



    return expanded_file

# train modells


# script
## start session
#session = login_transkribus(transkribus_credentials.username,transkribus_credentials.password)
## export pagexml
#export_file_url = export_pagexml(session, 80437, 535546, 29, 210)
## download exported file
#local_xml_files = download_export(export_file_url)
## unzip downloaded file
#unzip = unzip_file(local_xml_files)
# get abbreviations from existdb if provided using stored credentials
#dictionary_abbr_exist = get_exist_data(exist_credentials.user_exist, exist_credentials.pw_exist, config.exist_url, config.resources_folder)

filenames = load_pagexml('/home/michael/Dokumente/transpy/documents/535546/01_Transkription_BAV_Pal_lat_585/page')

with open('/home/michael/Dokumente/transpy/resources/abbreviation_dictionary.json','r') as json_file:
    dictionary_abbr_exist = json.load(json_file)

# open each pagexmlfile for postprocessing
for filename in filenames:
    tree = ET.parse(filename)
    root = tree.getroot()
    x = root.findall('.//{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode')
    for i in x:

        wordlist = i.text.split()
        # define special characters that point to abbreviated words as dictionary (depending on modell used for recognition)...
        special_characters_dict = {'-ur':'\uF1C2',
                '-bus':'\uF1AC',
                'b mit Strich':'\u0180',
                'd mit Strich':'\u0111',
                'h mit Strich':'\u0127',
                'K mit Strich':'\uA740',
                'k mit Strich':'\uA741',
                'L mit hohem Strich':'\uA748',
                'l mit hohem Strich':'\uA749',
                'l mit mittlerem Strich':'\u019A',
                'Pre':'P\u0304',
                'pre':'p\u0304',
                'Per':'\uA750',
                'per':'\uA751',
                'Pro':'\uA752',
                'pro':'\uA753',
                'Nasalstrich':'\u0304',
                'Kürzungsstrich':'\u0305',
                'q mit Strich':'\uA757',
                'q mit Schlaufe':'\uA759',
                '-rum':'\ua75D',
                '-RUM':'\ua75C',
                '-us':'\u1DD2',
                '-a (hochgestellt)':'\u1DD3',
                '-i (hochgestellt)':'\u0365',
                'hochgestelltes -o':'\u0366',
                'hochgestelltes -u':'\u0367',
                'Antwort-Zeichen R':'\u211E',
                'Q mit Strich':'\uA756',
                'Q mit Schlaufe':'\uA758'}

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
                    expansion = word
                    expansion = expansion.replace('om̅','omn')
                    expansion = expansion.replace('\uF1C2','ur')
                    expansion = expansion.replace('\uF1AC','us')
                    expansion = expansion.replace('P\u0304','Prae')
                    expansion = expansion.replace('p\u0304','prae')
                    expansion = expansion.replace('\uA750','Per')
                    expansion = expansion.replace('\uA751','per')
                    expansion = expansion.replace('\uA752','Pro')
                    expansion = expansion.replace('\uA753','pro')
                    expansion = expansion.replace('\u0304','m')
                    expansion = expansion.replace('\ua75D','rum')
                    expansion = expansion.replace('\ua75C','RUM')
                    expansion = expansion.replace('\u1DD2','us')
                    expansion = expansion.replace('c\u0305','con')
                    expansion = expansion.replace('t̅','ter')
                    expansion = expansion.replace('r̅','runt')

                #print(word, expansion)
                i.text = i.text.replace(word,expansion)
    new_filename = filename.replace('.xml','')+'_new.xml'
    with open(new_filename, 'w') as f:
        tree.write(f, encoding='unicode')
#eigentlich ist das so erstmal ausreichend, weil sich die meisten abkürzungen so ändern lassen ohne den wortumbruch zu erkennen
