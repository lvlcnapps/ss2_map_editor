f = open(f'default_name.txt', 'r')

load_it = []

while (True):
    str = f.readline()
    if (str == "END"):
        break
    if (str.startswith("WALL")):
        new_poly = []
        in_out = f.readline()
        if (in_out == "    OUTER\n"):
            new_poly.append(1)
        else:
            new_poly.append(0)
        while (True):
            str = f.readline()
            if (str == "END\n"):
                break
            if (str.startswith("    POINT")):
                kom = str.split()
                new_poly.append(float(kom[1]))
                new_poly.append(float(kom[2]))
        load_it.append(new_poly.copy())

print(load_it)