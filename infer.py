import os
from pdf2image import convert_from_path
import pdftotext
import pandas as pd
import numpy as np
from colorthief import ColorThief
from PIL import Image
import imagehash
from joblib import load


THRESHOLD = 10

def preprocess_file(folder, file):
    filename = os.path.join(folder, file)
    transcript = {'source': file}
    pages = []
    try:
        images = convert_from_path(filename, output_folder=folder, fmt='png')
        for i, image in enumerate(images):
            pagename = f'{file}_{i+1}.png'
            image.save(os.path.join(folder, pagename), "PNG")
            pages.append(pagename)
    except:
        print(f'bad file image data: {file}')
    transcript['pages'] = pages

    text = ''
    try:
        with open(filename, "rb") as f:
            pdf = pdftotext.PDF(f)
            text = "\n".join(pdf)
    except:
        print(f'bad file text data: {file}')
    transcript['text'] = text
    return transcript


def is_grayscale(palette):
    for pal in palette:
        if (max(pal) - min(pal)) > THRESHOLD:
            return 0
    return 1


def is_landscape(size):
    return 1 if size[1] < size[0] else 0


def hex_string_to_vector(hex_string):
    return [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]


def extract_features(transcript):
    palettes = []
    sizes = []
    hashes = []
    is_landscapes = []
    is_grayscales = []
    for page in transcript.get('pages'):
        page_filename = os.path.join(folder, page)
        color_thief = ColorThief(page_filename)
        palette = color_thief.get_palette(color_count=5)
        flat_palette = [item for sublist in palette for item in sublist]
        palettes.append(flat_palette)
        image = Image.open(page_filename)
        sizes.append(image.size)
        hash = imagehash.average_hash(image)
        flat_hash = hex_string_to_vector(str(hash))
        hashes.append(flat_hash)
        is_landscapes.append(is_landscape(image.size))
        is_grayscales.append(is_grayscale(palette))
    transcript['palettes'] = palettes
    transcript['sizes'] = sizes
    transcript['hashes'] = hashes
    transcript['is_landscape'] = is_landscapes
    transcript['is_grayscale'] = is_grayscales
    return transcript


def vectorize(transcript):
    pages = transcript.get('pages')
    palettes = transcript.get('palettes')
    hashes = transcript.get('hashes')
    is_landscapes = transcript.get('is_landscape')
    is_grayscales = transcript.get('is_grayscale')

    page_names = []
    vectors = []
    for i, page in enumerate(pages):
        page_names.append(page)
        vectors.extend(
            list(hashes[i]) + [is_grayscales[i]] + [is_landscapes[i]] + list(palettes[i])
        )
    X = np.array(vectors)
    X = X.reshape((int(len(vectors)/25), 25))
    return page_names, X


def load_labels(filename):
    with open(filename, 'r') as file:
        return file.readlines()


if __name__ == "__main__":
    folder = 'samples'
    file = 'R11963430-25840119-file0001.pdf'
    transcript = preprocess_file(folder, file)
    transcript = extract_features(transcript)
    print(transcript)
    labels = load_labels('labels.txt')
    labels = [label.strip() for label in labels]

    model = load('transcript_LR.joblib')
    names, vectors = vectorize(transcript)
    print(vectors)
    prob = model.predict_proba(vectors)
    print(prob)

    for i, name in enumerate(names):
        print(f'page: {name}')
        max_value = max(prob[i])
        idx = list(prob[i]).index(max_value)
        print(f'{labels[idx]}: {max_value:02%}')
