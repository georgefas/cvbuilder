# from pdfminer.converter import TextConverter
# from pdfminer.pdfinterp import PDFPageInterpreter
# from pdfminer.pdfinterp import PDFResourceManager
# from pdfminer.layout import LAParams
# from pdfminer.pdfpage import PDFPage

# import docx2txt
# import io

from numpy import str_
import spacy
from spacy.matcher import Matcher

import pandas as pd
import re
import cv.constants as cs

import nltk 
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


from cv.addresst import get_new_address

import textdistance
# nltk.download('words')
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
#nltk.download('omw-1.4')

nlp = spacy.load('en_core_web_sm')

STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII', 'Bachelor in', 'Mathematics'
        ]

RESERVED_WORDS = [
    'school',
    'college',
    'univers',
    'academy',
    'faculty',
    'institute',
    'faculdades',
    'Schola',
    'schule',
    'lise',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
]

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as fh:
#         # iterate over all pages of PDF document
#         for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
#             # creating a resoure manager
#             resource_manager = PDFResourceManager()
            
#             # create a file handle
#             fake_file_handle = io.StringIO()
            
#             # creating a text converter object
#             converter = TextConverter(
#                                 resource_manager, 
#                                 fake_file_handle, 
#                                 codec='utf-8', 
#                                 laparams=LAParams()
#                         )

#             # creating a page interpreter
#             page_interpreter = PDFPageInterpreter(
#                                 resource_manager, 
#                                 converter
#                             )

#             # process current page
#             page_interpreter.process_page(page)
            
#             # extract text
#             text = fake_file_handle.getvalue()
#             yield text

#             # close open handles
#             converter.close()
#             fake_file_handle.close()

# # calling above function and extracting text
# text = ""
# for page in extract_text_from_pdf('./resume.pdf'):
    
#     text += ' ' + page



# def extract_text_from_doc(doc_path):
#     temp = docx2txt.process(doc_path)
#     text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
#     return ' '.join(text)



def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', [pattern])
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

def extract_address(resume_text):
    return get_new_address(str(resume_text))


def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + str(number)
        else:
            return str(number)

def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return "-"

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)    

    noun_chunks=  nlp_text.noun_chunks

    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # reading the csv file
    data = pd.read_csv("cv/skills.csv") 
    
    # extract values
    skills = list(data.columns.values)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]



# def extract_title(resume_text):
#     titles = open('cv/titles.txt', 'r').readlines()


def extract_education(input_text):
    organizations = []
 
    # first get all the organization names using nltk
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(c[0] for c in chunk.leaves()))
 
    # we search for each bigram and trigram for reserved words
    # (college, university etc...)
    education = set()
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word):
                education.add(org)
 
    return education




def extract_experience(resume_text):
    '''
    Helper function to extract experience from resume text
    :param resume_text: Plain resume text
    :return: list of experience
    '''
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # word tokenization
    word_tokens = nltk.word_tokenize(resume_text)

    # remove stop words and lemmatize
    filtered_sentence = [
            w for w in word_tokens if w not
            in stop_words and wordnet_lemmatizer.lemmatize(w)
            not in stop_words
        ]
    sent = nltk.pos_tag(filtered_sentence)

    # parse regex
    cp = nltk.RegexpParser('P: {<NNP>+}')
    cs = cp.parse(sent)

    # for i in cs.subtrees(filter=lambda x: x.label() == 'P'):
    #     print(i)

    test = []

    for vp in list(
        cs.subtrees(filter=lambda x: x.label() == 'P')
    ):
        test.append(" ".join([
            i[0] for i in vp.leaves()
            if len(vp.leaves()) >= 2])
        )

    # Search the word 'experience' in the chunk and
    # then print out the text after it
    x = [
        x[x.lower().index('experience') + 10:]
        for i, x in enumerate(test)
        if x and 'experience' in x.lower()
    ]
    return x

#resume_text = extract_text_from_doc('./resume_doc2.docx')


# print('Name :' + extract_name(resume_text))
# print("============================================")
# print('Address:'+  extract_address(resume_text))
# print("============================================")
# print("Mobile Number: "+ extract_mobile_number(resume_text))
# print("============================================")
# print('Email:'+  extract_email(resume_text))
# print("============================================")
# print('Skills:'+  str(extract_skills(resume_text)))
# print("============================================")
# print('Education:'+ str(extract_education(resume_text)))
# print("============================================")
# print('Experience:'+ str(extract_experience(resume_text)))
# print("============================================")



def extract_languages(list_items):
    languages_list = [
        "Afrikaans",
        "Arabic",
        "Bengali",
        "Bulgarian",
        "Catalan",
        "Cantonese",
        "Croatian",
        "Czech",
        "Danish",
        "Dutch",
        "Lithuanian",
        "Malay",
        "Malayalam",
        "Panjabi",
        "Tamil",
        "English",
        "Finnish",
        "French",
        "German",
        "Greek",
        "Hebrew",
        "Hindi",
        "Hungarian",
        "Indonesian",
        "Italian",
        "Japanese",
        "Javanese",
        "Korean",
        "Norwegian",
        "Polish",
        "Portuguese",
        "Romanian",
        "Russian",
        "Serbian",
        "Slovak",
        "Slovene",
        "Spanish",
        "Swedish",
        "Telugu",
        "Thai",
        "Turkish",
        "Ukrainian",
        "Vietnamese",
        "Welsh",
        "Sign language",
        "Algerian",
        "Aramaic",
        "Armenian",
        "Berber",
        "Burmese",
        "Bosnian",
        "Brazilian",
        "Bulgarian",
        "Cypriot",
        "Corsica",
        "Creole",
        "Scottish",
        "Egyptian",
        "Esperanto",
        "Estonian",
        "Finn",
        "Flemish",
        "Georgian",
        "Hawaiian",
        "Indonesian",
        "Inuit",
        "Irish",
        "Icelandic",
        "Latin",
        "Mandarin",
        "Nepalese",
        "Sanskrit",
        "Tagalog",
        "Tahitian",
        "Tibetan",
        "Gypsy",
        "Wu",
        "saas sales"
            ]
    presented_languages= []
    
    for item in list_items:
        for language in languages_list:
            if textdistance.hamming.similarity(item, language ) > 4:
                presented_languages.append(item)
              
    
    return presented_languages

def real_skills(extracted_skills, languages):
    new_skills = extracted_skills

    for language in languages:
        if language in new_skills:
            new_skills.remove(language)
    
    return new_skills
    



def get_resume_data(resume_text):
    languages= extract_languages(extract_skills(resume_text))

    extracted_skills = extract_skills(resume_text)

    resume_data = {
        'name': str(extract_name(resume_text)),
        'address': str(extract_address(resume_text)),
        'mobile_number': str(extract_mobile_number(resume_text)) ,
        'email': str(extract_email(resume_text)),
        'skills': real_skills(extracted_skills,languages) ,
        'languages': languages,
        'education': list(extract_education(resume_text)) ,
        'experience': extract_experience(resume_text),
    }
    print(resume_data)
    return resume_data



