def finder_drob(n):
    liste = n.split('/')
    n1 = int(liste[0])
    n2 = int(liste[1])
    liste = []
    liste.append(n1//n2)
    while True:
        if n1%n2 == 0:
            break
        else:
            n3 = n2
            n2 = n1%n2
            n1 = n3
            liste.append(n1//n2)
    liste = map(str,liste)
    liste = " ".join(liste)

    return liste

s = input()
print(finder_drob(s))