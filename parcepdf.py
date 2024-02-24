import PyPDF2
# Для анализа структуры PDF и извлечения текста
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# Для извлечения текста из таблиц в PDF
import pdfplumber
# Для извлечения изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# Для удаления дополнительно созданных файлов
import os
from enum import Enum
import csv
#from pypdf import PdfReader

class ParseState(Enum):
    Header = 1
    Item = 2
    Total = 3
    Footer = 4

def pdftojson(pdf_path):
    textofcheck = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            currStr = page.extract_text()
            textofcheck = textofcheck + "\n"+currStr
    return textofcheck

directory = './inpdf/'
checksfile = open("checks_header.csv", mode="w", encoding='utf-8')
headernamesofchecks = ["fd", "fp", "type", "kassir", "summ", "nal", "beznal"]
csv_writer_of_checks = csv.DictWriter(checksfile, delimiter = ";", lineterminator="\r", fieldnames=headernamesofchecks)
csv_writer_of_checks.writeheader()

postiotnsfile = open("checks_poss.csv", mode="w", encoding='utf-8')
headernamespostiotns = ["fd", "name", "quant", "price", "nds", "psr", "ppr", "mark"]
csv_writer_pos = csv.DictWriter(postiotnsfile, delimiter = ";", lineterminator="\r", fieldnames=headernamespostiotns)
csv_writer_pos.writeheader()

currNumOfFile = 0
listoffilesname = os.listdir(directory)
amountoffiles = len(listoffilesname)
for filename in listoffilesname:
    if currNumOfFile % 100 == 0:
        print("запись на диск...")
        checksfile.flush()
        postiotnsfile.flush()
    currNumOfFile = currNumOfFile + 1
    f = os.path.join(directory, filename)
    print("обработка", currNumOfFile, "из", amountoffiles, "имя файла", f)
    textofcheck = pdftojson(f)
    listofstr = textofcheck.split("\n")
    prevState = ParseState.Header
    stateCurr = ParseState.Header
    stateNew = ParseState.Header
    currHeaderRow = {}
    currPosRow = {}
    rowsAll = []
    currPos = 0
    obrabBeginNewPos = False
    prevWasPPR = False
    prevWasNameKodTovara = False
    prevWasKodTovara = False
    currIsNameKodTovara = False
    currIsKodTovara = False
    currIsPPR = False
    for str in listofstr:
        stateCurr = stateNew
        if len(str) == 0:
            continue
        obrabBeginNewPos = False
        if stateCurr==ParseState.Header:
            if str.find("Кассир") != -1:
                stateNew = ParseState.Item
        elif stateCurr == ParseState.Item:
            if str.find("Итог") != -1:
                stateCurr = ParseState.Total
                stateNew = stateCurr
        elif stateCurr == ParseState.Total:
            if str.find("места расчетов") != -1:
                stateCurr = ParseState.Footer
                stateNew = stateCurr
        if stateCurr == ParseState.Item:
            currIsPPR = False
            currIsNameKodTovara = False
            currIsKodTovara = False            
            if str[:11] == "Код товара:":
                currIsNameKodTovara = True
            if str[:3] == "ППР":
                currIsPPR = True
            if prevWasNameKodTovara:
                currIsKodTovara = True                
            #
            if (prevWasKodTovara or prevWasPPR) and (not(currIsNameKodTovara)):
                #новая позиция                                                     
                obrabBeginNewPos = True
            prevWasPPR = False
            prevWasNameKodTovara = False
            prevWasKodTovara = False
            if currIsNameKodTovara:
                prevWasNameKodTovara = True
            if currIsKodTovara:
               prevWasKodTovara = True 
            if currIsPPR:
                prevWasPPR = True
        #обработка текущего состояния и строки текста для определения типа объекта и его данных
        if stateCurr == ParseState.Header:
            if str[:12] == "КАССОВЫЙ ЧЕК":
                currHeaderRow.clear()
                currHeaderRow.update({"type": "приход"})
                if str.find("ВОЗВРАТ") != -1:
                    currHeaderRow.update({"type": "возврат"})    
            if str.find("Кассир") != -1:
                strkassir = str.split("Кассир")[1].strip()
                currHeaderRow.update({"kassir": strkassir})
            #if str[:4] == "Дата":
            #    sptempr = str.split(" ")
            #    strdata = sptempr[1].strip()
            #    strtime = sptempr[2].strip()
            #    currHeaderRow.update({"date": strdata})
            #    currHeaderRow.update({"time": strtime})
        if prevState == ParseState.Header and stateCurr == ParseState.Item:
            obrabBeginNewPos = True
        if obrabBeginNewPos:
            #обрабатывем конец позиции
            if currPos != 0:
                rowsAll.append(currPosRow.copy())
            #новая позиция    
            currPos=currPos+1
            currPosRow.clear()
            #currPosRow = {"name": str, "pos": currPos}
            currPosRow = {"name": str}
        if stateCurr == ParseState.Item:
            if currIsKodTovara:
                currPosRow.update({"mark": str.strip()})
            if currIsPPR:
                strPPR = str.split("ППР")[1].strip()
                currPosRow.update({"ppr": strPPR})
            if str[:10] == "Количество":
                strquant = str.split("Количество")[1].strip()
                currPosRow.update({"quant": strquant})
            if str[:22] == "Цена с учетом скидок и":
                strprice = str.split("Цена с учетом скидок и")[1].strip()
                currPosRow.update({"price": strprice})
            if str[:3] == "ПСР":
                strPSR = str.split("ПСР")[1].strip()
                currPosRow.update({"psr": strPSR})
            if str[:10] == "Ставка НДС":
                strNDS = str.split("Ставка НДС")[1].strip()
                currPosRow.update({"nds": strNDS})
        if stateCurr == ParseState.Total:
            if str[:4] == "Итог":
                strsumm = str.split("Итог")[1].strip()
                currHeaderRow.update({"summ": strsumm})
            if str[:9] == "Наличными":
                strnal = str.split("Наличными")[1].strip()
                currHeaderRow.update({"nal": strnal})
            if str[:12] == "Безналичными":
                strbeznal = str.split("Безналичными")[1].strip()
                currHeaderRow.update({"beznal": strbeznal})   
        if stateCurr == ParseState.Footer:
            #if prevState!=ParseState.Footer:
            #    print("**********Footer****************")
            #if str[:2] == "ФН":
            #    strfn = str.split("ФН")[1].strip()
            #    currHeaderRow.update({"fn": strfn})
            if str[:2] == "ФД":
                strfd = str.split("ФД")[1].strip()
                currHeaderRow.update({"fd": strfd})
            if str[:3] == "ФПД":
                strfp = str.split("ФПД")[1].strip()
                currHeaderRow.update({"fp": strfp})
            #if str[:3] == "СНО":
            #    strsno = str.split("СНО")[1].strip()
            #    currHeaderRow.update({"sno": strsno})
            #if str[:6] == "РН ККТ":
            #    strrn = str.split("РН ККТ")[1].strip()
            #    currHeaderRow.update({"regnum": strrn})
        prevState = stateCurr
    if currPos != 0:
        rowsAll.append(currPosRow.copy())
    for currRowPos in rowsAll:
        currRowPos["fd"] = currHeaderRow["fd"]
    csv_writer_of_checks.writerow(currHeaderRow)
    csv_writer_pos.writerows(rowsAll)