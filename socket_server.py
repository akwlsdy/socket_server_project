import os
import socket
from datetime import datetime
import re

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # Buffer size
        self.DIR_PATH = os.path.join(os.getcwd(), 'request')  # 使用绝对路径创建请求目录
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """创建目录"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_request(self, request):
        """保存请求到以日期时间命名的二进制文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # 获取当前时间并格式化
        file_path = os.path.join(self.DIR_PATH, f"{timestamp}.bin")  # 创建文件路径
        print(f"Saving request to {file_path}")  # 调试输出文件路径

        with open(file_path, 'wb') as file:  # 以二进制写模式打开文件
            file.write(request)  # 将请求内容写入文件
        print(f"Request saved to {file_path}")  # 打印确认保存成功

    def save_image(self, data):
        """保存多部分数据中的图像"""
        boundary = data.split(b'\r\n')[0]  # 获取分隔符
        parts = data.split(boundary)  # 根据分隔符拆分数据
        
        for part in parts:
            if b'Content-Disposition' in part:
                # 获取文件名
                match = re.search(r'filename="(.+?)"', part.decode('utf-8'))
                if match:
                    filename = match.group(1)
                    filename = os.path.join(self.DIR_PATH, filename)

                    # 提取图像数据
                    image_data = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0]
                    with open(filename, 'wb') as img_file:
                        img_file.write(image_data)
                    print(f"Image saved to {filename}")

    def run(self, ip, port):
        """运行服务器"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" to stop the server!\r\n")

        try:
            while True:
                clnt_sock, req_addr = self.sock.accept()
                print("Client connected from:", req_addr)

                # 接收请求
                request = b""
                while True:
                    data = clnt_sock.recv(self.bufsize)
                    if not data:
                        break
                    request += data

                # 判断请求类型并处理
                if b'GET' in request:
                    # 处理 GET 请求
                    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Server is running and ready to receive POST requests.</h1>"
                    clnt_sock.sendall(response)
                elif b'POST' in request or b'POST' in request.splitlines()[0]:
                    # 处理 POST 请求
                    print("POST request received, saving to .bin file...")
                    self.save_request(request)
                    if b'multipart/form-data' in request:
                        self.save_image(request)
                    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nRequest received"
                    clnt_sock.sendall(response)

                clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStop the server...")
            self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
