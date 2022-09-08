import transpy
import config
import lxml.etree as LET
import re

""" Helper functions for creating BDD:tei from pageXML

"""


def identify_placement_of_element(coords):
    """ Identifies place of element by coordinates taken from pageXML

    Takes list of coordinates of an elements textregion and checks side of placement on page.
    Returns 'lest' or 'right' as string for replacing placeholder {left|right} in xml.
    :param coords: coordinates of element as list
    :return side: 'left' or 'right' as string
    """

    width = coords[0].split(' ')
    for points in width:
        points = points.split(',')
        if int(points[0])<800:
            side = 'left'
        else:
            side = 'right'
    return side

# TODO muss implementiert werden: ids der Bilder muss rein, eventuell collection
#facs="https://sammlungen.ub.uni-frankfurt.de/i3f/v20/2035625/full/full/0/default.jpg"
# corresp="https://sammlungen.ub.uni-frankfurt.de/msma/i3f/v20/2035614/canvas/2035625"
# ana="/annotations/frankfurt-ub-b-50-annotation-2035625"/

# Frankfurt
# link to facs: https://sammlungen.ub.uni-frankfurt.de/i3f/v20/2035625/full/full/0/default.jpg
# iiif canvas https://sammlungen.ub.uni-frankfurt.de/msma/i3f/v20/2035614/canvas/2035625
# ana /annotations/frankfurt-ub-b-50-annotation-2035625

#Vatikan:
# link to facs https://digi.vatlib.it/pub/digit/MSS_Pal.lat.585/iiif/Pal.lat.585_0010_fa_0001v.jp2/full/full/0/default.jpg
#iiif canvas https://digi.vatlib.it/iiif/MSS_Pal.lat.585/canvas/p0013
# ana /annotations/vatican-bav-pal-lat-585-annotation-p0013


def create_tei_pb(root, start_folia, iiif_image_id, ms):
    """ create tei:pb

    Creates tei:bp element including link to facsimile from information stored in pageXML
    as well as external information provided.

    :param root: Takes root from etree
    :param start_folia: Takes first folio (e.g. 10r) as string for incrementing folia
    :param link_to_facs: Takes base url link to iiif facsimilie without pagenumber
    :param link_to_canvas: Takes base url link to iiif canvas without pagenumber
    :param path_to_annotation: Takes path to annotation file without pagenumber
    :param iiif_image_id: Takes iiif image id as int
    :param iiif_image_id: Name3 of manuscript to be processed (F, V or B) as string
    :return page_break: Returns tei:pb element as string
    :return image_number: Returns image_number for debugging
    :return start_folia: Returns incremented folio
    """

#Vatikan:
# link to facs https://digi.vatlib.it/pub/digit/MSS_Pal.lat.585/iiif/Pal.lat.585_0009_fa_0001r.jp2/full/full/0/default.jpg
#iiif canvas https://digi.vatlib.it/iiif/MSS_Pal.lat.585/canvas/p0009
# ana /annotations/vatican-bav-pal-lat-585-annotation-p0013

    if ms == 'V':
        if 'r' in start_folia:
            jpg_folia = start_folia[:-1].zfill(4)+'r'
        else:
            jpg_folia = start_folia[:-1].zfill(4)+'v'
        jpg_number = str(iiif_image_id).zfill(4) + '_fa_' + jpg_folia
        canvas_number = 'p' + str(iiif_image_id).zfill(4)
        page_break = '\n<pb n="'+ start_folia + '" facs="https://digi.vatlib.it/pub/digit/MSS_Pal.lat.585/iiif/Pal.lat.585_' + jpg_number + '.jp2/full/full/0/default.jpg" corresp="https://digi.vatlib.it/iiif/MSS_Pal.lat.585/canvas/'+ canvas_number + '" ana="/annotations/vatican-bav-pal-lat-585-annotation-' + canvas_number + '"/>'
        start_folia = transpy.increment_folia(start_folia)
        iiif_image_id = iiif_image_id+1
    elif ms == 'V2':
        if 'r' in start_folia:
            jpg_folia = start_folia[:-1].zfill(4)+'r'
        else:
            jpg_folia = start_folia[:-1].zfill(4)+'v'
        jpg_number = str(iiif_image_id).zfill(4) + '_fa_' + jpg_folia
        canvas_number = 'p' + str(iiif_image_id).zfill(4)
        page_break = '\n<pb n="'+ start_folia + '" facs="https://digi.vatlib.it/pub/digit/MSS_Pal.lat.586/iiif/Pal.lat.586_' + jpg_number + '.jp2/full/full/0/default.jpg" corresp="https://digi.vatlib.it/iiif/MSS_Pal.lat.585/canvas/'+ canvas_number + '" ana="/annotations/vatican-bav-pal-lat-585-annotation-' + canvas_number + '"/>'
        start_folia = transpy.increment_folia(start_folia)
        iiif_image_id = iiif_image_id+1


