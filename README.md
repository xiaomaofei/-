(orph) fei.wang@gpu-Rack-Server:~/Orpheus-TTS/additional_inference_options/watermark_audio$ python add_watermark.py   --input  laoluo-30s-wf.wav  --output  laoluo-30s12-5.wav  --id 125
[ADD] 读取音频: laoluo-30s-wf.wav
[ADD] 采样率: 16000, 形状: (538378,)
[ADD] 水印内容: 125, 比特长度: 24
[ADD] 写入完成: laoluo-30s12-5.wav
(orph) fei.wang@gpu-Rack-Server:~/Orpheus-TTS/additional_inference_options/watermark_audio$ python  check_watermark.py    --input  laoluo-30s12-5.wav   --id 125
[CHECK] 读取音频: laoluo-30s12-5.wav
[CHECK] 采样率: 16000, 形状: (538378,)
[CHECK] 期望水印: 125, 比特长度: 24
[CHECK] 解码出的文本: '125'
[CHECK] ✅ 检测到匹配水印！
音频文件隐写信息，不影响声纹的波动。
