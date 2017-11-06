import os

os.chdir("C:\WORK\Backup\GCAT files")
p = os.listdir("C:\WORK\Backup\GCAT files")

for row in p:
    with open(row, 'r') as f:
        first_line = f.readline()
        print(",('tblGCAT_"+ row.replace(".txt", "")+"', '"+first_line.replace("\n", "")+"')")
        # print(first_line)