import os
import xmltodict
import datetime
import requests
from lxml import etree as et
from io import StringIO, BytesIO
from dotenv import dotenv_values
import modules.mp_api as mp_api

config = dotenv_values(".env") 
DATA_path = config['DATA_FOLDER']
METADATA_path = config['METADATA_FOLDER']
SIP_path = config['SIP_FOLDER']
LIDO_SOURCE = config['LIDO_SOURCE']
if "Production" in config['CONF_MP']:
    MP_URL = config['MP_PROD_URL'] 
    MP_PASSI = config['MP_PROD_PASS']
    MP_ENV = 'MuseumPlus PRODUCTION ENVIRONMENT'
else:
    MP_URL = config['MP_TEST_URL'] 
    MP_PASSI = config['MP_TEST_PASS']
    MP_ENV = 'MuseumPlus TESTING ENVIRONMENT'
MP_PASS = tuple(MP_PASSI.split(","))


def read_lido_xml():
    try:
        files = os.listdir(METADATA_path)
        for file in files:
            if "lido_description.xml" in file:
                filepath = METADATA_path + file
                lidofile = open(filepath, "r")
                xml_obj = xmltodict.parse(lidofile.read())
                mp_name = xml_obj['lido:lidoWrap']['lido:lido']['lido:descriptiveMetadata']['lido:objectIdentificationWrap']['lido:titleWrap']['lido:titleSet']['lido:appellationValue']['#text']
                recordWrap = xml_obj['lido:lidoWrap']['lido:lido']['lido:administrativeMetadata']['lido:recordWrap']
                mp_inv = xml_obj['lido:lidoWrap']['lido:lido']['lido:lidoRecID']['#text']
                mp_id = recordWrap['lido:recordID']['#text']
                if recordWrap['lido:recordInfoSet']['lido:recordMetadataDate'] == None:
                    mp_created = datetime.datetime.now().isoformat()
                else:
                    CreatedDate = recordWrap['lido:recordInfoSet']['lido:recordMetadataDate']
                    CreatedDateISO = CreatedDate.replace(" ", "T")
                    mp_created = CreatedDateISO
                lidofile.close()
    except:
        mp_inv = ""
        mp_id = ""
        mp_name = ""
        mp_created = ""
    if not os.path.exists(METADATA_path + "lido_description.xml"):
        mp_inv = ""
        mp_id = ""
        mp_name = ""
        mp_created = ""
    return mp_inv, mp_id, mp_name, mp_created

def read_mets_lido_xml():
    try:
        files = os.listdir(SIP_path)
        for file in files:
            if "mets.xml" in file:
                filepath = SIP_path + file
                metsfile = open(filepath, "r")
                xml_obj = xmltodict.parse(metsfile.read())
                lido_wrap = xml_obj['mets:mets']['mets:dmdSec']['mets:mdWrap']['mets:xmlData']['lido:lidoWrap']
                lido_name = lido_wrap['lido:lido']['lido:descriptiveMetadata']['lido:objectIdentificationWrap']['lido:titleWrap']['lido:titleSet']['lido:appellationValue']['#text']
                lido_inv = lido_wrap['lido:lido']['lido:lidoRecID']['#text']
                recordWrap = lido_wrap['lido:lido']['lido:administrativeMetadata']['lido:recordWrap']
                lido_id = recordWrap['lido:recordID']['#text']
                if recordWrap['lido:recordInfoSet']['lido:recordMetadataDate'] == None:
                    lido_created = datetime.datetime.now().isoformat()
                else:
                    CreatedDate = recordWrap['lido:recordInfoSet']['lido:recordMetadataDate']
                    CreatedDateISO = CreatedDate.replace(" ", "T")
                    lido_created = CreatedDateISO
                metsfile.close()
    except:
        lido_inv = ""
        lido_id = ""
        lido_name = ""
        lido_created = ""
    if not os.path.exists(SIP_path + "mets.xml"):
        lido_inv = ""
        lido_id = ""
        lido_name = ""
        lido_created = ""
    return lido_inv, lido_id, lido_name, lido_created

def save_object_by_id(object_id):
    thumb_stat = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    try:
        mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
        input = BytesIO(mp_response.content)
        xml = et.parse(input)
        ###
        file = open(DATA_path+"MP_obj_id_"+object_id+".xml", "w")
        byte_string = et.tostring(xml)
        regular_string = byte_string.decode('utf-8')
        file.write(regular_string)
        file.close()
        ###
        message = ""
    except Exception as e: 
        message = str(e)
    return message

def get_object_by_id(object_id):
    thumb_status = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    try:
        mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
        input = BytesIO(mp_response.content)
        xml_data ={}
        xml_obj = xmltodict.parse(input)
        xml_data = mp_api.parse_xml_object(xml_obj)
        if len(xml_data["thumbnail"]) > 0:
            thumb_status = True
    except:
        pass
    return xml_data, thumb_status

