import sys
# import pygame
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sttings import *
import pyaudio
import wave
import pyttsx3 as pyttsx
import os
# from pocketsphinx import AudioFile
import speech_recognition as sr
import uuid

class ResultWindow(QDialog):
    def __init__(self, parent=None, data_list=None):
        super(ResultWindow, self).__init__(parent)
        self.setWindowTitle('查询结果')
        self.resize(600, 400)
        # 创建表格控件
        self.table_widget = QTableWidget()

        # 设置表头
        self.set_table_header()
        self.table_widget.setColumnCount(3)

        # 添加查询结果到表格
        if data_list:
            self.fill_table_widget(data_list)

        # 设置主布局
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def set_table_header(self):
        header_labels = ['ID', "用户名", "文本"]  # 根据实际情况修改表头标签
        self.table_widget.setColumnCount(len(header_labels))
        self.table_widget.setHorizontalHeaderLabels(header_labels)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自动调整列

    def fill_table_widget(self, data_list):
        self.table_widget.setRowCount(len(data_list))

        for row_index, record in enumerate(data_list):
            for column_index, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row_index, column_index, item)


class AudioRecorder(QThread):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    resd_path=pyqtSignal(str)

    def __init__(self, filename='./init/recorded_audio.wav', sample_rate=44100, chunk_size=1024):
        super(AudioRecorder, self).__init__()
        self.filename = filename
        self.samplerate = sample_rate
        self.chunk_size = chunk_size
        self.is_recording = False
        self.data_chunks = []
        self.p = pyaudio.PyAudio()

    # 录音期间持续读取音频数据，并在录音开始和结束时发出信号
    def run(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.samplerate,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)
        self.is_recording = True
        self.recording_started.emit()
        while self.is_recording:
            data = self.stream.read(self.chunk_size)
            self.data_chunks.append(data)
            if not self.is_recording:  # 检查录音是否已经停止
                break
        self.stream.stop_stream()
        self.stream.close()
        self.save_recording()
        self.recording_stopped.emit()

    # 停止录音，手动停止
    def stop_recording(self):
        self.is_recording = False

    def save_recording(self):
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(1)  # 设置音频文件的声道数为1
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))  # 获取音频文件的样本宽度（采样深度）
            wf.setframerate(self.samplerate)  # 设置音频文件的采样率
            wf.writeframes(b''.join(self.data_chunks))  # 将所有录音数据块连接起来，并写入文件中
        print(f"录音已成功保存为 {self.filename}")
        self.resd_path.emit(self.filename)
        self.data_chunks = []  # 清空录音数据列表


class WhernerTex(QThread):
    txt_started = pyqtSignal(str)

    def __init__(self, ):
        super(WhernerTex, self).__init__()
        self.path = None

    def wrtext(self, audio_path):
        # 使用SpeechRecognition库的Recognizer类创建一个识别器对象
        recognizer = sr.Recognizer()
        # 读取音频文件
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        # 使用recognize_google方法将音频数据转换为文本，指定语言为中文
        try:
            text = recognizer.recognize_google(audio, language='zh-cn')
        except sr.UnknownValueError:
            text = "无法理解音频"  # 音频无法识别时的错误处理
        except sr.RequestError as e:
            text = f"请求出错; {e}"  # 请求有问题时的错误处理
        self.txt_started.emit(text)


