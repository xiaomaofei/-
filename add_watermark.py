import argparse
import soundfile as sf
import numpy as np


def text_to_bits(text: str) -> np.ndarray:
    """把字符串转成比特数组，例如 'wf' -> [0,1,1,1,...]"""
    data = text.encode("utf-8")
    bits = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)
    return np.array(bits, dtype=np.uint8)


def embed_lsb(int16_audio: np.ndarray, watermark_bits: np.ndarray) -> np.ndarray:
    """
    利用 LSB 给音频增加水印。
    自动重复比特直到填满整个音频长度。
    """
    if int16_audio.ndim == 2:
        target = int16_audio[0].copy()  # 只写入第一个声道
        multi_channel = True
    else:
        target = int16_audio.copy()
        multi_channel = False

    n_samples = target.shape[0]

    # 动态计算 repeat，保证 bits 的长度 >= n_samples
    repeat = (n_samples + len(watermark_bits) - 1) // len(watermark_bits)
    bits_full = np.tile(watermark_bits, repeat)[:n_samples]  # 截断到刚好匹配长度

    # 写入 LSB
    watermarked = (target & ~1) | bits_full

    if multi_channel:
        int16_audio = int16_audio.copy()
        int16_audio[0] = watermarked
        return int16_audio
    else:
        return watermarked


def main():
    parser = argparse.ArgumentParser(description="给 WAV 文件加上 LSB 水印")
    parser.add_argument("--input", required=True, help="输入音频路径 WAV")
    parser.add_argument("--output", required=True, help="输出音频路径 WAV")
    parser.add_argument("--id", default="wf", help="水印内容字符串")
    args = parser.parse_args()

    print(f"[ADD] 读取音频: {args.input}")
    audio, sr = sf.read(args.input)
    print(f"[ADD] 采样率: {sr}, 形状: {audio.shape}")

    # 转 int16
    if audio.dtype != np.int16:
        audio_int16 = (audio * 32768.0).astype(np.int16)
    else:
        audio_int16 = audio

    # 转为 [C,N]
    if audio_int16.ndim == 1:
        audio_int16_proc = audio_int16
    else:
        audio_int16_proc = audio_int16.T  # [N,C] -> [C,N]

    wm_bits = text_to_bits(args.id)
    print(f"[ADD] 水印内容: {args.id}, 比特长度: {len(wm_bits)}")

    wm_audio_int16 = embed_lsb(audio_int16_proc, wm_bits)

    # 还原维度
    if audio_int16.ndim == 1:
        wm_audio_int16 = wm_audio_int16
    else:
        wm_audio_int16 = wm_audio_int16.T  # [C,N] -> [N,C]

    # 保存为 float32 WAV
    wm_audio_float = wm_audio_int16.astype(np.float32) / 32768.0

    sf.write(args.output, wm_audio_float, sr)
    print(f"[ADD] 写入完成: {args.output}")


if __name__ == "__main__":
    main()

