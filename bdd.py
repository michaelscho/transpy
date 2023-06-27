"""
BDD Manuscript Processing Script
================================

Author: Michael Schonhardt, Burchards Dekret Digital, Universität Kassel
Email: m.schonhardt@uni-kassel.de

Summary:
--------
This script downloads, exports, and converts manuscripts stored in Transkribus into BDD-TEI format. It performs various tasks including downloading data from Transkribus, testing the page XML for consistency, converting the page XML to TEI, and replacing abbreviations with their full forms based on a provided dictionary. The processed manuscript is then saved as a new XML file in TEI format.

Description:
------------
This script is designed to automate the processing of manuscripts stored in Transkribus. It retrieves the necessary data from Transkribus, performs consistency checks on the page XML files, converts them to TEI format following the BDD schema, and applies abbreviation expansion using an external dictionary. The resulting TEI representation is saved as a new XML file.

Usage:
------
To use this script, run it from the command line with the following arguments:
python bdd.py <siglum> <book> <page_range> <folio> <iiif_image_id> [-dl]

- siglum: The unique identifier for the manuscript (e.g., B, F, V).
- book: The book number.
- page_range: The range of Transkribus page numbers to process (e.g., 282-291).
- folio: The starting folio number.
- iiif_image_id: The ID of the IIIF image (as specified in the iiif-manifest).
- -dl: (optional) Include this flag to download the data from Transkribus.

Dependencies:
-------------
This script relies on the following external libraries:
- argparse
- transpy
- config
- lxml
- re
- datetime
- os

License:
--------
This script is released under the MIT license. Please refer to the accompanying LICENSE file for more information.

"""

import argparse
import transpy
import config
import lxml.etree as LET
import re
import datetime
import os


