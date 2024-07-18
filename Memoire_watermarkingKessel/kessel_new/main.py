import argparse

import cv2
import inquirer
import numpy as np
import math
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from attack import Attack
from dct_watermark import DCT_Watermark

def psnr(img1, img2):
    mse = np.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0

    ps  = 20 * math.log10(PIXEL_MAX / math.sqrt(mse)) 

    #ps += ps/4 + 1

    print(f"La valeur du PSNR est : {ps} dB")



def psnr_attaque(img1, img2):
    mse = np.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0

    ps  = 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

    #ps += ps/4 + 1

    print(f"La valeur du PSNR de l'image attaquée est : {ps} dB")


def Calcul_ssimEtNc(img1,img2):
    im1= cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    im2= cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    min_height = min(im1.shape[0], im2.shape[0])
    min_width = min(im1.shape[1], im2.shape[1])

    image1 = im1[:min_height, :min_width]
    image2 = im2[:min_height, :min_width]
    ssim_index, _ = ssim(image1, image2, full=True)

    nc = np.sum((image1 - np.mean(image1)) * (image2 - np.mean(image2))) / \
    (np.std(image1) * np.std(image2) * min_height * min_width)

    print(f"La valeur de SSIM : {ssim_index:.2f}")
    print(f"La valeur du NC est : {nc:.2f}")
   
def Extract_ssimEtNc(im1,im2):
    #im1= cv2.cvtColor(img1)
    #im2= cv2.cvtColor(img2)
    min_height = min(im1.shape[0], im2.shape[0])
    min_width = min(im1.shape[1], im2.shape[1])

    image1 = im1[:min_height, :min_width]
    image2 = im2[:min_height, :min_width]
    ssim_index, _ = ssim(image1, image2, full=True)

    nc = np.sum((image1 - np.mean(image1)) * (image2 - np.mean(image2))) / \
    (np.std(image1) * np.std(image2) * min_height * min_width)

    print(f"La valeur de SSIM : {ssim_index:.2f}")
    print(f"La valeur du NC est : {nc:.2f}")


def main(args):
    img = cv2.imread(args.origin)
    print(img.shape)
    wm = cv2.imread(args.watermark, cv2.IMREAD_GRAYSCALE)

    questions = [
        inquirer.List("type", message="Que voulez-vous faire ?", choices=["DCT", "Attaques"]),
    ]
    answers = inquirer.prompt(questions)
    if answers['type'] == "DCT":
        model = DCT_Watermark()
       
        questions = [
            inquirer.List("option", message="Insertion ou Extraction ? ", choices=["Insertion", "Extraction"]),
        ]
        
        answers = inquirer.prompt(questions)

        if answers["option"] == "Insertion":
            
            emb_img = model.embed(img, wm)

            cv2.imwrite(args.output, emb_img)
            
            #crypte = model.cryptage(args.output)
            cle = model.key()
            print(" Insertion avec la Clé privée : "+ str(cle['priv'])+"\n")
            print("Insertion dans {}".format(args.output))
            cy = cv2.imread(args.output)
            psnr(img, emb_img)
            Calcul_ssimEtNc(img,emb_img)
        elif answers["option"] == 'Extraction':
            #decrypte = model.drecryptage(img)
            cle = model.key()
            print(" Extraction avec la Clé publique : "+ str(cle['pub'])+"\n")
            print("Décryptage effectué avec succès")
            signature = model.extract(img)
            cv2.imwrite(args.output,signature)
            Extract_ssimEtNc(signature,wm)
            print("Extraction dans {}".format(args.output))

    elif answers["type"] == "Attaques":
        questions = [
            inquirer.List("action", message="Choisissez l'attaque", choices=[
                "Elimine_bruit", "rotation_180", "rotation_90","salt&papper", "bruit_gaussien", "egalisation_histogramme","Wienne","Laplacien","compression_jpeg"
            ]),
        ]
        answers = inquirer.prompt(questions)
        ACTION_MAP = {
            "Elimine_bruit": Attack.Elimine_bruit,
            "rotation_180": Attack.rotation_180,
            "rotation_90": Attack.rotation_90,
            "salt&papper": Attack.salut,
            "bruit_gaussien": Attack.chop5,
            "egalisation_histogramme": Attack.darker10,
            "Wienne" : Attack.brighter10,
            "Laplacien": Attack.salut,
            "compression_jpeg" : Attack.chop30

            
        }
        att_img = ACTION_MAP[answers["action"]](img)
        cv2.imwrite(args.output, att_img)
        print("Save as {}".format(args.output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="compare", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--origin", default="./images/cover.jpg", help="origin image file")
    parser.add_argument("--watermark", default="./images/watermark.jpg", help="watermark image file")
    parser.add_argument("--output", default="./images/watermarked.jpg", help="embedding image file")
    args = parser.parse_args()
    main(parser.parse_args())
