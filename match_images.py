import cv2
import pathlib
import numpy as np
import re
import imutils
from configparser import ConfigParser


class MatchMaker:
    config_path = pathlib.Path('config.ini')
    config = ConfigParser()

    x_offset = None
    y_offset = None
    rotation = None
    scale = None
    matched = False
    reg_temp = re.compile(r"(?:RGB|IR)_(\d*_\d*_\d*_\d*)")
    win = cv2.namedWindow("Preview", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    def __init__(self, ir_images):
        self.config.read('config.ini')
        self._sync_config()

        self.ir_images = {}
        self._scan_thermal_images(ir_images)

    def match(self, rgb_image: pathlib.Path, save_path=None, set_match=True):
        ir_img = self._find_match(rgb_image)
        if not ir_img:
            return

        rgb = cv2.imread(str(rgb_image), 1)
        ir = cv2.imread(ir_img, 0)

        if set_match:
            img = self._overlay_images(rgb, ir, viz=True)
            while not self._adjust_control(img):
                img = self._overlay_images(rgb, ir, viz=True)

        if not save_path:
            return

        new_img = self._overlay_images(rgb, ir, viz=False)
        new_file = save_path / rgb_image.name
        cv2.imwrite(str(new_file), new_img)

    def _scan_thermal_images(self, path):
        path = pathlib.Path(path)
        for p in path.glob('*.png'):
            res = self.reg_temp.match(p.stem)
            if not res:
                continue
            cap_time = res.groups()[0]
            self.ir_images[cap_time] = str(p)

            print(p, " > ", cap_time)

    def _find_match(self, rgb_image):
        res = self.reg_temp.match(rgb_image.stem)
        if not res:
            return
        cap_time = res.groups()[0]

        ir_img = self.ir_images.get(cap_time, None)
        if not ir_img:
            print("No matching IR image . . .")
            return

        print(rgb_image, " < MATCHED >", ir_img)
        return ir_img

    def _overlay_images(self, rgb, thermal, viz=False):
        if viz:
            thermal = self._as_heatmap(thermal)
            rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            rgb = np.stack([rgb, rgb, rgb], axis=2)
        else:
            thermal = cv2.cvtColor(thermal, cv2.COLOR_GRAY2BGR)
            thermal[:, :, :2] = 0

        resized = imutils.resize(thermal, height=thermal.shape[0]+self.scale)
        rt = imutils.rotate_bound(resized, self.rotation)

        border_t = 500
        xof = self.x_offset + border_t
        yof = self.y_offset + border_t

        overlay = cv2.copyMakeBorder(np.zeros_like(rgb), border_t, border_t, border_t, border_t, cv2.BORDER_CONSTANT)
        overlay[:, :, 1] = 255

        overlay[yof:yof + rt.shape[0], xof:xof + rt.shape[1], :] = rt

        if viz:
            overlay = cv2.addWeighted(overlay[border_t:-border_t, border_t:-border_t], .5, rgb, 1, 0.0)

        return overlay

    @classmethod
    def _adjust_control(cls, img):
        cv2.imshow('Preview', img)
        cv2.resizeWindow("Preview", np.array(img.shape[:2]) // 2)
        k = cv2.waitKey(0)

        if k == ord('t'):
            cls._sync_config()
            return True
        if k == ord('r'):
            return True
        if k == ord('a'):
            cls.x_offset -= 1
        if k == ord('d'):
            cls.x_offset += 1
        if k == ord('w'):
            cls.y_offset -= 1
        if k == ord('s'):
            cls.y_offset += 1
        if k == ord('q'):
            cls.rotation -= 1
        if k == ord('e'):
            cls.rotation += 1
        if k == ord('z'):
            cls.scale -= 1
        if k == ord('x'):
            cls.scale += 1

        print("X>{}\tY:{}\nR:{}\nS:{}".format(cls.x_offset, cls.y_offset, cls.rotation, cls.scale))
        return False

    @classmethod
    def _sync_config(cls):
        transforms = cls.config['transforms']

        if cls.x_offset:
            transforms['x_offset'] = str(cls.x_offset)
        else:
            cls.x_offset = int(transforms['x_offset'])

        if cls.y_offset:
            transforms['y_offset'] = str(cls.y_offset)
        else:
            cls.y_offset = int(transforms['y_offset'])

        if cls.rotation:
            transforms['rotation'] = str(cls.rotation)
        else:
            cls.rotation = int(transforms['rotation'])

        if cls.scale:
            transforms['scale'] = str(cls.scale)
        else:
            cls.scale = int(transforms['scale'])

        with open(cls.config_path, 'w') as configfile:
            cls.config.write(configfile)

    @staticmethod
    def _as_heatmap(img):
        # Color-maps https://docs.opencv.org/4.x/d3/d50/group__imgproc__colormap.html#ga9a805d8262bcbe273f16be9ea2055a65
        return cv2.applyColorMap(cv2.equalizeHist(img), cv2.COLORMAP_PLASMA)
