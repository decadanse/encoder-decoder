import os
import sys
import math
import struct
import string
import binascii
import re #for razradnost
import decimal#from decimal import *#Decimal #округление дробных чисел 
#https://docs-python.ru/standart-library/modul-decimal-python/rezhimy-okruglenija-modulja-decimal/
  
from Crypto.Cipher import AES
import codecs


def user_action_choose():
    print("What do you want to do?\n 1 - open file\n 2 - encode file\n 3 - decode file\n 4 - write smth to new file\n")
    try:
        action = int(input(""))
    except ValueError:
        print("smth go wrong")
    return action

def encrypt_decrypt(action):
    x = input("print full name of your file: ")
    original_file = x
    lam, okruglenie, razradnost = user_input()
    name_new_file = input("print the name for your new enc/dec file: ")

    encryptor=Encryptor()
    if action == 2: #encode
        encryptor.file_encrypt(x, lam, okruglenie, razradnost, original_file, name_new_file)
    elif action == 3: #decodencrypt_
        encryptor.file_decrypt(x, lam, okruglenie, razradnost, original_file, name_new_file)

def user_input():
    x = 124 
    lam = 2872
    okruglenie = 'round'
    razradnost = 4
    # try:
    #     lam = int(input("input your lambda: "))
    #     okruglenie = input("input your method okrugleniya for encryption: ")
    #     razradnost = int(input("input your razradnost okrugleniya: "))
    # except ValueError:
    #     print("smth go wrong. exiting")
    #     sys.exit()
    return lam, okruglenie, razradnost


def chunks(x, razradnost): #разделение на части
    n = razradnost
    chunks = [x[i:i+n] for i in range(0, len(x), n)]
    return chunks

def use_okruglenie(f, okruglenie, razradnost):
    #округляet ДРОБНЫЕ числа -> ceil floor trunc 
    D = decimal.Decimal
    zeros = '0'*razradnost

    if okruglenie == 'round': #correct as if
        f = D(f).quantize(D("1."+zeros), decimal.ROUND_HALF_UP)
        #D("0.444").quantize(D("1.00"), decimal.ROUND_HALF_UP)
        # Decimal('0.44')
    elif okruglenie == 'ceil':
        #D("0.4400001").quantize(D("1.00"), decimal.ROUND_CEILING) - example of usage
        # Decimal('0.45')
        f = D(f).quantize(D("1."+zeros), decimal.ROUND_CEILING)
        print("f ceil = ", f)
    elif okruglenie == 'floor':
        f = D(f).quantize(D("1."+zeros), decimal.ROUND_FLOOR)
    elif okruglenie == 'trunc':
        f = D(f).quantize(D("1."+zeros), decimal.ROUND_DOWN)
    else:
        print("wrong input of method okruglenia. exiting")
        sys.exit()

    return f

def enc_key(lam, okruglenie, razradnost):

    x = 124 # any number which I choose
    if (x >= 0) and (x <= lam): 
        key = x/lam
    elif (x > lam) and (x <= 1):
        key = (1-x)/(1-lam)  
    print('key before okruglenie = ', key)
    enc_key = use_okruglenie(key, okruglenie, razradnost)
    key = str(enc_key)
    print('key after okruglenie  = ', key)

    l = len(key)
    if (l%16 or l%24 or l%36) != 0: #AES key must be either 16, 24, or 32 bytes long
        if l > 36:
            key = key[0:36]
        elif l > 16:
            key = key[0:16]
        else:
            print('key length = ', len(key))
            need_leng = 16 - len(key)
            key = key + '0'*need_leng
    print('key modified for correct length = ', key)
    return key

def encrypt(plain_text, iv, key): #AES encryption
    obj = AES.new(key, AES.MODE_CFB, iv)
    enc_text = obj.encrypt(plain_text)
    return enc_text 
def decrypt(enc_text, iv, key): #AES decryption
    obj = AES.new(key, AES.MODE_CFB, iv)
    plain_text = obj.decrypt(enc_text)
    return plain_text 

def encrypt_func(x, lam, okruglenie, razradnost):
    #x = codecs.decode(x, 'UTF-8')#x.decode('UTF-8')
    #разделяем входные данные на равные части, количество символов в 1-й части = razradnost 
    arr = chunks(x, razradnost) 
    print("chunked data for encryption = ", arr)

    iv = "TestMeInitVector"
    key = enc_key(lam, okruglenie, razradnost)# генерация ключа с помощью функции f(x)

    encrypted = b''
    for el in arr:
        encrypted_el = encrypt(el, iv, key)
        encrypted += encrypted_el
    return encrypted


def decrypt_func(x, lam, okruglenie, razradnost):
    #разделяем входные данные на равные части, количество символов в 1-й части = razradnost 
    arr = chunks(x, razradnost)
    print("chunked data for decryption = ", arr)

    iv = "TestMeInitVector" #any str with len = 16 (because of AES)
    key = enc_key(lam, okruglenie, razradnost)# генерация ключа с помощью функции f(x)

    decrypted = b''
    for el in arr:
        decrypted_el = decrypt(el, iv, key)
        decrypted += decrypted_el

    return decrypted
    
class Encryptor():

    def file_encrypt(self, x, lam, okruglenie, razradnost, original_file, encrypted_file):

        with open(original_file, 'rb') as file:
            original = file.read()
            file.close()
            #print("original = ", original)

        encrypted = encrypt_func(original, lam, okruglenie, razradnost)
        #print("encrypted = ", encrypted)
        with open (encrypted_file, 'wb') as file:
            file.write(encrypted)
            file.close()


    def file_decrypt(self, x, lam, okruglenie, razradnost, original_file, decrypted_file):
        
        with open(original_file, 'rb') as file:
            original = file.read()
            file.close()
            #print("original = ", original)

        decrypted = decrypt_func(original, lam, okruglenie, razradnost)
        #print("decrypted = ", decrypted)
        with open(decrypted_file, 'wb') as file:
            file.write(decrypted)
            file.close()

def open_file(): #чтение информации из файла
    file_name = input("input file name: ")
    access_mode = 'r'
    f = open(file_name, access_mode)
    try:
        text = f.readlines()
        print(text)
    finally:
        f.close()
        sys.exit()

def save_file(content): #Запись введенного пользователем в файл
    new_name = input("input new file name: ")
    with open(f'{new_name}', 'w') as text_file:
        text_file.write(content) 
        text_file.close()

if __name__ == '__main__':  

    action = user_action_choose()
    print("action = ", action)
    if action == int(1):
        open_file()
    elif (action == 2) or (action == 3):
        encrypt_decrypt(action)
    elif (action == 4):
        content = input("print what you want to save: ")
        save_file(content)
    else:
        print("wrong input. exiting")
        sys.exit()