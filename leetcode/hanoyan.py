def hanoya(n,start,buf,to):
    if n > 0:
        hanoya(n-1,start,to,buf)
        print(f'{start} - {to}')
        hanoya(n-1,buf,start,to)


hanoya(3,'A','B','C')