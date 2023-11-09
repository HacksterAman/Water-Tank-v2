from io import BytesIO
from PIL import Image

path_to_image = input('Location of Image: ')
x = int(input('Width of Image: '))
y = int(input('Hight of Image: '))

im = Image.open(path_to_image).convert('1')
im_resize = im.resize((x,y))
buf = BytesIO()
im_resize.save(buf, 'ppm')
byte_im = buf.getvalue()
temp = len(str(x) + ' ' + str(y)) + 4
print(byte_im[temp::])