def load_attachment(object_id):
    ria = mp_api.load_attachment_by_id(object_id, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    return input

def get_object_by_number(object_inv):
    ria = mp_api.get_objects_by_number(object_inv, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    try:
        tree = et.parse(input)
    except:
        totalSize="0"
        mylist=[["1","Error:"],["2","MuseumPlus API interface:"],["3","503 Service Temporarily Unavailable"]]
        xml=""
        return totalSize, mylist, xml
    mylist = []
    totalSize="0"
    xml=""
    ns_mod = {'ns':'http://www.zetcom.com/ria/ws/module'}
    ###############################################
    def get_values(element):
        name = element.attrib['name']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value:
            value = ['']
        list = [name, value[0]]
        return list
    ###############################################
    def get_thumbnail(element):
        name = "thumbnail=" + element.attrib['size']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value:
            value = ['']
        list = [name, value[0]]
        return list
    ###############################################
    for element in tree.iter():
        try:
            totalSize = element.attrib['totalSize']
        except:
            pass
        try:
            name = element.attrib['name']
            list = get_values(element)
            mylist.append(list)
        except:
            pass
        try:
            name = element.attrib['size']
            list = get_thumbnail(element)
            mylist.append(list)
        except:
            pass
    output = et.tostring(tree, pretty_print=True, encoding='utf8') # For testing
    return totalSize, mylist, output

def get_object_by_title(title):
    ria = mp_api.get_objects_by_title(title, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    try:
        tree = et.parse(input)
    except:
        totalSize="0"
        mylist=[["1","Error:"],["2","MuseumPlus API interface:"],["3","503 Service Temporarily Unavailable"]]
        xml=""
        return totalSize, mylist, xml
    mylist = []
    totalSize="0"
    xml=""
    ns_mod = {'ns':'http://www.zetcom.com/ria/ws/module'}
    ###############################################
    def get_values(element):
        name = element.attrib['name']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value:
            value = ['']
        list = [name, value[0]]
        return list
    ###############################################
    def get_thumbnail(element):
        name = "thumbnail=" + element.attrib['size']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value:
            value = ['']
        list = [name, value[0]]
        return list
    ###############################################
    for element in tree.iter():
        try:
            totalSize = element.attrib['totalSize']
        except:
            pass
        try:
            name = element.attrib['name']
            list = get_values(element)
            mylist.append(list)
        except:
            pass
        try:
            name = element.attrib['size']
            list = get_thumbnail(element)
            mylist.append(list)
        except:
            pass
    output = et.tostring(tree, pretty_print=True, encoding='utf8') # For testing
    return totalSize, mylist, output

def create_lido_xml(object_id):
    #session.back_link_id = request.env.http_referer
    thumb_stat = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    xml_data ={}
    xml_obj = xmltodict.parse(input)
    xml_data = mp_api.parse_xml_object(xml_obj)
    ###
    output = mp_api.parse_lido_xml(et, xml_data, LIDO_SOURCE)

    file = open(METADATA_path+"lido_description.xml", "w")
    regular_string = output.decode('utf-8')
    file.write(str(regular_string))
    file.close()
    ###
    message = ""
    return message



##############################
### ANOTHER WAY TO DO THIS ###
##############################
def get_object_by_id_dev(object_id):
    thumb_stat = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    ###############################################
    xml_parse = et.parse(input)
    xml_parsed = et.tostring(xml_parse, encoding="unicode", pretty_print=True)
    tree = xml_parse
    mydict = {}
    ns_mod = {'ns':'http://www.zetcom.com/ria/ws/module'}
    ###>>>
    def get_values(element):
        name = element.attrib['name']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value: 
            value = ['']
        list = [name, value[0]]
        return list
    ###>>>
    for element in tree.xpath('//ns:moduleItem/ns:systemField', namespaces = ns_mod):
        list = get_values(element)
        mydict[list[0]] = list[1]
    for element in tree.xpath('//ns:moduleItem/ns:dataField', namespaces = ns_mod):
        list = get_values(element)
        mydict[list[0]] = list[1]
    for element in tree.xpath('//ns:moduleItem/ns:virtualField', namespaces = ns_mod):
        list = get_values(element)
        mydict[list[0]] = list[1]
    for element in tree.xpath('//ns:moduleItem/ns:thumbnails/ns:thumbnail/ns:value/text()', namespaces = ns_mod):
        list = ["thumbnail", element]
        thumbnail = element
        mydict[list[0]] = list[1]
        thumb_stat = True
    ###############################################
    xml_data ={}
    xml_obj = xmltodict.parse(input)
    xml_data = mp_api.parse_xml_object(xml_obj)
    ###############################################
    return xml_parsed, mydict, thumb_stat, xml_data

