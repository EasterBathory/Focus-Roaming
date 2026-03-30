"""
阿里云视觉智能 - 图像场景分类
将检测到的场景标签映射到拍摄偏好标签
"""
import os, hmac, hashlib, base64, json, time, uuid
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import URLError

# 场景标签 → 拍摄偏好映射
SCENE_MAP = {
    # 星空/天文
    "星空": "星空", "银河": "星空", "夜空": "星空", "天文": "星空",
    "night sky": "星空", "milky way": "星空", "galaxy": "星空",
    # 城市夜景
    "城市夜景": "城市夜景", "夜景": "城市夜景", "城市": "城市夜景",
    "建筑": "城市夜景", "skyline": "城市夜景", "cityscape": "城市夜景",
    # 自然风光
    "山": "自然风光", "山脉": "自然风光", "森林": "自然风光",
    "草原": "自然风光", "瀑布": "自然风光", "湖泊": "自然风光",
    "mountain": "自然风光", "forest": "自然风光", "landscape": "自然风光",
    # 海景
    "海": "海景", "海滩": "海景", "海岸": "海景", "大海": "海景",
    "ocean": "海景", "beach": "海景", "sea": "海景",
    # 人像
    "人物": "人像", "人像": "人像", "portrait": "人像", "人": "人像",
    # 日出日落
    "日出": "日出日落", "日落": "日出日落", "黄昏": "日出日落",
    "sunrise": "日出日落", "sunset": "日出日落", "golden hour": "日出日落",
    # 雪景
    "雪": "雪景", "雪山": "雪景", "冰雪": "雪景", "snow": "雪景",
}

def _sign(method, params: dict, secret: str) -> str:
    """阿里云 API 签名"""
    sorted_params = sorted(params.items())
    query = "&".join(f"{quote(k, safe='')}={quote(str(v), safe='')}" for k, v in sorted_params)
    string_to_sign = f"{method}&{quote('/', safe='')}&{quote(query, safe='')}"
    key = (secret + "&").encode()
    sig = hmac.new(key, string_to_sign.encode(), hashlib.sha1).digest()
    return base64.b64encode(sig).decode()

def analyze_image(image_bytes: bytes, content_type: str = "image/jpeg") -> list[str]:
    """
    调用阿里云图像场景分类 API
    返回映射后的拍摄偏好标签列表
    """
    ak_id = os.getenv("ALI_AK_ID", "")
    ak_secret = os.getenv("ALI_AK_SECRET", "")
    if not ak_id or not ak_secret:
        return []

    # 转 base64
    img_b64 = base64.b64encode(image_bytes).decode()

    params = {
        "Action": "ClassifyingRubbish",  # 使用场景识别接口
        "Format": "JSON",
        "Version": "2019-09-30",
        "AccessKeyId": ak_id,
        "SignatureMethod": "HMAC-SHA1",
        "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "ImageURL": f"data:{content_type};base64,{img_b64}",
    }

    # 改用图像场景分类接口
    params["Action"] = "RecognizeScene"
    params["Signature"] = _sign("GET", params, ak_secret)

    url = "https://imagerecog.cn-shanghai.aliyuncs.com/?" + "&".join(
        f"{quote(k)}={quote(str(v))}" for k, v in params.items()
    )

    try:
        req = Request(url, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (URLError, Exception):
        return []

    # 解析返回的场景标签
    raw_tags = []
    try:
        tags = data.get("Data", {}).get("Tags", [])
        for t in tags:
            name = t.get("Value", "") or t.get("Name", "")
            confidence = float(t.get("Confidence", 0))
            if confidence >= 0.3:
                raw_tags.append(name)
    except Exception:
        return []

    # 映射到偏好标签
    pref_tags = []
    for raw in raw_tags:
        for key, pref in SCENE_MAP.items():
            if key.lower() in raw.lower() and pref not in pref_tags:
                pref_tags.append(pref)

    return pref_tags


def update_user_tags(current_tags_json: str, new_tags: list[str]) -> str:
    """
    合并新标签到用户偏好权重
    current_tags_json: '{"星空":3,"城市夜景":1}'
    返回更新后的 JSON 字符串
    """
    try:
        tags = json.loads(current_tags_json or "{}")
    except Exception:
        tags = {}

    for tag in new_tags:
        tags[tag] = tags.get(tag, 0) + 1

    return json.dumps(tags, ensure_ascii=False)


def get_top_preferences(tags_json: str, top_n: int = 3) -> list[str]:
    """返回权重最高的前 N 个偏好标签"""
    try:
        tags = json.loads(tags_json or "{}")
    except Exception:
        return []
    sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    return [t[0] for t in sorted_tags[:top_n]]
