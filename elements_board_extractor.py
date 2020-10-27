from sudokuextract.extract import extract_sudoku, load_image, predictions_to_suduko_string
import argparse
import io
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

class Extract:
    def extract_sudoku(imagePath):
        fd = urlopen(imagePath)
        imagePath = io.BytesIO(fd.read())
        img = load_image(imagePath)
        predictions, sudoku_box_images, whole_sudoku_image = extract_sudoku(img)
        result = predictions_to_suduko_string(predictions)
        print(result)

parser = argparse.ArgumentParser()
parser.add_argument("--pathImage", help="Caminho da imagem a ser solucionada")
args = parser.parse_args()
if(args.pathImage):
    Extract.extract_sudoku(args.pathImage)