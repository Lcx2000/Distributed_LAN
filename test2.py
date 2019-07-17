import paramiko,os,sys,time,hashlib,json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DirEventHandler(FileSystemEventHandler):
    def __init__(self,root,concernedFile,changedFile):
        self.__rootDir__       =  root
        self.__concernedFile__ =  concernedFile
        self.changedFiles  =  changedFile
    #需记录原路径（src_path),现路径（dest_path）重命名
    def on_moved(self, event):
        if event.dest_path:
            src_relpath  = os.path.relpath(event.src_path  , self.__rootDir__)
            if src_relpath in self.__concernedFile__:
                dest_relpath = os.path.relpath(event.dest_path , self.__rootDir__)      
                self.changedFiles["moved"][src_relpath] = dest_relpath
    
    def on_deleted(self, event):
        relpath = os.path.relpath(event.src_path,self.__rootDir__)
        if relpath in self.__concernedFile__ :
            self.changedFiles["deleted"].append(relpath)

    def on_modified(self, event):
        relpath=os.path.relpath(event.src_path,self.__rootDir__)
        if relpath in self.__concernedFile__ and relpath not in self.changedFiles["modified"]:
            self.changedFiles["modified"].append(relpath)

class boundNode:
    def __init__(self,name,IPv4=None,IPv6=None,isLAN=True,targetDir=None,synNum=0):
        self.IPv4      = IPv4
        self.IPv6      = IPv6
        self.name      = name
        self.isLAN     = isLAN
        self.targetDir = targetDir
        self.synNum    = synNum
class blacklist:
    def __init__(self,files=[],suffixs=[],dirs=[]):
        self.specifiedFile   = files
        self.specifiedSuffix = suffixs
        self.specifiedDirs   = dirs
class whitelist:
    def __init__(self,files=[],suffixs=[],dirs=[]):
        self.specifiedFile   = files
        self.specifiedSuffix = suffixs
        self.specifiedDirs   = dirs

