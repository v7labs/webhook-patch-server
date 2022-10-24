import json
import cv2
import requests
from typing import Optional
import hashlib
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import shutil

DEFAULT_PATCH_SIZE = (500, 500)

@dataclass
class Bbox():
    xmin: int
    ymin: int
    w: int
    h: int

    @property
    def xmax(self):
        return self.xmin + self.w
    
    @property
    def ymax(self):
        return self.ymin + self.h
    
    def offset_x(self, offset:int):
        self.xmin = self.xmin + offset
        
    def offset_y(self, offset:int):
        self.ymin = self.ymin + offset

def download_file(url: str, file_name: Optional[str] = None):
    if file_name is None:
        split_url = url.split("?")[0]
        image_ext = Path(split_url).suffix
        md5 = hashlib.md5(split_url.encode("utf-8")).hexdigest()
        file_name = f"{md5}{image_ext}"

    path = Path("/tmp/") / file_name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    return str(path)


def bbox_exists(annotation):
    return "bounding_box" in annotation

def is_keypoint(annotation):
    return 'keypoint' in annotation

    
def parse_multibox_string(filename):
    
    parts = filename.split("(")
    parts = parts[1].split("x")
    columns = parts[0]
    rows = parts[1].split(")")[0]
    columns = ".".join(d for d in columns if d.isdigit())
    rows = ".".join(d for d in columns if d.isdigit())

    return (int(columns), int(rows))
    
def is_multi_box(annotation):
    # Check if there is any (<digits>'x'<digits>) string
    filename = annotation['name']
    if not ("x" in filename and "(" in filename and ")" in filename):
        return False
    
    columns, rows = parse_multibox_string(filename)
    
    return columns > 0 and rows > 0    


def extract_multi_box(annotation):
    filename = annotation['name']
    columns, rows = parse_multibox_string(filename)
    bbox = extract_bbox(annotation)
    
    width = int(bbox.w / columns)
    height = int(bbox.h / rows)
    
    bboxes = []
    for c in range(columns):
        for r in range(rows):
            
            xmin = bbox.xmin + (c)*width
            ymin = bbox.ymin + (r)*height
            bboxes.append(Bbox(xmin, ymin, width, height))
    return bboxes


def extract_bbox(annotation):
    bbox = annotation["bounding_box"]
    
    x = round(bbox['x'])
    y = round(bbox['y'])
    w = round(bbox['w'])
    h = round(bbox['h'])
    
    return Bbox(x,y,w,h)

def bbox_from_keypoint(annotation, patch_size=DEFAULT_PATCH_SIZE):
    keypoint = annotation["keypoint"]
    x = round(keypoint['x'])
    y = round(keypoint['y'])
    
    _w = round(patch_size[0] / 2)
    _h = round(patch_size[1] / 2)
    
    bbox = Bbox(x-_w, y-_h, patch_size[0], patch_size[1])
    
    return bbox
    

def move_bbox_if_outside_image(image, bbox):
    
    
    assert (image.shape[0] >= bbox.h), f"bbox is higher ({bbox.h}) than the image ({image.shape[0]})"
    assert (image.shape[1] >= bbox.w), f"bbox is higher ({bbox.w}) than the image ({image.shape[1]})"
    
    # Offset width if needed
    if bbox.xmin < 0:
        bbox.offset_x(-bbox.xmin)
    elif bbox.xmax > image.shape[1]:
        bbox.offset_x(image.shape[1] - bbox.xmax)
    
    # Offset height if needed
    if bbox.ymin < 0:
        bbox.offset_y(-bbox.ymin)
    elif bbox.ymax > image.shape[0]:
        bbox.offset_y(image.shape[0] - bbox.ymax)
    
    return bbox


def generate_patches(image, annotations, default_patch_size=DEFAULT_PATCH_SIZE):
    
    patches = []
    for annotation in annotations:
        
        if not is_patch_annotation(annotation):
            continue        
        
        if bbox_exists(annotation):
            if is_multi_box(annotation):
                bbox = extract_multi_box(annotation)
            else:
                bbox = [extract_bbox(annotation)]
            
        elif is_keypoint(annotation):
            bbox = [bbox_from_keypoint(annotation)]
            
        for b in bbox:
            b = move_bbox_if_outside_image(image, b)
            patch = image[b.ymin: b.ymax, b.xmin: b.xmax]
            patches.append(patch)
    return patches


def save_patches(patches, save_dir, filename):
    save_dir = Path(save_dir)
    filename = Path(filename)
    for i, patch in enumerate(patches):
        save_path = save_dir.joinpath(f"{filename.stem}_{i}.png") #{filename.suffix}")
        cv2.imwrite(str(save_path), patch)

        
def clean_up_files(tmp_folder):
    shutil.rmtree(tmp_folder, ignore_errors=True)
    

def is_patch_annotation(annotation):
    return annotation['name'].__contains__("patch") or annotation['name'].__contains__("crop")


def parse_request(json_request, tmp_folder="tmp", default_patch_size=DEFAULT_PATCH_SIZE):
    tmp_folder = Path(tmp_folder)
    remote_file_name = json_request['files'][0]['filename']
    remote_url = json_request['files'][0]['url']
    
    if not tmp_folder.exists():
        tmp_folder.mkdir(parents=True)
    
    tmp_img_path = download_file(remote_url, remote_file_name)

    image = cv2.imread(str(tmp_img_path))
    assert image is not None
    
    patches = generate_patches(image, json_request['annotations'][0], default_patch_size=default_patch_size)
    save_patches(patches, tmp_folder, remote_file_name)
    
    Path(tmp_img_path).unlink()
    
    return tmp_folder


def clean_up(folder):
     clean_up_files(folder)
        

bbox = Bbox(-10, 16, 4, 10)
test_img = np.zeros((20, 20))
new_bbox = move_bbox_if_outside_image(test_img, bbox)
assert new_bbox.xmin == 0 and new_bbox.ymin == 10 and new_bbox.xmax == 4 and new_bbox.ymax == 20, "Test failed..."