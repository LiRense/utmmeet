# open('2048MB.pdf', "w").truncate((1024*1024*1024*2-189))
# open('2047MB.pdf', "w").truncate((1024*1024*1024*2-189-2**20))
# open('2049MB.pdf', "w").truncate((1024*1024*1024*2-189+2**20))
# open('norm2048MB.pdf', "w").truncate((1024*1024*1024*2))
open('1GB.zip', "w").truncate((1024*1024*1024))

# 2**10 - 1024 B - 1 KB
# 2**20 - 1024*1024 - 1 MB
# 2**20*100
