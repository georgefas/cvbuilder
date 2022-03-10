#from address_extractor import extract_all
from address_parser import Parser

from address import AddressParser, Address


def get_new_address(resume_test):
    ap = AddressParser()
    address = ap.parse_address(str(resume_test))
    address_text =  str(address.house_number)+" "+str(address.apartment)+" "+str(address.street)+" "+str(address.city)+" "+str(address.state)
    
    return address_text