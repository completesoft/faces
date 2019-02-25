from PIL import Image, ImageDraw
import os


def foto_combine (main_foto_np, person_foto_path, face_loc):
    main_foto = Image.fromarray(main_foto_np, 'RGB')
    w_main, h_main = main_foto.size

    person = Image.open(person_foto_path)
    top, right, bottom, left = face_loc
    w_person, h_person = person.size

    #top right corner
    x_axis = w_main - w_person
    y_axis = 0

    main_foto.paste(person, (x_axis, y_axis))

    draw = ImageDraw.Draw(main_foto)
    draw.rectangle([left, top, right, bottom], outline="#ff8888")
    del draw

    # main_foto.show()

    return main_foto, os.path.basename(person_foto_path)