# Frankfurt
# link to facs: https://sammlungen.ub.uni-frankfurt.de/i3f/v20/2035625/full/full/0/default.jpg
# iiif canvas https://sammlungen.ub.uni-frankfurt.de/msma/i3f/v20/2035614/canvas/2035625
# ana /annotations/frankfurt-ub-b-50-annotation-2035625
    elif ms == 'F':
        page_break = '\n<pb n="'+ start_folia +'" facs="https://sammlungen.ub.uni-frankfurt.de/i3f/v20/' + str(iiif_image_id) + '/full/full/0/default.jpg" corresp="https://sammlungen.ub.uni-frankfurt.de/msma/i3f/v20/2035614/canvas/' + str(iiif_image_id) + '" ana="/annotations/frankfurt-ub-b-50-annotation-' + str(iiif_image_id) + '"/>'
        start_folia = transpy.increment_folia(start_folia)
        image_number = root.xpath('.//ns0:TranskribusMetadata/@pageNr', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        iiif_image_id = iiif_image_id+1
    elif ms == 'B':
        page_break = '\n<pb n="'+ start_folia +'" facs="{URL}' + str(iiif_image_id) + '/full/full/0/default.jpg" corresp="{URL}' + str(iiif_image_id) + '" ana="/annotations/bamberg-sb-c-6-annotation-' + str(iiif_image_id) + '"/>'
        start_folia = transpy.increment_folia(start_folia)
        image_number = root.xpath('.//ns0:TranskribusMetadata/@pageNr', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        iiif_image_id = iiif_image_id+1
    elif ms == 'K':
        page_break = '\n<pb n="'+ start_folia +'" facs="https://digital.dombibliothek-koeln.de/i3f/v20/' + str(iiif_image_id) + '/full/full/0/default.jpg" corresp="https://digital.dombibliothek-koeln.de/i3f/v20/284343/canvas/' + str(iiif_image_id) + '" ana="/annotations/koeln-edd-c-119-annotation-' + str(iiif_image_id) + '"/>'
        start_folia = transpy.increment_folia(start_folia)
        image_number = root.xpath('.//ns0:TranskribusMetadata/@pageNr', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        iiif_image_id = iiif_image_id+1
    # für generische Lösung:
    # page_break = '\n<pb n="'+ start_folia +'" facs="'+ link_to_facs + str(iiif_image_id) + '/full/full/0/default.jpg" corresp="'+ link_to_canvas + str(iiif_image_id) + '" ana="'+path_to_annotation + iiif_image_id + '"/>'
    # start_folia = transpy.increment_folia(start_folia)
    # image_number = root.xpath('.//ns0:TranskribusMetadata/@pageNr', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
    # iiif_image_id = iiif_image_id+1

    # hier muss image id rein
    #page_break = page_break.replace('{image_number}',image_number.zfill(4))
    return page_break, iiif_image_id, start_folia


def coords_baseline(root, xpath, ms):
    """ Koordinaten aus baseline holen
    """

    if ms == 'V':
        x = 1
    elif ms == 'V2':
        x = 1
    elif ms == 'F':
        x = 1.34
    elif ms == 'B':
        x = 1
    elif ms == 'K':
        x = 1

    coords = root.xpath(xpath, namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

    for i in coords:
        coord = i.split(' ')
        coord_left = coord[0].split(',')
        coord_right = coord[-1].split(',')
        c1 = int(int(coord_left[0])*x)-20 #full bild von frankfurt 1.3 größer als in transkribus
        c2 = int(int(coord_left[1])*x)-50
        w = int(coord_right[0])-int(coord_left[0])+80
        w = int(w*x)
        h = 100
    coord_string = str(c1) + ',' + str(c2) + ',' + str(w) + ',' + str(h)
    return coord_string


def coords_text_region(root, xpath, ms):
    """ Koordinaten aus textregion holen
    """

    if ms == 'V':
        x = 1
    elif ms == 'V2':
        x = 1
    elif ms == 'F':
        x = 1.34
    elif ms == 'B':
        x = 1
    elif ms == 'K':
        x = 1
    coords = root.xpath(xpath, namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

    for i in coords:
        coords_list_left = []
        coords_list_right = []
        coord = i.split(' ')
        for e in coord:
            e=e.split(',')
            coords_list_left.append(int(e[0]))
            coords_list_right.append(int(e[1]))

    c1 = int(min(coords_list_left)*x)
    w = max(coords_list_left)
    w = int(w*x)
    w = w-c1
    w = w+30
    c2 = min(coords_list_right)
    c2 = int(c2*x)
    h = max(coords_list_right)
    h = int(h*x)
    h = h-c2
    h = h+30
    c2 = c2-30

    coord_string = str(c1) + ',' + str(c2) + ',' + str(w) + ',' + str(h)
    return coord_string


def create_tei_fw_head(root, ms):
    """ create tei:fw for header

    Creates tei:fw element including header if available from pageXML.

    :param root: Takes root from etree
    :return text_header: Returns tei:fw element as string
    """

    try:
        header = root.xpath('//ns0:TextRegion[contains(@type,"header")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        text_header = '\n<fw type="page-header" place="top" facs="{facs}">{fw}</fw>'
        unicode_header = header.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        coords_header = coords_baseline(header, './/ns0:TextLine//ns0:Baseline/@points', ms)

        #print(unicode_header)
        text_header = text_header.replace('{fw}',unicode_header[0])
        #print(text_header)
        text_header = text_header.replace('{facs}',coords_header)
    except Exception as e:
        #handleException(e)
        #raise
        print(e)
        #pass
        text_header = ''

    return text_header

def create_column_1(root, image_number, ms):
    """ creates text of column 1 from pageXML

    Creates text of column one including tei:lb elements as well as coordinates stored in tei:@facs from pageXML.

    :param root: Takes root from etree
    :param image_number: Takes image_number provided by create_tei_pb() for debuging
    :return text_column_1: Returns text of column 1 element as string
    """

    try:
        column_1 = root.xpath('//ns0:TextRegion[contains(@custom,"type:column_1")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        # create column 1 with coordiantes
        text_column_1 = '<cb n="a" facs="{facs}"/>'

        #coords_column = column_1.xpath('.//ns0:TextLine//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        #text_column_1 = text_column_1.replace('{facs}',coords_column[0])
        coords_column = coords_text_region(column_1, './ns0:Coords/@points', ms)
        text_column_1 = text_column_1.replace('{facs}',coords_column)

        # lines in column
        unicode_column_1 = column_1.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        line_number = 0
        for line in unicode_column_1:
            line_text = line.xpath('.//ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            #line_coords = line.xpath('.//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_coords = coords_text_region(line, './/ns0:Coords/@points', ms)
            line_number += 1
            text_column_1 = text_column_1 + '\n<lb n="' + str(line_number) + '" facs="' + line_coords + '"/>' + line_text[0]
    except Exception as e:
        print(str(e) + ' >>>Textpage col 1 ('+str(image_number)+')<<<')
        text_column_1 = '\n<cb n="a"/>'
    return text_column_1

def create_column_2(root, image_number, ms):
    """ creates text of column 2 from pageXML

    Creates text of column one including tei:lb elements as well as coordinates stored in tei:@facs from pageXML.

    :param root: Takes root from etree
    :param image_number: Takes image_number provided by create_tei_pb() for debuging
    :return text_column_2: Returns text of column 2 element as string
    """

    try:
        column_2 = root.xpath('//ns0:TextRegion[contains(@custom,"type:column_2")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        text_column_2 = '\n<cb n="b" facs="{facs}"/>'

        #coords_column = column_2.xpath('.//ns0:TextLine//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        #text_column_2 = text_column_2.replace('{facs}',coords_column[0])

        coords_column = coords_text_region(column_2, './ns0:Coords/@points', ms)
        text_column_2 = text_column_2.replace('{facs}',coords_column)

        unicode_column_2 = column_2.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        line_number = 0
        for line in unicode_column_2:
            line_text = line.xpath('.//ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            #line_coords = line.xpath('.//ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_coords = coords_text_region(line, './/ns0:Coords/@points', ms)
            line_number += 1
            text_column_2 = text_column_2 + '\n<lb n="' + str(line_number) + '" facs="' + line_coords + '"/>' + line_text[0]
    except Exception as e:
        print(str(e) + ' >>>Textpage col 2 ('+str(image_number)+')<<<')
        text_column_2 = '\n<cb n="b"/>'
    return text_column_2

def create_tei_fw_foot(root, ms):
    """ create tei:fw for footer

    Creates tei:fw element including footer if available from pageXML.

    :param root: Takes root from etree
    :return text_footer: Returns tei:fw element as string
    """

    try:
        footer = root.xpath('//ns0:TextRegion[contains(@type,"footer")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        text_footer = '\n<fw type="quire-numeral" place="bottom" facs="{facs}">{fw}</fw>'
        unicode_footer = footer.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        coords_footer = coords_baseline(footer, './/ns0:TextLine//ns0:Baseline/@points', ms)

        text_footer = text_footer.replace('{fw}',unicode_footer[0])
        text_footer = text_footer.replace('{facs}',coords_footer[0])
    except:
        text_footer = ''
    return text_footer

def test_text_page_for_element(search_string, string_to_be_replaced, replace_string, text_page):
    """ Replaces special placeholder with proper xml

    Takes placeholder as well as replacement provided by list in create_text_from_pageXML()
    and replaces in tei and returns updated tei.

    :param search_string:
    :param string_to_be_replaced:
    :param replace_string:
    :param text_page: Takes tei created from pageXML
    :return text_page: Returns updated tei
    """

    if search_string in text_page:
        text_page = re.sub(string_to_be_replaced, replace_string, text_page, flags=re.DOTALL)
    else:
        pass
    return text_page

def store_toc_label_for_later_replacement(toc_label_for_later_replacement, root, ms):
    for chapter_number_toc in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        # create label element
        chapter_number_toc_text = chapter_number_toc.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        #print(chapter_number_toc_text)
        label_toc = '<item n="{n}"><label place="margin {left|right}" type="chapter-number" facs="{facs}"><hi rend="color:red">{chapter_number_toc}</hi></label> <hi rend="color:red">'.replace('{chapter_number_toc}',chapter_number_toc_text)
        coords_label_toc_a = chapter_number_toc.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        coords_label_toc_b = coords_text_region(chapter_number_toc, './ns0:Coords/@points', ms)
        label_toc = label_toc.replace('{facs}',coords_label_toc_b)
        side = identify_placement_of_element(coords_label_toc_a)
        label_toc = label_toc.replace('{left|right}',side)
        replace_key = re.search('~(\d+)~',chapter_number_toc_text)
        replace_key = replace_key.group(0)
        div_number = replace_key.replace('~','')
        label_toc = label_toc.replace('{n}',div_number)
        # append div number and label_toc for later replacement to list
        list_item = [div_number,replace_key,label_toc]
        toc_label_for_later_replacement.append(list_item)
    return toc_label_for_later_replacement

def store_label_for_later_replacement(label_for_later_replacement, root, ms):

    for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        try:
            print(chapter_number)
            chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            print(chapter_number_text)
            label = '<div n="{n}" type="chapter"><head type="chapter-title"><label type="chapter-number" place="margin {left|right}" facs="{facs}"><hi rend="color:red">{chapter_number}</hi></label> <hi rend="color:red">'.replace('{chapter_number}',chapter_number_text)
            coords_label_a = chapter_number.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_label_b = coords_text_region(chapter_number, './ns0:Coords/@points', ms)
            label = label.replace('{facs}',coords_label_b)
            side = identify_placement_of_element(coords_label_a)
            label = label.replace('{left|right}',side)
            replace_key = re.search('\*(\d+)\*',label)
            replace_key = replace_key.group(0)
            div_number = replace_key.replace('*','')
            label = label.replace('{n}',div_number)
            list_item = [div_number,replace_key,label]
            label_for_later_replacement.append(list_item)

        except Exception as e:
            print(str(e) + '>>>label<<<')

    return label_for_later_replacement

def store_interrogation_label_for_later_replacement(interrogation_label_for_later_replacement, root, ms):
    for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
        try:
            if '*i' in chapter_number_text:
                label = '<div n="{n}" type="interrogation"><label type="chapter-number" place="margin {left|right}" facs="{facs}"><hi rend="color:red">{chapter_number}</hi></label> \n<p n="1"><hi rend="color:red">'.replace('{chapter_number}',chapter_number_text)
                coords_label_a = chapter_number.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                coords_label_b = coords_text_region(chapter_number, './ns0:Coords/@points', ms)
                label = label.replace('{facs}',coords_label_b)
                side = identify_placement_of_element(coords_label_a)
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

def store_inscription_for_later_replacement(inscriptions_to_replace, root, ms):
    for inskription in root.xpath('//ns0:TextRegion[contains(@custom,"type:Inskription")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        inskription_text = ''
        for line in inskription.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            inskription_text = inskription_text + ' ' + line
        inskription_xml = '</hi></head>\n<note type="inscription" place="margin {left|right}" anchored="false" facs="{facs}">{Inskription}</note>'.replace('{Inskription}',inskription_text)

        coords_inskription_a = inskription.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
        coords_inskription_b = coords_text_region(inskription, './ns0:Coords/@points', ms)
        side = identify_placement_of_element(coords_inskription_a)

        inskription_xml = inskription_xml.replace('{facs}',coords_inskription_b)
        inskription_xml = inskription_xml.replace('> ','>')
        inskription_xml = inskription_xml.replace('{left|right}',side)

        replace_key = re.search('\*(i\d+|\d+)\*',inskription_text)
        replace_key = replace_key.group(0)
        div_number = replace_key.replace('*','')
        text_to_be_replaced = '<div n="' + div_number + '" type="chapter"'
        replace_text = inskription_xml + '\n<p n="1"><hi rend="color:red initial">'
        #print(replace_key, replace_text)
        inscriptions_to_replace.append([replace_text,text_to_be_replaced, replace_key])

    return inscriptions_to_replace

def create_text_from_pageXML(filenames, start_folia, iiif_image_id, ms, ms_id):
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
        page_break, iiif_image_id, start_folia = create_tei_pb(root, start_folia, iiif_image_id, ms)
        # adds tei:fw if header exists on page
        text_header = create_tei_fw_head(root, ms)
        # creates text of column 1 from lines
        text_column_1 = create_column_1(root, iiif_image_id, ms)
        # creates text of column 2 from lines
        text_column_2 = create_column_2(root, iiif_image_id, ms)
        # creates tei:fw footer element
        text_footer = create_tei_fw_foot(root, ms)
        # create page
        text_page = text_page + page_break + text_header + '\n' + text_column_1 + '\n' + text_column_2 + '\n' + text_footer
        # create list of toc_labels for later replacment
        try:
            toc_label_for_later_replacement = store_toc_label_for_later_replacement(toc_label_for_later_replacement, root, ms)
        except:
            pass
        # create list of labels for later replacment
        try:
            label_for_later_replacement = store_label_for_later_replacement(label_for_later_replacement, root, ms)
        except Exception as e:
            print(e)
        # create list of interrogation labels for later replacment
        try:
            interrogation_label_for_later_replacement = store_interrogation_label_for_later_replacement(interrogation_label_for_later_replacement, root, ms)
        except:
            pass
        # create list of inscriptions for later replacment
        try:
            inscriptions_to_replace = store_inscription_for_later_replacement(inscriptions_to_replace, root, ms)
        except:
            pass

        # test pagexml for certain elements and replace with corresponding tei
        elements_to_be_tested = [['~i~',r'~i~(.*?)~','<!-- Beginn Inhaltsverzeichnis -->\n<div type="toc" xml:id="'+ ms_id +'-toc">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head>\n<list>\n~'],
                                ['*i*',r'\*i\*(.*?)\*p\*','</list>\n</div>\n<!-- Beginn des Haupttextes  -->\n<div type="content" xml:id="'+ ms_id +'-con">\n<div xml:id="'+ ms_id +'-con-000" type="praefatiuncula">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head><p n="1"><hi rend="color:red">'],
                                ['#p#','#p#','</hi></p>\n</div>']]
        for element in elements_to_be_tested:
            text_page = test_text_page_for_element(element[0], element[1], element[2], text_page)

    return text_page, inscriptions_to_replace, interrogation_label_for_later_replacement, label_for_later_replacement, toc_label_for_later_replacement

## transform pagexml as single tei file according to bdd schematics
def bdd_export_tei(filenames, start_folia, iiif_image_id, ms, ms_id):
    text_page, inscriptions_to_replace, interrogation_label_for_later_replacement, label_for_later_replacement, toc_label_for_later_replacement = create_text_from_pageXML(filenames, start_folia, iiif_image_id, ms, ms_id)

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
    ['<pc type="distinctio"><g ref="#char-f1f8"></g></pc>',''],
    ['<pc type="p-versus"><g ref="#char-f1ea"></g></pc>',''],
    ['<pc type="p-flexus"><g ref="#char-f1f5"></g></pc>',''],
    ['<pc type="p-comma-positura"><g ref="#char-f1e4"></g></pc>',''],
    ['<pc type="p-elevatus"><g ref="#char-f1f0"></g></pc>',''],
    ['<pc type="p-interrogativus"><g ref="#char-f160"></g></pc>',''],
    ['<pc type="p-interrogativus-positura"><g ref="#char-int-posit"></g></pc>',''],
    ['<g ref="#char-f1e1"></g>',''],
    ['<g ref="#char-0180">ƀ</g>','ƀ'],
    ['<g ref="#char-0111">đ</g>','đ'],
    ['<g ref="#char-0127">ħ</g>','ħ'],
    ['<g ref="#char-f1c2"></g>',''],
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
    ['<g ref="#char-0304">&#x0304;</g>','\u0304'],
    ['<g ref="#char-0305">&#x0305;</g>','\u0305'],
    ['<g ref="#char-a757">ꝗ</g>','ꝗ'],
    ['<g ref="#char-a759">ꝙ</g>','ꝙ'],
    ['<g ref="#char-a75D">ꝝ</g>','ꝝ'],
    ['<g ref="#char-a75C">Ꝝ</g>','Ꝝ'],
    ['<g ref="#char-1dd2">&#x1dd2;</g>','\u1dd2'],
    ['<g ref="#char-1dd3">&#x1dd3;</g>','\u1dd3'],
    ['<g ref="#char-0365">&#x0365;</g>','\u0365'],
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

def bdd_specific_tei(text_page, ms_id):
    # <add> used in Transkribus to show inline additions
    text_page = text_page.replace('<add>', '<add place="above" type="contemporary">')

    # unclear
    text_page = text_page.replace('...', '<unclear reason="tight-binding" resp="Transkribus" cert="low">...</unclear>')

    # editorial comment
    text_page = text_page.replace('[', '<note type="editorial-comment" resp="transkribus">')
    text_page = text_page.replace(']', '</note>')
    text_page = text_page.replace('<note>', '<note type="editorial-comment" resp="transkribus">')

    # del
    text_page = text_page.replace('<del>', '<del rend="">')

    # seg
    n = 1
    for i in re.findall('<seg>.*?</seg>', text_page):
        print(i)
        id = ms_id + '-supp-' + str(n).zfill(3)
        seg_text = i.replace('<seg>','').replace('</seg>','')
        supplied = i.replace('<seg>', '<supplied xml:id="' + id + '" reason="displaced-over-the-line">').replace('</seg>', '</supplied>').replace('', '')

        text_page = text_page.replace(i, '<seg corresp="#' + id + '" type="pos-of-displaced">' + seg_text + '§' + '</seg>' + supplied,1)
        print(supplied)
        n += 1

    text_page = text_page.replace('§', '')
    return text_page

def pp_choice(xml,text_page):
    text_page = re.sub('(<choice><abbr>)(<'+xml+'.*?>)(.*?</abbr><expan>)(<'+xml+'.*?>)(.*?</expan></choice>)','\g<2>\g<1>\g<3>\g<5>',text_page)
    text_page = re.sub('(<choice><abbr>.*?)</'+xml+'>(</abbr><expan>.*?)</'+xml+'>(.*?</expan></choice>)','\g<1>\g<2>\g<3></'+xml+'>',text_page)
    return text_page

def preprocessing(text_page):
    # replace pre character
    text_page = text_page.replace('\ue665','p\u0304')
    # replace wrong -tur sign
    text_page = text_page.replace('\u1dd1','\uf1c2')
    # make shure, -ur ligatur has not been put behind interpunctuation
    text_page = text_page.replace('','')
    return text_page

def postprocessing(text_page):
    # delete double expansion of cap in <fw>
    text_page = re.sub('<choice><abbr><fw type="page-header" place="top" facs="(.*?)"><choice><abbr>Cap<g ref="#char-0305">&#x0305;</g></abbr><expan>Capitula</expan></choice></abbr><expan><fw type="page-header" place="top" facs="(.*?)">Capitulum</expan></choice>','<fw type="page-header" place="top" facs="\g<1>"><choice><abbr>Cap<g ref="#char-0305">&#x0305;</g></abbr><expan>Capitula</expan></choice>',text_page)

    return text_page

""" wrapper

    AUflösung von Sonderzeichen muss ganz am Ende kommen
"""

def dl_and_export_to_oxygen(collection_id, document_id, startpage, endpage, start_folia, iiif_image_id, ms, book, dl, ms_id):
    if dl == True:
        transpy.download_data_from_transkribus(collection_id, document_id, startpage, endpage)
    else:
        pass
    if ms == 'B':
        path_to_files = transpy.load_pagexml(config.export_folder + '732612/01_Transkription_Bamberg_Stabi_Can_6/page/')
        ms_id = 'bamberg-sb-c-6-' + str(book).zfill(2)
    elif ms == 'V':
        path_to_files = transpy.load_pagexml(config.export_folder + '855714/01_Transkription_BAV_Pal_lat_585/page/')
        ms_id = 'vatikan-bav-pal-lat-585-' + str(book).zfill(2)
    elif ms == 'V2':
        path_to_files = transpy.load_pagexml(config.export_folder + '788015/01_Transkription_BAV_Pal_lat_586/page/')
        ms_id = 'vatikan-bav-pal-lat-586-' + str(book).zfill(2)
    elif ms == 'F':
        path_to_files = transpy.load_pagexml(config.export_folder + '637541/01_Transkription_Frankfurt-ub-b-50/page/')
        ms_id = 'frankfurt-ub-b-50-' + str(book).zfill(2)
    elif ms == 'K':
        path_to_files = transpy.load_pagexml(config.export_folder + '796594/01_Transkription_Köln_EDD_Cod_119/page/')
        ms_id = 'koeln-edd-c-119-' + str(book).zfill(2)

    dictionary_abbr_external = transpy.load_abbreviation_dict()
    text_page = bdd_export_tei(path_to_files, start_folia, iiif_image_id, ms, ms_id)
    text_page = preprocessing(text_page)
    text_page = transpy.line_breaks_angled_dash(text_page)
    text_page = transpy.replace_abbreviations_from_tei(dictionary_abbr_external, text_page)
    text_page = bdd_specific_tei(text_page, ms_id)


    # TODO put into postprocessing
    # correction special cases
    text_page = re.sub('<choice><abbr><choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice></abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>','<choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>' ,text_page)
    text_page = re.sub('(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> )<choice><abbr><hi rend="color:red">','\g<1><hi rend="color:red"><choice><abbr>',text_page,flags=re.DOTALL)
    text_page = re.sub('(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> <hi rend="color:red"><choice><abbr>.*?<expan>)<hi rend="color:red">','\g<1>',text_page,flags=re.DOTALL)
    text_page = re.sub('(\n\n<pb.*?/>\n<fw.*?>\n<cb n="a".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',text_page)
    text_page = re.sub('(\n<cb n="b".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',text_page)
    text_page = re.sub('(\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',text_page)
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
    text_page = re.sub('<choice><abbr><fw type="page-header" place="top" facs="638,58,210,100"><choice><abbr>Cap̅</abbr><expan>Capitula</expan></choice></abbr><expan><fw type="page-header" place="top" facs="638,58,210,100">Capitulum</expan></choice>','<fw type="page-header" place="top" facs="638,58,210,100"><choice><abbr>Cap̅</abbr><expan>Capitula</expan></choice>', text_page)
    #text_page = re.sub('<choice><abbr>earu<g ref="#char-0304">\u0304</g><add place="above" type="contemporary">roru<g ref="#char-0304">\u0304</g></abbr><expan>earumr<add place="above" type="contemporary">orum</expan></choice></add>','<choice><abbr>earu<g ref="#char-0304">&#x0304;</g></abbr><expan>earum<add place="above" type="contemporary">orum</expan></choice><add place="above" type="contemporary"><choice><abbr>roru<g ref="#char-0304">\u</g></abbr><expan>rorum</expan></choice></add>', text_page)
    text_page = re.sub('<choice><abbr></p></div><div n="10" type="interrogation"><label type="chapter-number" place="margin left" facs="205,219,157,181"><hi rend="color:red">Int̅</abbr><expan></p></div><div n="10" type="interrogation">I<label type="chapter-number" place="margin left" facs="205,219,157,181">n<hi rend="color:red">terrogatio</expan></choice>','</p></div><div n="10" type="interrogation"><label type="chapter-number" place="margin left" facs="205,219,157,181"><hi rend="color:red"><choice><abbr>Int̅</abbr><expan>Interrogatio</expan></choice>',text_page)
    text_page = re.sub('<choice><abbr>ep̅o<add place="above" type="contemporary">s</abbr><expan>epis<add place="above" type="contemporary">copos</expan></choice></add>', '<choice><abbr>ep̅o</abbr><expan>episcopo</expan></choice><add place="above" type="contemporary">s</add>', text_page)
    text_page = re.sub('<add place="above" type="contemporary"><choice><abbr>e</add>ade<g ref="#char-0304">&#x0304;</g></abbr><expan>e</add>adem</expan></choice>', '<choice><abbr><add place="above" type="contemporary">e</add>ade<g ref="#char-0304">&#x0304;</g></abbr><expan><add place="above" type="contemporary">e</add>adem</expan></choice>', text_page)
    text_page = re.sub('<add place="above" type="contemporary"><choice><abbr>n̅</add>posset</abbr><expan>ER</add>ROR</expan></choice>','<add place="above" type="contemporary"><choice><abbr>n̅</abbr><expan>non</expan></choice></add> posset', text_page)


    text_page = sc_to_g(text_page)
    text_page = postprocessing(text_page)


    #replace placeholder in template file and save as new file
    with open('/home/michael/Dokumente/transpy/resources/tei_template_' + ms + '.xml','r') as xmlfile:
        template_file = xmlfile.read()

    new_file = template_file.replace('%%',text_page)
    with open('/home/michael/Dokumente/transpy/output/'+ ms +'-' + str(book).zfill(2) + '-new.xml','w') as newfile:
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

def prepare_01_ms(ms, book, dl):
    if ms == 'B':
        dl_and_export_to_oxygen(80437, 732612, 410, 416, '203v', 410, ms, book, dl, ms_id)
    elif ms == 'V':
        dl_and_export_to_oxygen(80437, 855714, 177, 188, '85r', 37, ms, book, dl, ms_id)
    elif ms == 'V2':
        dl_and_export_to_oxygen(80437, 788015, 177, 188, '85r', 177, ms, book, dl, ms_id)
    elif ms == 'F':
        dl_and_export_to_oxygen(80437, 637541, 412, 418, '203v', 2036028, ms, book, dl, ms_id)
    elif ms == 'K':
        ms_id = 'koeln-edd-c-119-' + str(book).zfill(2)
        dl_and_export_to_oxygen(80437, 796594, 242, 247, '118v', 284583, ms, book, dl, ms_id)

prepare_01_ms('K', 13, True)



# Test der Datei und ggf. bearbeitung:
# Alle Dateien neu Numerieren
# Preprocessing
# Postprocessing
# -
# Nachbearbeitung besser machen
# - Am Ende Liste mit Errors erstellen
