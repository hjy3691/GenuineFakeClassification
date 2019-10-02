from PIL import Image

img = Image.open('/home/lgc/image/testData/fake1.png')
area = (140, 140, 200, 200)
cropped_img = img.crop(area)
#[[489, 479], [615, 476], [616, 495], [490, 498]]]}}

cropped_img.show()
