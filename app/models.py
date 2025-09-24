import enum

class AlgorithmEnum(str, enum.Enum):
    YOLO = "YOLO"
    ResNet = "ResNet"
    EfficientNet = "EfficientNet"
    DenseNet = "DenseNet"
    MaskRCNN = "Mask R-CNN"
    DeepLab = "DeepLab"
    ViT = "ViT / Swin Transformer"
    Hybrid = "Hybrid CNN-Transformer"
    ImageNet = "ImageNet"
    UNet = "U-Net"

