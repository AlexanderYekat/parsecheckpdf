import PyPDF2
# Для анализа структуры PDF и извлечения текста
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# Для извлечения текста из таблиц в PDF
import pdfplumber
# Для извлечения изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# Для выполнения OCR, чтобы извлекать тексты из изображений 
import pytesseract 
# Для удаления дополнительно созданных файлов
import os
#from pypdf import PdfReader

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Создаём функцию для вырезания элементов изображений из PDF
def crop_image(element, pageObj):
    # Получаем координаты для вырезания изображения из PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    # Обрезаем страницу по координатам (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Сохраняем обрезанную страницу в новый PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Сохраняем обрезанный PDF в новый файл
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)        

# Создаём функцию для преобразования PDF в изображения
def convert_to_images(input_file,):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")

# Создаём функцию для считывания текста из изображений
def image_to_text(image_path):
    # Считываем изображение
    img = Image.open(image_path)
    # Извлекаем текст из изображения
    text = pytesseract.image_to_string(img)
    return text

print("fdfdfdfd")
#reader = PyPDF2.PdfReader("test3.pdf")
reader = PyPDF2.PdfReader("marky.pdf")
page = reader.pages[0]
print(page.extract_text())
meta = reader.metadata
#print('author: %s'%meta.author)
#print('title: %s'%meta.title)
#print('creator: %s'%meta.creator)
#print('subject: %s'%meta.subject)

pdf_path =  "marky.pdf"
for pagenum, page2 in enumerate(extract_pages(pdf_path)):
    for element in page2:
# Проверяем, является ли элемент текстовым
        if isinstance(element, LTChar):
            print("LTChar")
            print(element.get_text())        
            pass
        if isinstance(element, LTTextContainer):
            print("LTTextContainer")
            # Функция для извлечения текста из текстового блока
            pass
            # Функция для извлечения формата текста
            pass

        # Проверка элементов на наличие изображений
        if isinstance(element, LTFigure):
            print("LTFigure")
            crop_image(element, page)
            #convert_to_images('cropped_image.pdf')
            #image_text = image_to_text('PDF_image.png')
            #print(image_text)
            # Функция для преобразования PDF в изображение
            pass
            # Функция для извлечения текста при помощи OCR
            pass

        # Проверка элементов на наличие таблиц
        if isinstance(element, LTRect):
            print("LTRect")
            # Функция для извлечения таблицы
            pass
            # Функция для преобразования содержимого таблицы в строку
            pass    
print("***************************")
for element in page:
    print(element)
    if isinstance(element, LTChar):
        print("LTChar")
        print(element.get_text())
    if isinstance(element, LTTextContainer):
        print("LTTextContainer")
        print(element.get_text())
    if isinstance(element, LTFigure):
        print("LTFigure")
        print(element.name)
    if isinstance(element, LTRect):
        print("LTRect")
        print(element.width)

count = 0
for image_file_object in page.images:
    print(str(count) + image_file_object.name)
    with open(str(count) + image_file_object.name, "wb") as fp:
        fp.write(image_file_object.data)
        count += 1