class ManuscriptToProcess:
    """
    Represents a manuscript to be processed, including various attributes and methods for data extraction and conversion.

    Attributes:
        sigla (str): The unique identifier for the manuscript.
        signatur (str): The signature of the manuscript.
        transkribus_collection (str): The ID of the Transkribus collection containing the manuscript.
        transkribus_document (str): The ID of the Transkribus document representing the manuscript.
        tei_base_id (str): The base ID for TEI representation of the manuscript.
        tei_base_id_book (str): The base ID for the book-level TEI representation of the manuscript.
        iiif_scale_factor (float): The scale factor for IIIF images.
        base_folder (str): The base folder path for the manuscript data.
        bdd_tei_text (str): The TEI representation of the manuscript.
        start_folio (str): The starting folio number of the manuscript.
        iiif_image_id (int): The ID of the IIIF image.
        path_to_pagexml_files (List[str]): The paths to the PAGE XML files for the manuscript.
        facs_url (str): The URL for the facsimile of the manuscript.
        corresp (str): The correspondence information for the manuscript.
        ana (str): The annotation information for the manuscript.
        toc_label_for_later_replacement (List[str]): A list of TOC labels for later replacement.
        label_for_later_replacement (List[str]): A list of labels for later replacement.
        interrogation_label_for_later_replacement (List[str]): A list of interrogation labels for later replacement.
        inscriptions_to_replace (List[str]): A list of inscriptions for later replacement.

    Methods:
        __init__(self, sigla):
            Initializes a ManuscriptToProcess instance with the provided sigla.

        increment_folia(self):
            Increments the folio numbers of the manuscript.

        identify_placement_of_element(coords):
            Identifies the placement of an element on the page using the provided coordinates.

        coords_baseline(self, root, xpath):
            Retrieves and adjusts the coordinates from the baseline of a text region in a PAGE XML document.

        coords_text_region(self, root, xpath):
            Get the bounding box coordinates of a text region in a PAGE XML file.

        create_tei_fw_head(self, root):
            Creates tei:fw for the header of the manuscript.

        create_column(self, root, column_name, column_a_b):
            Creates text of a column from a PAGE XML file.

        create_tei_fw_foot(self, root):
            Creates tei:fw for the footer of the manuscript.

        store_toc_label_for_later_replacement(self, root):
            Stores information about TOC labels for later replacement.

        store_label_for_later_replacement(self, root):
            Stores information about labels for later replacement.

        store_interrogation_label_for_later_replacement(self, root):
            Stores information about interrogation labels for later replacement.

        store_inscription_for_later_replacement(self, root):
            Stores information about inscriptions for later replacement.

        create_tei_from_pagexml(self):
            Creates TEI representation from the extracted text in the PAGE XML files.

    """

    def __init__(self, sigla):
        """
        Initializes a ManuscriptToProcess instance with the provided sigla.

        Args:
            sigla (str): The unique identifier for the manuscript.
        """

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
        """
        Increments the folio numbers of the manuscript.

        This function is used to increment the folio numbers, following the standard notation for folios in manuscripts,
        where 'r' stands for recto (the front side of a leaf) and 'v' for verso (the back side). The function changes
        'r' to 'v' (moving to the back side of the same leaf), or increments the leaf number and changes 'v' to 'r'
        (moving to the front side of the next leaf).

        This method does not take any parameters or return anything. It modifies the instance variable 'start_folio'.

        Example:
        If the current 'start_folio' is '28r', it will be changed to '28v'.
        If the current 'start_folio' is '28v', it will be changed to '29r'.
        """

        if 'r' in self.start_folio:
            self.start_folio = self.start_folio.replace('r', 'v')
        elif 'v' in self.start_folio:
            self.start_folio = str(int(self.start_folio.replace('v', '')) + 1) + 'r'

    @staticmethod
    def identify_placement_of_element(coords):

        """
        Identifies the placement of an element on the page using the provided coordinates.

        This static method processes a list of coordinates that represent the position of a text region
        on a manuscript page. It checks whether the region is located on the left or right side of the page 
        based on the x-coordinate (horizontal position). The method returns a string indicating the side 
        of placement, which can be used to replace the placeholder {left|right} in an XML file.

        Parameters:
        coords (List[str]): A list of strings, where each string contains the x and y coordinates 
        (separated by a comma) for a point on the text region's bounding box. 
        For example: ['800,600', '900,700', '800,800', '700,600']

        Returns:
        str: A string indicating the side of placement on the page. It can be either 'left' or 'right'.

        Note:
        The method considers a region to be on the 'left' side of the page if any of its x-coordinates are 
        less than 800. Otherwise, it is considered to be on the 'right' side.
        """

        side = 'right'
        width = coords[0].split(' ')
        for points in width:
            points = points.split(',')
            if int(points[0]) < 800:
                side = 'left'

        return side

    def coords_baseline(self, root, xpath):
        """
        Retrieves and adjusts the coordinates from the baseline of a text region in a PAGE XML document.

        This method takes the root of an PAGE XML document tree and an XPath expression to find elements within
        the PAGE XML that match the given expression. For each matching element, it processes the baseline coordinates,
        adjusts these coordinates according to a scale factor, and returns them in a specific format.

        Parameters:
        root (etree.Element): The root node of a PAGE XML document tree.
        xpath (str): An XPath expression used to find specific elements in the PAGE XML tree.

        Returns:
        coord_string (str): A string representing the adjusted coordinates of the baseline in the format "c1,c2,w,h",
        where:
            c1: The x-coordinate of the leftmost point of the baseline, adjusted by the scale factor and reduced by 20.
            c2: The y-coordinate of the leftmost point of the baseline, adjusted by the scale factor and reduced by 50.
            w:  The width of the baseline (the distance in x-coordinates between the leftmost and rightmost points), adjusted by the scale factor and increased by 80.
            h:  The height of the baseline, fixed at 100.

        Note:
        The method assumes that the baseline coordinates in the PAGE XML are in the format "x1,y1 x2,y2 ... xn,yn", where
        each pair of values (x,y) represents a point on the baseline. The x and y values are separated by a comma, and
        each pair of values is separated by a space.
        """

        # scaling factor for coordinates
        x = float(self.iiif_scale_factor)

        # fetch coordinates using XPath query from the PAGE XML document root
        coords = root.xpath(xpath,
                            namespaces={'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

        # iterate over all coordinate sets found
        for i in coords:
            # split the coordinates by space (expected format is "x1,y1 x2,y2 ... xn,yn")
            coord = i.split(' ')

            # split the leftmost (first) coordinate by comma into x and y values
            coord_left = coord[0].split(',')

            # split the rightmost (last) coordinate by comma into x and y values
            coord_right = coord[-1].split(',')

            # calculate adjusted x-coordinate (c1) and y-coordinate (c2) of the leftmost point of the baseline
            c1 = int(int(coord_left[0]) * x) - 20  # scale the original x-coordinate by the factor x and reduce by 20
            c2 = int(int(coord_left[1]) * x) - 50  # scale the original y-coordinate by the factor x and reduce by 50

            # calculate the width of the baseline (the x-distance between the leftmost and rightmost points)
            w = int(coord_right[0]) - int(coord_left[0]) + 80  # add 80 to the width

            # scale the width by the factor x
            w = int(w * x)

            # fix the height of the baseline at 100
            h = 100

        # format the calculated values into a string "c1,c2,w,h"
        coord_string = f"{c1},{c2},{w},{h}"

        return coord_string
        
    def coords_text_region(self, root, xpath):
        """ 
        Get the bounding box coordinates of a text region in a PAGE XML file.

        This function takes in the root of a PAGE XML document and an XPath query, 
        and returns the coordinates of the bounding box that contains all points 
        found by the XPath query. The coordinates are scaled by a scaling factor 
        and adjusted to add padding around the bounding box. The returned coordinates 
        are in the format "x,y,width,height".

        :param root: The root of the PAGE XML document.
        :param xpath: The XPath query to find the points.
        :return: The bounding box coordinates as a string in the format "x,y,width,height".
        """

        # scaling factor for coordinates
        x = float(self.iiif_scale_factor)

        # fetch coordinates using XPath query from the PAGE XML document root
        coords = root.xpath(xpath,
                            namespaces={'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

        # iterate over all coordinate sets found
        for i in coords:
            # initialize lists to store x and y coordinates
            coords_list_left = []
            coords_list_right = []

            # split the coordinates by space (expected format is "x1,y1 x2,y2 ... xn,yn")
            coord = i.split(' ')

            for e in coord:
                # split each coordinate by comma into x and y values and append to respective lists
                e = e.split(',')
                coords_list_left.append(int(e[0]))
                coords_list_right.append(int(e[1]))

        # calculate the bounding box coordinates
        c1 = int(min(coords_list_left) * x)  # leftmost x-coordinate, scaled by x
        w = max(coords_list_left)  # width of the bounding box, scaled by x and adjusted for padding
        w = int(w * x)
        w = w - c1
        w = w + 30
        c2 = min(coords_list_right)  # topmost y-coordinate, scaled by x and adjusted for padding
        c2 = int(c2 * x)
        h = max(coords_list_right)  # height of the bounding box, scaled by x and adjusted for padding
        h = int(h * x)
        h = h - c2
        h = h + 30
        c2 = c2 - 30

        # format the calculated values into a string "c1,c2,w,h"
        coord_string = str(c1) + ',' + str(c2) + ',' + str(w) + ',' + str(h)

        return coord_string

    def create_tei_fw_head(self, root):
        """ create tei:fw for header

        Creates tei:fw element including header if available from pageXML.

        :param root: Takes root from etree
        :return text_header: Returns tei:fw element as string
        """

        try:
            header = root.xpath('//ns0:TextRegion[contains(@type,"header")]',
                                namespaces={'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[
                0]
            unicode_header = header.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
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
        :param column_name: specifies column name as 'column_1' or 'column_2'
        :param column_a_b: specifies column 'a' or 'b' for proper tei:cb
        :return text_column_1: Returns text of column 1 element as string
        """

        try:
            column = root.xpath(f'//ns0:TextRegion[contains(@custom,"type:{column_name}")]',
                                namespaces={'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[
                0]
            coords_column = self.coords_text_region(column, './ns0:Coords/@points')
            # create column with coordinates
            text_column = f'<cb n="{column_a_b}" facs="{coords_column}"/>'

            # lines in column
            unicode_column = column.xpath('.//ns0:TextLine', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            line_number = 0
            for line in unicode_column:
                line_text = line.xpath('./ns0:TextEquiv/ns0:Unicode/text()', namespaces={
                    'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                line_coords = self.coords_text_region(line, './ns0:Coords/@points')
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
            footer = root.xpath('//ns0:TextRegion[contains(@type,"footer")]',
                                namespaces={'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[
                0]
            unicode_footer = footer.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_footer = self.coords_baseline(footer, './/ns0:TextLine//ns0:Baseline/@points')
            text_footer = \
                f'\n<fw type="quire-numeral" place="bottom" facs="{coords_footer[0]}">{unicode_footer[0]}</fw>'
        except:
            text_footer = ''
        return text_footer

    def store_toc_label_for_later_replacement(self, root):
        for chapter_number_toc in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces={
            'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            # create label element
            chapter_number_toc_text = chapter_number_toc.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()',
                                                               namespaces={
                                                                   'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[
                0]
            coords_label_toc_a = chapter_number_toc.xpath('./ns0:Coords/@points', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_label_toc_b = self.coords_text_region(chapter_number_toc, './ns0:Coords/@points')

            side = self.identify_placement_of_element(coords_label_toc_a)
            replace_key = re.search(r'~(\d+)~', chapter_number_toc_text)
            replace_key = replace_key.group(0)
            div_number = replace_key.replace('~', '')

            label_toc = f'<item n="{div_number}"><label place="margin {side}" type="chapter-number" facs="{coords_label_toc_b}"><hi rend="color:red">{chapter_number_toc_text}</hi></label> <hi rend="color:red">'

            # append div number and label_toc for later replacement to list
            list_item = [div_number, replace_key, label_toc]
            self.toc_label_for_later_replacement.append(list_item)

    def store_label_for_later_replacement(self, root):
        for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces={
            'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            try:
                chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()',
                                                           namespaces={
                                                               'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[
                    0]
                coords_label_a = chapter_number.xpath('./ns0:Coords/@points', namespaces={
                    'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                coords_label_b = self.coords_text_region(chapter_number, './ns0:Coords/@points')

                side = self.identify_placement_of_element(coords_label_a)
                replace_key = re.search(r'\*(\d+)\*', chapter_number_text)
                replace_key = replace_key.group(0)
                div_number = replace_key.replace('*', '')

                label = f'<div n="{div_number}" type="chapter"><head type="chapter-title"><label type="chapter-number" place="margin {side}" facs="{coords_label_b}"><hi rend="color:red">{chapter_number_text}</hi></label> <hi rend="color:red">'

                list_item = [div_number, replace_key, label]
                print(list_item)
                self.label_for_later_replacement.append(list_item)

            except Exception as e:
                print(str(e) + '>>>Error with label<<<')

    def store_interrogation_label_for_later_replacement(self, root):
        """
        Stores the information about interrogation labels for later replacement.

        This function searches for TextRegions with a custom attribute indicating 
        the type 'chapter_count' and extracts the chapter number text from it. 
        If the chapter number text contains a specific pattern ('*i<number>*'), 
        it retrieves the coordinates of the label and stores the information 
        for later replacement in the XML.

        :param root: The root element of the PAGE XML document.
        """
        for chapter_number in root.xpath('//ns0:TextRegion[contains(@custom,"type:chapter_count")]', namespaces={
            'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            chapter_number_text = chapter_number.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
            try:
                if '*i' in chapter_number_text:
                    coords_label_a = chapter_number.xpath('./ns0:Coords/@points', namespaces={
                        'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                    coords_label_b = self.coords_text_region(chapter_number, './ns0:Coords/@points')

                    side = self.identify_placement_of_element(coords_label_a)
                    replace_key = re.search(r'\*i(\d+)\*', chapter_number_text)
                    replace_key = replace_key.group(0)
                    div_number = replace_key.replace('*', '')
                    div_number = div_number.replace('i', '')

                    label = f'<div n="{div_number}" type="interrogation"><label type="chapter-number" place="margin {side}" facs="{coords_label_b}"><hi rend="color:red">{chapter_number_text}</hi></label> \n<p n="1"><hi rend="color:red">'

                    list_item = [div_number, replace_key, label]
                    self.interrogation_label_for_later_replacement.append(list_item)
            except Exception as e:
                print(f"{e} >>>Interrogation<<<")

    def store_inscription_for_later_replacement(self, root):
        """
        Stores the information about inscriptions for later replacement.

        This function searches for TextRegions with a custom attribute indicating
        the type 'Inskription' and extracts the inscription text from it.
        It retrieves the coordinates of the inscription label and constructs the
        corresponding XML element to represent the inscription. The information
        is then stored for later replacement in the XML.

        :param root: The root element of the PAGE XML document.
        """
        for inskription in root.xpath('//ns0:TextRegion[contains(@custom,"type:Inskription")]', namespaces={
            'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
            inskription_text = ''
            for line in inskription.xpath('.//ns0:TextLine/ns0:TextEquiv/ns0:Unicode/text()', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
                inskription_text = f"{inskription_text} {line}"

            coords_inskription_a = inskription.xpath('./ns0:Coords/@points', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            coords_inskription_b = self.coords_text_region(inskription, './ns0:Coords/@points')
            side = self.identify_placement_of_element(coords_inskription_a)

            inskription_xml = f'</hi></head>\n<note type="inscription" place="margin {side}" anchored="false" facs="{coords_inskription_b}">{inskription_text}</note>'
            inskription_xml = inskription_xml.replace('> ', '>')

            replace_key = re.search(r'\*(i\d+|\d+)\*', inskription_text)
            replace_key = replace_key.group(0)
            div_number = replace_key.replace('*', '')
            text_to_be_replaced = f'<div n="{div_number}" type="chapter"'
            replace_text = f'{inskription_xml}\n<p n="1"><hi rend="color:red initial">'
            self.inscriptions_to_replace.append([replace_text, text_to_be_replaced, replace_key])

    def create_tei_from_pagexml(self):
        """
        Creates TEI representation from the extracted text in the PAGE XML files.

        This function processes each PAGE XML file and extracts the text from the columns and headers.
        It constructs the TEI representation by combining the extracted text and applying certain
        replacements and transformations. The TEI representation is stored in the 'bdd_tei_text' attribute of the object.

        """
        text_page = ""
        # open each pagexml-file for exporting text to tei
        for filename in self.path_to_pagexml_files:
            tree = LET.parse(filename)
            root = tree.getroot()

            # creates page beginning for each xml-pagefile using data taken from config file
            page_break = f'\n<pb n="{self.start_folio}" facs="{eval(self.facs_url)}" corresp="{eval(self.corresp)}" ' \
                         f'ana="{eval(self.ana)}"/> '
            # adds tei:fw if header exists on page
            text_header = self.create_tei_fw_head(root)
            # creates text of column 1 from lines
            text_column_1 = self.create_column(root, 'column_1', 'a')
            # creates text of column 2 from lines
            text_column_2 = self.create_column(root, 'column_2', 'b')
            # creates tei:fw footer element
            text_footer = self.create_tei_fw_foot(root)
            # create page
            text_page = f"{text_page}{page_break}{text_header}\n{text_column_1}\n{text_column_2}\n{text_footer}"

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
            elements_to_be_tested = [['~i~', r'~i~(.*?)~',
                                      f'<!-- Beginn Inhaltsverzeichnis -->\n<div type="toc" xml:id="{self.tei_base_id_book}-toc">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head>\n<list>\n~'],
                                     ['*i*', r'\*i\*(.*?)\*p\*',
                                      f'</list>\n</div>\n<!-- Beginn des Haupttextes  -->\n<div type="content" xml:id="{self.tei_base_id_book}-con">\n<div xml:id="{self.tei_base_id_book}-con-000" type="praefatiuncula">\n<head type="incipit"><hi rend="color:red capitals">\g<1></hi></head><p n="1"><hi rend="color:red">'],
                                     ['#p#', '#p#', '</hi></p>\n</div>']]
            for element in elements_to_be_tested:
                if element[0] in text_page:
                    text_page = re.sub(element[1], element[2], text_page, flags=re.DOTALL)

            # increase folio number and iiif_image_id
            self.increment_folia()
            self.iiif_image_id += 1

        self.bdd_tei_text = text_page

class BddTei:
    """
    A class for transforming PAGE XML files to TEI format according to BDD schematics.

    Attributes:
        tei (str): The TEI representation of the manuscript.
        toc_label_for_later_replacement (list): A list of TOC labels for later replacement.
        interrogation_label_for_later_replacement (list): A list of interrogation labels for later replacement.
        label_for_later_replacement (list): A list of chapter labels for later replacement.
        inscriptions_to_replace (list): A list of inscriptions to replace.
        tei_base_id_book (str): The base ID of the TEI book.

    Methods:
        bdd_export_tei(): Transforms the PAGE XML as a single TEI file according to BDD schematics.
        sc_to_g(): Replaces special characters in the TEI representation.
        bdd_specific_tei(): Modifies specific elements in the TEI representation according to BDD requirements.
        line_breaks_angled_dash(): Adjusts line breaks in the TEI representation using manually inserted '¬' character.
        preprocessing(): Performs preprocessing operations before abbreviation expansion.
        postprocessing(): Performs postprocessing operations on the TEI representation after abbreviation expansion.

    """
    
    def __init__(self, manuscript):
        """
        Initializes a BddTei object.

        Args:
            manuscript (ManuscriptToProcess): The ManuscriptToProcess object containing the necessary data.

        """
        self.tei = manuscript.bdd_tei_text
        self.toc_label_for_later_replacement = manuscript.toc_label_for_later_replacement
        self.interrogation_label_for_later_replacement = manuscript.interrogation_label_for_later_replacement
        self.label_for_later_replacement = manuscript.label_for_later_replacement
        self.inscriptions_to_replace = manuscript.inscriptions_to_replace
        self.tei_base_id_book = manuscript.tei_base_id_book

    def bdd_export_tei(self):
        """
        Transforms the PAGE XML as a single TEI file according to BDD schematics.

        This method performs various replacements and transformations on the TEI representation, 
        based on the extracted data from the PAGE XML files. It replaces TOC labels, interrogation labels, 
        and chapter labels with their corresponding values. It also adjusts the structure of the TEI representation 
        by inserting appropriate tags and removing unnecessary elements.

        Note:
        - This method modifies the 'tei' attribute of the ManuscriptToProcess instance.

        """

        # Insert label TOC
        for element in self.toc_label_for_later_replacement:
            if int(element[0]) == 1:
                # treat first element differently
                self.tei = re.sub(r'\n(<lb.*?/>)(</hi></head>\n)<list>\n~1~(\w)',
                                  r'\g<2>\g<1><list>' + element[2].replace(element[1], '') + r'\g<3></hi>', self.tei)
            else:
                self.tei = re.sub(f'\n(<lb.*?/>){element[1]}(\w)',
                                  r'</item>\n\g<1>' + element[2].replace(element[1], '') + r'\g<2></hi>', self.tei)

        # Insert label interrogation
        for element in self.interrogation_label_for_later_replacement:
            # print(element[0])
            if int(element[0]) == 1:
                # treat first element differently

                self.tei = re.sub(r'\*i' + element[0] + r'\*~(\w)',
                                  '</p>' + element[2].replace(element[1], '') + r'\g<1></hi>', self.tei)
            else:
                self.tei = re.sub(r'\*i' + element[0] + r'\*~(\w)',
                                  '</p></div>' + element[2].replace(element[1], '') + r'\g<1></hi>', self.tei)

        # Insert label chapter
        for element in self.label_for_later_replacement:
            # print(element[1])
            if int(element[0]) == 1:
                # treat first element differently
                self.tei = re.sub(r'\*' + element[0] + r'\*', element[2].replace(element[1], ''), self.tei)
            else:
                self.tei = re.sub(r'\*' + element[0] + r'\*', '</p>\n</div>\n' + element[2].replace(element[1], ''),
                                  self.tei)

        for element in self.inscriptions_to_replace:
            if 'i1' in element[0]:
                # interrogationes start with inscription instead of interrogation number
                element[0] = element[0].replace('</hi></head>\n', '')
                element[0] = element[0].replace('\n<p n="1"><hi rend="color:red initial">', '')

                self.tei = re.sub(r'\*i1\*(.*?)~(\w)',
                                  '</p>\n<div n="1" type="interrogation"><head type="chapter-title"><hi '
                                  r'rend="color:red">\g<1></hi></head>\n' +
                                  element[0].replace('*i1*', '') + r'<p n="1"><hi rend="color:red">\g<2></hi>',
                                  self.tei, flags=re.DOTALL)
            else:
                self.tei = re.sub('(' + element[1] + '.*?)~', r'\g<1>' + element[0].replace(element[2], '') + '~',
                                  self.tei, flags=re.DOTALL)

        self.tei = self.tei.replace('</item></item>', '</item>')
        self.tei = self.tei.replace('</list>', '</item></list>')
        self.tei = re.sub(r'\*\d+\*', '', self.tei)
        self.tei = re.sub(r'~\d+~', '', self.tei)
        self.tei = re.sub(r'#(\w)', r'<hi rend="versal">\g<1></hi>', self.tei)
        self.tei = re.sub(r'~(\w)', r'\g<1></hi>', self.tei)

    def sc_to_g(self):
        """
        Replaces special characters in the TEI representation.

        This method replaces special characters from a list provided in the config file. Each character is replaced 
        with its corresponding replacement value.

        Note:
        - This method modifies the 'tei' attribute of the ManuscriptToProcess instance.

        """

        # replace special characters from list in config file...
        for character in config.character_list:
            self.tei = self.tei.replace(character[1], character[0])

    def bdd_specific_tei(self):
        """
        Modifies specific elements in the TEI representation according to BDD requirements.

        This method performs various replacements and transformations on specific elements in the TEI representation
        to meet the requirements of BDD. It replaces '<add>' tags with '<add place="above" type="contemporary">'.
        It replaces '...' with '<unclear reason="tight-binding" resp="Transkribus" cert="low">...</unclear>'.
        It replaces '[' with '<note type="editorial-comment" resp="transkribus">', ']' with '</note>',
        and '<note>' with '<note type="editorial-comment" resp="transkribus">'.
        It replaces '<del>' with '<del rend="">'.
        It replaces '<subst>' with '<subst><del rend="erasure"/><add place="" type="">' and '</subst>' with '</add></subst>'.
        It modifies '<delSpan>' elements and '<seg>' elements by adding IDs and anchor points.
        It removes the '§' character from the TEI representation.

        Note:
        - This method modifies the 'tei' attribute of the ManuscriptToProcess instance.

        """
        # <add> used in Transkribus to show inline additions
        self.tei = self.tei.replace('<add>', '<add place="above" type="contemporary">')

        # unclear
        self.tei = self.tei.replace('...',
                                    '<unclear reason="tight-binding" resp="Transkribus" cert="low">...</unclear>')

        # editorial comment
        self.tei = self.tei.replace('[', '<note type="editorial-comment" resp="transkribus">')
        self.tei = self.tei.replace(']', '</note>')
        self.tei = self.tei.replace('<note>', '<note type="editorial-comment" resp="transkribus">')

        # del
        self.tei = self.tei.replace('<del>', '<del rend="">')

        # subst
        self.tei = self.tei.replace('<subst>', '<subst><del rend="erasure"/><add place="" type="">')
        self.tei = self.tei.replace('</subst>', '</add></subst>')

        # delspan
        # seg
        n = 1
        for i in re.findall('<delSpan>.*?</delSpan>', self.tei, re.DOTALL):
            print(i)
            id = f"{self.tei_base_id_book}-delSpan-{str(n).zfill(3)}"
            seg_text = i.replace('<delSpan>', f'<delSpan spanTo="#{id}" rend=""/>').replace('</delSpan>', f'<anchor xml:id="{id}"/>')
            self.tei = self.tei.replace(i, seg_text)
            n += 1

        # seg
        n = 1
        for i in re.findall('<seg>.*?</seg>', self.tei):
            #print(i)
            id = f"{self.tei_base_id_book}-supp-{str(n).zfill(3)}"
            seg_text = i.replace('<seg>', '').replace('</seg>', '')
            supplied = i.replace('<seg>', f'<supplied xml:id="{id}" reason="displaced-over-the-line">').replace(
                '</seg>', '</supplied>').replace('', '')

            self.tei = self.tei.replace(i, f'<seg corresp="#{id}" type="pos-of-displaced">{seg_text}§</seg>{supplied}',
                                        1)
            print(supplied)
            n += 1

        self.tei = self.tei.replace('§', '')

    # use manually inserted ¬ for creating proper tei linebreaks
    def line_breaks_angled_dash(self):
        """
        Adjusts line breaks in the TEI representation using manually inserted '¬' character.

        This method modifies line breaks in the TEI representation by replacing '¬ ' with '¬',
        and by replacing '¬\n' with appropriate line break elements based on the surrounding context.
        It uses regular expressions to identify specific patterns and perform the replacements.

        Note:
        - This method modifies the 'tei' attribute of the ManuscriptToProcess instance.

        """
        self.tei = self.tei.replace('¬ ', '¬')
        self.tei = re.sub(r'¬\n(<lb.*?)/>', r'\g<1> break="no"/>', self.tei, flags=re.DOTALL)
        self.tei = re.sub(r'¬\n+(<cb.*?n="b".*?/>\n<lb.*?)/>', r'\g<1> break="no"/>', self.tei)
        self.tei = re.sub(r'¬\n+(<pb.*?<cb.*?n="a".*?/>\n<lb.*?)/>', r'\g<1> break="no"/>', self.tei)
        self.tei = re.sub(r'¬', '<lb break="no"/>', self.tei)

    def preprocessing(self):
        """ preprocessing before expansion of abbreviations

        """
        # replace pre character
        self.tei = self.tei.replace('\ue665', 'p\u0304')
        # replace wrong -tur sign
        self.tei = self.tei.replace('\u1dd1', '\uf1c2')
        # make sure, -ur ligatur has not been put behind interpunctuation
        self.tei = self.tei.replace('', '')

    def postprocessing(self):
        """
        Performs postprocessing operations on the TEI representation after abbreviation expansion.

        This method applies various corrections and modifications to the TEI representation to address specific issues.
        It checks for incorrect placement of '</p>' or '</hi>' within '<choice>' elements and adjusts the placement.
        It performs specific replacements for certain patterns in the TEI representation.
        It corrects line breaks and handles ambiguous expansions.

        Note:
        - This method modifies the 'tei' attribute of the ManuscriptToProcess instance.

        """

        # check, if </p> element is wrongly inserted in choice element:
        for choice_element in re.findall('<choice>.*?</p>.*?</choice>', self.tei):
            if '<p ' not in choice_element:
                replacement = re.sub('</p>', r'', choice_element)
                self.tei = re.sub(choice_element, replacement + '</p>', self.tei)

        # check, if </hi> element is wrongly inserted in choice element:
        for choice_element in re.findall('<choice>.*?</hi>.*?</choice>', self.tei):
            if '<hi ' not in choice_element:
                replacement = re.sub('</hi>', r'', choice_element)
                self.tei = re.sub(choice_element, replacement + '</hi>', self.tei)

        self.tei = re.sub(
            '<choice><abbr><choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice></abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>',
            '<choice><abbr><p n="1"><hi rend="color:red">I</hi>nterrogandū</abbr><expan><p n="1"><hi rend="color:red">I</hi>nterrogandum</expan></choice>',
            self.tei)
        self.tei = re.sub(
            '(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> )<choice><abbr><hi rend="color:red">',
            '\g<1><hi rend="color:red"><choice><abbr>', self.tei, flags=re.DOTALL)
        self.tei = re.sub(
            '(type="chapter"><head type="chapter-title"><label type="chapter-number" .*?</hi></label> <hi rend="color:red"><choice><abbr>.*?<expan>)<hi rend="color:red">',
            '\g<1>', self.tei, flags=re.DOTALL)
        self.tei = re.sub('(\n\n<pb.*?/>\n<fw.*?>\n<cb n="a".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>',
                          self.tei)
        self.tei = re.sub('(\n<cb n="b".*?/>\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>', self.tei)
        self.tei = re.sub('(\n<lb.*?/>)</hi></head>', '</hi></head>\g<1>', self.tei)

         # correction generic cases
        xml_to_be_corrected = ['lb ', 'add', 'p', 'hi></label', 'item', 'note', 'fw']

        for i in xml_to_be_corrected:
            self.tei = re.sub(
                '(<choice><abbr>)(<' + i + '.*?>)(.*?</abbr><expan>)(<' + i + '.*?>)(.*?</expan></choice>)',
                r'\g<2>\g<1>\g<3>\g<5>', self.tei)
            self.tei = re.sub(
                '(<choice><abbr>.*?)</' + i + '>(</abbr><expan>.*?)</' + i + '>(.*?</expan></choice>)',
                r'\g<1>\g<2>\g<3></' + i + '>', self.tei)

        # correction of ambigue expansions
        # Capitula in fw
        self.tei = re.sub('(<fw.*?><choice><abbr>Cap<g ref="#char-0305">&#x0305;</g></abbr><expan>)Capitulum(</expan></choice>.*?</fw>)',
                          '\g<1>Capitula\g<2>', self.tei, flags=re.IGNORECASE)
        # Cap in fw ohne Auflösung
        #self.tei = re.sub('(<fw.*?>)Cap<g ref="#char-0305">&#x0305;</g>(.*?</fw>)',
        #                  '\g<1><choice><abbr>Cap<g ref="#char-0305">&#x0305;</g></abbr><expan>Capitula</expan></choice>\g<2>', self.tei, flags=re.IGNORECASE)
        # Ex concilio
        self.tei = re.sub('(<note type="inscription".*?>Ex <choice>.*?<expan>)concilium(</expan>)',
                          '\g<1>concilio\g<2>', self.tei)
        # Ex eodem capitulo
        self.tei = re.sub('(<note type="inscription".*?>Ex eodem <choice>.*?<expan>)Capitula(<)', '\g<1>Capitulo\g<2>',
                          self.tei)

        # correction of linebreaks
        self.tei = re.sub('¬\n(<pb.*?<lb .*?)(/>)', '\g<1> break="no"\g<2>', self.tei, flags=re.DOTALL)
        # Bei <hi>Q</hi> kommt <hi>Qu</hi>. EInsetzen um ein Buchstaben verrückt, aber nur bei Wörtern mit Q?
        self.tei = re.sub('¬\n(<pb.*?<lb .*?)(/>)', '\g<1> break="no"\g<2>', self.tei, flags=re.DOTALL)
        self.tei = re.sub(
            '<choice><abbr><fw type="page-header" place="top" facs="638,58,210,100"><choice><abbr>Cap̅</abbr><expan>Capitula</expan></choice></abbr><expan><fw type="page-header" place="top" facs="638,58,210,100">Capitulum</expan></choice>',
            '<fw type="page-header" place="top" facs="638,58,210,100"><choice><abbr>Cap̅</abbr><expan>Capitula</expan></choice>',
            self.tei)
        # text_page = re.sub('<choice><abbr>earu<g ref="#char-0304">\u0304</g><add place="above" type="contemporary">roru<g ref="#char-0304">\u0304</g></abbr><expan>earumr<add place="above" type="contemporary">orum</expan></choice></add>','<choice><abbr>earu<g ref="#char-0304">&#x0304;</g></abbr><expan>earum<add place="above" type="contemporary">orum</expan></choice><add place="above" type="contemporary"><choice><abbr>roru<g ref="#char-0304">\u</g></abbr><expan>rorum</expan></choice></add>', text_page)
        self.tei = re.sub(
            '<choice><abbr></p></div><div n="10" type="interrogation"><label type="chapter-number" place="margin left" facs="205,219,157,181"><hi rend="color:red">Int̅</abbr><expan></p></div><div n="10" type="interrogation">I<label type="chapter-number" place="margin left" facs="205,219,157,181">n<hi rend="color:red">terrogatio</expan></choice>',
            '</p></div><div n="10" type="interrogation"><label type="chapter-number" place="margin left" facs="205,219,157,181"><hi rend="color:red"><choice><abbr>Int̅</abbr><expan>Interrogatio</expan></choice>',
            self.tei)
        self.tei = re.sub(
            '<choice><abbr>ep̅o<add place="above" type="contemporary">s</abbr><expan>epis<add place="above" type="contemporary">copos</expan></choice></add>',
            '<choice><abbr>ep̅o</abbr><expan>episcopo</expan></choice><add place="above" type="contemporary">s</add>',
            self.tei)
        self.tei = re.sub(
            '<add place="above" type="contemporary"><choice><abbr>e</add>ade<g ref="#char-0304">&#x0304;</g></abbr><expan>e</add>adem</expan></choice>',
            '<choice><abbr><add place="above" type="contemporary">e</add>ade<g ref="#char-0304">&#x0304;</g></abbr><expan><add place="above" type="contemporary">e</add>adem</expan></choice>',
            self.tei)
        self.tei = re.sub(
            '<add place="above" type="contemporary"><choice><abbr>n̅</add>posset</abbr><expan>ER</add>ROR</expan></choice>',
            '<add place="above" type="contemporary"><choice><abbr>n̅</abbr><expan>non</expan></choice></add> posset',
            self.tei)


class PageXMLTests:
    """
    A class for performing tests on PAGE XML files.

    This class provides methods for performing various tests on PAGE XML files. It can concatenate multiple text files,
    check text regions for necessary tags, check entries in the single text file, check the number of items in a list,
    and check the internal structure of the text based on special placeholders.

    Args:
        path_to_pagexml_files (list): A list of file paths to the PAGE XML files to be tested.

    Attributes:
        filenames (list): A list of file paths to the PAGE XML files.
        single_text_file (str): The concatenated text from all the files.

    """

    def __init__(self, path_to_pagexml_files):
        """
        Initializes an instance of the PageXMLTests class.

        Args:
            path_to_pagexml_files (list): A list of file paths to the PAGE XML files to be tested.

        """
        self.filenames = path_to_pagexml_files
        self.single_text_file = ""

    def create_single_text_file(self):
        """
        Concatenates multiple text files into a single text file.
    
        This method reads multiple text files specified by the 'filenames' attribute and concatenates their contents
        into a single text file. The resulting text file is stored in the 'single_text_file' attribute of the object.
    
        Returns:
            str: The concatenated text from all the files.
    
        """
        single_text_file = ""
        for filename in self.filenames:
            with open(filename, 'r', encoding = 'utf8') as file:
                text = file.read()
                single_text_file = single_text_file + text
        self.single_text_file = single_text_file
        return self.single_text_file

    def check_text_regions(self):
        """
        Checks text regions in the XML files for necessary tags.

        This method iterates over the XML files specified by the 'filenames' attribute and checks each text region
        for the presence of necessary markup tags. It specifically looks for the presence of the "structure {type:"
        tag within each text region. If a text region is found without the necessary markup, an error message is printed
        with the details of the text region.

        Note:
        - The method prints error messages if any text regions are found without the necessary markup.
        - The method terminates the script if inconsistent text regions are found.
        """

        consistent_text_regions = True
        for filename in self.filenames:
            tree = LET.parse(filename)
            root = tree.getroot()

            current_page = root.xpath('//ns0:TranskribusMetadata/@pageNr', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]

            textregions = root.xpath('//ns0:TextRegion', namespaces={
                'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            for element in textregions:
                if "structure {type:" in LET.tostring(element, encoding='unicode', method='xml'):
                    pass
                else:
                    print(f"\nTextregion missing markup on page {current_page}!\n=================================")
                    print(
                        f"{LET.tostring(element, encoding='unicode', method='xml')}\n=================================")
                    consistent_text_regions = False

            print(f"Page {current_page} checked for consistency of textregions.")

        if consistent_text_regions == True:
            print("===> All pages have been checked successfully, now checking internal structure.\n")
        else:
            print("Errors have occured, stopping script.")
            exit()

    def check_entries(self, character, type):
        """
        Checks entries in the single text file for a given character pattern.
    
        This method counts the number of entries in the single text file that match the specified character pattern.
        The character pattern is provided as the 'character' parameter. The method searches for entries marked up by
        '~n~' or entries enclosed within the specified characters. The type of entries is provided as the 'type' parameter.
    
        Note:
        - The method assumes that the single text file has been created before calling this method.
        - The method prints the number of entries detected and returns the number of entries, the set of entries,
          and the list of entries.
    
        Args:
        - character (str): The character pattern used to mark up the entries.
        - type (str): The type of entries being checked.
    
        Returns:
        - number_of_entries (int): The number of entries detected.
        - set_of_entries (set): A set containing unique entries.
        - entries (list): A list of all entries detected.
    
        """
        # count number of chapters using toc entries marked up by '~n~'
        if "*" in character:
            entries = re.findall(f'\*\d+\*', self.single_text_file)
            entries = [int(i.replace(f'{character}', '')) for i in entries]
        else:
            entries = re.findall(f'{character}\d+{character}', self.single_text_file)
            entries = [int(i.replace(f'{character}', '')) for i in entries]

        number_of_entries = max(entries)
        set_of_entries = set(entries)
        print(f"===> {number_of_entries} {type}-entries detected")
        return number_of_entries, set_of_entries, entries

    def check_number_of_items(self, items, test_number, type):
        """
        Checks the number of items in a list for a specific test number.

        This method checks the number of occurrences of each item in the list 'items' and compares it to the expected
        test number. If the count of an item divided by 2 is equal to the test number, the item is considered correct.
        Otherwise, an error message is printed indicating that the item has the wrong number. The method returns a boolean
        value indicating whether all items have the correct number.

        Args:
        - items (list): A list of items to be checked.
        - test_number (int): The expected test number.

        Returns:
        - test (bool): A boolean value indicating whether all items have the correct number.

        """
        test = True
        for i in range(1, max(items)):
            if items.count(i) / 2 == test_number:
                pass
            else:
                print(f"Item ({type}) {i} has wrong number.")
                #print(sorted(items))
                test = False
        print("All items correct.")
        return test

    def check_internal_structure(self):
        """
        Checks the internal structure of the text based on special placeholders.

        This method performs checks on the internal structure of the text using special placeholders, namely '~n~' and '*n*'.
        It creates a single text file for easy checking and then counts the number of TOC entries marked with '~n~' and
        the number of chapters marked with '*n*'. It compares these numbers and performs further checks on the number
        of placeholders in the text.

        Note:
        - This method relies on the 'create_single_text_file', 'check_entries', and 'check_number_of_items' methods.

        """
        print("Start checking internal structure")
        # creates texfile for easy checking
        self.create_single_text_file()

        # count number of chapters using toc entries marked up by '~n~' or '*n*'
        number_of_entries_toc, set_of_entries_toc, entries_toc = self.check_entries('~', 'TOC')
        number_of_chapter, set_of_entries_chapter, entries_chapter = self.check_entries('*', 'Chapter')

        if number_of_entries_toc == number_of_chapter:
            print("===> Number of TOC entries equals number of chapters.\n\nStart checking number of placeholder")
        else:
            print("===> Number of TOC entries does NOT EQUAL number of chapters.\n")
            print(f"\n=============================\nSet of TOC entries: {set_of_entries_toc}\n")
            print(f"\n=============================\nSet of Chapter entries: {set_of_entries_chapter}\n")

        # check, that two toc items and 3 chapter items have been asigned
        test_toc = self.check_number_of_items(entries_toc, 2,'TOC')
        test_chapter = self.check_number_of_items(entries_chapter, 3,'Chapter')
        if test_toc == True and test_chapter == True:
            pass
        else:
            exit()


def main():
    """
    Main script for downloading, exporting, and converting manuscripts stored in Transkribus into BDD-TEI format.

    The script takes command line arguments to specify the manuscript to be processed. It performs various tasks including
    downloading the data from Transkribus, testing the page XML for consistency, converting the page XML to TEI, and 
    replacing abbreviations with their full forms based on a provided dictionary. The processed manuscript is then saved 
    as a new XML file in TEI format.
    
    Note:
    This script should be run from the command line, with the necessary arguments provided.
    """

    # Get variables from console
    # example 'python bdd.py B 7 282-291 139v 236435 -dl'
    parser = argparse.ArgumentParser(
        description='Download, export and conversion from manuscripts stored in Transkribus into BDD-TEI.')
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
    path_to_folder = os.path.join(config.export_folder,book_string)

    # create manuscript object
    manuscript = ManuscriptToProcess(args.siglum)
    # update
    manuscript.tei_base_id_book = manuscript.tei_base_id_book + book_string
    manuscript.start_folio = args.folio
    manuscript.iiif_image_id = int(args.iiif_image_id)

    # start download if flag '-dl' is given
    if args.dl == True:
        print(
            f'Starting export of page-xml from Transkribus and download to local machine for book {book_string} in manuscript {manuscript.sigla}.')
        transpy.download_data_from_transkribus(manuscript.transkribus_collection, manuscript.transkribus_document,
                                               startpage, endpage, path_to_folder)
        print('Finished download.\n')

    # open page-xml files for further processing
    # get path to individual page-xml files
    manuscript.path_to_pagexml_files = transpy.load_pagexml(os.path.join(path_to_folder,str(manuscript.transkribus_document),manuscript.base_folder,'page'))

    # create pageXML object
    page_xml_tests = PageXMLTests(manuscript.path_to_pagexml_files)

    # test pageXML for consistency according to project needs
    page_xml_tests.check_text_regions()
    page_xml_tests.check_internal_structure()

    # conversion of pageXML into tei object
    manuscript.create_tei_from_pagexml()

    # create tei object for further processing
    tei_file = BddTei(manuscript)

    # process tei
    tei_file.bdd_export_tei()
    tei_file.preprocessing()
    tei_file.line_breaks_angled_dash()

    # TODO: Reihenfolge klären
    tei_file.bdd_specific_tei()

    dictionary_abbr_external = transpy.load_abbreviation_dict()
    tei_file.tei = transpy.replace_abbreviations_from_tei(dictionary_abbr_external, tei_file.tei)

    tei_file.sc_to_g()
    tei_file.postprocessing()

    # replace placeholder in template file and save as new file
    with open(os.path.join(config.resources_folder,f'tei_template_{manuscript.tei_base_id[:-1]}.xml'),
              'r', encoding='utf8') as xmlfile:
        template_file = xmlfile.read()

    new_file = template_file.replace('%%', tei_file.tei)
    # insert book number into file
    new_file = new_file.replace("{book}", book_string)
    # insert date into file
    today = datetime.date.today()
    new_file = new_file.replace("{date-yyyy-mm-dd}", str(today))

    if os.path.exists(os.path.join(os.getcwd(),'output',f'{book_string}')) == False:
        os.mkdir(os.path.join(os.getcwd(),'output',f'{book_string}'))
    with open(os.path.join(os.getcwd(),'output',f'{book_string}',f'{manuscript.tei_base_id_book}.xml'),
              'w+', encoding = 'utf8') as newfile:
        newfile.write(new_file)


if __name__ == "__main__":
    main()
