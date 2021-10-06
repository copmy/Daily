import requests
import re
import os
import subprocess



# 对网址进行分割获取BV号
def get_Bv(b_url) :
    bv = b_url.split("video/")[-1]
    print(bv)
    if "/" in bv :
        bv = bv.split("/")[0]
    elif "?" in bv :
        bv = bv.split("?")[0]
    print("BV号:" + bv)
    return bv


# 创建文件存放路径
def mkdir_bv_path(bv) :
    if not os.path.exists("video"):
        os.mkdir("video")
    if not os.path.exists(f"video/{bv}") :
        os.mkdir(f"video/{bv}")


def get_Html(b_url) :
    # b站网页url
    response = requests.get(b_url)
    if response.status_code == 200 :
        print("网页请求成功!")
        return response.text
    else :
        print("网页请求失败!")
        return


# 获取视频和音频的地址
def get_VideoAndAudio(text) :
    audio_url = re.search(r'"audio":\[\{"id":(\d+),"baseUrl":"(?P<audio>.*?)",', text, re.S).group("audio")
    vedio_url = re.search(r'{"id":\d+,"baseUrl":"(?P<vedio>.*?)"', text).group("vedio")
    if audio_url and vedio_url :
        print("视频and音频地址获取成功!")
        print(vedio_url + '\n' + audio_url)
        return vedio_url, audio_url
    else :
        print("视频and音频地址获取失败!!!")
        return


# 获取视频和音频长度的最大值
def get_range_max(b_url, m4s_url) :
    headers = {
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "referer" : b_url,
        "range" : "bytes=0-10"
    }
    response = requests.get(m4s_url, headers=headers)
    if response.status_code == 206 :
        resp_header = response.headers
        con_range = resp_header["Content-Range"]
        con_range = con_range.split("/")[-1]
        return con_range


# 请求地址下载保存
def Save_M4s(bv, b_url, d_url, max, save_name) :
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "range" : f"bytes=0-{int(max)}",
        "referer" : b_url,
    }

    m4s_data = requests.get(d_url, headers=headers)
    print(m4s_data.status_code)
    if m4s_data.status_code == 206 :

        if not os.path.exists(f"video/{bv}/{save_name}.mp4") :
            print("开始下载!" + d_url)
            with open(f"video/{bv}/{save_name}.mp4", 'wb')as fp :
                fp.write(m4s_data.content)
        print("文件写入成功!")
    else :
        print("下载地址请求失败!")


# 将视频与音频合并
def marge(bv) :
    video_path = f"E:\\ProgramData\\Requests\\Include\\日常玩耍\\m3u8下载\\video\\{bv}\\{bv}_video.mp4"
    audio_path = f"E:\\ProgramData\\Requests\\Include\\日常玩耍\\m3u8下载\\video\\{bv}\\{bv}_audio.mp4"
    out_path = f"E:\\ProgramData\\Requests\\Include\\日常玩耍\\m3u8下载\\video\\{bv}\\{bv}.mp4"
    subprocess.call(
        f"E:\\GameDownload\\ffmpeg-N-101944-g33db0cbfd0-win64-gpl-shared\\bin\\ffmpeg.exe -i " + video_path + " -i " + audio_path + " -acodec copy -vcodec copy " + out_path,
        shell=True)

#删除多余文件
def del_file(bv) :
    path = os.listdir(f"video/{bv}")
    for item in path :
        if "audio" in item :
            print(item)
            os.remove(f"video/{bv}/{item}")
        elif "video" in item :
            print(item)
            os.remove(f"video/{bv}/{item}")


def main(b_url) :
    bv = get_Bv(b_url)
    mkdir_bv_path(bv)
    page_text = get_Html(b_url)
    video_url, audio_url = get_VideoAndAudio(page_text)
    video_max = get_range_max(b_url, video_url)
    audio_max = get_range_max(b_url, audio_url)
    Save_M4s(bv, b_url, video_url, video_max, f"{bv}_video")
    Save_M4s(bv, b_url, audio_url, audio_max, f"{bv}_audio")
    marge(bv)
    del_file(bv)


if __name__ == '__main__' :
    b_url = "https://www.bilibili.com/video/BV1G64y127Uw?spm_id_from=333.999.0.0"
    main(b_url)
