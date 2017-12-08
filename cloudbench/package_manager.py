class PackageManager(object):
    def __init__(self, vm):
        self.vm_ = vm
        super(PackageManager, self).__init__()

    def install(self, package):
        pass

    def remove(self, package):
        pass

    def installed(self, package):
        pass


class AptManager(PackageManager):
    def __init__(self, *args, **kwargs):
        super(AptManager, self).__init__(*args, **kwargs)
        self.updated_ = False

    def install(self, package):
        self.update()
        self.vm_.execute('sudo apt-get install %s -y' % package)
        return True

    def installed(self, package):
        self.vm_.execute('sudo dpkg-query -f -W \'${Status}\n %s' % package)
        return True

    def remove(self, package):
        self.update()
        self.vm_.execute('sudo apt-get remove %s -y' % package)
        return True

    def update(self):
        if not self.updated_:
            self.vm_.execute('sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak')
            self.vm_.execute('sudo chmod 666 /etc/apt/sources.list')
            source = """sudo cat <<EOT >> /etc/apt/sources.list
# deb cdrom:[Ubuntu 16.04 LTS _Xenial Xerus_ - Release amd64 (20160420.1)]/ xenial main restricted





deb http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse #Added by software-properties
deb http://archive.canonical.com/ubuntu xenial partner
deb-src http://archive.canonical.com/ubuntu xenial partner
deb http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted multiverse universe #Added by software-properties
deb http://mirrors.aliyun.com/ubuntu/ xenial-security universe
deb http://mirrors.aliyun.com/ubuntu/ xenial-security multiverse
EOT"""
            format = source.format()
            self.vm_.execute('echo deb-src http://archive.ubuntu.com/ubuntu xenial main restricted >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial main restricted >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb-src http://mirrors.aliyun.com/ubuntu/ xenial main restricted multiverse universe >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-updates main restricted >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates main restricted multiverse universe >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial universe >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-updates universe >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial multiverse >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-updates multiverse >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb-src http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://archive.canonical.com/ubuntu xenial partner >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb-src http://archive.canonical.com/ubuntu xenial partner >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted multiverse universe >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-security universe >> /etc/apt/sources.list')
            self.vm_.execute(
                'echo deb http://mirrors.aliyun.com/ubuntu/ xenial-security multiverse >> /etc/apt/sources.list')
            self.vm_.execute('sudo apt-get update -y')
            self.updated_ = True
