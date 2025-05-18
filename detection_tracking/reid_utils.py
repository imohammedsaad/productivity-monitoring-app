import torchreid
import torch
import numpy as np
import cv2

# Load a pre-trained ReID model (do this once)
def load_reid_model():
    model = torchreid.models.build_model(
        name='osnet_x0_25',
        num_classes=1000,
        loss='softmax',
        pretrained=True
    )
    model.eval()
    model.cuda() if torch.cuda.is_available() else model.cpu()
    return model

# Extract feature vector from a person crop
def extract_reid_feature(model, img):
    # img: numpy array (H, W, 3) in BGR
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (128, 256))
    img = img.astype(np.float32) / 255.0
    img = torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0)
    img = img.cuda() if torch.cuda.is_available() else img
    with torch.no_grad():
        feat = model(img)
    return feat.cpu().numpy().flatten()