class fileSynchronizerClass: 
    def __init__(self,configFilePath):
        # 配置初始化，配置文件读取及配置方式参考《工程规范》
        # 初始化主节点IPv4及IPv6地址
        # 初始化日志，日志规定参考《工程规范》
        # 读取秘钥，用来与主节点通信
        # 初始化被绑定节点self.__boundNode__,数据结构参考boundNode,一个类别只绑定一个节点
        # 初始化self.__filterMode__="blacklist/whitelist"，从配置文件中读取默认值
        # 初始化self.__blacklist__ 从配置文件中读取默认值
        # 初始化self.__rootDir__ 同步的本地根目录
        # 初始化self.__allFiles__ 存储根目录下所有扫描到的文件的相对路径
        # 初始化self.__concernedFile__ 经过筛选后的文件相对路径列表
        # 初始化self.__changedFiles__ 检测到的需要修改的文件
        with open(configFilePath, "r", encoding='utf-8') as f:
            __configObj__ = json.load(f)
        self.__boundNode__     =  __configObj__['boundNode']
        self.__filterMode__    =  __configObj__['filterMode']
        self.__blacklist__     =  __configObj__['blacklist']
        self.__whitelist__     =  __configObj__['whitelist']
        self.__rootDir__       =  __configObj__['rootdir']
        self.__allFiles__      =  __configObj__['allFiles']
        self.__concernedFile__ =  __configObj__['concernedFile']
        self.__changedFiles__  =  __configObj__['changedFiles']
    
    def setRootDir(self,path):
        #设置self.__rootDir__
        self.__rootDir__ = path
    
    # 以下为黑白名单管理
    def showBlacklist(self):
        return self.__blacklist__
    def showWhitelist(self):
        return self.__whitelist__
    def addFileBlacklist(self,fileName):
        #添加文件名到黑名单
        self.__blacklist__.specifiedFile.append(fileName)
    def removeFileBlacklist(self,fileName):
        #从黑名单中删除指定文件名
        self.__blacklist__.specifiedFile.remove(fileName)
    def addSuffixBlacklist(self,suffix):
        #添加后缀名到黑名单
        self.__blacklist__.specifiedSuffix.append(suffix)
    def removeSuffixBlacklist(self,suffix):
        #从黑名单中删除指定后缀名
        self.__blacklist__.specifiedSuffix.remove(suffix)
    def addDirBlacklist(self,dir):
        #添加目录到黑名单
        self.__blacklist__.specifiedDirs.append(dir)
    def removeDirBlacklist(self,dir):
        #从黑名单中删除指定目录
        self.__blacklist__.specifiedDirs.remove(dir)
    def addFileWhitelist(self,fileName):
        #添加文件名到白名单
        self.__whitelist__.specifiedFile.append(fileName)
    def removeFileWhitelist(self,fileName):
        #从白名单中删除指定文件名
        self.__whitelist__.specifiedFile.remove(fileName)
    def addSuffixWhitelist(self,suffix):
        #添加后缀名到白名单
        self.__whitelist__.specifiedSuffix.append(suffix)
    def removeSuffixWhitelist(self,suffix):
        #从白名单中删除指定后缀
        self.__whitelist__.specifiedSuffix.remove(suffix)
    def addDirWhitelist(self,dir):
        #添加目录到白名单
        self.__whitelist__.specifiedDirs.append(dir)
    def removeDirWhitelist(self,dir):
        #从白名单中删除指定目录       
        self.__whitelist__.specifiedDirs.remove(dir)
    
    def __listdir__(self,path,flag):
        #flag表示目录是否出现在黑白名单上
        for file in os.listdir(path):  
            file_path = os.path.join(path, file)  
            relpath = os.path.relpath(file_path, self.__rootDir__)  
            if os.path.isdir(file_path):
                if (self.__filterMode__=="whitelist" and relpath in self.__whitelist__.specifiedDirs) or \
                    (self.__filterMode__=="blacklist" and relpath in self.__blacklist__.specifiedDirs):
                    flag = True
                self.__listdir__(file_path,flag)  
            else:
                self.__allFiles__.append(relpath)
                (filename,extension) = os.path.splitext(file_path)
                if self.__filterMode__ == "whitelist":
                    if extension in self.__whitelist__.specifiedSuffix or relpath in self.__whitelist__.specifiedFile or flag:
                        self.__concernedFile__.append(relpath)
                else:
                    if extension not in self.__blacklist__.specifiedSuffix and relpath not in self.__blacklist__.specifiedFile and not flag:
                        self.__concernedFile__.append(relpath)
    def scanRootDir(self):
        # 判断当前名单模式
        # 扫描当前根目录下所有文件添加进self.__allFiles__
        # 得到筛选后的文件self.__concernedFile__ ，筛选规则为根据名单机制筛选
        self.__listdir__(self.__rootDir__,False)

    def detectDiff(self):
        # 扫描self.__concernedFile__中的改动，通过检测修改时间，【此处需要你调研下，有无更好的方式】
        observer = Observer()
        fileHandler = DirEventHandler(self.__rootDir__,self.__concernedFile__,self.__changedFiles__)
        observer.schedule(fileHandler, self.__rootDir__, True)
        observer.start()
        try:
            while True:
                time.sleep(4)
                self.__changedFiles__ = fileHandler.changedFiles
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def __checkNodeByIPv4__(self, IPv4):
        # 通过ping来判断是否在局域网内
        return isInLAN
    def __checkNodeByIPv6__(self, IPv6):
        #通过ping来判断是否在局域网内
        return isInLAN
    def __queryNode__(self, nodeName):
        #通过主节点查询该节点的IPv4和IPv6
        pass
    def bindingNode(self, nodeName):
        #绑定节点
        #通过nodeName，调用self.__queryNodeInfo__(nodeName)来获得该节点的IPv4及IPv6地址
        #测试是否在局域网内
        #最后设置self.__boundNode__
        (IPv4,IPv6)        = self.__queryNode__
        isInLAN            = self.__checkNodeByIPv4__(IPv4) or self.__checkNodeByIPv6__(IPv6)
        self.__boundNode__ = boundNode(IPv4,IPv6,nodeName,isInLAN)
    def updateNode(self, nodeName):
        #更新绑定的节点
        #通过nodeName，调用self.__queryNodeInfo__(nodeName)来获得该节点的IPv4及IPv6地址
        #测试是否在局域网内
        #最后设置self.__boundNode__
        (IPv4,IPv6)        = self.__queryNode__
        isInLAN            = self.__checkNodeByIPv4__(IPv4) or self.__checkNodeByIPv6__(IPv6)
        self.__boundNode__ = boundNode(IPv4,IPv6,nodeName,isInLAN)
    
    
    def __synchronize__(self):
        #self.__changedFiles__同步这里面的文件
    #调用用来同步文件
    #局域网内采用ssh直传到绑定节点
