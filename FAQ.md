### Q1、worker中docker pull fail `Error response from daemon: Get https://registry-1.docker.io/v2/: dial tcp: lookup registry-1.docker.io on 114.114.114.114:53: no such host`
是因为DNS解析不到docker仓库，修改DNS为8.8.8.8谷歌DNS  
修改 /etc/resolv.conf 增加 nameserver 8.8.8.8  

### Q2、nvidia docker 启动报错，执行 nvidia-smi 命令也报错`NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver. Make sure that the latest NVIDIA driver is installed and running.`

重装nvidia显卡驱动
```bazaar
ls /usr/src | grep nvidia # 查看之前安装的显卡驱动版本
sudo apt install dkms
sudo dkms install -m nvidia -v xxx.xx.xx(版本号) 
```
重装显卡驱动之后 `nvidia-smi` 命令执行成功  
`sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi`验证nvidia docker也正常  
