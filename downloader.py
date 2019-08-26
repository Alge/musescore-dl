#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as bs
import shutil
import tempfile
from pprint import pprint
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from PyPDF2 import PdfFileReader, PdfFileWriter

from PIL import Image

class Downloader:

    def __init__(self, url):
        self.url = url
        self.score_id = url.split("/")[-1]

    def remove_transparency(self, im, bg_colour=(255, 255, 255)):
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            alpha = im.convert('RGBA').split()[-1]
            bg = Image.new("RGBA", im.size, bg_colour + (255,))
            bg.paste(im, mask=alpha)
            return bg

        else:
            return im

    def get_midi(self):

        print("Starting MIDI download")

        response = requests.get(self.url)

        soup = bs(response.text, 'html.parser')
        image_base_url = soup.find('img', attrs={'id':'score_0'})['src']
        midi_url = image_base_url.replace("score_0.svg", "score.mid")
        print(f"Downloading {midi_url}")
        r = requests.get(midi_url, stream=True)
        if r.status_code == 200:
            filename = f"{tempfile.gettempdir()}/{self.score_id}.mid"
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            return filename
        return False

    def get_images(self):

        response = requests.get(self.url)

        soup = bs(response.text, 'html.parser')

        pages = int(soup.find('td', text="Pages").findNext('td').text)

        image_base_url = soup.find('img', attrs={'id':'score_0'})['src']

        if 'score_0.svg' in image_base_url:
            self.image_type = 'svg'
        if 'score_0.png' in image_base_url:
            self.image_type = 'png'

        image_list = []

        for page in range(pages):
            if 'score_0.svg' in image_base_url:
                url = image_base_url.replace('score_0.svg', f"score_{page}.svg")
            if 'score_0.png' in image_base_url:
                url = image_base_url.replace('score_0.png', f"score_{page}.png")

            print(f"Downloading: {url}")
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                filename = f"{tempfile.gettempdir()}/{self.score_id}-{page}.{self.image_type}"
                with open(filename, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

                image_list.append(filename)

        return image_list
        # return list of images
    def generate_pdf_png(self, image_files):
        pil_images = []
        for image in image_files:
            i = Image.open(image)
            i = self.remove_transparency(i)
            i = i.convert("RGB")
            pil_images.append(i)

        filename = f"{tempfile.gettempdir()}/{self.score_id}.pdf"
        pil_images[0].save(
                filename,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=pil_images[1:]
        )
        return filename

    def generate_pdf_svg(self, image_files):
        output = PdfFileWriter()
        tmpdir = tempfile.gettempdir()
        for n, image in enumerate(image_files):
            print(f"rendering page {n}")
            filename = image.split("/")[-1]
            filename = filename.replace(".svg", ".pdf")

            drawing = svg2rlg(image)
            renderPDF.drawToFile(drawing, tmpdir+filename)

            reader = PdfFileReader(open(tmpdir+filename, 'rb'))
            output.addPage(reader.getPage(0))

        print("Rendering output file")
        filename = f"{tmpdir}{self.score_id}.pdf"
        outputStream = open(filename, "wb")
        output.write(outputStream)

        return filename

    def get_pdf(self):
        print("Starting PDF download")
        images = self.get_images()
        if self.image_type == 'png':
            return self.generate_pdf_png(images)
        if self.image_type == 'svg':
            return self.generate_pdf_svg(images)


if __name__ == '__main__':
    url = 'https://musescore.com/user/******/scores/******'
    d = Downloader(url)
    print(d.get_pdf())
