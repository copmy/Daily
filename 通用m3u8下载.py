# encoding=gbk
import requests
import os
import re
from Crypto.Cipher import AES
from concurrent.futures import ProcessPoolExecutor
import time
from urllib.parse import urljoin


"""
˵��:��Ҫ���ļ���ǰ·���´���file��video�ļ���
    ���и���os.chdir��·��Ϊ��ǰ�ļ�����·��
"""


# ����m3u8
def download_m3u8(m3u8_url, m3u8_name) :
    os.chdir("E:\\ProgramData\\Requests\\Include\\�ճ���ˣ\\m3u8����\\")
    headers = {
        # �ֻ���
        # "user-agent" :"User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat"
        # ���԰�
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }
    response = requests.get(m3u8_url, headers=headers)
    if response.status_code == 200 :
        with open(f'file/{m3u8_name}.m3u8', 'wb')as fp :
            fp.write(response.content)
        print(f'{m3u8_name}.m3u8 ���سɹ�!!!')
    else :
        print('����״̬:', response.status_code, 'm3u8����ʧ��!!')


# ����ts�ļ�
def download_ts(ts_url, ts_name, m3u8_name) :
    print(f'{ts_name}', '��ʼ����!')
    try :
        response = requests.get(ts_url, timeout=10)
        with open(f'video/{m3u8_name}/{ts_name}', 'wb')as fp :
            fp.write(response.content)
        if os.stat(f'video/{m3u8_name}/{ts_name}')[6] == 0 :
            download_ts(ts_url, ts_name, m3u8_name)
    except Exception as e :
        print(ts_name, "�����쳣�������أ�")
        download_ts(ts_url, ts_name, m3u8_name)

    print(f'{ts_name}', '���سɹ�!')


# ����ts��ַ������
def repair_ts_url(url, m3u8_name) :
    print("��ַȱʧ���ڲ���!")
    with ProcessPoolExecutor(9) as pool :
        with open(f'file/{m3u8_name}.m3u8', 'r')as fp :
            for line in fp :
                if line.startswith('#') :
                    continue
                line = urljoin(url, line.strip())
                ts_name = line.rsplit('/', 1)[-1].split('?')[0]
                pool.submit(download_ts, ts_url=line, ts_name=ts_name, m3u8_name=m3u8_name)


# ��ȡm3u8�ļ��е�ts����������
def reader_m3u8_ts(url, m3u8_name) :
    if not os.path.exists(f'file/{m3u8_name}.m3u8') :
        print(f"error: No such file or directory: '{m3u8_name}.m3u8'")
        return
    if not os.path.exists(f'video/{m3u8_name}') :
        os.mkdir(f'video/{m3u8_name}')
    with ProcessPoolExecutor(10) as pool :
        with open(f'file/{m3u8_name}.m3u8', 'r')as fp :
            for line in fp :
                if line.startswith('#') :
                    continue
                line = line.strip()
                if 'http' not in line :
                    print('ts�����ص�ַ�������벹��')
                    repair_ts_url(url, m3u8_name)
                    break
                ts_name = line.rsplit('/', 1)[-1].split('?')[0]
                pool.submit(download_ts, ts_url=line, ts_name=ts_name, m3u8_name=m3u8_name)


# �鿴�Ƿ���©��ts�ļ�
def Make_up_ts(url, m3u8_name) :
    with open(f'file/{m3u8_name}.m3u8', 'r')as fp :
        for line in fp :
            if line.startswith('#') :
                continue
            line = urljoin(url, line.strip())
            ts_name = line.rsplit('/', 1)[-1].split('?')[0]
            if not os.path.exists(f'video/{m3u8_name}/{ts_name}') :
                download_ts(line, ts_name, m3u8_name)
                print(f'{ts_name}', '����ɹ�!')


# ������Կkey ����еĻ�
def download_key(url, m3u8_name) :
    key_url = ''
    with open(f'file/{m3u8_name}.m3u8', 'r')as fp :
        for line in fp :
            if '#EXT-X-KEY:' in line :
                key_url = re.search('URI="(.*?)"', line).group(1)
                if key_url.find("http") == -1 :
                    key_url = urljoin(url, key_url)
                break
    if key_url :
        response = requests.get(key_url)
        with open(f'file/{m3u8_name}.key', 'wb')as fp :
            fp.write(response.content)
        print(f'{m3u8_name}.key ��Կ�������!')
        return True
    else :
        print('û��key,�������')
        return False


