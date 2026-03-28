import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import urllib.request

def fetch_xml(url):
    """Downloads the XML from the provided URL."""
    try:
        response = urllib.request.urlopen(url)
        return response.read()
    except Exception as e:
        print(f"Error fetching the URL: {e}")
        return None

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').strip()

def convert_feed_to_selltoro(xml_data, output_file):
    # Parse from string data instead of a local file
    root = ET.fromstring(xml_data)

    rss = ET.Element('rss', {'xmlns:g': 'http://base.google.com/ns/1.0', 'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'Hobby365'
    ET.SubElement(channel, 'link').text = 'https://hobby365.se'
    ET.SubElement(channel, 'description').text = 'Product feed for Selltoro'

    for product in root.findall('product'):
        item = ET.SubElement(channel, 'item')

        # ID
        article_num = product.find('articleNumber')
        if article_num is not None and article_num.text:
            ET.SubElement(item, 'g:id').text = article_num.text

        # Title
        name = product.find('name/sv')
        if name is not None and name.text:
            ET.SubElement(item, 'g:title').text = name.text

        # Description
        desc = product.find('description/sv')
        if desc is not None and desc.text:
            ET.SubElement(item, 'g:description').text = clean_html(desc.text)

        # URL
        url_node = product.find('url/sv')
        if url_node is not None and url_node.text:
            ET.SubElement(item, 'g:link').text = url_node.text

        # Image
        image = product.find('images/item')
        if image is not None and image.text:
            ET.SubElement(item, 'g:image_link').text = image.text

        # Price
        regular_price = product.find('price/regular/SEK')
        if regular_price is not None and regular_price.text:
            ET.SubElement(item, 'g:price').text = f"{regular_price.text}.00 SEK"

        current_price = product.find('price/current/SEK')
        if current_price is not None and current_price.text and current_price.text != regular_price.text:
            ET.SubElement(item, 'g:sale_price').text = f"{current_price.text}.00 SEK"

        # GTIN
        ean = product.find('ean')
        if ean is not None and ean.text:
            ET.SubElement(item, 'g:gtin').text = ean.text

        # Weight
        weight = product.find('weight')
        if weight is not None and weight.text:
            ET.SubElement(item, 'g:shipping_weight').text = f"{weight.text} g"

        ET.SubElement(item, 'g:condition').text = 'new'

        # Availability
        is_buyable = product.find('isBuyable')
        if is_buyable is not None and is_buyable.text == '1':
            ET.SubElement(item, 'g:availability').text = 'in stock'
        else:
            ET.SubElement(item, 'g:availability').text = 'out of stock'

    xml_str = ET.tostring(rss, 'utf-8')
    parsed_xml = minidom.parseString(xml_str)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(parsed_xml.toprettyxml(indent="  "))

# Configuration
SOURCE_URL = "https://admin.abicart.se/pricefile/144481/google/sv/SEK/SE?format=xml"
OUTPUT_FILENAME = "selltoro_feed.xml"

if __name__ == "__main__":
    print("Fetching data...")
    raw_data = fetch_xml(SOURCE_URL)
    if raw_data:
        print("Converting data...")
        convert_feed_to_selltoro(raw_data, OUTPUT_FILENAME)
        print(f"Successfully created {OUTPUT_FILENAME}")