#     外网采用ssh直传到主节点，又主节点再ssh传到绑定节点
#     同步过程：
#     1.读取self.__changedFiles__内的文件比对本地和远程对应文件的MD5或SHA-1
#     2.若远程不存在该文件直接同步
#     3.若MD5或SHA-1不同才进行同步
        if self.__boundNode__.isLAN:
            uploader = fileUploaderClass("192.168.101.57","gdp","glass123456")
            for file in self.__changedFiles__[modified]:
                localFile  = os.path.join(self.__rootDir__, file)
                remoteFile = os.path.join(self.__boundNode__.targetDir, file)
                flag_exists,remoteFile_md5 = uploader.sshScpGetmd5(remoteFile)
                if flag_exists:
                    file = open(localFile,'r')
                    if hashlib.new('md5', file.read()).hexdigest() != remoteFile_md5:
                        uploader.sshScpPut(localFile,remoteFile)
                    file.close()
                else:
                    uploader.sshScpPut(localFile,remoteFile)
                self.__changedFiles__[modified].remove(file)
            for file in self.__changedFiles__[moved].keys():
                oldpath = os.path.join(self.__boundNode__.targetDir, file)
                newpath = os.path.join(self.__boundNode__.targetDir, self.__changedFiles__[moved][file])
                uploader.sshScpRename(oldpath,newpath)

        else:
            pass



                

# ssh传输类：

class fileUploaderClass(object):
    def __init__(self,serverIp,userName,passWd):
        self.__ip__         = serverIp
        self.__userName__   = userName
        self.__passWd__     = passWd
        self.__port__       = 22
        self.__ssh__        = paramiko.SSHClient()
        self.__ssh__.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def sshScpPut(self,localFile,remoteFile):
        self.__ssh__.connect(self.__ip__, self.__port__ , self.__userName__, self.__passWd__)
        sftp = paramiko.SFTPClient.from_transport(self.__ssh__.get_transport())
        sftp = self.__ssh__.open_sftp()
        sftp.put(localFile, remoteFile,callback =self.__putCallBack__)
        sftp.close()
        self.__ssh__.close()
    
    def sshScpGet(self, remoteFile, localFile):
        self.__ssh__.connect(self.__ip__, self.__port__, self.__userName__, self.__passWd__)
        sftp = paramiko.SFTPClient.from_transport(self.__ssh__.get_transport())
        sftp = self.__ssh__.open_sftp()
        sftp.get(remoteFile, localFile,callback =self.__putCallBack__)
    
    def __putCallBack__(self,transferred,total):
        print("current transferred %.1f percent"%(transferred/total*100))
    
    def sshScpGetmd5(self, file_path):
        self.__ssh__.connect(self.__ip__, self.__port__, self.__userName__, self.__passWd__)
        sftp = paramiko.SFTPClient.from_transport(self.__ssh__.get_transport())
        sftp = self.__ssh__.open_sftp() 
        try:
            file = sftp.open(file_path, 'r')
            return (True,hashlib.new('md5', file.read()).hexdigest())
        except:
            return (False,None)
    def sshScpRename(self, oldpath, newpath):
        self.__ssh__.connect(self.__ip__, self.__port__ , self.__userName__, self.__passWd__)
        sftp = paramiko.SFTPClient.from_transport(self.__ssh__.get_transport())
        sftp = self.__ssh__.open_sftp()
        sftp.rename(oldpath,newpath)
#if __name__=="__main__":

#     uploader = fileUploaderClass("192.168.101.57","gdp","glass123456")
#     uploader.sshScpPut("D:\\下载\\新建文件夹\\result1.avi","/home/gdp/Website/webserver/output_video/1.avi")
#     uploader.sshScpGet("/home/gdp/Website/webserver/output_video/1.avi","D:\\下载\\新建文件夹\\result2.avi")