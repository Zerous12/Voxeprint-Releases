import numpy as np
from PIL import Image, ImageFilter


class ImageAdjustmentPipeline:
    """Pipeline for applying image adjustments (contrast, brightness, saturation, etc.)"""

    @staticmethod
    def apply(image, *, contrast=0, brightness=0, saturation=0,
              sharpness=0, gamma=0, rotation=0, flip_h=False, flip_v=False,
              skip_rotation=False):
        no_rotation = skip_rotation or rotation == 0
        if (contrast == 0 and brightness == 0 and saturation == 0 and
            sharpness == 0 and gamma == 0 and no_rotation and
            not flip_h and not flip_v):
            return image

        if flip_h:
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if flip_v:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        if not skip_rotation and rotation != 0:
            image = image.rotate(-rotation, expand=True, fillcolor=(0, 0, 0, 0))

        img_array = np.array(image)

        if brightness != 0:
            factor = brightness * 2.55
            rgb = img_array[:, :, :3].astype(np.float32)
            rgb = np.clip(rgb + factor, 0, 255)
            img_array[:, :, :3] = rgb.astype(np.uint8)

        if contrast != 0:
            factor = (contrast + 100) / 100.0
            rgb = img_array[:, :, :3].astype(np.float32)
            rgb = np.clip(((rgb - 128) * factor) + 128, 0, 255)
            img_array[:, :, :3] = rgb.astype(np.uint8)

        if saturation != 0:
            rgb = img_array[:, :, :3].astype(np.float32)
            gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
            gray = np.stack([gray] * 3, axis=-1)
            factor = (saturation + 100) / 100.0
            rgb = np.clip(gray + (rgb - gray) * factor, 0, 255)
            img_array[:, :, :3] = rgb.astype(np.uint8)

        if gamma != 0:
            gamma_val = 1.0 + gamma / 100.0
            rgb = img_array[:, :, :3].astype(np.float32) / 255.0
            rgb = np.power(rgb, 1.0 / gamma_val)
            rgb = np.clip(rgb * 255.0, 0, 255)
            img_array[:, :, :3] = rgb.astype(np.uint8)

        if sharpness != 0:
            image = Image.fromarray(img_array, 'RGBA')
            intensity = abs(sharpness) / 50.0
            if sharpness > 0:
                radius = max(1, int(intensity * 3))
                percent = int(intensity * 150)
                image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=0))
            else:
                radius = intensity * 2
                image = image.filter(ImageFilter.GaussianBlur(radius=radius))
            return image

        return Image.fromarray(img_array, 'RGBA')
