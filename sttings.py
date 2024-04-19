import pymysql
import librosa
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
# matplotlib.use('TkAgg')



def plt_imgs(filename):
    plt.figure()
    # 音频文件路径
    audio_path = filename
    # 加载音频文件，默认参数会将音频转换为单声道并重采样到22050Hz
    y, sr = librosa.load(audio_path, sr=22050, mono=True)
    # 绘制波形图

    librosa.display.waveshow(y, sr=sr)
    plt.title('Waveform of the Audio', fontproperties="SimSun",fontsize=20)  # 设置标题
    plt.xlabel('Time (s)', fontsize=12)  # 设置x轴标签
    plt.ylabel('Amplitude', fontsize=12)  # 设置y轴标签
    plt.tight_layout()  # 调整布局以避免重叠
    filename1 = f'./init/spectrogram_4.png'
    plt.savefig( filename1)

    S, phase = librosa.magphase(librosa.stft(y))
    log_S = librosa.amplitude_to_db(S, ref=np.max)
    # 绘制语谱图

    librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel', fmax=8000)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram of the Audio', fontproperties="SimSun",fontsize=20)
    filename = f'./init/spectrogram.png'
    plt.savefig(filename)
    return filename1, filename


def mysql_connection():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root',
                           passwd='123456',
                           db='ascent', charset='utf8')  # 数据库链接

    cur = conn.cursor()

    return conn, cur

def execute_sql(query, parameters=None):
    conn ,cursor = mysql_connection()
    try:
        cursor.execute(query, parameters)
        result = cursor.fetchall()
        return result
    except Exception  as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.commit()

