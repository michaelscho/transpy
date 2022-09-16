import argparse
import transpy
import config
import lxml.etree as LET
import re
import datetime

class Manuscript_to_be_processed:
    def __init__(self, sigla):
        self.sigla = sigla
        self.signatur = config.manuscript_data[sigla]['signatur']
        self.transkribus_collection = config.manuscript_data[sigla]['transkribus_collection_id']
        self.transkribus_document = config.manuscript_data[sigla]['transkribus_document_id']
        self.tei_base_id = config.manuscript_data[sigla]['tei_base_id']
        self.tei_base_id_book = config.manuscript_data[sigla]['tei_base_id']
        self.iiif_scale_factor = config.manuscript_data[sigla]['iiif_scale_factor']
        self.base_folder = config.manuscript_data[sigla]['base_folder']
        self.bdd_tei_text = ""
        self.start_folio = ""
        self.iiif_image_id = 0
        self.path_to_pagexml_files = []
        self.facs_url = config.manuscript_data[sigla]['facs_url']
        self.corresp = config.manuscript_data[sigla]['corresp']
        self.ana = config.manuscript_data[sigla]['ana']
        self.toc_label_for_later_replacement = []
        self.label_for_later_replacement = []
        self.interrogation_label_for_later_replacement = []
        self.inscriptions_to_replace = []

    """ Import data from pageXML and preapre conversion to BDD:TEI

    """
    # function for incrementing folia_numbers, e.g. 28v-30r
    def increment_folia(self):

        if 'r' in self.start_folio:
            self.start_folio = self.start_folio.replace('r','v')
        elif 'v' in self.start_folio:
            self.start_folio = str(int(self.start_folio.replace('v',''))+1)+'r'

    def identify_placement_of_element(self, coords):
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

    def coords_baseline(self, root, xpath):
        """ Koordinaten aus baseline holen
        """

        x = float(self.iiif_scale_factor)

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
        coord_string = f"{c1},{c2},{w},{h}"
        return coord_string


    def coords_text_region(self, root, xpath):
        """ Koordinaten aus textregion holen
        """

        x = float(self.iiif_scale_factor)
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


    def create_tei_fw_head(self, root):
        """ create tei:fw for header

        Creates tei:fw element including header if available from pageXML.

        :param root: Takes root from etree
        :return text_header: Returns tei:fw element as string
        """

        try:
            header = root.xpath('//ns0:TextRegion[contains(@type,"header")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            unicode_header = header.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_header = self.coords_baseline(header, './/ns0:TextLine//ns0:Baseline/@points')
            text_header = f'\n<fw type="page-header" place="top" facs="{coords_header}">{unicode_header[0]}</fw>'

        except Exception as e:
            print(e)
            text_header = ''

        return text_header

    def create_column(self, root, column_name, column_a_b):
        """ creates text of column 1 from pageXML

        Creates text of column one including tei:lb elements as well as coordinates stored in tei:@facs from pageXML.

        :param root: Takes root from etree
        :return text_column_1: Returns text of column 1 element as string
        """

        try:
            column = root.xpath(f'//ns0:TextRegion[contains(@custom,"type:{column_name}")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            coords_column = self.coords_text_region(column, './ns0:Coords/@points')
            # create column with coordiantes
            text_column = f'<cb n="{column_a_b}" facs="{coords_column}"/>'

            # lines in column
            unicode_column = column.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_number = 0
            for line in unicode_column:
                line_text = line.xpath('.//ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                line_coords = self.coords_text_region(line, './/ns0:Coords/@points')
                line_number += 1
                text_column = f'{text_column}\n<lb n="{line_number}" facs="{line_coords}"/>{line_text[0]}'
        except Exception as e:
            print(str(e) + f'===>Textpage {column_name} wrong.')
            text_column = f'\n<cb n="{column_a_b}"/>'
        return text_column

    def create_tei_fw_foot(self, root):
        """ create tei:fw for footer

        Creates tei:fw element including footer if available from pageXML.

        :param root: Takes root from etree
        :return text_footer: Returns tei:fw element as string
        """

        try:
            footer = root.xpath('//ns0:TextRegion[contains(@type,"footer")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            unicode_footer = footer.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_footer = self.coords_baseline(footer, './/ns0:TextLine//ns0:Baseline/@points')
            text_footer = f'\n<fw type="quire-numeral" place="bottom" facs="{coords_footer[0]}">{unicode_footer[0]}</fw>'
        except:
            text_footer = ''
        return text_footer

    def test_text_page_for_element(self, search_string, string_to_be_replaced, replace_string, text_page):
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

    def store_toc_label_for_later_replacement(self, root):
        for chapter_number_toc in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            # create label element
            chapter_number_toc_text = chapter_number_toc.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            coords_label_toc_a = chapter_number_toc.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_label_toc_b = self.coords_text_region(chapter_number_toc, './ns0:Coords/@points')

            side = self.identify_placement_of_element(coords_label_toc_a)
            replace_key = re.search('~(\d+)~',chapter_number_toc_text)
            replace_key = replace_key.group(0)
            div_number = replace_key.replace('~','')

            label_toc = f'<item n="{div_number}"><label place="margin {side}" type="chapter-number" facs="{coords_label_toc_b}"><hi rend="color:red">{chapter_number_toc_text}</hi></label> <hi rend="color:red">'

            # append div number and label_toc for later replacement to list
            list_item = [div_number,replace_key,label_toc]
            self.toc_label_for_later_replacement.append(list_item)

    def store_label_for_later_replacement(self, root):
        for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            try:
                chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
                coords_label_a = chapter_number.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                coords_label_b = self.coords_text_region(chapter_number, './ns0:Coords/@points')

                side = self.identify_placement_of_element(coords_label_a)
                replace_key = re.search('\*(\d+)\*',label)
                replace_key = replace_key.group(0)
                div_number = replace_key.replace('*','')

                label = f'<div n="{div_number}" type="chapter"><head type="chapter-title"><label type="chapter-number" place="margin {side}" facs="{coords_label_b}"><hi rend="color:red">{chapter_number_text}</hi></label> <hi rend="color:red">'

                list_item = [div_number,replace_key,label]
                self.label_for_later_replacement.append(list_item)

            except Exception as e:
                print(str(e) + '>>>Error with label<<<')

    def store_interrogation_label_for_later_replacement(self, root):
        for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            try:
                if '*i' in chapter_number_text:
                    coords_label_a = chapter_number.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                    coords_label_b = self.coords_text_region(chapter_number, './ns0:Coords/@points')

                    side = self.identify_placement_of_element(coords_label_a)
                    replace_key = re.search('\*i(\d+)\*',label)
                    replace_key = replace_key.group(0)
                    div_number = replace_key.replace('*','')
                    div_number = div_number.replace('i','')

                    label = f'<div n="{div_number}" type="interrogation"><label type="chapter-number" place="margin {side}" facs="{coords_label_b}"><hi rend="color:red">{chapter_number_text}</hi></label> \n<p n="1"><hi rend="color:red">'

                    list_item = [div_number,replace_key,label]
                    self.interrogation_label_for_later_replacement.append(list_item)
            except Exception as e:
                print(e + ' >>>Interrogation<<<')

    def store_inscription_for_later_replacement(self, root):
        for inskription in root.xpath('//ns0:TextRegion[contains(@custom,"type:Inskription")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            inskription_text = ''
            for line in inskription.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
                inskription_text = f"{inskription_text} {line}"

            coords_inskription_a = inskription.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_inskription_b = self.coords_text_region(inskription, './ns0:Coords/@points')
            side = self.identify_placement_of_element(coords_inskription_a)

            inskription_xml = f'</hi></head>\n<note type="inscription" place="margin {side}" anchored="false" facs="{coords_inskription_b}">{inskription_text}</note>'
            inskription_xml = inskription_xml.replace('> ','>')

            replace_key = re.search('\*(i\d+|\d+)\*',inskription_text)
            replace_key = replace_key.group(0)
            div_number = replace_key.replace('*','')
            text_to_be_replaced = f'<div n="{div_number}" type="chapter"'
            replace_text = f'{inskription_xml}\n<p n="1"><hi rend="color:red initial">'
            self.inscriptions_to_replace.append([replace_text,text_to_be_replaced, replace_key])

    def create_tei_from_pageXML(self):
        text_page = ""
        # open each pagexmlfile for exporting text to tei
        for filename in self.path_to_pagexml_files:
            tree = LET.parse(filename)
            root = tree.getroot()

            # creates page beginning for each xml-pagefile using data taken from config file
            page_break = f'\n<pb n="{self.start_folio}" facs="{eval(self.facs_url)}" corresp="{eval(self.corresp)}" ana="{eval(self.ana)}"/>'
            # adds tei:fw if header exists on page
            text_header = self.create_tei_fw_head(root)
            # creates text of column 1 from lines
            text_column_1 = self.create_column(root, 'column_1', 'a')
            # creates text of column 2 from lines
            text_column_2 = self.create_column(root, 'column_2', 'b')
            # creates tei:fw footer element
            text_footer = self.create_tei_fw_foot(root)
            # create page
            text_page = text_page + page_break + text_header + '\n' + text_column_1 + '\n' + text_column_2 + '\n' + text_footer

            # create list of toc_labels for later replacment
            try:
                self.store_toc_label_for_later_replacement(root)
            except:
                pass
            # create list of labels for later replacment
            try:
                self.store_label_for_later_replacement(root)
            except Exception as e:
                print(e)
            # create list of interrogation labels for later replacment
            try:
                self.store_interrogation_label_for_later_replacement(root)
            except:
                pass
            # create list of inscriptions for later replacment
            try:
                self.store_inscription_for_later_replacement(root)
            except:
                pass

            # test pagexml for certain elements and replace with corresponding tei
            elements_to_be_tested = [['~i~',r'~i~(.*?)~',f'<!-- Beginn Inhaltsverzeichnis -->\n<div type="toc" xml:id="{self.tei_base_id_book}-toc">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head>\n<list>\n~'],
                                    ['*i*',r'\*i\*(.*?)\*p\*',f'</list>\n</div>\n<!-- Beginn des Haupttextes  -->\n<div type="content" xml:id="{self.tei_base_id_book}-con">\n<div xml:id="{self.tei_base_id_book}-con-000" type="praefatiuncula">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head><p n="1"><hi rend="color:red">'],
                                    ['#p#','#p#','</hi></p>\n</div>']]
            for element in elements_to_be_tested:
                text_page = self.test_text_page_for_element(element[0], element[1], element[2], text_page)

            # increase folio number and iiif_image_id
            self.increment_folia()
            self.iiif_image_id += 1

        self.bdd_tei_text = text_page

class Bdd_Tei():
    def __init__(self, manuscript):
        self.tei = manuscript.bdd_tei_text
        self.toc_label_for_later_replacement = manuscript.toc_label_for_later_replacement
        self.interrogation_label_for_later_replacement = manuscript.interrogation_label_for_later_replacement
        self.label_for_later_replacement = manuscript.label_for_later_replacement
        self.inscriptions_to_replace = manuscript.inscriptions_to_replace
        self.tei_base_id_book = manuscript.tei_base_id_book

    ## transform pagexml as single tei file according to bdd schematics
    def bdd_export_tei(self):

        # Insert label TOC
        for element in self.toc_label_for_later_replacement:
            if int(element[0]) == 1:
                # treat first element differently
                self.tei = re.sub('\n(<lb.*?/>)(</hi></head>\n)<list>\n~1~(\w)', '\g<2>\g<1><list>' + element[2].replace(element[1],'') + '\g<3></hi>', self.tei)
            else:
                self.tei = re.sub('\n(<lb.*?/>)' + element[1] + '(\w)', '</item>\n\g<1>' + element[2].replace(element[1],'') + '\g<2></hi>', self.tei)

        # Insert label interrogation
        for element in self.interrogation_label_for_later_replacement:
            #print(element[0])
            if int(element[0]) == 1:
                # treat first element differently

                self.tei = re.sub('\*i' + element[0] + '\*~(\w)', '</p>' + element[2].replace(element[1],'') + '\g<1></hi>', self.tei)
            else:
                self.tei = re.sub('\*i' + element[0] + '\*~(\w)', '</p></div>' + element[2].replace(element[1],'') + '\g<1></hi>', self.tei)

        # Insert label chapter
        for element in self.label_for_later_replacement:
            #print(element[1])
            if int(element[0]) == 1:
                # treat first element differently
                self.tei = re.sub('\*' + element[0] + '\*', element[2].replace(element[1],''), self.tei)
            else:
                self.tei = re.sub('\*' + element[0] + '\*','</p>\n</div>\n' + element[2].replace(element[1],''), self.tei)

        for element in self.inscriptions_to_replace:
            if 'i1' in element[0]:
                # interrogationes start with inscription instead of interrogation number
                element[0] = element[0].replace('</hi></head>\n', '')
                element[0] = element[0].replace('\n<p n="1"><hi rend="color:red initial">', '')

                self.tei = re.sub('\*i1\*(.*?)~(\w)', '</p>\n<div n="1" type="interrogation"><head type="chapter-title"><hi rend="color:red">\g<1></hi></head>\n' + element[0].replace('*i1*', '') + '<p n="1"><hi rend="color:red">\g<2></hi>',self.tei,flags=re.DOTALL)
            else:
                self.tei = re.sub('(' + element[1] + '.*?)~','\g<1>' + element[0].replace(element[2], '') + '~',self.tei,flags=re.DOTALL)

        # TODO put Postprocessing in function
        self.tei = self.tei.replace('</item></item>','</item>')
        self.tei = self.tei.replace('</list>','</item></list>')
        self.tei = re.sub('\*\d+\*','',self.tei)
        self.tei = re.sub('\~\d+\~','',self.tei)
        self.tei = re.sub('#(\w)','<hi rend="versal">\g<1></hi>',self.tei)
        self.tei = re.sub('~(\w)','\g<1></hi>',self.tei)

    def sc_to_g(self):

        # replace special characters from list in config file...
        for character in config.character_list:
            self.tei = self.tei.replace(character[1],character[0])

    def bdd_specific_tei(self):
        # <add> used in Transkribus to show inline additions
        self.tei = self.tei.replace('<add>', '<add place="above" type="contemporary">')

        # unclear
        self.tei = self.tei.replace('...', '<unclear reason="tight-binding" resp="Transkribus" cert="low">...</unclear>')

        # editorial comment
        self.tei = self.tei.replace('[', '<note type="editorial-comment" resp="transkribus">')
        self.tei = self.tei.replace(']', '</note>')
        self.tei = self.tei.replace('<note>', '<note type="editorial-comment" resp="transkribus">')

        # del
        self.tei = self.tei.replace('<del>', '<del rend="">')

        # seg
        n = 1
        for i in re.findall('<seg>.*?</seg>', self.tei):
            print(i)
            id = f"{self.tei_base_id_book}-supp-{str(n).zfill(3)}"
            seg_text = i.replace('<seg>','').replace('</seg>','')
            supplied = i.replace('<seg>', f'<supplied xml:id="{id}" reason="displaced-over-the-line">').replace('</seg>', '</supplied>').replace('', '')

            self.tei = self.tei.replace(i, f'<seg corresp="#{id}" type="pos-of-displaced">{seg_text}§</seg>{supplied}', 1)
            print(supplied)
            n += 1

        self.tei = self.tei.replace('§', '')

    def pp_choice(self, xml):
        self.tei = re.sub('(<choice><abbr>)(<'+xml+'.*?>)(.*?</abbr><expan>)(<'+xml+'.*?>)(.*?</expan></choice>)','\g<2>\g<1>\g<3>\g<5>',self.tei)
        self.tei = re.sub('(<choice><abbr>.*?)</'+xml+'>(</abbr><expan>.*?)</'+xml+'>(.*?</expan></choice>)','\g<1>\g<2>\g<3></'+xml+'>',self.tei)

    def preprocessing(self):
        # replace pre character
        self.tei = self.tei.replace('\ue665','p\u0304')
        # replace wrong -tur sign
        self.tei = self.tei.replace('\u1dd1','\uf1c2')
        # make shure, -ur ligatur has not been put behind interpunctuation
        self.tei = self.tei.replace('','')


    # use manually inserted ¬ for creating proper tei linebreaks
    def line_breaks_angled_dash(self):
        self.tei = self.tei.replace('¬ ','¬')
        self.tei = re.sub(r'¬\n(<lb.*?)/>','\g<1> break="no"/>',self.tei, flags=re.DOTALL)
        self.tei = re.sub(r'¬\n+(<cb.*?n="b".*?/>\n<lb.*?)/>','\g<1> break="no"/>',self.tei)
        self.tei = re.sub(r'¬\n+(<pb.*?<cb.*?n="a".*?/>\n<lb.*?)/>','\g<1> break="no"/>',self.tei)
        self.tei = re.sub(r'¬','<lb break="no"/>',self.tei)

    def postprocessing(self):
        # correction special cases
        self.tei = re.sub('<choice><abbr><choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice></abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>','<choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>' ,self.tei)
        self.tei = re.sub('(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> )<choice><abbr><hi rend="color:red">','\g<1><hi rend="color:red"><choice><abbr>',self.tei,flags=re.DOTALL)
        self.tei = re.sub('(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> <hi rend="color:red"><choice><abbr>.*?<expan>)<hi rend="color:red">','\g<1>',self.tei,flags=re.DOTALL)
        self.tei = re.sub('(\n\n<pb.*?/>\n<fw.*?>\n<cb n="a".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',self.tei)
        self.tei = re.sub('(\n<cb n="b".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',self.tei)
        self.tei = re.sub('(\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',self.tei)
        # correction of ambigue expansions
        # delete double expansion of cap in <fw>
        self.tei = re.sub('<choice><abbr><fw type="page-header" place="top" facs="(.*?)"><choice><abbr>Cap<g ref="#char-0305">&#x0305;</g></abbr><expan>Capitula</expan></choice></abbr><expan><fw type="page-header" place="top" facs="(.*?)">Capitulum</expan></choice>','<fw type="page-header" place="top" facs="\g<1>"><choice><abbr>Cap<g ref="#char-0305">&#x0305;</g></abbr><expan>Capitula</expan></choice>', self.tei)
        # Capitula in fw
        self.tei = re.sub('(<fw.*?><choice><abbr>Cap\u0305</abbr><expan>)Capitulum(</expan></choice>.*?</fw>)','\g<1>Capitula\g<2>',self.tei)
        # Cap in fw ohne Auflösung
        self.tei = re.sub('(<fw.*?>)Cap\u0305(.*?</fw>)','\g<1><choice><abbr>Cap\u0305</abbr><expan>Capitula</expan></choice>\g<2>',self.tei)
        # Ex concilio
        self.tei = re.sub('(<note type="inscription".*?>Ex <choice>.*?<expan>)concilium(</expan>)','\g<1>concilio\g<2>',self.tei)
        # Ex eodem capitulo
        self.tei = re.sub('(<note type="inscription".*?>Ex eodem <choice>.*?<expan>)Capitula(<)','\g<1>Capitulo\g<2>',self.tei)
        # correction generic cases
        xml_to_be_corrected = ['lb ', 'add', 'p','hi></label', 'item', 'note']

        for i in xml_to_be_corrected:
            self.pp_choice(i)

        # correction of linebreaks
        self.tei = re.sub('¬\n(<pb.*?<lb .*?)(/>)','\g<1> break="no"\g<2>', self.tei,flags=re.DOTALL)
        # Bei <hi>Q</hi> kommt <hi>Qu</hi>. EInsetzen um ein Buchstaben verrückt, aber nur bei Wörtern mit Q?
        self.tei = re.sub('¬\n(<pb.*?<lb .*?)(/>)','\g<1> break="no"\g<2>', self.tei,flags=re.DOTALL)
        self.tei = re.sub('<choice><abbr><fw type="page-header" place="top" facs="638,58,210,100"><choice><abbr>Cap̅</abbr><expan>Capitula</expan></choice></abbr><expan><fw type="page-header" place="top" facs="638,58,210,100">Capitulum</expan></choice>','<fw type="page-header" place="top" facs="638,58,210,100"><choice><abbr>Cap̅</abbr><expan>Capitula</expan></choice>', self.tei)
        #text_page = re.sub('<choice><abbr>earu<g ref="#char-0304">\u0304</g><add place="above" type="contemporary">roru<g ref="#char-0304">\u0304</g></abbr><expan>earumr<add place="above" type="contemporary">orum</expan></choice></add>','<choice><abbr>earu<g ref="#char-0304">&#x0304;</g></abbr><expan>earum<add place="above" type="contemporary">orum</expan></choice><add place="above" type="contemporary"><choice><abbr>roru<g ref="#char-0304">\u</g></abbr><expan>rorum</expan></choice></add>', text_page)
        self.tei = re.sub('<choice><abbr></p></div><div n="10" type="interrogation"><label type="chapter-number" place="margin left" facs="205,219,157,181"><hi rend="color:red">Int̅</abbr><expan></p></div><div n="10" type="interrogation">I<label type="chapter-number" place="margin left" facs="205,219,157,181">n<hi rend="color:red">terrogatio</expan></choice>','</p></div><div n="10" type="interrogation"><label type="chapter-number" place="margin left" facs="205,219,157,181"><hi rend="color:red"><choice><abbr>Int̅</abbr><expan>Interrogatio</expan></choice>',self.tei)
        self.tei = re.sub('<choice><abbr>ep̅o<add place="above" type="contemporary">s</abbr><expan>epis<add place="above" type="contemporary">copos</expan></choice></add>', '<choice><abbr>ep̅o</abbr><expan>episcopo</expan></choice><add place="above" type="contemporary">s</add>', self.tei)
        self.tei = re.sub('<add place="above" type="contemporary"><choice><abbr>e</add>ade<g ref="#char-0304">&#x0304;</g></abbr><expan>e</add>adem</expan></choice>', '<choice><abbr><add place="above" type="contemporary">e</add>ade<g ref="#char-0304">&#x0304;</g></abbr><expan><add place="above" type="contemporary">e</add>adem</expan></choice>', self.tei)
        self.tei = re.sub('<add place="above" type="contemporary"><choice><abbr>n̅</add>posset</abbr><expan>ER</add>ROR</expan></choice>','<add place="above" type="contemporary"><choice><abbr>n̅</abbr><expan>non</expan></choice></add> posset', self.tei)

class Page_XML_Tests:
    def __init__(self, path_to_pagexml_files):
        self.filenames = path_to_pagexml_files
        self.single_text_file = ""

    def create_single_text_file(self):
        single_text_file = ""
        for filename in self.filenames:
            with open(filename,'r') as file:
                text = file.read()
                single_text_file = single_text_file + text
        self.single_text_file = single_text_file
        return self.single_text_file

    def check_text_regions(self):
        """ Checks text regions for necessary tags

        """

        consistent_text_regions = True
        for filename in self.filenames:
            tree = LET.parse(filename)
            root = tree.getroot()

            current_page = root.xpath('//ns0:TranskribusMetadata/@pageNr', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]

            textregions = root.xpath('//ns0:TextRegion', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            for element in textregions:
                if "structure {type:" in LET.tostring(element, encoding='unicode', method='xml'):
                    pass
                else:
                    print(f"\nTextregion missing markup on page {current_page}!\n=================================")
                    print(f"{LET.tostring(element, encoding='unicode', method='xml')}\n=================================")
                    consistent_text_regions = False

            print(f"Page {current_page} checked for consistency of textregions.")

        if consistent_text_regions == True:
            print("===> All pages have been checked successfully, now checking internal structure.\n")
        else:
            print("Errors have occured, stopping script.")
            exit()

    def check_entries(self, character, type):
            # count number of chapters using toc entries marked up by '~n~'
            if "*" in character:
                entries = re.findall(f'\*\d+\*', self.single_text_file)
                entries = [int(i.replace(f'{character}','')) for i in entries]
            else:
                entries = re.findall(f'{character}\d+{character}', self.single_text_file)
                entries = [int(i.replace(f'{character}','')) for i in entries]

            number_of_entries = max(entries)
            set_of_entries = set(entries)
            print(f"===> {number_of_entries} {type}-entries detected")
            return number_of_entries, set_of_entries, entries

    def check_number_of_items(self, items, test_number):
        test = True
        for i in range(1,max(items)):
            if items.count(i)/2 == test_number:
                pass
            else:
                print(f"Item {i} has wrong number.\n")
                print(sorted(items))
                test = False
        print("All items correct.")
        return test

    def check_internal_structure(self):
        """ Checks internal structure as marked up using special placeholders ~n~ and *n*

        """
        print("Start checking internal structure")
        # creates texfile for easy checking
        self.create_single_text_file()

        # count number of chapters using toc entries marked up by '~n~' or '*n*'
        number_of_entries_toc, set_of_entries_toc, entries_toc = self.check_entries('~','TOC')
        number_of_chapter, set_of_entries_chapter, entries_chapter = self.check_entries('*','Chapter')

        if number_of_entries_toc == number_of_chapter:
            print("===> Number of TOC entries equals number of chapters.\n\nStart checking number of placeholder")
        else:
            print("===> Number of TOC entries does NOT EQUAL number of chapters.\n")
            print(f"\n=============================\nSet of TOC entries: {set_of_entries_toc}\n")
            print(f"\n=============================\nSet of Chapter entries: {set_of_entries_chapter}\n")

        # check, that two toc items and 3 chapter items have been asigned
        test_toc = self.check_number_of_items(entries_toc, 2)
        test_chapter = self.check_number_of_items(entries_chapter, 3)
        if test_toc == True and test_chapter == True:
            pass
        else:
            exit()

def main():

    # Get variables from console
    # example 'python bdd.py B 7 282-291 139v 236435 -dl'
    parser = argparse.ArgumentParser(description='Download, export and conversion from manuscripts stored in Transkribus into BDD-TEI.')
    parser.add_argument('siglum', metavar='S', help='Angabe der Handschriften-Sigle, z.B. B, F oder V')
    parser.add_argument('book', metavar='B', type=int, help='Angabe der Buchnummer')
    parser.add_argument('page_range', metavar='P', help='Angabe der Seitennummer')
    parser.add_argument('folio', metavar='F', help='Angabe der Folionummer')
    parser.add_argument('iiif_image_id', metavar='I', help='Angabe der IIIF-Image-ID')
    parser.add_argument('-dl', help='Download?', action='store_true')
    args = parser.parse_args()

    # creating variables from arguments
    book_int = args.book
    book_string = str(book_int).zfill(2)
    startpage = int(args.page_range.split('-')[0])
    endpage = int(args.page_range.split('-')[1])

    # create path to folder
    path_to_folder = config.export_folder + book_string + '/'

    # create manuscript object
    manuscript = Manuscript_to_be_processed(args.siglum)
    # update
    manuscript.tei_base_id_book = manuscript.tei_base_id_book + book_string
    manuscript.start_folio = args.folio
    manuscript.iiif_image_id = args.iiif_image_id

    # start download if flag '-dl' is given
    if args.dl == True:
        print(f'Starting export of page-xml from Transkribus and download to local machine for book {book_string} in manuscript {manuscript.sigla}.')
        transpy.download_data_from_transkribus(manuscript.transkribus_collection, manuscript.transkribus_document, startpage, endpage, path_to_folder)
        print('Finished download.\n')

    # open page-xml files for further processing
    # get path to individual page-xml files
    manuscript.path_to_pagexml_files = transpy.load_pagexml(f'{path_to_folder}{manuscript.transkribus_document}/{manuscript.base_folder}/page/')

    # create pageXML object
    page_xml_tests = Page_XML_Tests(manuscript.path_to_pagexml_files)

    # test pageXML for consistency according to project needs
    page_xml_tests.check_text_regions()
    page_xml_tests.check_internal_structure()

    # conversion of pageXML into tei object
    manuscript.create_tei_from_pageXML()

    #create tei object for further processing
    tei_file = Bdd_Tei(manuscript)

    # process tei
    tei_file.bdd_export_tei()
    tei_file.preprocessing()
    tei_file.line_breaks_angled_dash()

    dictionary_abbr_external = transpy.load_abbreviation_dict()
    tei_file.tei = transpy.replace_abbreviations_from_tei(dictionary_abbr_external, tei_file.tei)

    tei_file.bdd_specific_tei()
    tei_file.postprocessing()
    # Test: maybe postprocessing must come after sc_to_g
    tei_file.sc_to_g()

    #replace placeholder in template file and save as new file
    with open(f'/home/michael/Dokumente/transpy/resources/tei_template_{manuscript.tei_base_id[:-1]}.xml', 'r') as xmlfile:
        template_file = xmlfile.read()

    new_file = template_file.replace('%%', tei_file.tei)
    # insert book number into file
    new_file = new_file.replace("{book}", book_string)
    # insert date into file
    today = datetime.date.today()
    new_file = new_file.replace("{date-yyyy-mm-dd}", str(today))


    with open(f'/home/michael/Dokumente/transpy/output/{book_string}/{manuscript.tei_base_id_book}.xml', 'w') as newfile:
        newfile.write(new_file)

if __name__ == "__main__":
    main()
