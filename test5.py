# import subprocess
# child = subprocess.Popen(['ping','-c','4','www.baidu.com'])
# print ('parent process')
import os,time,hashlib
# child = subprocess.Popen(['ping','-c','4','www.baidu.com'])
# time_start=time.time()
# p=os.system("ping -n 2 -w 1 %s"%"www.baidu.com")
# if p:
#     print("ping不通") 
# else:
#     print("ping通了")
# time_end=time.time()
# print(time_end-time_start)
# time_start=time.time()
# p=os.popen("ping -n 2 -w 1 %s"%"www.baidu.com")
# x=p.read()
# p.close()
# if x.count('temeout'):
#     print("ping不通")
# else:
#     print("ping通了")
# time_end=time.time()
#print(time_end-time_start)
file=open("D:\\1.jpg",'rb')
print(type(file.read()))
print((hashlib.new('md5', file.read()).hexdigest()))
file_path="E:\\Distributed_LAN\\test4.py"
rootDir="E:\\Distributed_LAN"
relpath=os.path.relpath(file_path, rootDir)
print(relpath)
path=os.path.join(rootDir,relpath)
print(path)
a=path.split("\\")  
print(a)
#file=open(path,'rb')
dict={}
def dict_get(dict,objkey,flag,data,i):
    if i<len(objkey)-1:
        if dict!=None and objkey[i] in dict.keys():
            return dict_get(dict[objkey[i]],objkey,True, data,i+1)
                
        else:
            dict[objkey[i]]={}
            return dict_get(dict[objkey[i]],objkey,False, data,i+1)
    else:
        if objkey[i] in dict.keys():
            if dict[objkey[i]]!=data:
                dict[objkey[i]]=data
                return True
            else:
                return False
        else:
            dict[objkey[i]]=data
            return True

z=dict_get(dict,[1,2,3,4],True,5,0)
print(dict)
y=dict_get(dict,[1,2,3,4],True,2,0)
print(dict)
x=dict_get(dict,[1,2,3,5],True,5,0)
print(dict)
q=dict_get(dict,[1,2,5],True,0,0)
print(dict)
p=dict_get(dict,[1,2,3,4],True,5,0)
print(dict)
t=dict_get(dict,[1,2,3,4],True,5,0)
print(dict)
print(x)
print(y)
print(z)
print(q)
print(p)
print(t)
