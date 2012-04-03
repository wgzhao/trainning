#LSB 脚本规范技术交流
  
  
#### wgzhao <wgzhao@kingbase.com.cn>

##什么是LSB
[LSB]，即**Linux标准规范**(英语:Linux Standard Base)是一个在[Linux基金会]结构下对Linux发行版的联合项目，使Linux操作系统符合软件系统架构，或文件系统架构标准的规范及标准。[LSB]基于[POSIX]，统一UNIX规范及其他开放标准，共在某些领域扩展它们。详细情况请参考相关链接。


##LSB脚本动作

由[LSB]应用程序提供的脚本应该需要接受一个指示其动作(action)的参数，目前包括：

+ **start** 		启动服务
+ **stop**  		停止服务
+ **restart** 		如果服务在运行，则先停止，再启动，否则启动服务
+ **try-restart** 如果服务正在运行，重启服务
+ **reload** 		不通过重启服务的方式重新加载配置文件
+ **force-reload**  如果服务支持的话，重新加载配置文件，否则重启服务
+ **status** 		打印服务的当前状态

`start`，`stop`，`restart`，`force-reload` 和`status`是所有lsb脚本必须支持的；`reload`和`try-restart`是可选的。当然自己也可以定义别的一些动作。

在下列情况下，lsb脚本要求确保对其接受的动作(action)有其明确且合理的行为

+ 服务已经启动，然后调用`start`
+ 服务已经停止，然后调用`stop`

对于这些行为，为了满足其一致性，最好使用`/lib/lsb/init-functions`脚本(后面分析)

在主流的Linux发行版版本中，一个软件包卸载(remove)时，并不会将一些脚本，配置文件同时删除，除非你强制指定为清除(purge)。因此，在你的lsb脚本最前面应该包括一个判断真正的可执行文件是否存在，类似于下面这个样子:

`[ -x /usr/sbin/ifconfig ] || exit 5`

如果调用`status`动作，lsb脚本应该根据其状态返回下面的值:

+ **0**  程序正在运行，或者服务正常
+ **1**  程序已死，但/var/run/下的pid文件还存在(或者在别的位置)
+ **2**  程序已死，但/var/lock/下的锁文件还存在(或者在别的位置)
+ **3**  程序没有运行
+ **4**  程序或者服务状态未知
+ **5-99** LSB为扩展保留
+ **100-149**  为发行版本使用保留
+ **150-199**   为应用程序使用保留
+ **200-254**  保留

除`status`动作外，指定其他动作，lsb脚本必须返回状态值(`exit $?`)，如果完成动作其他的结果，返回为0，否则应该根据动作情况，返回下列值之一:

+ **1**  通用(generic)错误或者非规范化错误
+ **2**  无效参数，或者参数过多
+ **3**  未实现的特性（比如`reload`）
+ **4**  用户权限不够
+ **5**  程序没有安装
+ **6**  程序没有配置
+ **7**  程序没有运行
+ **8-99**  LSB为扩展保留
+ **100-149**  为发行版本保留
+ **150-199**  为应用程序使用保留
+ **200-254**  保留

错误和状态消息应该通过日志函数来输出，比如lsb提供的`log_failure_msg`。

因为lsb脚本有可能是由系统管理员在非标准的环境下手工运行，比如没有`PATH`，`USER`，`LOGNAME`等环境变量。因此lsb脚本不能依赖环境变量，它需要自己设定自己需要的变量或者使用缺省值。

##LSB脚本注释约定

在`init.d`目录的lsb脚本，其脚本描述信息应该用`### BEGIN INIT INFO` 和 `### END INIT INFO`来分隔。分隔行可以包行尾部空白，脚本会忽略它。在分隔行之间包围区域其描述信息需要遵循这样的格式：
`# {keyword}: [arg1] [arg2] ...`。在`#`和`keyword`之间只能而且必须有一个空格，类似下面的例子：

    
        # Provides: boot_facility_1 [ boot_facility_2...]
        # Required-Start: boot_facility_1 [ boot_facility_2...]
        # Required-Stop: boot_facility_1 [ boot_facility_2...]
        # Should-Start: boot_facility_1 [ boot_facility_2...]
        # Should-Stop: boot_facility_1 [ boot_facility_2...]
        # Default-Start: run_level_1 [ run_level_2...]
        # Default-Stop: run_level_1 [ run_level_2...]
        # Short-Description: short_description
        # Description: multiline_description
    