class ObjectDetectionApp(QDialog):
    def __init__(self, username):
        super().__init__()

        # 创建主窗口
        self.setWindowIcon(QIcon('./img/ios-option-jizhang.png'))
        self.setWindowTitle("智能垃圾识别系统")
        self.resize(1030, 660)
        self.username = username
        self.is_recording = False
        self.samplerate = 44100  # 采样率
        self.filename = './init/recorded_audio.wav'  # 录音文件保存路径
        self.chunk_size = 1024  # 数据块大小
        self.p = pyaudio.PyAudio()  # 初始化 PyAudio 实例
        self.stream = None
        self.init_util()
        self.audio_recorder = AudioRecorder()
        self.audio_recorder.recording_started.connect(self.on_recording_started)
        self.audio_recorder.recording_stopped.connect(self.on_recording_stopped)
        self.audio_recorder.resd_path.connect(self.path_lbaef)
        model_path = './cmusphinx-zh-cn-5.2'
        self.config = {
            'verbose': False,
            'audio_file': self.filename,
            'buffer_size': 44100,
            'no_search': False,
            'full_utt': False,
            'hmm': os.path.join(model_path, 'zh_cn.cd_cont_5000'),
            'lm': os.path.join(model_path, 'zh_cn.lm.bin'),
            'dic': os.path.join(model_path, 'zh_cn.dic')
        }
        self.whernerTex = WhernerTex()
        self.whernerTex.txt_started.connect(self.loginText)

    def init_util(self):
        self.bg_label = QLabel(self)
        self.bg_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("./img/bj.jpg")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)  # 自动缩放图片以适应 QLabel 大小
        self.bg_label.resize(self.size())
        self.bt_label = QLabel(f'欢迎{self.username}使用本系统', self)
        self.bt_label.setGeometry(QRect(720, 10, 200, 30))
        self.bt_label.setStyleSheet("""

                 color: red;               /* 设置字体颜色 */
                 font-size: 15px;           /* 设置字体大小 */

             """)

        bt_label = QLabel('智能垃圾识别系统', self)
        bt_label.setFont(QFont('楷体', 15))
        bt_label.setGeometry(QRect(360, 10, 300, 30))
        self.log_txt = QTextEdit(self)
        self.log_txt.setGeometry(QRect(10, 60, 980, 250))
        self.log_txt.setReadOnly(True)
        self.lu_button = QPushButton('开始录音', self)
        self.lu_button.setGeometry(QRect(50, 610, 100, 30))
        self.lu_button.clicked.connect(self.on_lu_button_clicked)
        self.setStyleSheet('''
                                
                                  QTextEdit{

                            
                            border-radius: 5px; 
                            font-size:20px;
                            background-color: #66DD9;
                            color:  #3388FF;
                        }
                          QPushButton {

                              background-color:#3388FF ;
                              color: white;
                              border: none;

                              border-radius: 5px;
                              padding: 5px 10px;
                  }

                               QLineEdit{

                                   border: 1px solid #ccc;
                                   border-radius: 5px; 
                                   font-size:20px
                               }

                                 ''')
        self.bxt_label = QLabel(self)
        self.bxt_label.setGeometry(QRect(10, 320, 490, 250))
        self.tu_label = QLabel(self)
        self.tu_label.setGeometry(QRect(510, 320, 490, 250))
        self.radio_button1 = QRadioButton("播放", self)  # 综合
        self.radio_button1.setGeometry(QRect(250, 610, 100, 30))
        self.radio_button1.setStyleSheet("""

                      color: white;               /* 设置字体颜色 */
                      font-size: 20px;           /* 设置字体大小 */

                  """)
        select_button = QPushButton("查看记录", self)
        select_button.setGeometry(QRect(500, 610, 100, 30))
        select_button.clicked.connect(self.on_select_button_clicked)
        self.label = ClickableLabel("退出")
        self.label.setParent(self)
        self.label.setGeometry(950, 10, 200, 30)
        self.label.clicked.connect(self.on_label_clicked)
        self.label.setStyleSheet("""

                  color: white;               /* 设置字体颜色 */
                  font-size: 20px;           /* 设置字体大小 */

              """)
    def path_lbaef(self,path):
        self.filename=path
    def on_label_clicked(self):
        self.close()
        mainWin = LoginDialog()
        mainWin.show()
        mainWin.exec_()

    # 点击查看历史记录
    def on_select_button_clicked(self):
        sql = "select * from UserRecords where UserName = %s"
        parame = (self.username)
        data_list = execute_sql(sql, parame)
        if data_list:
            result_window = ResultWindow(data_list=data_list)
            result_window.show()
            result_window.exec_()

    # 点击开始录音
    def on_lu_button_clicked(self):
        if not self.audio_recorder.isRunning():  # 检查当前是否正在进行录音
            self.audio_recorder.start()  # 若没在录音则调用start()启动录音
        else:
            self.audio_recorder.stop_recording()  # 若已经在录音，择调用stop_recording()停止录音

    def on_recording_started(self):
        self.lu_button.setText("结束录音")  # 在录音开始时被调用，调用 setText() 方法将"开始录音"按钮的文本修改为"结束录音""

    def audio_to_text_cn(seff, audio_path):
        # 创建Recognizer对象
        recognizer = sr.Recognizer()
        # 读取音频文件
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        # 将音频转换为文字，指定中文的语言代码
        try:
            text = recognizer.recognize_google(audio, language='zh-cn')
        except sr.UnknownValueError:
            text = "无法理解音频"  # 音频无法识别时的错误处理
        except sr.RequestError as e:
            text = f"请求出错; {e}"  # 请求有问题时的错误处理
        return text  # 接受一个音频文件的路径作为参数，并返回该音频文件中的文本内容

    # 在录音停止时被调用：
    def on_recording_stopped(self):
        self.lu_button.setText("开始录音")  # 将录音按钮的文本设置为"开始录音"
        print(self.filename)
        filename1, filename = plt_imgs(self.filename)  # 调用 plt_imgs 函数处理录音文件，获取文件名并返回图像文件的路径
        self.load_recording(filename1, filename)  # 调用 load_recording 方法加载录音文件，并将获取的图像文件路径作为参数传递
        self.whernerTex.wrtext(self.filename)  # 调用 wrtext 方法处理录音文件，将数据信息写入文件中
        self.whernerTex.start()
        # decoder = AudioFile(**self.config)
        # txt = ''
        # for phrase in decoder:
        #     txt += str(phrase)
        # txt=self.audio_to_text_cn(self.filename)
        # print(txt)
        # self.loginText(txt)

    # 关闭窗口时先终止录音再执行关闭操作
    def closeEvent(self, event):
        self.audio_recorder.terminate()
        super().closeEvent(event)

    def loginText(self, text):
        usql = 'INSERT INTO UserRecords (UserName, UserInformation) VALUES ( %s, %s) '  # 构建 SQL 查询语句 usql，向数据库的 UserRecords 表中插入用户名和用户信息。
        parameters = (self.username, text)
        if execute_sql(usql, parameters) == None:           # 函数执行 SQL 查询语句，将参数传递给它，如果执行成功，则向用户显示信息插入数据失败的消息，并返回
            QMessageBox.information(self, "提醒", "插入数据失败！")
            return
        ssql = 'select  Q ,A from msgs '
        result = execute_sql(ssql)
        if result:
            data_txt = '小周正在学习中......'
            for i in result:                #
                if text in str(i[0]):
                    data_txt = i[1]
                    break
            self.log_txt.append(data_txt)       # 将data_txt中的信息追加到log_txt控件中显示
            if self.radio_button1.isChecked():
                self.status_cell(data_txt)      # 如果按钮radio_button1被选中，则调用status_cell方法，将data_txt中的信息显示在状态栏中，即播放声音

    def status_cell(self, text):

        engine = pyttsx.init()      # 初始化一个文本到语音转换引擎
        engine.say(text)            # 使用 say 方法将输入的文本传递给引擎，以进行语音合成
        engine.runAndWait()         # 使用runAndWait方法来等待语音合成引擎完成播放。

    def load_recording(self, filename1, filename):
        pixmap = QPixmap(filename1).scaled(500, 250)
        self.bxt_label.setPixmap(pixmap)
        pixmap1 = QPixmap(filename).scaled(500, 250)
        self.tu_label.setPixmap(pixmap1)


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)            # 初始化方法中调用了父类QLabel的初始化方法
        self.installEventFilter(self)       # 安装了事件过滤器

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.clicked.emit()
            return True
        return super().eventFilter(source, event)


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.setWindowIcon(QIcon('./img/ios-option-jizhang.png'))
        self.setFixedSize(1000, 600)
        self.initUI()

    def initUI(self):
        # 创建部件
        self.bg_label = QLabel(self)
        self.bg_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("./img/bj.jpg")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)  # 自动缩放图片以适应 QLabel 大小
        self.bg_label.resize(self.size())

        user_login_label = QLabel("  用 户 登 录", self)
        name_label = QLabel("用户名:", self)
        name_label.setFont(QFont('楷体', 12))
        self.name_input = QLineEdit(self)

        password_label = QLabel("密   码:", self)
        password_label.setFont(QFont('Arial', 12))
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.label = ClickableLabel("修改密码？")
        self.label.setParent(self)
        self.label.setGeometry(900, 360, 200, 30)
        self.label.clicked.connect(self.on_label_clicked)
        self.label.setStyleSheet("""
           
            color: red;               /* 设置字体颜色 */
            font-size: 15px;           /* 设置字体大小 */
         
        """)
        lio_button = QPushButton("注册", self)
        lio_button.setFont(QFont('楷体', 10))
        register_button = QPushButton("登录", self)
        register_button.setFont(QFont('楷体', 10))
        lio_button.clicked.connect(self.lio_buttonData)
        register_button.clicked.connect(self.register_login)
        # 设置部件位置和大小
        user_login_label.setGeometry(630, 100, 350, 30)
        name_label.setGeometry(610, 220, 100, 30)
        self.name_input.setGeometry(750, 220, 200, 30)
        password_label.setGeometry(610, 320, 100, 30)
        self.password_input.setGeometry(750, 320, 200, 30)

        lio_button.setGeometry(880, 480, 100, 30)
        register_button.setGeometry(650, 480, 100, 30)

        # 设置部件样式
        user_login_label.setAlignment(Qt.AlignCenter)
        user_login_label.setFont(QFont("楷体", 15))
        name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setStyleSheet('''
                          QLabel{
                          color:  #ccc;
                          }
                            QTextEdit{

                      border: 1px solid #ccc;
                      border-radius: 5px; 
                      font-size:20px;
                      background-color: #66DD9;
                      color:  #3388FF;
                  }
                    QPushButton {
                        
                        background-color:#3388FF ;
                        color: white;
                        border: none;
               
                        border-radius: 5px;
                        padding: 5px 10px;
            }

                         QLineEdit{

                             border: 1px solid #ccc;
                             border-radius: 5px; 
                             font-size:20px
                         }

                           ''')

    def lio_buttonData(self):
        username = self.name_input.text()
        password = self.password_input.text()
        if username == "" or password == "":
            QMessageBox.warning(self, "Warning", "用户名或密码不能为空！")
            return
        sql = 'SELECT * FROM users WHERE username = %s '
        params = (username)
        result = execute_sql(sql, params)
        if result:
            QMessageBox.warning(self, "Warning", "用户名已存在！")
            return
        usql = 'INSERT INTO users (username, password) VALUES (%s, %s)'
        uparams = (username, password)
        if execute_sql(usql, uparams) != None:
            QMessageBox.information(self, "提醒", "注册成功！")
            return

        QMessageBox.warning(self, "提醒", "注册失败！")
