import transpy
import config
import xml.etree.ElementTree as ET # for parsing xml data
import lxml.etree as LET # TODO replace etree for parsing xml data
from os import walk # handles filenames in folder
import pandas as pd
import re

""" Helper functions for 

"""

def identify_placement_of_element(coords):
    # left or right mit coordinaten bestimmen
    width = coords[0].split(' ')
    for points in width:
        points = points.split(',')
        #print(points)
        if int(points[0])<800:
            side = 'left'
        else:
            side = 'right'
    return side

def create_tei_pb(root, start_folia, link_to_facs):
    # create tei:pb
    page_break = '\n<pb n="'+ start_folia +'" facs="'+ link_to_facs + '{image_number}"/>'
    start_folia = transpy.increment_folia(start_folia)
    image_number = root.xpath('.//ns0:TranskribusMetadata/@pageNr', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
    page_break = page_break.replace('{image_number}',image_number.zfill(4))
    return page_break, image_number, start_folia

def create_tei_fw_head(root):
    # add tei:fw
    try:
        header = root.xpath('//ns0:TextRegion[contains(@type,"header")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        text_header = '\n<fw type="page-header" place="top" ana="{ana}">{fw}</fw>'
        unicode_header = header.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        coords_header = header.xpath('.//ns0:TextLine//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        #print(unicode_header)
        text_header = text_header.replace('{fw}',unicode_header[0])
        #print(text_header)
        text_header = text_header.replace('{ana}',coords_header[0])
    except:
        text_header = ''

    return text_header

def create_column_1(root, image_number):
    try:
        column_1 = root.xpath('//ns0:TextRegion[contains(@custom,"type:column_1")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        # create column 1 with coordiantes
        text_column_1 = '<cb n="a" ana="{ana}"/>'
        coords_column = column_1.xpath('.//ns0:TextLine//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        text_column_1 = text_column_1.replace('{ana}',coords_column[0])
        # lines in column
        unicode_column_1 = column_1.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        line_number = 0
        for line in unicode_column_1:
            line_text = line.xpath('.//ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_coords = line.xpath('.//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_number += 1
            text_column_1 = text_column_1 + '\n<lb n="' + str(line_number) + '" ana="' + line_coords[0] + '"/>' + line_text[0]
    except Exception as e:
        print(str(e) + ' >>>Textpage col 1 ('+image_number+')<<<')
        text_column_1 = '\n<cb n="a"/>'
    return text_column_1

def create_column_2(root, image_number):
    try:
        column_2 = root.xpath('//ns0:TextRegion[contains(@custom,"type:column_2")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        text_column_2 = '\n<cb n="b" ana="{ana}"/>'
        coords_column = column_2.xpath('.//ns0:TextLine//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        text_column_2 = text_column_2.replace('{ana}',coords_column[0])
        unicode_column_2 = column_2.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        line_number = 0
        for line in unicode_column_2:
            line_text = line.xpath('.//ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_coords = line.xpath('.//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_number += 1
            text_column_2 = text_column_2 + '\n<lb n="' + str(line_number) + '" ana="' + line_coords[0] + '"/>' + line_text[0]
    except Exception as e:
        print(str(e) + ' >>>Textpage col 2 ('+image_number+')<<<')
        text_column_2 = '\n<cb n="b"/>'
    return text_column_2

def create_tei_fw_foot(root):
    try:
        footer = root.xpath('//ns0:TextRegion[contains(@type,"footer")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        text_footer = '\n<fw type="quire-numeral" place="bottom" ana="{ana}">{fw}</fw>'
        unicode_footer = footer.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        coords_footer = footer.xpath('.//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        text_footer = text_footer.replace('{fw}',unicode_footer[0])
        text_footer = text_footer.replace('{ana}',coords_footer[0])
    except:
        text_footer = ''
    return text_footer

def test_text_page_for_element(search_string, string_to_be_replaced, replace_string, text_page):
    if search_string in text_page:
        text_page = re.sub(string_to_be_replaced, replace_string, text_page, flags=re.DOTALL)
    else:
        pass
    return text_page

def store_toc_label_for_later_replacement(toc_label_for_later_replacement, root):
    for chapter_number_toc in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        # create label element
        chapter_number_toc_text = chapter_number_toc.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        #print(chapter_number_toc_text)
        label_toc = '<item n="{n}"><label place="margin {left|right}" type="chapter-number" ana="{ana}"><hi rend="color:red">{chapter_number_toc}</hi></label> <hi rend="color:red">'.replace('{chapter_number_toc}',chapter_number_toc_text)
        coords_label_toc = chapter_number_toc.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        label_toc = label_toc.replace('{ana}',coords_label_toc[0])
        side = identify_placement_of_element(coords_label_toc)
        label_toc = label_toc.replace('{left|right}',side)
        replace_key = re.search('~(\d+)~',chapter_number_toc_text)
        replace_key = replace_key.group(0)
        div_number = replace_key.replace('~','')
        label_toc = label_toc.replace('{n}',div_number)
        # append div number and label_toc for later replacement to list
        list_item = [div_number,replace_key,label_toc]
        toc_label_for_later_replacement.append(list_item)
    return toc_label_for_later_replacement

def store_label_for_later_replacement(label_for_later_replacement, root):

    for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        try:
            #print(chapter_number)
            chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            print(chapter_number_text)
            label = '<div n="{n}" type="chapter"><head type="chapter-title"><label type="chapter-number" place="margin {left|right}" ana="{ana}"><hi rend="color:red">{chapter_number}</hi></label> <hi rend="color:red">'.replace('{chapter_number}',chapter_number_text)
            coords_label = chapter_number.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            label = label.replace('{ana}',coords_label[0])
            side = identify_placement_of_element(coords_label)
            label = label.replace('{left|right}',side)
            replace_key = re.search('\*(\d+)\*',label)
            replace_key = replace_key.group(0)
            div_number = replace_key.replace('*','')
            label = label.replace('{n}',div_number)
            list_item = [div_number,replace_key,label]
            label_for_later_replacement.append(list_item)

        except Exception as e:
            print(str(e) + ' >>>label<<<')

    return label_for_later_replacement

def store_interrogation_label_for_later_replacement(interrogation_label_for_later_replacement, root):
    for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        try:
            if '*i' in chapter_number_text:
                label = '<div n="{n}" type="interrogation"><label type="chapter-number" place="margin {left|right}" ana="{ana}"><hi rend="color:red">{chapter_number}</hi></label> \n<p n="1"><hi rend="color:red">'.replace('{chapter_number}',chapter_number_text)
                coords_label = chapter_number.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                label = label.replace('{ana}',coords_label[0])
                side = identify_placement_of_element(coords_label)
                label = label.replace('{left|right}',side)
                replace_key = re.search('\*i(\d+)\*',label)
                replace_key = replace_key.group(0)
                div_number = replace_key.replace('*','')
                div_number = div_number.replace('i','')
                label = label.replace('{n}',div_number)
                list_item = [div_number,replace_key,label]
                interrogation_label_for_later_replacement.append(list_item)
        except Exception as e:
            print(e + ' >>>Interrogation<<<')

    return interrogation_label_for_later_replacement

def store_inscription_for_later_replacement(inscriptions_to_replace, root):
    for inskription in root.xpath('//ns0:TextRegion[contains(@custom,"type:Inskription")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        inskription_text = ''
        for line in inskription.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            inskription_text = inskription_text + ' ' + line
        inskription_xml = '</hi></head>\n<note type="inscription" place="margin {left|right}" anchored="false" ana="{ana}">{Inskription}</note>'.replace('{Inskription}',inskription_text)

        coords_inskription = inskription.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

        side = identify_placement_of_element(coords_inskription)

        inskription_xml = inskription_xml.replace('{ana}',coords_inskription[0])
        inskription_xml = inskription_xml.replace('> ','>')
        inskription_xml = inskription_xml.replace('{left|right}',side)

        replace_key = re.search('\*(i\d+|\d+)\*',inskription_text)
        replace_key = replace_key.group(0)
        div_number = replace_key.replace('*','')
        text_to_be_replaced = '<div n="' + div_number + '" type="chapter"'
        replace_text = inskription_xml + '\n<p n="1"><hi rend="color:red initial">'
        inscriptions_to_replace.append([replace_text,text_to_be_replaced, replace_key])

    return inscriptions_to_replace

def create_text_from_pageXML(filenames, link_to_facs, start_folia):
    text_page = ""
    inscriptions_to_replace = []
    toc_label_for_later_replacement = []
    label_for_later_replacement = []
    interrogation_label_for_later_replacement =[]

    # open each pagexmlfile for exporting text to tei
    for filename in filenames:
        tree = LET.parse(filename)
        root = tree.getroot()
        # creates page beginning for each xml-pagefile
        page_break, image_number, start_folia = create_tei_pb(root, start_folia, link_to_facs)
        # adds tei:fw if header exists on page
        text_header = create_tei_fw_head(root)
        # creates text of column 1 from lines
        text_column_1 = create_column_1(root, image_number)
        # creates text of column 2 from lines
        text_column_2 = create_column_2(root, image_number)
        # creates tei:fw footer element
        text_footer = create_tei_fw_foot(root)
        # create page
        text_page = text_page + page_break + text_header + '\n' + text_column_1 + '\n' + text_column_2 + '\n' + text_footer
        # create list of toc_labels for later replacment
        try:
            toc_label_for_later_replacement = store_toc_label_for_later_replacement(toc_label_for_later_replacement, root)
        except:
            pass
        # create list of labels for later replacment
        try:
            label_for_later_replacement = store_label_for_later_replacement(label_for_later_replacement, root)
        except Exception as e:
            print(e)
        # create list of interrogation labels for later replacment
        try:
            interrogation_label_for_later_replacement = store_interrogation_label_for_later_replacement(interrogation_label_for_later_replacement, root)
        except:
            pass
        # create list of inscriptions for later replacment
        try:
            inscriptions_to_replace = store_inscription_for_later_replacement(inscriptions_to_replace, root)
        except:
            pass

        # test pagexml for certain elements and replace with corresponding tei
        elements_to_be_tested = [['~i~',r'~i~(.*?)~','<!-- Beginn Inhaltsverzeichnis -->\n<div type="toc" xml:id="vatican-bav-pal-585-01-toc">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head>\n<list>\n~'],
                                ['*i*',r'\*i\*(.*?)\*p\*','</list>\n</div>\n<!-- Beginn des Haupttextes  -->\n<div type="content" xml:id="vatican-bav-pal-585-01-con">\n<div xml:id="vatican-bav-pal-585-01-con-000" type="praefatiuncula">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head><p n="1"><hi rend="color:red">'],
                                ['#p#','#p#','</hi></p>\n</div>']]
        for element in elements_to_be_tested:
            text_page = test_text_page_for_element(element[0], element[1], element[2], text_page)

    return text_page, inscriptions_to_replace, interrogation_label_for_later_replacement, label_for_later_replacement, toc_label_for_later_replacement

## transform pagexml as single tei file according to bdd schematics
def bdd_export_tei(filenames, link_to_facs, start_folia):
    text_page, inscriptions_to_replace, interrogation_label_for_later_replacement, label_for_later_replacement, toc_label_for_later_replacement = create_text_from_pageXML(filenames, link_to_facs, start_folia)

    # Insert label TOC
    for element in toc_label_for_later_replacement:
        if int(element[0]) == 1:
            # treat first element differently
            text_page = re.sub('\n(<lb.*?/>)(</hi></head>\n)<list>\n~1~(\w)', '\g<2>\g<1><list>' + element[2].replace(element[1],'') + '\g<3></hi>', text_page)
        else:
            text_page = re.sub('\n(<lb.*?/>)' + element[1] + '(\w)', '</item>\n\g<1>' + element[2].replace(element[1],'') + '\g<2></hi>', text_page)

    # Insert label interrogation
    for element in interrogation_label_for_later_replacement:
        #print(element[0])
        if int(element[0]) == 1:
            # treat first element differently

            text_page = re.sub('\*i' + element[0] + '\*~(\w)', '</p>' + element[2].replace(element[1],'') + '\g<1></hi>', text_page)
        else:
            text_page = re.sub('\*i' + element[0] + '\*~(\w)', '</p></div>' + element[2].replace(element[1],'') + '\g<1></hi>', text_page)

    # Insert label chapter
    for element in label_for_later_replacement:
        #print(element[1])
        if int(element[0]) == 1:
            # treat first element differently
            text_page = re.sub('\*' + element[0] + '\*', element[2].replace(element[1],''), text_page)

        else:
            text_page = re.sub('\*' + element[0] + '\*','</p>\n</div>\n' + element[2].replace(element[1],''), text_page)



    for element in inscriptions_to_replace:
        if 'i1' in element[0]:
            # interrogationes start with inscription instead of interrogation number
            element[0] = element[0].replace('</hi></head>\n', '')
            element[0] = element[0].replace('\n<p n="1"><hi rend="color:red initial">', '')

            text_page = re.sub('\*i1\*(.*?)~(\w)', '</p>\n<div n="1" type="interrogation"><head type="chapter-title"><hi rend="color:red">\g<1></hi></head>\n' + element[0].replace('*i1*', '') + '<p n="1"><hi rend="color:red">\g<2></hi>',text_page,flags=re.DOTALL)
        else:
            text_page = re.sub('(' + element[1] + '.*?)~','\g<1>' + element[0].replace(element[2], '') + '~',text_page,flags=re.DOTALL)

    # TODO put Postprocessing in function
    text_page = text_page.replace('</item></item>','</item>')
    text_page = text_page.replace('</list>','</item></list>')
    text_page = re.sub('\*\d+\*','',text_page)
    text_page = re.sub('\~\d+\~','',text_page)
    text_page = re.sub('#(\w)','<hi rend="versal">\g<1></hi>',text_page)
    text_page = re.sub('~(\w)','\g<1></hi>',text_page)

    return text_page

def sc_to_g(text_page):
    """ TODO

    """
    # declare special character and corresponding g-element according to project standard...
    # TODO: update special character and put into config

    character_list = [['<g ref="#char-f1ac"></g>',''],
    ['<g ref="#char-f1f8"></g>',''],
    ['<g ref="#char-f1ea"></g>',''],
    ['<g ref="#char-f1f5"></g>',''],
    ['<g ref="#char-f1f0"></g>',''],
    ['<g ref="#char-f160"></g>',''],
    ['<g ref="#char-int-pcode"></g>',''],
    ['<g ref="#char-f1e1"></g>',''],
    ['<g ref="#char-0180">ƀ</g>','ƀ'],
    ['<g ref="#char-0111">đ</g>','đ'],
    ['<g ref="#char-0127">ħ</g>','ħ'],
    ['<g ref="#char-a740">Ꝁ</g>','Ꝁ'],
    ['<g ref="#char-a741">ꝁ</g>','ꝁ'],
    ['<g ref="#char-a748">Ꝉ</g>','Ꝉ'],
    ['<g ref="#char-a749">ꝉ</g>','ꝉ'],
    ['<g ref="#char-019a">ƚ</g>','ƚ'],
    ['<g ref="#char-0119">ę</g>','ę'],
    ['<g ref="#char-a750">Ꝑ</g>','Ꝑ'],
    ['<g ref="#char-a751">ꝑ</g>','ꝑ'],
    ['<g ref="#char-a752">Ꝓ</g>','Ꝓ'],
    ['<g ref="#char-a753">ꝓ</g>','ꝓ'],
    ['<g ref="#char-0304">&#x0304;</g>','&#x0304;'],
    ['<g ref="#char-0305">&#x0305;</g>','&#x0305;'],
    ['<g ref="#char-a757">ꝗ</g>','ꝗ'],
    ['<g ref="#char-a759">ꝙ</g>','ꝙ'],
    ['<g ref="#char-a75D">ꝝ</g>','ꝝ'],
    ['<g ref="#char-a75C">Ꝝ</g>','Ꝝ'],
    ['<g ref="#char-1dd2">&#x1dd2;</g>','&#x1dd2;'],
    ['<g ref="#char-1dd3">&#x1dd3;</g>','&#x1dd3;'],
    ['<g ref="#char-0365">&#x0365;</g>','&#x0365;'],
    ['<g ref="#char-0300">◌̀</g>','◌̀'],
    ['<g ref="#char-0301">◌́</g>','◌́'],
    ['<g ref="#char-0302">◌̂</g>','◌̂'],
    ['<g ref="#char-0306">◌̆</g>','◌̆'],
    ['<g ref="#char-0366">◌ͦ</g>','◌ͦ'],
    ['<g ref="#char-0367">◌ͧ</g>','◌ͧ'],
    ['<g ref="#char-211E">℞</g>','℞'],
    ['<g ref="#char-a756">Ꝗ</g>','Ꝗ'],
    ['<g ref="#char-a758">Ꝙ</g>','Ꝙ'],
    ['<g ref="#char-2234">∴</g>','∴'],
    ['<g ref="#char-23D1">⏑</g>','⏑']]

    # ...replace special character...
    for character in character_list:
        text_page = text_page.replace(character[1],character[0])

    return text_page

def bdd_specific_tei(text_page):
    # <add> used in Transkribus to show inline additions
    # TODO best to leave attributs empty to mark dem in oxygen
    text_page = text_page.replace('<add>','<add place="above" type="contemporary">')

    # unclear
    text_page = text_page.replace('...','<unclear reason="tight-binding" resp="Transkribus" cert="low">...</unclear>')

    # editorial comment
    text_page = text_page.replace('[','<note type="editorial-comment" resp="transkribus">')
    text_page = text_page.replace(']','</note>')
    return text_page

def pp_choice(xml,text_page):
    text_page = re.sub('(<choice><abbr>)(<'+xml+'.*?>)(.*?</abbr><expan>)(<'+xml+'.*?>)(.*?</expan></choice>)','\g<2>\g<1>\g<3>\g<5>',text_page)
    text_page = re.sub('(<choice><abbr>.*?)</'+xml+'>(</abbr><expan>.*?)</'+xml+'>(.*?</expan></choice>)','\g<1>\g<2>\g<3></'+xml+'>',text_page)
    return text_page

""" wrapper

    AUflösung von Sonderzeichen muss ganz am Ende kommen
"""

def dl_and_export_to_oxygen(collection_id, document_id, startpage, endpage):
    #transpy.download_data_from_transkribus(collection_id, document_id, startpage, endpage)
    path_to_files = transpy.load_pagexml(config.export_folder + '855714/Rom_BAV_Pal__lat__585_ED_duplicated/page/')
    dictionary_abbr_external = transpy.load_abbreviation_dict()
    text_page = bdd_export_tei(path_to_files, 'https://digi.ub.uni-heidelberg.de/diglit/bav_pal_lat_585/', '15r')
    text_page = transpy.line_breaks_angled_dash(text_page)
    text_page = transpy.replace_abbreviations_from_tei(dictionary_abbr_external, text_page)
    text_page = bdd_specific_tei(text_page)

    # correction special cases
    text_page = re.sub('<choice><abbr><choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice></abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>','<choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>' ,text_page)
    text_page = re.sub('(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> )<choice><abbr><hi rend="color:red">','\g<1><hi rend="color:red"><choice><abbr>',text_page,flags=re.DOTALL)
    text_page = re.sub('(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> <hi rend="color:red"><choice><abbr>.*?<expan>)<hi rend="color:red">','\g<1>',text_page,flags=re.DOTALL)

    text_page = re.sub('(\n\n<pb.*?/>\n<fw.*?>\n<cb n="a".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',text_page)
    text_page = re.sub('(\n<cb n="b".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',text_page)
    text_page = re.sub('(\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',text_page)



#(<lb.*?\/>)<\/hi><\/head>


    # correction of ambigue expansions
    # Capitula in fw
    text_page = re.sub('(<fw.*?><choice><abbr>Cap\u0305</abbr><expan>)Capitulum(</expan></choice>.*?</fw>)','\g<1>Capitula\g<2>',text_page)

    # Cap in fw ohne Auflösung
    text_page = re.sub('(<fw.*?>)Cap\u0305(.*?</fw>)','\g<1><choice><abbr>Cap\u0305</abbr><expan>Capitula</expan></choice>\g<2>',text_page)

    # Ex concilio
    text_page = re.sub('(<note type="inscription".*?>Ex <choice>.*?<expan>)concilium(</expan>)','\g<1>concilio\g<2>',text_page)

    # Ex eodem capitulo
    text_page = re.sub('(<note type="inscription".*?>Ex eodem <choice>.*?<expan>)Capitula(<)','\g<1>Capitulo\g<2>',text_page)

    # correction generic cases
    xml_to_be_corrected = ['lb ', 'add', 'p','hi></label', 'item', 'note']

    for i in xml_to_be_corrected:
        text_page = pp_choice(i, text_page)

    # correction of linebreaks
    text_page = re.sub('¬\n(<pb.*?<lb .*?)(/>)','\g<1> break="no"\g<2>', text_page,flags=re.DOTALL)

    # Bei <hi>Q</hi> kommt <hi>Qu</hi>. EInsetzen um ein Buchstaben verrückt, aber nur bei Wörtern mit Q?
    text_page = re.sub('¬\n(<pb.*?<lb .*?)(/>)','\g<1> break="no"\g<2>', text_page,flags=re.DOTALL)

    text_page = sc_to_g(text_page)

    #replace placeholder in template file and save as new file
    with open('/home/michael/Dokumente/transpy/resources/tei_template.xml','r') as xmlfile:
        template_file = xmlfile.read()

    new_file = template_file.replace('%%',text_page)
    with open('/home/michael/Dokumente/transpy/resources/8855714-01-new.xml','w') as newfile:
        newfile.write(new_file)



# TODO Quod mit hi
# angled dash bei inscription

# TODO einzelne Sonderzeichen ersetzen durch tei:g, code aufräumen
"""


# prepare for collation using collatex
def postprocess_for_collatex(text,sigla):
    # delete interpunctuation
    text = text.replace('\uF1F8','').replace('\uF1EA','').replace('\uF1F5','').replace('\uF1F0','').replace('\uF160','').replace('\uF1E2','').replace('\uF1E1','')
    # delete linebreaks
    text = text.replace("\n<cb n='b'/>",'')
    text = text.replace("\n<pb/><cb n='a'/>",'')
    text = text.replace("<pb/><cb n='a'/>",'')
    text = text.replace('\n<lb/>',' ')
    text = text.replace("<lb break='no'/>",'')
    text = text.replace("<cb n='b'/><lb break='no'/>",'')
    text = text.replace("<cb n='b'/>",'')
    with open('/home/michael/Dokumente/BDD/Collation/witnesses/'+sigla+'.txt','w') as f:
        f.write(text)
    return text

"""
""" execute

"""

# download_data_from_transkribus(80437, 855714, 37, 33)
dl_and_export_to_oxygen(80437, 855714, 37, 218)

#v
#download_data_from_transkribus(80437,793755,37,218)
#text = postproccess_tei('793755/Rom_BAV_Pal__lat__585_ED/page', 'output.xml')
#postprocess_for_collatex(text,'V')

#b
#download_data_from_transkribus(80437,732612,24,48)
#text = postproccess_tei('732612/01_Transkription_Bamberg_Stabi_Can_6/page', 'output.xml')
#postprocess_for_collatex(text,'B')

#postprocess_pagexml('793755/Rom_BAV_Pal__lat__585_ED/page', 'output.xml')
## converts files to simple tei
#path_to_files = load_pagexml(config.export_folder + '793755/Rom_BAV_Pal__lat__585_ED/page/expanded/')
#print(path_to_files)
#text_page = export_tei(path_to_files)
#print('Starting creating linebreaks')
#processed_text = line_breaks(text_page)
#print(processed_text)
#with open('./bav-pal-lat-585.txt','w') as f:
#    f.write(processed_text)