`init.d`下的lsb脚本可以用`Required-Start`关键字来申明在运行该脚本之前应该需要先运行哪些脚本，这些信息一般是由安装程序或者启动脚本工具根据相互依赖关系来生成其正确的顺序(比如所有依赖网络的服务都应该应该在`network`脚本启动之后运行)。当lsb脚本带`start`参数运行时，在`Provides`指定的设施(facility)应该存在，而且lsb脚本也要求这些设施能够正确运行。  

类似的，`Required-Stop`里定义的启动设施应该在该脚本停止时都有效。  

`Should-Start`关键字和`Should-Stop`关键字的概念和`Required-Start`及`Required-Stop`类似，只是对其后面定义的设施是希望而不是必须。  

`Default-Start`和`Default-Stop` 定义了缺省情况下该脚本在哪些运行级别下启动和停止，它可以通过init脚本来控制。  


`Short-Description`和`Description`关键字是描述该脚本的行为，如关键字说描述的那样，`Short-Description`希望是简洁的介绍该脚本，而`Description`则可以更详细一点。如果描述信息多余一行，从描述信息的第二行起，每一行都必须以`#`符号开头，然后接一个`tab`键，或者至少两个空格。  

##安装和移除(removal) init.d 脚本

通过将脚本拷贝到`init.d`目录或者符号链接到该目录，就完成了脚本的安装工作，在执行安装包的`postinstall`脚本阶段(RPM包管理)，`/usr/lib/lsb/install_initd`程序调用安装程序的`init.d`脚本文件来安装，`/usr/lib/lsb/inistall_initd`程序可以带一个参数，类似如下：

`/usr/lib/lsb/install_initd /etc/init.d/foo`  

如果脚本已经安装或者安装成功，该程序均返回为0，其他情况返回为非0值。  

卸载软件包时，通过`preuninstall`脚本来调用`/usr/lib/lsb/remove_initd`程序来移走`init.d`目录对应的文件，类似如下：  

`/usr/lib/lsb/remove_initd /etc/init.d/foo`

如果脚本已经移除或者移除成功，则返回为0，否则返回为非0值。  


系统发行版本应该提供一个有效的工具（比如红帽的`chkconfig`)来提供给系统管理员来管理多运行级别下，脚本的启动停止控制。


##运行级别

绝大部分通用Linux发行版都提供了多种启动级别，前面说到的`Default-Start`，`Default-Stop`也表明了这点。系统init脚本通过调用对应运行级别目录(`rc?.d`)下的脚本(符号链接)来控制哪些脚本应该在该级别启动和停止。`/usr/lib/lsb/inistall_initd`程序通过查询脚本的`Default-Start`和`Default-Stop`的定义来创建对应运行级别目录的符号链接。  
系统启动级别及描述如下：  

+ **0**  停机  
+ **1**  单用户模式  
+ **2**  多用户无网络模式（很少使用）  
+ **3**  完整的多用户终端模式（无图形界面）  
+ **4**  保留  
+ **5**  多用户带GUI模式  
+ **6**  重启  


##设施(facility)名称

启动设施用来指示init脚本之间的依赖性。以`$`符号开头设施名都是系统设施，它由LSB定义，发行版吧必须提供。符合LSB规范的应用程序不能提供以`$`开头的设施名称。  当前LSB定义下面的几种设施名称：  

+ **$local_fs**  所有的本地文件系统已经挂载
+ **$network**   底层网络已经有效(指网卡，IP地址，PCMCI之类的)
+ **$named**      域名解析后台服务(DNS)正在运行
+ **$portmap**    提供SunRPC/ONCRPC端口映射的服务(如果存在的话)正在运行
+ **$remote_fs**  所有远程文件系统已经挂载
+ **$syslog**     系统日志服务可用
+ **$time**       系统时钟已经设置

其他(非系统)的设施可以由LSB应用程序来定义，这些设施名称应该采取脚本名同名的命名约定，通常情况下，发行版版本都是如此。  


##脚本名称  

所有的init脚本都在同一个目录，因此名字不能冲突，[LSB]规范提供了三种有效命名空间方式:  

