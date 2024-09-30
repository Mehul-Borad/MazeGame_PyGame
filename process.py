from PIL import Image
spritefolder = "Sprites/assassin/"
def processplayerimages(s):
    for i in range(1,5):
        dest = spritefolder + f"{s}{i}.png"
        src = spritefolder + "right1.png"
        Image.open(src).save(dest)

processplayerimages("front")
processplayerimages("back")
# processplayerimages("left")