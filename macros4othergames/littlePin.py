from utilitypack.util_solid import *
from utilitypack.util_np import *
from utilitypack.util_ocv import *
from utilitypack.util_app import *

# 添加Pillow库的导入
from PIL import Image, ImageSequence


class ImgRenderingBase(fullScrHUD.Region):

    def reshapeKeepingRatio(self, img: np.ndarray, wh: np.ndarray):
        whimg = img.shape[:2]
        ratio = np.array(wh) / np.array(whimg)
        ratio = np.min(ratio)
        img = cv.resize(
            img, dsize=None, fx=ratio, fy=ratio, interpolation=cv.INTER_LANCZOS4
        )
        return img

    def __init__(self, file_name, rectltwh: np.ndarray):
        super().__init__(lt=rectltwh[:2])
        self.wh = rectltwh[2:]
        self.file_name = file_name

    @staticmethod
    def of(file_name: str):
        extName = UrlFullResolution.of_file(file_name).extName
        mapping = {
            "gif": RegionGifRendering,
            "png": RegionStaticImgRendering,
            "jpg": RegionStaticImgRendering,
            "jpeg": RegionStaticImgRendering,
            "bmp": RegionStaticImgRendering,
        }
        return mapping.get(extName, RegionStaticImgRendering)


class RegionStaticImgRendering(ImgRenderingBase):
    def __init__(self, file_name, rectx1y1x2y2: np.ndarray):
        super().__init__(file_name=file_name, rectltwh=rectx1y1x2y2)
        img = np.frombuffer(ReadFile(file_name), dtype=np.uint8)
        img = cv.imdecode(img, 1)
        img = self.reshapeKeepingRatio(img, self.wh)
        img = np.maximum(img, 1)
        self.content = img
        self.claim_content_nontransparent()

    def update_content(self):
        pass


class RegionGifRendering(ImgRenderingBase):
    def __init__(self, file_name, rectx1y1x2y2: np.ndarray, frame_rate=10):
        super().__init__(file_name=file_name, rectltwh=rectx1y1x2y2)
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / self.frame_rate
        # 打开GIF文件并初始化帧相关变量
        self.gif = Image.open(file_name)
        self.frame_count = self.gif.n_frames
        self.current_frame_index = 0
        self.last_render_time = None

    def render_current_frame(self, current_time):
        self.gif.seek(self.current_frame_index)
        frame_array = np.array(self.gif.convert("RGB"))
        frame_resized = self.reshapeKeepingRatio(frame_array, self.wh)
        frame_bgr = cv.cvtColor(frame_resized, cv.COLOR_RGB2BGR)
        self.content = frame_bgr
        self.claim_content_nontransparent()
        self.last_render_time = current_time

    def update_content(self):
        current_time = time.time()
        if self.last_render_time is None:
            self.render_current_frame(current_time)
        else:
            elapsed = current_time - self.last_render_time
            if elapsed >= self.frame_interval:
                self.current_frame_index = (
                    self.current_frame_index + int(elapsed / self.frame_interval)
                ) % self.frame_count
                self.render_current_frame(current_time - elapsed % self.frame_interval)


# img = np.random.choice(AllFileIn(r"C:\Users\KITA\Pictures\long"))
img = r"C:\Users\KITA\Downloads\v2-5213a87299cd7e25d1b4327dd1745818_r.gif"
rectltwh = np.array((00, 00, 50, 50))
app = BulletinApp(fps=5)
region = app.hud.addRegion(ImgRenderingBase.of(img)(img, rectltwh))
app.go()