1. **Assigned namespace**   这种命令只能由`[a-z0-9]`类的字符组成(*没有大写字母*)。为了避免名字冲突，应该去[Linux Assigned Names and Numbers Authority(LANANA)](http://www.lanana.org)去申请你需要的名字。  

2. **Hierarchical namespace**  这种命名空间由类似`[hier1]-[hier2]-...-[name]`组成，其中`name`由`[a-z0-9]`内的字符组成。`[hier-n]`可以有一个或者多个，`[hier1]`的名字要不是LANANA分配给[LSB]的名字，要不就是脚本拥有者的DNS小写名称，至少包含一个`.`符号，比如`debian.org`，`kingbase.com`。 LSB提供的名字只能由`[a-z0-9]`内的ASCII码组成。  

3. **Reserved namespace**  这种命令空间以`_`符号开头，仅提供给版本发行商使用，而且这种命令空间也应该只用在核心软件包上。其他软件包绝不推荐这种命名方式。


##init脚本函数

每一个LSB兼容的`init.d`脚本必须包含`/lib/lsb/init-functions`，使用方式如下:  
`source /lib/lsb/init-functions`  
LSB自带的脚本应该仅仅依赖`/bin/sh`(*`/bin/sh`并不总是符号链接到`/bin/bash`*)  

+ `start_daemon [-f] [-n nicelevel] [-p pidfile] pathname [args]` 将指定的程序运行为守护进程(daemon)。`start_daemon`会检查对应的程序是否已经在运行，如果是，它不会再运行一次，除非使用`-f`参数。如果使用`-n`参数指定了nicelevel(参考nice(1))，`start_daemon` 应该返回LSB定义的退出代码。  如果程序运行成功，该函数返回为0，否则返回为非0。

+ `killproc [-p pidfile] pathname [signal]` 停止指定的程序。该程序应该通过`pidofproc`函数找到(下面描述)。如果指定了`signal`，则通过给`kill`指令传递`-signal_name`或`-signal_number`参数来终止程序，如果没有，则先使用`SIGTERM`信号，如果无法终止，再使用`SIGKILL`信号。LSB兼容的应用程序可以使用`basename`而不一定是`pathname`。 `killproc`应该返回LSB预定义的退出码。调用时，如果没有使用`signal`参数，该函数返回为0，假如程序已经停止，否则返回为非0。如果指定了`signal`参数，只有在程序还在运行的情况下，函数返回为0。

+ `pidofproc [-p pidfile] pathname` 该函数返回特定守护进程的一个或多个`pid`号。如果能找到`/var/run/basename.pid`文件，则返回该文件的值。如果`-p`参数指定，则返回该参数指定文件的内容。 LSB兼容的程序可以使用`basename`而不非得是`pathname`。`pidofproc`应该返回LSB预定义的的退出码，以便给`status`动作使用。如果程序正在运行，他应该返回为0，否则为非0。

+ `log_success_msg "message"`  打印一条成功消息，消息长度最好控制在60个字符内

+ `log_failure_msg "mesage"`   打印一条失败消息，消息长度最好控制在60个字符内

+ `log_warning_msg "message"`  打印一条警告消息，消息长度最好控制在60个字符内


##chkconfig

为了使得`chkconfig`能识别并能管理init脚本，需要在脚本第二行(第一行是`#!/bin/bash`)其增加下面这样几行:  

	#
	# chkconfig: 35 80 5
	# description: some description about this script
	# processname: foo
	
##检测LSB兼容性

1. 服务没有启动时，执行start操作  
`/etc/init.d/some_service start; echo $?`  
预期结果  
服务启动；start操作的返回值为0。  

2. 服务已经启动，执行status操作  
`/etc/init.d/some_server status; echo $?`  
预期结果  
服务仍在运行，status操作显示服务正在运行并且返回值为0。  

3. 服务已经启动，执行start操作  
`/etc/init.d/some_service start; echo $?`  
预期结果  
服务仍在运行，start操作返回值为0。  

4. 服务已经启动，执行stop操作  
`/etc/init.d/some_service stop; echo $?`  
预期结果  
服务停止，stop操作的返回值为0。  

5. 服务已经停止，执行status操作  
`/etc/init.d/some_service status; echo $?`  
预期结果  
服务保持停止，status操作显示服务已经停止并且返回值为3。  

6. 服务已经停止，执行stop操作  
`/etc/init.d/some_service stop; echo $?`  
预期结果  
服务保持停止，stop操作返回值为0。  

7. 服务失效时，执行status操作  
`/etc/init.d/some_service status; echo $?`  
预期结果  

[LSB]: https://wiki.linuxfoundation.org/en/LSB_Wiki "Linux Standard Base"
[Linux基金会]: http://zh.wikipedia.org/wiki/Linux%E5%9F%BA%E9%87%91%E6%9C%83 "Linux 基金会"
[POSIX]: http://zh.wikipedia.org/wiki/POSIX "POSIX"

