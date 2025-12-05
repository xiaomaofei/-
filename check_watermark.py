import argparse
import soundfile as sf
import numpy as np


def text_to_bits(text: str) -> np.ndarray:
    data = text.encode("utf-8")
    bits = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)
    return np.array(bits, dtype=np.uint8)


def extract_lsb_bits(int16_audio: np.ndarray, n_bits: int, repeat: int = 1000) -> np.ndarray:
    """
    从音频中读取 LSB 比特，并做重复投票。
    """
    if int16_audio.ndim == 2:
        target = int16_audio[0]  # 只看第一个声道
    else:
        target = int16_audio

    n_samples = target.shape[0]
    total_bits = n_bits * repeat
    if total_bits > n_samples:
        repeat = n_samples // n_bits
        total_bits = repeat * n_bits
        if repeat == 0:
            raise ValueError("音频太短，无法读取足够的水印比特。")

    lsbs = (target[:total_bits] & 1).astype(np.uint8)

    # 每 n_bits 为一组，做 repeat 次数的多数投票
    lsbs = lsbs.reshape(repeat, n_bits)  # [repeat, n_bits]
    votes = lsbs.mean(axis=0)  # 每个 bit 的平均值
    recovered = (votes >= 0.5).astype(np.uint8)
    return recovered


def bits_to_text(bits: np.ndarray) -> str:
    if len(bits) % 8 != 0:
        bits = bits[: len(bits) // 8 * 8]
    bytes_out = []
    for i in range(0, len(bits), 8):
        b = 0
        for j in range(8):
            b = (b << 1) | int(bits[i + j])
        bytes_out.append(b)
    try:
        return bytes(bytes_out).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser(description="检测 WAV 文件中的 LSB 水印")
    parser.add_argument("--input", required=True, help="输入音频路径（wav）")
    parser.add_argument("--id", default="wf", help="期望的水印内容（字符串），默认 'wf'")
    args = parser.parse_args()

    print(f"[CHECK] 读取音频: {args.input}")
    audio, sr = sf.read(args.input)
    print(f"[CHECK] 采样率: {sr}, 形状: {audio.shape}")

    if audio.dtype != np.int16:
        audio_int16 = (audio * 32768.0).astype(np.int16)
    else:
        audio_int16 = audio

    if audio_int16.ndim == 1:
        audio_int16_proc = audio_int16
    else:
        audio_int16_proc = audio_int16.T  # [N,C] -> [C,N]

    wm_bits = text_to_bits(args.id)
    print(f"[CHECK] 期望水印: {args.id}, 比特长度: {len(wm_bits)}")

    recovered_bits = extract_lsb_bits(audio_int16_proc, len(wm_bits), repeat=1000)
    recovered_text = bits_to_text(recovered_bits)

    print(f"[CHECK] 解码出的文本: {repr(recovered_text)}")

    if recovered_text.startswith(args.id):
        print("[CHECK] ✅ 检测到匹配水印！")
    else:
        print("[CHECK] ❌ 未检测到期望水印。")


if __name__ == "__main__":
    main()

