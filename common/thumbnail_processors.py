from django.conf import settings

def circular_crop_processor(im, circular=False, **kwargs):
    if circular:
        from PIL import Image, ImageOps

        try:
            size = im.size
            mask = Image.open('%s/images/masking/avatar.%dx%d.png' % (settings.STATIC_ROOT, size[0], size[1])).convert('L')

            im = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
            im.putalpha(mask)
        except IOError:
            pass

    return im