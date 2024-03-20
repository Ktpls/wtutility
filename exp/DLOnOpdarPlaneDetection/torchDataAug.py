
from torch import Tensor
from torchvision.transforms.autoaugment import AutoAugmentPolicy
from utilref import *
import torchvision


class NonAffineTorchAutoAugment(torchvision.transforms.AutoAugment):
    def forward(self, img: torch.Tensor) -> Tensor:
        img = (img * 255).to(dtype=torch.uint8)
        img = super().forward(img)
        img = img.to(dtype=torch.float32) / 255
        return img

    def _get_policies(
        self, policy: AutoAugmentPolicy
    ):
        policies = [
            [("AutoContrast", 0.5, None), ("Equalize", 0.9, None)],
            [("AutoContrast", 0.8, None), ("Solarize", 0.2, 8)],
            [("AutoContrast", 0.9, None), ("Solarize", 0.8, 3)],
            [("Brightness", 0.1, 3), ("Color", 0.7, 0)],
            [("Brightness", 0.9, 6), ("Color", 0.2, 8)],
            [("Color", 0.4, 0), ("Equalize", 0.6, None)],
            [("Color", 0.4, 3), ("Brightness", 0.6, 7)],
            [("Color", 0.6, 4), ("Contrast", 1.0, 8)],
            [("Color", 0.8, 8), ("Solarize", 0.8, 7)],
            [("Color", 0.9, 9), ("Equalize", 0.6, None)],
            [("Contrast", 0.6, 7), ("Sharpness", 0.6, 5)],
            [("Equalize", 0.0, None), ("Equalize", 0.8, None)],
            [("Equalize", 0.2, None), ("AutoContrast", 0.6, None)],
            [("Equalize", 0.2, None), ("Equalize", 0.6, None)],
            [("Equalize", 0.3, None), ("AutoContrast", 0.4, None)],
            [("Equalize", 0.4, None), ("Solarize", 0.2, 4)],
            [("Equalize", 0.6, None), ("Equalize", 0.5, None)],
            [("Equalize", 0.6, None), ("Posterize", 0.4, 6)],
            [("Equalize", 0.6, None), ("Solarize", 0.6, 6)],
            [("Equalize", 0.8, None), ("Equalize", 0.6, None)],
            [("Equalize", 0.8, None), ("Invert", 0.1, None)],
            [("Invert", 0.1, None), ("Contrast", 0.2, 6)],
            [("Invert", 0.6, None), ("Equalize", 1.0, None)],
            [("Invert", 0.9, None), ("AutoContrast", 0.8, None)],
            [("Invert", 0.9, None), ("Equalize", 0.6, None)],
            [("Posterize", 0.6, 7), ("Posterize", 0.6, 6)],
            [("Posterize", 0.8, 5), ("Equalize", 1.0, None)],
            [("Sharpness", 0.3, 9), ("Brightness", 0.7, 9)],
            [("Sharpness", 0.4, 7), ("Invert", 0.6, None)],
            [("Sharpness", 0.8, 1), ("Sharpness", 0.9, 3)],
            [("Solarize", 0.4, 5), ("AutoContrast", 0.9, None)],
            [("Solarize", 0.5, 2), ("Invert", 0.0, None)],
            [("Solarize", 0.6, 3), ("Equalize", 0.6, None)],
            [("Solarize", 0.6, 5), ("AutoContrast", 0.6, None)],
        ]
        policies = [
            [
                s
                for s in p
                if s[0]
                not in ["TranslateX", "TranslateY", "Rotate", "ShearX", "ShearY"]
            ]
            for p in policies
        ]
        policies = [p for p in policies if len(p) >= 2]
        return policies


def affineAugment(m):

    zoom = lambda rate: np.array(
        [[rate, 0, 0], [0, rate, 0], [0, 0, 1]],
        dtype=np.float32,
    )
    shift = lambda x, y: np.array(
        [[1, 0, x], [0, 1, y], [0, 0, 1]],
        dtype=np.float32,
    )
    flip = lambda lr, ud: np.array(
        [[lr, 0, 0], [0, ud, 0], [0, 0, 1]],
        dtype=np.float32,
    )
    rot = lambda the: np.array(
        [[np.cos(the), np.sin(the), 0], [-np.sin(the), np.cos(the), 0], [0, 0, 1]],
        dtype=np.float32,
    )
    identity = lambda: np.array(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        dtype=np.float32,
    )

    h, w, c = m.shape

    theta = np.random.uniform(-np.pi / 2, np.pi / 2)
    zoomrate = np.random.uniform(0.75, 1.25)
    ifflip = np.random.choice([1, -1], size=2, replace=True)
    movvec = np.random.uniform(-0.3, 0.3, size=2) * [w, h]
    m = cv.warpAffine(
        m,
        (
            shift(0.5 * w, 0.5 * h)
            @ shift(*movvec)
            @ flip(*ifflip)
            @ zoom(zoomrate)
            @ rot(theta)
            @ shift(-0.5 * w, -0.5 * h)
        )[0:2, :],
        np.flip(m.shape[0:2]),
        borderMode=cv.BORDER_REPLICATE,
    )
    return m


def noiseAugment(m):
    # rand line
    def draw_random_line(image, n):
        height, width, _ = image.shape
        color = (0, 0, 0)  # Black color
        for l in range(n):
            start_point = (np.random.randint(0, width), np.random.randint(0, height))
            end_point = (np.random.randint(0, width), np.random.randint(0, height))
            cv.line(image, start_point, end_point, color, 1)
        return image

    m = draw_random_line(m, 5)

    def gaussianNoise(src):
        noise = np.random.normal(0, 0.1, src.shape)
        src = np.clip(src + noise, 0, 1, dtype=np.float32)
        return src

    m = gaussianNoise(m)
    return m


f = r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\largeEnoughToRecon\0EJY7WF6W5.png"
m = cv.imread(f)
m = cv.cvtColor(m, cv.COLOR_BGR2RGB).astype(np.float32) / 255

i = 1
pltshape = (7, 7)
fig = plt.figure(figsize=(20, 20))
aa = NonAffineTorchAutoAugment()
while i <= np.prod(pltshape):
    plt.subplot(pltshape[0], pltshape[1], i)
    m_ = np.copy(m)
    m_ = affineAugment(m)
    m_ = noiseAugment(m_)
    m_ = torchvision.transforms.ToTensor()(m_)
    m_ = aa(m_)
    m_=tensorimg2ndarray(m_)
    plt.imshow(m_)
    i += 1