# 修改密码的按钮点击
    def on_label_clicked(self):
        self.close()
        mainWin = RegisterDialog()
        mainWin.show()
        mainWin.exec_()

    def register_login(self):
        username = self.name_input.text()
        password = self.password_input.text()
        if username == "" or password == "":
            QMessageBox.warning(self, "Warning", "用户名或密码不能为空！")
            return
        sql = 'SELECT * FROM users WHERE username = %s AND password = %s'
        params = (username, password)
        result = execute_sql(sql, params)
        if result:
            self.close()
            mainWin = ObjectDetectionApp(username)
            mainWin.show()
            mainWin.exec_()
        else:
            QMessageBox.warning(self, "Warning", "账号或者密码错误！")

# 注册界面
class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("register")
        self.setWindowIcon(QIcon('./img/ios-option-jizhang.png'))
        self.setFixedSize(1000, 600)
        self.bg_label = QLabel(self)
        self.bg_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("./img/bj.jpg")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)  # 自动缩放图片以适应 QLabel 大小
        self.bg_label.resize(self.size())

        # 创建注册信息布局
        user_login_label = QLabel("修 改 密 码", self)
        user_login_label.setGeometry(750, 100, 350, 30)
        user_login_label.setFont(QFont("Arial", 20))
        id_label = QLabel("用 户 名:", self)
        id_label.setFont(QFont('Arial', 15))
        id_label.setGeometry(650, 220, 100, 30)
        self.id_input = QLineEdit(self)
        self.id_input.setGeometry(750, 220, 200, 30)
        password_label = QLabel("原始密码:", self)
        password_label.setFont(QFont('Arial', 15))
        password_label.setGeometry(650, 280, 100, 30)
        new_password_label = QLabel("新 密 码:", self)
        new_password_label.setFont(QFont('Arial', 15))
        new_password_label.setGeometry(650, 340, 100, 30)
        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(750, 280, 200, 30)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input = QLineEdit(self)
        self.new_password_input.setGeometry(750, 340, 200, 30)
        self.new_password_input.setEchoMode(QLineEdit.Password)
        register_button = QPushButton("修改", self)
        register_button.setFont(QFont('Arial', 15))
        register_button.setGeometry(650, 480, 80, 30)
        register_button.clicked.connect(self.regisData)
        coles_button = QPushButton("返回", self)
        coles_button.setFont(QFont('Arial', 15))
        coles_button.setGeometry(880, 480, 80, 30)
        coles_button.clicked.connect(self.update_window)
        # 将注册信息组件添加到布局中
        self.setStyleSheet('''


                                 QLineEdit{

                                     border: 1px solid #ccc;
                                     border-radius: 5px; 
                                     font-size:20px
                                 }
                                     QPushButton {
                       
                        background-color:#3388FF ;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 10px;
            }
                                   QLabel{
                          color:  #ccc;
                          }

                                   ''')

    def regisData(self):
        username = self.id_input.text()
        password = self.password_input.text()
        newpassword = self.new_password_input.text()
        # 进行必要的验证
        if not username or not password or not newpassword:
            QMessageBox.warning(self, "警告", "请输入账号和密码!")
            return
        if password == newpassword:
            QMessageBox.warning(self, "Warning", "新密码不能与原始密码相同！")
            return

        sql = 'SELECT * FROM users WHERE username = %s '
        params = (username)
        result = execute_sql(sql, params)
        if not result:
            QMessageBox.warning(self, "Warning", "用户名不存在！")
            return
        usql = 'UPDATE users SET password = %s WHERE username = %s'
        uparams = (newpassword, username)
        execute_sql(usql, uparams)
        QMessageBox.information(self, "提醒", "修改成功！")

    def update_window(self):
        self.close()
        main_window = LoginDialog()
        main_window.show()
        main_window.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginDialog()
    window.show()
    sys.exit(app.exec_())
