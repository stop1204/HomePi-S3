import pigpio
import time
from  DeviceInfo import  device_info
# 替换为树莓派的 IP 地址
RASPBERRY_PI_IP = device_info.get_host_ip()

# 红外接收器连接的 GPIO 引脚（使用 BCM 编号）
IR_PIN = 17

class IRReceiver:
    def __init__(self, pi, pin):
        self.pi = pi
        self.pin = pin
        self.high_tick = 0
        self.gap = 10000  # 微秒
        self.code_timeout = 50000  # 微秒
        self.code = []
        self.in_code = False

        # 设置引脚为输入模式
        self.pi.set_mode(self.pin, pigpio.INPUT)

        # 注册回调函数
        self.cb = self.pi.callback(self.pin, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):
        if level != pigpio.TIMEOUT:
            edge = tick
            if self.high_tick != 0:
                duration = pigpio.tickDiff(self.high_tick, edge)
                if duration > self.gap:
                    if self.in_code:
                        # 处理接收到的代码
                        self.process_code(self.code)
                        self.code = []
                    self.in_code = True
                if self.in_code:
                    self.code.append(duration)
            self.high_tick = edge
        else:
            # 超时处理
            if self.in_code:
                self.process_code(self.code)
                self.code = []
                self.in_code = False

    def process_code(self, code):
        # 简单的 NEC 解码示例，实际使用中可能需要更复杂的处理
        if len(code) < 67:
            print("代码长度不足，无法解码")
            return

        bits = []
        for i in range(1, len(code), 2):
            if 1000 < code[i] < 2000:
                bits.append(0)
            elif 2000 < code[i] < 3000:
                bits.append(1)
            else:
                print("脉冲宽度异常，无法解码")
                return

        # 将位列表转换为整数
        value = 0
        for bit in bits:
            value = (value << 1) | bit

        print(f"解码结果：{hex(value)}")

    def cancel(self):
        self.cb.cancel()

# 主程序
if __name__ == "__main__":
    # 连接到树莓派上的 pigpio 守护进程
    pi = pigpio.pi(RASPBERRY_PI_IP)

    if not pi.connected:
        print("无法连接到树莓派的 pigpio 守护进程")
        exit()

    ir_receiver = IRReceiver(pi, IR_PIN)

    print("开始监听红外信号... 按 Ctrl+C 结束")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止监听")
    finally:
        ir_receiver.cancel()
        pi.stop()