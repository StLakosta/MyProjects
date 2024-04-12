from PIL import Image, ImageDraw, ImageFont


async def create_sticker_from_picture(res_rand):
    img = Image.open(res_rand)
    width, height = img.size

    while width < 512 or height < 512:
        width = width * 2
        height = height * 2

    new_img = img.resize(size=(width, height))
    new_img.thumbnail(size=(512, 512))
    new_img.save(res_rand)

    img.close()
    return res_rand