# ��ȡ��Կkey����
def open_read_key(key_name) :
    with open(f'file/{key_name}.key', 'rb')as fp :
        line = fp.read()
    return line


# ������Կ���н���
def AES_decode_ts(m3u8_name, key) :
    with open(f'file/{m3u8_name}.m3u8', 'r')as fp :
        for line in fp :
            if line.startswith('#') :
                continue
            line = line.strip()
            # ����׺���滻��ts
            ts_name = line.rsplit('/', 1)[-1].split('?')[0]
            read_ts_decode(m3u8_name, ts_name, key)


# ���ܾ������
def read_ts_decode(m3u8_name, ts_name, key) :
    aes = AES.new(key=key, IV=b'0000000000000000', mode=AES.MODE_CBC)
    with open(f'video/{m3u8_name}/{ts_name}', 'rb')as fp :
        with open(f'video/{m3u8_name}/temp_{ts_name}', 'wb')as f :
            bs = fp.read()
            f.write(aes.decrypt(bs))
            print(f'temp_{ts_name} �������!')


# ��дbat�ű���ts�ļ�д��
def write_bat(m3u8_name) :
    command = 'copy /b '
    ts_name_all = []
    with open(f'file/{m3u8_name}.m3u8', 'r')as fp :
        if os.path.exists(f'file/{m3u8_name}.key') :
            for line in fp :
                if line.startswith('#') :
                    continue
                line = line.strip()
                ts_name = 'temp_' + line.rsplit('/', 1)[-1].split('?')[0]
                ts_name_all.append(ts_name)
        else :
            for line in fp :
                if line.startswith('#') :
                    continue
                line = line.strip()
                ts_name = line.rsplit('/', 1)[-1].split('?')[0]
                ts_name_all.append(ts_name)

    for i in range(len(ts_name_all)) :
        if i == len(ts_name_all) - 1 :
            command += ts_name_all[i]
        else :
            command += f'{ts_name_all[i]}+'
    command += f' {m3u8_name}.mp4'

    with open(f'video/{m3u8_name}/{m3u8_name}.bat', 'w')as fp :
        fp.write(command)
    print(f'{m3u8_name}.bat д�����!')


# ����bat
def run_bat(name) :
    os.chdir(f"E:\\ProgramData\\Requests\\Include\\�ճ���ˣ\\m3u8����\\video\\{name}")
    os.startfile(f"{name}.bat")
    print("���ںϲ��ļ�!")
    while True :
        result = os.popen('tasklist -fi "IMAGENAME eq cmd.exe"')
        result = result.read().splitlines()[3 :]
        if len(result) < 2 :
            break


# ɾ�������ļ�
def del_files(name) :
    # cd
    os.chdir("E:\\ProgramData\\Requests\\Include\\�ճ���ˣ\\m3u8����\\video\\")
    data = os.listdir(f"{name}")
    if f"{name}.mp4" in data :
        for item in data :
            if item != f"{name}.mp4" :
                os.remove(f"{name}\\{item}")
        print("�ļ��������")
    else :
        print("mp4�ļ������������ºϳ�!")


# ������
def main(url, name) :
    download_m3u8(url, name)
    reader_m3u8_ts(url, name)
    status = download_key(url, name)
    Make_up_ts(url, name)
    if status :
        key = open_read_key(name)
        AES_decode_ts(name, key)
    write_bat(name)
    run_bat(name)
    del_files(name)


if __name__ == '__main__' :
    # name�в��ܰ����ո�
    name = ''
    url = '''
    https://videos7.lzafny.com/SYYY17GFH/10000kb/hls/index.m3u8?sign=bcea7c1d46d08c93badc23ab01172253&t=1632597805
    '''
    url = url.strip()
    start_time = time.time()
    main(url, name)
    end_time = time.time()
    print(name + ".mp4�ϳ��������!")
    print('��������ʱ��:', round((end_time - start_time) / 60, 2), '����')
