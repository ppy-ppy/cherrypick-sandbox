一定要在hadoop目录下使用sudo***命令进行安装！！！！！
绝对不能用root或者ubuntu用户进行安装！！！！！
使用不同的用户配置环境会出现很多莫名其妙的报错，切记把每一次切换用户都按步骤完成。
记得设置root密码与hadoop用户密码。

进入服务器后，首先点击上面菜单栏里的新建文件传输，将ernest压缩包与login.sh拖入/home/ubuntu目录下，关掉传输窗口。
在命令行中输入sudo su进入root用户，进入/home/ubuntu
输入chmod –R 777 ernest-master.tar.gz，使得别的用户也有权限操作该文件
再输入chmod 777 login.sh，用途同上
输入./login.sh运行服务器联网脚本，不要忘了/前面的点。
之后输入mv ernest-master.tat.gz /home/hadoop，将压缩包移动至hadoop目录中
输入exit，从root用户切换回ubuntu用户
输入sudo su hadoop，进入hadoop用户
输入tar –zxvf ernest-master.tar.gz，解压压缩包。
再输入exit，回到ubuntu用户，进入下一步配置过程

配置过程：
1.	首先从ubuntu用户输入sudo su命令进入root用户，并设置root密码，设个简单的，设置方式百度
2.	换源，记得换完以后输入sudo apt-get update ，再输入sudo apt-get upgrade在输入第二条命令后隔十几秒会出现问题，输入y后回车，切记不要直接回车，如果不小心直接回车了在之后询问是否重启的窗口里选择no，接下来会再弹出一个窗口按方向键中的“下”键再按回车
3.	换源后安装pip，此时在root用户下，可直接输入apt-get install python-pip，出现询问do you want to continue时输入y并按回车
4.	更新pip，输入pip install –upgrade pip
5.	设置hadoop用户密码：passwd hadoop ， 尽量与root密码相同，以后使用方便。
6.	输入 exit 回到ubuntu用户，再输入sudo su hadoop进入hadoop用户。
7.	输入cd /home/hadoop/ernest-master进入之前解压的文件夹
8.	输入sudo pip install –r requirement.txt，此时会要求输入密码，输入之前设置的密码。

可能的报错：
每一个报错按照文档处理后都继续输入sudo pip install –r requirement.txt，出现新的问题继续按文档，出现Successfully installed cvxpy-0.2.22 ecos-2.0.5 scs-1.0.7 toolz-0.9.0时证明环境配置成功
如果出现

Traceback (most recent call last):
      File "<string>", line 1, in <module>
    ImportError: No module named setuptools
    
    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-nbXlu7/cvxpy/ 
输入sudo pip install setuptools

如果出现

Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/tmp/pip-build-XzmZkQ/ecos/setup.py", line 10, in <module>
        import numpy
    ImportError: No module named numpy
    
    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-XzmZkQ/ecos/ 
输入sudo pip install numpy

如果出现
x86_64-linux-gnu-gcc: error: unrecognized command line option ‘-Wdate-time’
    x86_64-linux-gnu-gcc: error: unrecognized command line option ‘-fstack-protector-strong’
    error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
    
    ----------------------------------------
Command "/usr/bin/python -u -c "import setuptools, tokenize;__file__='/tmp/pip-build-jI5wN_/ecos/setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" install --record /tmp/pip-0RZfnc-record/install-record.txt --single-version-externally-managed --compile" failed with error code 1 in /tmp/pip-build-jI5wN_/ecos
 
输入sudo apt-get install gcc
不要只看error这一行，后面有一个别的报错error这一行显示的内容相同但是解决办法不同，记得看error上两行，如果是这个报错就用这个办法


如果出现
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security -fPIC -DPYTHON -DDLONG -DLDL_LONG -DCTRLC=1 -Iecos/include -I/usr/local/lib/python2.7/dist-packages/numpy/core/include -Iecos/external/amd/include -Iecos/external/ldl/include -Iecos/external/SuiteSparse_config -I/usr/include/python2.7 -c src/ecosmodule.c -o build/temp.linux-x86_64-2.7/src/ecosmodule.o
    src/ecosmodule.c:4:20: fatal error: Python.h: No such file or directory
    compilation terminated.
    error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
    
    ----------------------------------------
Command "/usr/bin/python -u -c "import setuptools, tokenize;__file__='/tmp/pip-build-dpj7X8/ecos/setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" install --record /tmp/pip-GDMo67-record/install-record.txt --single-version-externally-managed --compile" failed with error code 1 in /tmp/pip-build-dpj7X8/ecos/
 
输入 sudo apt-get install python-dev

我遇到的报错就这么多，如果有问题先把报错行复制进入百度搜索一下看看别人的解决办法。

## Ernest: Efficient Performance Prediction for Advanced Analytics

Ernest is a performance prediction framework for analytics jobs developed using frameworks like Apache Spark and run on cloud computing infrastructure. 

One of the main challenges in deploying large scale analytics applications in
the cloud is choosing the right hardware configuration. Specifically in Amazon
EC2 or Google Compute Engine clusters, choosing the right instance type and the
right number of instances can significantly improve performance or lower cost. 

Ernest is a performance prediction framework that helps address this problem.
Ernest builds performance models based on the behavior of the job on small
samples of data and then predicts its performance on larger datasets and cluster
sizes. To minimize the time and resources spent in building a model, Ernest
uses [optimal experiment design](https://en.wikipedia.org/wiki/Optimal_design),
a statistical technique that allows us to collect as few training points as
required. For more details please see our [paper]
(http://shivaram.org/publications/ernest-nsdi.pdf) and [talk slides](http://shivaram.org/talks/ernest-nsdi-2016.pdf) from NSDI 2016.

### Installing Ernest

The easiest way to install Ernest is by cloning this repository.

Running Ernest requires installing [SciPy](http://scipy.org), [NumPy](http://numpy.org) and
[CVXPY](http://www.cvxpy.org). An easy way to do this is using the `requirements.txt` file.

```
pip install -r requirements.txt
```

### Using Ernest

At a high level there are three main steps to use Ernest as summarized in the following figure.

<p style="text-align: center;">
  <img src="docs/img/ernest-workflow.png" title="Ernest Workflow" alt="Ernest Workflow" style="width: 100%; max-width: 500px;" />
</p>

These include:

1. Determining what sample data points to collect. To do this we will be using experiment design
   implemented in [expt_design.py](expt_design.py). This will return the set of training data points
required to build a performance model.  
2. Collect running time for the set of training data points. These can be executed using [Spark EC2
   scripts](http://github.com/amplab/spark-ec2) or Amazon EMR etc.
3. Building a performance model and using it for prediction. To do this we create a CSV file with
   measurements from previous step and use [predictor.py](predictor.py). 

For a more detailed example you can see our [example](examples/mllib_rcv1.md) on building a
performance model for Spark MLlib algorithms.

## Limitations, Work In Progress

One of the key insights that is used by Ernest is that a number of machine learning workloads are
iterative in nature and have predictable structure in terms of computation and communication.
Thus we are able to run a few iterations of the job on small samples of data to build a performance
model. However this assumption may not be valid for all workloads.

Further, to compare across instance types, we currently need to build a separate model for each instance
type. We are working on developing new techniques to share performance models across instance types.