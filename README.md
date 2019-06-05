##                                 Doki Docker linux club !

![](./img/ddlc.jpg)



### 目标 ：

* 实现 IO 隔离，至少包括文件系统，PCI 设备

* 实现进程隔离

  ​	容器进程无法影响其他进程

  ​	包括环境变量的隔离

  ​	

* 实现用户隔离

  ​	？？

* 实现网络隔离:

​		model 1 网络完全隔离

​		model 2 网络联通，端口不对外开放

​		model3 端口映射,容器端口对外开放



### 参考资料 :

> <http://man7.org/linux/man-pages/man7/namespaces.7.html>
>
> <http://man7.org/linux/man-pages/man2/clone.2.html>
>
> <http://man7.org/linux/man-pages/man2/chroot.2.html>

### 注意：	

操作系统 ： Unix like 

语言 ： 不限	，但不建议使用太高级的语言

附件 : assets/rootfs.tar 是我使用的一个简单的文件系统	



​	













