def getDef(secNo):

    with open('indian-penal-code_final.csv') as f:
        z=[]

        mylist = list(f)
        mylist=" ".join(mylist)
        for d in range(1,512):
            l=[]
            j="Section "+str(d)
            k="Section "+str(d+1)
            a,b = mylist.find(j),mylist.find(k)
            output=mylist[a+len(j):b]
            test_string =output
            k=test_string
            l.append("Section "+str(d))
            l.append(str(k))
            z.append(l)

        return z






# z=[]
# with open('indian-penal-code_final.csv') as f:
#     mylist = list(f)
#     mylist=" ".join(mylist)
#     for d in range(1,512):
#         l=[]
#         j="Section "+str(d)
#         k="Section "+str(d+1)
#         a,b = mylist.find(j),mylist.find(k)
#         x=mylist[a+len(j):b]
#         test_string =x
#         k=clean(test_string)
#         l.append("Section "+str(d))
#         l.append(str(k))
#         z.append(l)