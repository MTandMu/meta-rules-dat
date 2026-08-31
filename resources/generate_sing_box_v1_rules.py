import os
import json

# 💡 动态获取脚本自身所在的 resources 目录的上一级，即项目根目录的绝对路径
# 这样无论在哪个目录下执行该脚本，都能精准定位到 geo/ 和 geo-lite/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定义需要处理的四个官方目标路径（使用绝对路径拼接）
TARGET_DIRS = [
    os.path.join(BASE_DIR, "geo", "geosite"),
    os.path.join(BASE_DIR, "geo", "geoip"),
    os.path.join(BASE_DIR, "geo-lite", "geosite"),
    os.path.join(BASE_DIR, "geo-lite", "geoip"),
    os.path.join("asn")
]

# 1.9.3 版本 sing-box 不支持的 V2 新匹配字段
V2_UNSUPPORTED_KEYS = {"adblocker", "invert"}

def process_and_save_v1(file_path):
    if file_path.endswith('.v1.json'):
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            # 将版本降级为 1
            data["version"] = 1

            # 剔除 1.9.3 无法识别的 V2 独有字段
            if "rules" in data and isinstance(data["rules"], list):
                for rule in data["rules"]:
                    if isinstance(rule, dict):
                        for unsupported_key in V2_UNSUPPORTED_KEYS:
                            if unsupported_key in rule:
                                del rule[unsupported_key]

            # 构造新文件名：abc.json -> abc.v1.json
            output_path = file_path.replace('.json', '.v1.json')

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True

    except Exception as e:
        print(f"❌ 处理文件失败 {file_path}: {e}")
    return False

def main():
    success_count = 0
    total_count = 0

    for abs_dir in TARGET_DIRS:
        if not os.path.exists(abs_dir):
            print(f"⚠️ 找不到目录，跳过: {abs_dir}")
            continue

        print(f"📂 正在扫描目录: {abs_dir} ...")
        for root, _, files in os.walk(abs_dir):
            for file in files:
                if file.endswith('.json') and not file.endswith('.v1.json'):
                    total_count += 1
                    file_path = os.path.join(root, file)
                    if process_and_save_v1(file_path):
                        success_count += 1

    print(f"\n🎉 转换结束！读取了 {total_count} 个官方规则，成功生成了 {success_count} 个对应的 *.v1.json 文件。")

if __name__ == "__main__":
    main()
