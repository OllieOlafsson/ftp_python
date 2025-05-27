import sys
file_location = sys.argv[1]

formats = {
        "jpg" : [b'\xff\xd8\xff\xe0\x00\x10JFIF', b'\xff\xd8\xff\xe1\x14\x0cExif'],
        "gif" : [b'GIF89a']
        }
#for form, typ in formats.items():
#    for i in typ:
#        print(i)


with open(file_location, 'rb') as file:
    data = file.read(10)
    print(data)
    print(F"reading metadata: {data}")
    for form, typ in formats.items():
        print(type(typ))
        if form == "gif":
            for each in typ:
                if each == data[:6]:
                    print(f"Found format {form}")
        else:
            if form == "jpg":
                for each in typ:
                    print(each)
                    if each == data[:10]:
                        print(f"Found format {form}")


