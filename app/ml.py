import io
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

MODEL_PATH = Path("model/best_model.pth")

CLASS_NAMES = ["I-II", "III", "IV", "V", "VI"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    model = models.resnet18(weights=None)
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    )

    state_dict = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()

    return model


model = load_model()

image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def predict_phototype(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = image_transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_index = torch.max(probabilities, dim=1)

    phototype = CLASS_NAMES[predicted_index.item()]

    return {
        "phototype": phototype,
        "confidence": round(confidence.item(), 4)
    }