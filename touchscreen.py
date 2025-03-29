from evdev import InputDevice, ecodes
from Xlib import X, display
from Xlib.ext import xtest

# 配置参数
DEVICE_PATH = "/dev/input/event2"
SCREEN_WIDTH = 170    # 替换为实际屏幕宽度
SCREEN_HEIGHT = 560   # 替换为实际屏幕高度

# 初始化X11连接
d = display.Display()

# 打开输入设备
dev = InputDevice(DEVICE_PATH)
dev.grab()  # 独占设备

# 初始化坐标
x, y = 0, 0
_x, _y = 0, 0
tracking_id = -1

try:
    for event in dev.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_MT_POSITION_X:
                _x = event.value
            elif event.code == ecodes.ABS_MT_POSITION_Y:
                _y = event.value
            elif event.code == ecodes.ABS_MT_TRACKING_ID:
                tracking_id = event.value
        elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                if event.value == 1:  # 触摸开始
                    xtest.fake_input(d, X.ButtonPress, 1)  # 模拟鼠标左键按下
                    print("Clicked")
                else:                 # 触摸结束
                    xtest.fake_input(d, X.ButtonRelease, 1)  # 模拟鼠标左键释放

        x, y = _y, (SCREEN_HEIGHT - _x)

        # 检测触摸开始/结束
        if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
            if event.value == 1:  # 触摸开始
                xtest.fake_input(d, X.MotionNotify, x=x, y=y)
            else:                 # 触摸结束
                pass  # 保持最后位置

        # 当坐标有效时移动指针
        if tracking_id != -1 and x != 0 and y != 0:
            xtest.fake_input(d, X.MotionNotify, x=x, y=y)
            d.sync()

finally:
    dev.ungrab()