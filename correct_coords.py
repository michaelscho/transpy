from lxml import etree
import os

class TeiCorrector:
    def __init__(self, tei_file_path, pagexml_dir, fileout, scale_factor=3.6):
        self.tei_tree = etree.parse(tei_file_path)
        self.pagexml_files = sorted(os.listdir(pagexml_dir), key=lambda x: int(x.split('.')[0]))
        print(self.pagexml_files, len(self.pagexml_files))
        self.pagexml_dir = pagexml_dir
        self.file_out = fileout
        self.scale_factor = scale_factor
        self.ns = {
            'ns0': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15',
            'tei': 'http://www.tei-c.org/ns/1.0'
        }
        self.scale_factor = scale_factor

       
    def coords_text_region(self, coords):
        x = float(self.scale_factor)
        
        coords_list_left = []
        coords_list_right = []
        coord = coords.split(' ')
        for e in coord:
            e = e.split(',')
            coords_list_left.append(int(e[0]))
            coords_list_right.append(int(e[1]))

        c1 = int(min(coords_list_left) * x)
        w = max(coords_list_left)
        w = int(w * x)
        w = w - c1

        c2 = min(coords_list_right)
        c2 = int(c2 * x)
        h = max(coords_list_right)
        h = int(h * x)
        h = h - c2

        coord_string = str(c1) + ',' + str(c2) + ',' + str(w) + ',' + str(h)
        return coord_string


    def correct_lines(self):
        i = 1
        for pagexml_file in self.pagexml_files:
            pagexml_tree = etree.parse(f'{self.pagexml_dir}/{pagexml_file}')
                
            folio = self.tei_tree.xpath(f'(//tei:pb[not(ancestor::tei:expan)])[{i}]', namespaces = {'tei':'http://www.tei-c.org/ns/1.0'})[0].attrib['n']
                

            print(f"==================  {i, folio, pagexml_file}  =========================")            

            
            try:
            
                # get column 1 in TEI
                cb_a = self.tei_tree.xpath(f'.//tei:lb[preceding::tei:pb[not(ancestor::tei:expan)][{i}] and count(preceding::tei:cb[@n="b"][not(ancestor::tei:expan)]) = {i-1} and not(ancestor::tei:expan) and not(ancestor::tei:note[@type="inscription"])]', namespaces = {'tei':'http://www.tei-c.org/ns/1.0'})
                for k in cb_a:
                    if 'n' not in k.attrib:
                        print(etree.tostring(k))
                # get column 1 in PageXML
                column_1 = pagexml_tree.xpath('//ns0:TextRegion[contains(@custom,"type:column_1")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
                lines_column_1 = column_1.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                print(f"Spalte a: {len(cb_a), len(lines_column_1)}")

                # loop through cb_a and lines_column_1 and print the coords
                for k,y in zip(cb_a,lines_column_1):
                    coords = y.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
                    coord_string = self.coords_text_region(coords)
                    #try:
                        #print(k.attrib['n'], k.attrib['facs'] + ";" + y.attrib['custom'],coord_string) 
                    #except:
                        #print(k.attrib,y.attrib['custom'],coord_string)
                        
                    k.set('facs',coord_string)
    
            except Exception as e:
                print(e)

            try:
    
                # get column b in TEI
                cb_b = self.tei_tree.xpath(f'.//tei:lb[count(preceding::tei:cb[@n="b"][not(ancestor::tei:expan)]) = {i} and count(preceding::tei:cb[@n="a"][not(ancestor::tei:expan)]) = {i} and not(ancestor::tei:expan) and not(ancestor::tei:note[@type="inscription"])]', namespaces = {'tei':'http://www.tei-c.org/ns/1.0'})
                column_2 = pagexml_tree.xpath('//ns0:TextRegion[contains(@custom,"type:column_2")]', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
                lines_column_2 = column_2.xpath('.//ns0:TextLine', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
                print(f"Spalte b: {len(cb_b), len(lines_column_2)}")
                for k,y in zip(cb_b,lines_column_2):
                    coords = y.xpath('./ns0:Coords/@points', namespaces = {'ns0':'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0]
                    coord_string = self.coords_text_region(coords)
                    #try:
                        #print(k.attrib['n'], k.attrib['facs'] + ";" + y.attrib['custom'],coord_string) 
                    #except:
                        #print(k.attrib,y.attrib['custom'],coord_string)
                        
                    k.set('facs',coord_string)
            except Exception as e:
                print(e)
    
    
    
            i += 1

        
    def correct_other_elements(self,xpath):
        print(xpath)
        elements = self.tei_tree.xpath(xpath, namespaces = {'tei':'http://www.tei-c.org/ns/1.0'})
        for element in elements:
            coords = element.attrib['facs']
            coords_int = coords.split(',')
            coords_string = ','.join([str(int(int(x) * self.scale_factor)) for x in coords_int])
            element.set('facs',coords_string)
            print(coords_string)

    def write_file(self):
        self.tei_tree.write(self.file_out, pretty_print=True)


# use the class
file_in = os.path.join(os.getcwd(), 'coords','bamberg-sb-c-6-20.xml') 
file_out = os.path.join(os.getcwd(), 'coords','bamberg-sb-c-6-20_new.xml')
path_to_pagexml = os.path.join(os.getcwd(), 'coords','20')
tei_corrector = TeiCorrector(file_in, path_to_pagexml,file_out)
#tei_corrector.correct_lines()
tei_corrector.correct_other_elements('//tei:label')
tei_corrector.correct_other_elements('//tei:cb')
tei_corrector.correct_other_elements('//tei:fw')
tei_corrector.correct_other_elements('//tei:note[@type="inscription"]')
tei_corrector.write_file()
