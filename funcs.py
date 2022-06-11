import re
import pdfkit
import os


def get_clean_name(word):
    word = re.sub('[^a-zа-я\d#ё-]', ' ', word, flags=re.IGNORECASE)
    word = word.strip('-')
    return ' '.join(word.split())


def html_to_pdf(html, path):
    config = pdfkit.configuration(wkhtmltopdf='wkhtmltopdf/bin/wkhtmltopdf.exe')
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        {html}
    <body>
    </html>
    """
    my_pdf = open('myfile.html', 'w', encoding='utf-8')
    my_pdf.write(html)
    my_pdf.close()
    pdfkit.from_file('myfile.html', path, configuration=config)
    os.remove('myfile.html')
