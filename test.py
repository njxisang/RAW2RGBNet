import argparse
import os
from importlib import import_module

from PIL import Image
import numpy as np
import torch
from torch import nn, optim
from torchvision import transforms
from tqdm import tqdm
import torchvision.transforms.functional as F
from skimage.io import imsave

import utils

parser = argparse.ArgumentParser(description="Test Script")
parser.add_argument(
    "--model",
    required=True,
    type=str,
    help="name of model for this training"
)
parser.add_argument("--checkpoint", type=str, required=True, help="path to load model checkpoint")
parser.add_argument("--output", type=str, required=True, help="path to save output images")
parser.add_argument("--data", type=str, required=True, help="path to load data images")

opt = parser.parse_args()
print(opt)

if not os.path.exists(opt.output):
    os.makedirs(opt.output)

model = import_module('models.' + opt.model.lower()).make_model(opt)


def infer(im, model, path):
    model.load_state_dict(torch.load(path)['state_dict_model'])
    model = model.cuda()
    model = model.eval()
    transform = transforms.Compose([
        transforms.ToTensor()
    ])
    im_augs = [
        transform(im),
        transform(F.hflip(im)),
        transform(F.vflip(im)),
        transform(F.hflip(F.vflip(im)))
    ]
    im_augs = torch.stack(im_augs)
    im_augs = im_augs.cuda()

    with torch.no_grad():
        output_augs = model(im_augs)
    output_augs = np.transpose(output_augs.cpu().numpy(), (0, 2, 3, 1))
    output_augs = [
        output_augs[0],
        np.fliplr(output_augs[1]),
        np.flipud(output_augs[2]),
        np.fliplr(np.flipud(output_augs[3]))
    ]
    return np.mean(output_augs, axis=0)


images = utils.load_all_image(opt.data)
images.sort()

for im_path in tqdm(images):
    filename = im_path.split('/')[-1]
    img = Image.open(im_path)
    # output = infer(img)
    c1 = '/data1/kangfu/Checkpoints/RAW2RGB/_mix_ednet_light_increase_32_8_10_128/11.pth'
    c2 = '/data1/kangfu/Checkpoints/RAW2RGB/_mix_ednet_light_increase_32_8_12_128/42.pth'
    c3 = '/data1/kangfu/Checkpoints/RAW2RGB/_mix_ednet_light_increase_32_8_12_128/43.pth'
    output_aug = [infer(img, model, c1),
                  # infer(img, model, c2),
                  # infer(img, model, c3)
                  ]
    output_aug = np.round(np.mean(output_aug, axis=0) * 255.).astype(np.uint8)
    output_aug = np.clip(output_aug, 0, 255)
    imsave(os.path.join(opt.output, filename), output_aug)