import time
import torch
import torchvision
import timm
# from torch import nn
import torch.nn.functional as F

from torchsummary import summary
from torchvision import transforms
from tqdm import tqdm

import torch.optim as optim
import torch.nn as nn

BATCH_SIZE = 224
EPOCHS = 5
WORKERS = 48
IMG_DIMS = (336, 336)
CLASSES = 10

# MODEL_NAME = 'eva_large_patch14_336.in22k_ft_in22k_in1k'
MODEL_NAME = 'resnet50d'

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize(IMG_DIMS),
])

data = torchvision.datasets.CIFAR10('./',
                                    train=True,
                                    download=True,
                                    transform=transform)
data_loader = torch.utils.data.DataLoader(data,
                                          batch_size=BATCH_SIZE,
                                          shuffle=True,
                                          num_workers=WORKERS)

# model = timm.create_model('eva_giant_patch14_560.m30m_ft_in22k_in1k', pretrained=True)
model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=CLASSES)
# model = timm.create_model('resnet50d', pretrained=True, num_classes=256)

device_ids = [i for i in range(torch.cuda.device_count())]
model = nn.DataParallel(model, device_ids=device_ids)

device = torch.device('cuda')
model = model.to(device)

loss_fn = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

start = time.perf_counter()
for epoch in range(EPOCHS):
    epoch_start_time = time.perf_counter()

    model.train()
    for batch in tqdm(data_loader, total=len(data_loader)):
        features, labels = batch[0].to(device), batch[1].to(device)

        optimizer.zero_grad()

        preds = model(features)
        loss = loss_fn(preds, labels)

        loss.backward()
        optimizer.step()

    epoch_end_time = time.perf_counter()
    print(f"Epoch {epoch+1} Time", epoch_end_time - epoch_start_time)
end = time.perf_counter()
print("Training Took", end - start)

# print("Model Parameters", model.parameters())
# print("Model Summary", summary(model, (3,336,336)))