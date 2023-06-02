""" Corrects the coordinates of the bounding boxes in the XML file.
"""

from lxml import etree
import os



def calculate_facs(value):

    # If the attribute does not contain a comma, return the original value
    if ',' not in value:
        return value

    values = list(map(int, value.split(',')))

    # If the attribute does not have exactly four values, return original
    if len(values) != 4:
        return value

    # Split the value into x, y, w, h
    x, y, w, h = values

    # Perform the calculations
    x_new = x * 3.6 - 50
    y_new = y * 3.6 + 140
    w_new = w * 3.6
    h_new = h * 3.6 - 160

    # Return the calculated values
    return f"{int(x_new)},{int(y_new)},{int(w_new)},{int(h_new)}"

filename = os.path.join(os.getcwd(),'documents','bamberg-01.xml')
print(filename)
new_file = os.path.join(os.getcwd(),'output','01','bamberg-sb-c-6-01_new_coords.xml')


# Parse the XML
parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(filename, parser)  # Replace 'file.xml' with your xml file path

# Define the namespace
namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Iterate through all the attributes in the XML
for facs in tree.xpath('//tei:*/@facs', namespaces=namespaces):
    facs.getparent().set('facs', calculate_facs(facs))

# Save the result to a new xml file
tree.write('new_file.xml', pretty_print=True, xml_declaration=True, encoding='UTF-8')  # Replace 'new_file.xml' with your desired output file path
