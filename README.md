# 破解你的有道词典笔 S6/S6Pro
对于 S6Pro，由于根分区是只读的因此破解相当安全(除了第一步)，而 S6 根分区可读可写意味着可玩性更高同时也有一定风险。以下操作只要未特别注明都不会对原本功能产生影响。
## 1.拿到 ADB 权限
感谢 @SkySight-666 和 @LittleSadSheep 两位提供的[教程](https://github.com/orgs/PenUniverse/discussions/277)，另外 S6Pro 用户可以查看[我的补充](https://github.com/orgs/PenUniverse/discussions/277#discussioncomment-12398830)。我也会把我替换好密码的镜像上传到 [Release](https://github.com/ovo-Tim/Youdao-DictPenS6P/releases) (仅适用于 S6Pro, 密码是 1145141919810)。

## 2.关闭有道原有服务(暂时的)
进入 shell 之后不难发现词典笔使用 `init.d` 来管理服务，可以通过查看 `/etc/init.d/` 目录下的文件来观察他们。
经过实验，想要关闭原有服务并保持 wifi 连接你可以执行:
``` shell
/etc/init.d/S50launcher stop
/etc/init.d/S01systeminit stop
/usr/bin/S40network start &

/usr/bin/guardian_run /usr/bin/runWpas &
/usr/bin/guardian_run /usr/bin/runWifiMgr &
```

另外，由于词典笔内存较小，建议开启 swap 文件(建议放到 `/userdisk/Favorite`)

## 3.chroot
由于词典笔根分区只读而且为 busybox 环境，因此我们需要先进入 chroot 环境才能做更多事情。这里示例使用的是 `Debian 12` 镜像，你也可以选择自己喜欢的发行版。我也会把我的环境上传到 [Release](https://github.com/ovo-Tim/Youdao-DictPenS6P/releases)，已经安装了 `Xorg Chromium` 还有我的一些小脚本。

使用步骤：
1. 下载镜像，解压到 `/userdisk/Favorite` 目录下。
2. 初始化 chroot (每次重启词典笔后执行一次):
``` shell
mount -t proc proc /userdisk/Favorite/chroot/proc
mount -t sysfs sys /userdisk/Favorite/chroot/sys
mount --bind /dev /userdisk/Favorite/chroot/dev

/etc/init.d/S50launcher stop
/etc/init.d/S01systeminit stop
/usr/bin/S40network start &
swapon /userdisk/Favorite/swapfile # 开启 swap 文件(可选)，需保证 swapfile 已存在
/usr/bin/guardian_run /usr/bin/runWpas &
/usr/bin/guardian_run /usr/bin/runWifiMgr &
```
3. 进入 chroot 环境: `chroot /userdisk/Favorite/chroot /bin/bash`
4. Have fun!

## 4.图形化界面
由于词典笔屏幕为 framebuffer，因此只能使用 Xorg(不要尝试 wayland)。安装过程比较简单(apt)，这里不再赘述。需要注意的是，启动之前建议先启动一下 DBus，顺便做一些小事:
``` shell
mount -t tmpfs tmpfs /run
mkdir -p /run/dbus
chmod 755 /run/dbus

pkill dbus-daemon
dbus-daemon --system --fork
```
(如果你使用我的环境，你可以直接使用 `bash /user-init.sh `)

启动 Xorg: `Xorg &`
现在你就可以使用 `xeyes` 来测试一下了, 如果出现一双眼睛则正常。如果提示 `Error: Can't open display:` 则说明你需要设置 `export DISPLAY=:0` (0也有可能是1)

关于屏幕方向：
细心的你一定发现屏幕方向是竖着的，但是可能由于 framebuffer 这个问题几乎没有解决方案，请不要再浪费时间研究了(我一个周末已经没了)，解决方案是开发一些旋转过的程序比如 `broswer.py`(暂时显示不出网页，问题未知)。

## 5.触摸屏
由于一些驱动问题，词典笔的触摸屏默认无法正常工作，这里我提供了一个脚本 `touchscreen.py` 来模拟触摸事件，这样就能正常使用了。使用方法:
``` shell
python3 touchscreen.py &
```

## 6.后续
由于学校现在可以让我们把电脑带去玩所以我可能不会继续折腾了，但是如果有兴趣的话我可以提供一些思路:
1. 在没有电脑的情况下开启自定义程序(同样不破坏词典笔原本功能):
<br/>
观察可以发现 `userdisk/Favorite/WordBook.txt` 里存放了你收藏的单词，因此你可以在启动时启动一些自定义程序用于后台检测是否有特定单词被收藏，如果有就启动你的自定义程序。
<br/>
不过 S6Pro 的根分区是只读的，而且镜像解包比较困难因此实施有一定难度和风险，S6 用户可以试试看
2. 关于开发适配屏幕方向的程序
<br/>
正如上面所说，由于屏幕方向问题你可能需要开发一些旋转过的程序，仓库里的 `browser.py` 是一个简单的示例，但是不知道为什么网页始终显示不出来也没有报错(chromium 正常)，一个备选思路是基于 `Electron` 制作浏览器，网上有教程，难度也不大(`Tauri` 不行)。