"""
Scene-driven photography recommendation engine.
Each scene defines: required APIs, scoring weights, and recommendation logic.
API calls are strictly controlled - only fetch what the scene needs.
"""
import math
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

# ============================================================
#  Scene Definitions
# ============================================================

SCENE_CATALOG = {
    # --- Basic ---
    "star":         {"label": "星空",     "group": "basic",    "apis": ["weather", "astronomy", "moon", "light_pollution"]},
    "city":         {"label": "城市",     "group": "basic",    "apis": ["weather", "air_quality"]},
    "snow":         {"label": "雪山",     "group": "basic",    "apis": ["weather"]},
    "desert":       {"label": "沙漠",     "group": "basic",    "apis": ["weather"]},
    "sea":          {"label": "海景",     "group": "basic",    "apis": ["weather", "astronomy"]},
    "mountain":     {"label": "山景",     "group": "basic",    "apis": ["weather"]},
    "landform":     {"label": "风蚀地貌", "group": "basic",    "apis": ["weather", "astronomy"]},
    # --- Advanced ---
    "golden_hour":  {"label": "日出日落", "group": "advanced",  "apis": ["astronomy", "weather"]},
    "blue_hour":    {"label": "蓝调时刻", "group": "advanced",  "apis": ["astronomy", "weather"]},
    "sea_of_clouds":{"label": "云海",     "group": "advanced",  "apis": ["weather"]},
    "fog":          {"label": "雾景",     "group": "advanced",  "apis": ["weather"]},
    "rainbow":      {"label": "彩虹",     "group": "advanced",  "apis": ["weather"]},
    "storm":        {"label": "雷暴",     "group": "advanced",  "apis": ["weather"]},
    "rime":         {"label": "雾凇",     "group": "advanced",  "apis": ["weather"]},
    "tide":         {"label": "潮汐",     "group": "advanced",  "apis": ["weather", "astronomy"]},
    "city_night":   {"label": "城市夜景", "group": "advanced",  "apis": ["weather", "astronomy"]},
    "light_trails": {"label": "车轨",     "group": "advanced",  "apis": ["weather", "astronomy"]},
    "grassland":    {"label": "草原",     "group": "advanced",  "apis": ["weather"]},
    "dunes":        {"label": "沙丘光影", "group": "advanced",  "apis": ["weather", "astronomy"]},
    "snow_clear":   {"label": "雪后晴天", "group": "advanced",  "apis": ["weather"]},
    "autumn":       {"label": "秋景",     "group": "advanced",  "apis": ["weather"]},
    "flower":       {"label": "花海",     "group": "advanced",  "apis": ["weather"]},
    "architecture": {"label": "建筑摄影", "group": "advanced",  "apis": ["weather"]},
}

# Scoring weight definitions per scene
SCORE_WEIGHTS = {
    "star":         {"cloud": 0.40, "light_pollution": 0.30, "moon": 0.30},
    "city":         {"cloud": 0.50, "aqi": 0.50},
    "snow":         {"temp": 0.40, "cloud": 0.30, "wind": 0.30},
    "desert":       {"cloud": 0.40, "wind": 0.30, "visibility": 0.30},
    "sea":          {"cloud": 0.35, "wind": 0.35, "golden": 0.30},
    "mountain":     {"cloud": 0.40, "humidity": 0.30, "wind": 0.30},
    "landform":     {"cloud": 0.35, "visibility": 0.35, "golden": 0.30},
    "golden_hour":  {"cloud": 0.60, "golden": 0.40},
    "blue_hour":    {"cloud": 0.60, "blue": 0.40},
    "sea_of_clouds":{"humidity": 0.35, "temp_diff": 0.30, "wind": 0.20, "cloud": 0.15},
    "fog":          {"humidity": 0.50, "wind": 0.30, "temp_diff": 0.20},
    "rainbow":      {"rain_sun": 0.60, "cloud": 0.40},
    "storm":        {"storm_prob": 0.50, "cloud": 0.30, "rain": 0.20},
    "rime":         {"temp_below_zero": 0.50, "humidity": 0.50},
    "tide":         {"cloud": 0.30, "wind": 0.30, "golden": 0.40},
    "city_night":   {"cloud": 0.50, "sunset_timing": 0.50},
    "light_trails": {"cloud": 0.40, "sunset_timing": 0.60},
    "grassland":    {"cloud": 0.50, "wind": 0.50},
    "dunes":        {"cloud": 0.35, "wind": 0.30, "golden": 0.35},
    "snow_clear":   {"snow_then_clear": 0.60, "cloud": 0.40},
    "autumn":       {"temp": 0.50, "cloud": 0.50},
    "flower":       {"temp": 0.40, "rain": 0.30, "cloud": 0.30},
    "architecture": {"cloud": 0.50, "visibility": 0.50},
}

# ============================================================
#  API Dispatcher - only call what's needed
# ============================================================

def resolve_required_apis(scenes: List[str]) -> set:
    """Given selected scenes, return the union of required APIs (deduplicated)."""
    apis = set()
    for s in scenes:
        if s in SCENE_CATALOG:
            apis.update(SCENE_CATALOG[s]["apis"])
    return apis


async def fetch_weather_current(lat: float, lng: float) -> dict:
    """Fetch current weather from Open-Meteo (free, no key)."""
    import httpx
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lng}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,"
        f"wind_speed_10m,cloud_cover,visibility,precipitation"
        f"&timezone=auto"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json().get("current", {})


async def fetch_weather_hourly(lat: float, lng: float) -> dict:
    """Fetch 24h hourly forecast from Open-Meteo."""
    import httpx
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lng}"
        f"&hourly=temperature_2m,relative_humidity_2m,cloud_cover,"
        f"visibility,wind_speed_10m,precipitation_probability,weather_code"
        f"&forecast_days=1&timezone=auto"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json().get("hourly", {})


async def fetch_astronomy(lat: float, lng: float) -> dict:
    """Fetch sunrise/sunset/twilight from Open-Meteo."""
    import httpx
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lng}"
        f"&daily=sunrise,sunset&timezone=auto&forecast_days=1"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        daily = r.json().get("daily", {})
        sunrise = daily.get("sunrise", [None])[0]
        sunset = daily.get("sunset", [None])[0]
        # Calculate blue hour and golden hour
        result = {"sunrise": sunrise, "sunset": sunset}
        if sunrise:
            sr = datetime.fromisoformat(sunrise)
            result["golden_am_start"] = (sr - timedelta(minutes=30)).isoformat()
            result["golden_am_end"] = (sr + timedelta(minutes=30)).isoformat()
            result["blue_am_start"] = (sr - timedelta(minutes=60)).isoformat()
            result["blue_am_end"] = (sr - timedelta(minutes=15)).isoformat()
        if sunset:
            ss = datetime.fromisoformat(sunset)
            result["golden_pm_start"] = (ss - timedelta(minutes=30)).isoformat()
            result["golden_pm_end"] = (ss + timedelta(minutes=30)).isoformat()
            result["blue_pm_start"] = (ss + timedelta(minutes=15)).isoformat()
            result["blue_pm_end"] = (ss + timedelta(minutes=60)).isoformat()
            result["astro_twilight_end"] = (ss + timedelta(minutes=90)).isoformat()
        return result


def calc_moon_phase() -> dict:
    """Calculate current moon phase and illumination."""
    known = datetime(2000, 1, 6, 18, 14)
    cycle = 29.530588853
    now = datetime.utcnow()
    phase = (((now - known).total_seconds() / 86400) % cycle + cycle) % cycle
    pct = phase / cycle
    illum = round(abs(math.cos(pct * 2 * math.pi)) * 100)
    if pct < 0.03 or pct > 0.97:
        name = "新月"
    elif pct < 0.22:
        name = "娥眉月"
    elif pct < 0.28:
        name = "上弦月"
    elif pct < 0.47:
        name = "盈凸月"
    elif pct < 0.53:
        name = "满月"
    elif pct < 0.72:
        name = "亏凸月"
    elif pct < 0.78:
        name = "下弦月"
    else:
        name = "残月"
    return {"name": name, "illumination": illum, "phase_pct": round(pct, 3)}

def estimate_light_pollution(lat: float, lng: float) -> dict:
    """Estimate Bortle scale from known city positions (static, no API)."""
    cities = [
        (39.9, 116.4, 21), (31.2, 121.5, 24), (23.1, 113.3, 15),
        (30.6, 104.1, 16), (22.5, 114.1, 13), (29.6, 106.5, 8),
        (32.1, 118.8, 8),  (30.3, 120.2, 7),  (36.1, 120.4, 9),
        (34.3, 108.9, 8),  (25.0, 102.7, 7),  (28.2, 113.0, 8),
        (45.8, 126.5, 10), (41.8, 123.4, 8),  (36.7, 117.0, 9),
    ]
    min_bortle = 9
    for clat, clng, pop in cities:
        d = math.sqrt((lat - clat)**2 + (lng - clng)**2) * 111
        b = max(1, min(9, 9 - math.log2(pop * 80 / max(d, 5) + 1) * 1.2))
        if b < min_bortle:
            min_bortle = b
    bortle = round(min_bortle)
    desc_map = {
        1: "极暗天空", 2: "真正暗天", 3: "农村天空", 4: "农村/郊区",
        5: "郊区天空", 6: "明亮郊区", 7: "郊区/城市", 8: "城市天空", 9: "市中心"
    }
    return {"bortle": bortle, "description": desc_map.get(bortle, "未知")}


async def fetch_air_quality(lat: float, lng: float) -> dict:
    """Fetch AQI from Open-Meteo Air Quality API."""
    import httpx
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lng}&current=pm2_5,pm10,us_aqi"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        current = r.json().get("current", {})
        aqi = current.get("us_aqi", 50)
        return {"aqi": aqi, "pm25": current.get("pm2_5", 0), "pm10": current.get("pm10", 0)}


# ============================================================
#  Unified Data Fetcher
# ============================================================

async def fetch_scene_data(
    lat: float, lng: float,
    scenes: List[str],
    mode: str = "light"  # "light" or "deep"
) -> Dict[str, Any]:
    """
    Fetch only the APIs required by the selected scenes.
    Returns a unified data dict.
    """
    required = resolve_required_apis(scenes)
    tasks = {}

    if "weather" in required:
        if mode == "deep":
            tasks["weather_hourly"] = fetch_weather_hourly(lat, lng)
        tasks["weather_current"] = fetch_weather_current(lat, lng)

    if "astronomy" in required:
        tasks["astronomy"] = fetch_astronomy(lat, lng)

    if "air_quality" in required:
        tasks["air_quality"] = fetch_air_quality(lat, lng)

    # Execute all needed API calls concurrently
    keys = list(tasks.keys())
    results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
    results = {}
    for k, v in zip(keys, results_list):
        results[k] = v if not isinstance(v, Exception) else {}

    # Sync computations (no API call)
    if "moon" in required:
        results["moon"] = calc_moon_phase()
    if "light_pollution" in required:
        results["light_pollution"] = estimate_light_pollution(lat, lng)

    return {
        "apis_called": list(required),
        "mode": mode,
        "data": results,
    }

# ============================================================
#  Scoring Engine
# ============================================================

def _score_factor(name: str, data: dict) -> float:
    """Score a single factor 0-100 based on raw data."""
    wx = data.get("weather_current", {})
    moon = data.get("moon", {})
    lp = data.get("light_pollution", {})
    aq = data.get("air_quality", {})
    astro = data.get("astronomy", {})

    cloud = wx.get("cloud_cover", 50)
    wind = wx.get("wind_speed_10m", 5)
    vis = (wx.get("visibility", 10000)) / 1000  # km
    humid = wx.get("relative_humidity_2m", 50)
    temp = wx.get("temperature_2m", 15)
    precip = wx.get("precipitation", 0)
    wcode = wx.get("weather_code", 0)

    if name == "cloud":
        return max(0, 100 - cloud * 1.2)
    elif name == "wind":
        if wind <= 3: return 100
        if wind <= 8: return 70
        if wind <= 15: return 40
        return 10
    elif name == "visibility":
        if vis >= 20: return 100
        if vis >= 10: return 75
        if vis >= 5: return 40
        return 10
    elif name == "humidity":
        if humid <= 50: return 100
        if humid <= 70: return 65
        return 30
    elif name == "temp":
        # For snow: colder is better; for autumn/flower: moderate is better
        return max(0, min(100, 100 - abs(temp - 5) * 3))
    elif name == "temp_below_zero":
        return 100 if temp < 0 and humid > 80 else (50 if temp < 3 else 0)
    elif name == "temp_diff":
        # Proxy: high humidity + moderate temp = cloud sea potential
        return min(100, humid * 1.2) if humid > 70 else humid * 0.5
    elif name == "light_pollution":
        b = lp.get("bortle", 5)
        return max(0, (9 - b) / 8 * 100)
    elif name == "moon":
        illum = moon.get("illumination", 50)
        return max(0, 100 - illum * 1.5)
    elif name == "aqi":
        aqi = aq.get("aqi", 50)
        if aqi <= 50: return 100
        if aqi <= 100: return 70
        if aqi <= 150: return 40
        return 10
    elif name == "golden":
        # Is current time near golden hour?
        return _time_proximity_score(astro, "golden")
    elif name == "blue":
        return _time_proximity_score(astro, "blue")
    elif name == "sunset_timing":
        return _time_proximity_score(astro, "sunset")
    elif name == "rain_sun":
        # Rainbow: need recent rain + clearing
        if precip > 0 and cloud < 70: return 90
        if precip > 0: return 50
        return 10
    elif name == "storm_prob":
        if wcode >= 95: return 100
        if wcode >= 80: return 60
        return 10
    elif name == "rain":
        return max(0, 100 - precip * 20)
    elif name == "snow_then_clear":
        if wcode in (71, 73, 75, 77, 85, 86) and cloud < 40: return 90
        if cloud < 30: return 50
        return 10
    return 50  # default


def _time_proximity_score(astro: dict, kind: str) -> float:
    """Score how close current time is to golden/blue/sunset."""
    now = datetime.now()
    targets = []
    if kind == "golden":
        for k in ("golden_am_start", "golden_am_end", "golden_pm_start", "golden_pm_end"):
            v = astro.get(k)
            if v:
                targets.append(datetime.fromisoformat(v))
    elif kind == "blue":
        for k in ("blue_am_start", "blue_am_end", "blue_pm_start", "blue_pm_end"):
            v = astro.get(k)
            if v:
                targets.append(datetime.fromisoformat(v))
    elif kind == "sunset":
        v = astro.get("sunset")
        if v:
            ss = datetime.fromisoformat(v)
            targets = [ss - timedelta(minutes=30), ss, ss + timedelta(minutes=60)]

    if not targets:
        return 50
    min_dist = min(abs((now - t).total_seconds()) for t in targets)
    # Within 30 min = 100, within 2h = 50, beyond = 10
    if min_dist < 1800: return 100
    if min_dist < 7200: return max(10, 100 - (min_dist - 1800) / 54)
    return 10


def score_scene(scene: str, data: dict) -> dict:
    """Score a single scene against fetched data. Returns {score, factors}."""
    weights = SCORE_WEIGHTS.get(scene, {"cloud": 1.0})
    factors = {}
    total = 0
    for factor_name, weight in weights.items():
        val = _score_factor(factor_name, data)
        factors[factor_name] = round(val)
        total += val * weight
    score = round(max(0, min(100, total)))
    label = SCENE_CATALOG.get(scene, {}).get("label", scene)

    if score >= 80:
        verdict = "极佳"
    elif score >= 60:
        verdict = "适合"
    elif score >= 40:
        verdict = "一般"
    else:
        verdict = "不推荐"

    return {"scene": scene, "label": label, "score": score, "verdict": verdict, "factors": factors}

# ============================================================
#  Timeline Generator (Deep Mode)
# ============================================================

def generate_timeline(scene: str, hourly: dict, astro: dict) -> List[dict]:
    """Generate hourly score timeline for a scene over 24h."""
    times = hourly.get("time", [])
    clouds = hourly.get("cloud_cover", [])
    winds = hourly.get("wind_speed_10m", [])
    humids = hourly.get("relative_humidity_2m", [])
    vis_list = hourly.get("visibility", [])
    precip_probs = hourly.get("precipitation_probability", [])
    temps = hourly.get("temperature_2m", [])

    weights = SCORE_WEIGHTS.get(scene, {"cloud": 1.0})
    timeline = []

    for i, t in enumerate(times):
        mock_wx = {
            "cloud_cover": clouds[i] if i < len(clouds) else 50,
            "wind_speed_10m": winds[i] if i < len(winds) else 5,
            "relative_humidity_2m": humids[i] if i < len(humids) else 50,
            "visibility": (vis_list[i] if i < len(vis_list) else 10000),
            "temperature_2m": temps[i] if i < len(temps) else 15,
            "precipitation": 0,
            "weather_code": 0,
        }
        mock_data = {"weather_current": mock_wx, "astronomy": astro, "moon": calc_moon_phase(), "light_pollution": {}, "air_quality": {}}
        total = 0
        for factor_name, weight in weights.items():
            total += _score_factor(factor_name, mock_data) * weight
        score = round(max(0, min(100, total)))
        timeline.append({"time": t, "score": score})

    # Find best window
    best_start = None
    best_score = 0
    for i in range(len(timeline)):
        window = timeline[i:i+3]
        avg = sum(x["score"] for x in window) / len(window)
        if avg > best_score:
            best_score = avg
            best_start = timeline[i]["time"]

    return {
        "timeline": timeline,
        "best_window": {"start": best_start, "avg_score": round(best_score)} if best_start else None,
        "not_recommended": [t for t in timeline if t["score"] < 30],
    }


# ============================================================
#  Stargazing Area Recommender
# ============================================================

# Pre-defined dark sky areas (Bortle <= 3)
DARK_SKY_AREAS = [
    {"name": "阿里暗夜公园", "lat": 32.3, "lng": 80.1, "bortle": 1, "radius_km": 30},
    {"name": "那曲暗夜保护区", "lat": 31.5, "lng": 92.1, "bortle": 1, "radius_km": 40},
    {"name": "青海冷湖", "lat": 38.7, "lng": 93.3, "bortle": 1, "radius_km": 25},
    {"name": "甘肃敦煌雅丹", "lat": 40.5, "lng": 93.5, "bortle": 2, "radius_km": 20},
    {"name": "内蒙古锡林郭勒", "lat": 44.0, "lng": 116.0, "bortle": 2, "radius_km": 35},
    {"name": "新疆赛里木湖", "lat": 44.6, "lng": 81.2, "bortle": 2, "radius_km": 20},
    {"name": "云南香格里拉", "lat": 27.8, "lng": 99.7, "bortle": 3, "radius_km": 15},
    {"name": "四川稻城亚丁", "lat": 29.0, "lng": 100.3, "bortle": 2, "radius_km": 20},
    {"name": "西藏珠峰大本营", "lat": 28.1, "lng": 86.9, "bortle": 1, "radius_km": 30},
    {"name": "新疆喀纳斯", "lat": 48.7, "lng": 87.0, "bortle": 2, "radius_km": 25},
    {"name": "黑龙江漠河", "lat": 53.5, "lng": 122.4, "bortle": 2, "radius_km": 30},
    {"name": "海南五指山", "lat": 18.8, "lng": 109.5, "bortle": 3, "radius_km": 10},
    {"name": "浙江千岛湖", "lat": 29.6, "lng": 119.0, "bortle": 4, "radius_km": 10},
    {"name": "福建武夷山", "lat": 27.7, "lng": 118.0, "bortle": 3, "radius_km": 15},
    {"name": "贵州平塘FAST", "lat": 25.6, "lng": 106.9, "bortle": 2, "radius_km": 20},
]


def recommend_stargazing_areas(
    lat: float, lng: float,
    cloud_cover: float = 50,
    max_results: int = 5
) -> List[dict]:
    """
    Star scene: recommend dark sky AREAS (not points).
    Filter: Bortle <= 3, cloud < 30%, sort by distance.
    """
    results = []
    for area in DARK_SKY_AREAS:
        if area["bortle"] > 3:
            continue
        dist = math.sqrt((lat - area["lat"])**2 + (lng - area["lng"])**2) * 111
        # Score: lower bortle + closer distance = higher
        bortle_score = (4 - area["bortle"]) / 3 * 50  # 0-50
        dist_score = max(0, 50 - dist / 50)  # closer = higher, max 50
        cloud_penalty = max(0, (cloud_cover - 30) * 1.5) if cloud_cover > 30 else 0
        total = round(bortle_score + dist_score - cloud_penalty)
        total = max(0, min(100, total))

        reason_parts = []
        if area["bortle"] <= 1:
            reason_parts.append("极暗天空")
        elif area["bortle"] <= 2:
            reason_parts.append("暗天保护区")
        else:
            reason_parts.append("低光污染")
        reason_parts.append(f"距离{dist:.0f}km")
        if cloud_cover <= 20:
            reason_parts.append("云量极低")

        results.append({
            "name": area["name"],
            "type": "stargazing_area",
            "center": {"lat": area["lat"], "lng": area["lng"]},
            "radius_km": area["radius_km"],
            "bortle": area["bortle"],
            "distance_km": round(dist),
            "score": total,
            "reason": "，".join(reason_parts),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]

# ============================================================
#  Photography Spot Database (with coordinates, tips, lens)
# ============================================================

PHOTO_SPOTS = {
    "city": [
        {"name": "上海外滩", "lat": 31.2397, "lng": 121.4918, "tip": "对岸陆家嘴天际线", "lens": "广角 16-35mm", "best_time": "blue_hour"},
        {"name": "重庆洪崖洞", "lat": 29.5630, "lng": 106.5780, "tip": "夜景层叠建筑", "lens": "标准 24-70mm", "best_time": "night"},
        {"name": "香港太平山", "lat": 22.2759, "lng": 114.1455, "tip": "俯瞰维港全景", "lens": "广角 16-35mm", "best_time": "sunset"},
        {"name": "北京国贸", "lat": 39.9087, "lng": 116.4605, "tip": "CBD天际线", "lens": "长焦 70-200mm", "best_time": "blue_hour"},
    ],
    "sea": [
        {"name": "厦门环岛路", "lat": 24.4370, "lng": 118.1280, "tip": "礁石前景+日出", "lens": "广角 16-35mm + ND", "best_time": "sunrise"},
        {"name": "三亚天涯海角", "lat": 18.2431, "lng": 109.2050, "tip": "礁石剪影", "lens": "广角 16-35mm", "best_time": "sunset"},
        {"name": "青岛栈桥", "lat": 36.0596, "lng": 120.3175, "tip": "栈桥+回澜阁", "lens": "标准 24-70mm", "best_time": "golden_hour"},
    ],
    "mountain": [
        {"name": "黄山光明顶", "lat": 30.1370, "lng": 118.1710, "tip": "云海日出", "lens": "广角 + 长焦", "best_time": "sunrise"},
        {"name": "张家界天门山", "lat": 29.0500, "lng": 110.4800, "tip": "云雾缭绕", "lens": "广角 16-35mm", "best_time": "morning"},
        {"name": "泰山日观峰", "lat": 36.2560, "lng": 117.1010, "tip": "日出云海", "lens": "长焦 70-200mm", "best_time": "sunrise"},
    ],
    "snow": [
        {"name": "玉龙雪山", "lat": 27.1167, "lng": 100.2333, "tip": "雪山倒影蓝月谷", "lens": "广角 16-35mm", "best_time": "morning"},
        {"name": "长白山天池", "lat": 42.0040, "lng": 128.0550, "tip": "天池全景", "lens": "广角 + 偏振镜", "best_time": "morning"},
        {"name": "贡嘎雪山", "lat": 29.5960, "lng": 101.8780, "tip": "日照金山", "lens": "长焦 70-200mm", "best_time": "sunrise"},
    ],
    "desert": [
        {"name": "敦煌鸣沙山", "lat": 40.0820, "lng": 94.6720, "tip": "沙丘光影线条", "lens": "长焦 70-200mm", "best_time": "golden_hour"},
        {"name": "巴丹吉林沙漠", "lat": 39.7600, "lng": 102.3500, "tip": "沙漠湖泊", "lens": "广角 16-35mm", "best_time": "sunrise"},
    ],
    "landform": [
        {"name": "张掖丹霞", "lat": 38.9180, "lng": 100.1330, "tip": "彩色丘陵", "lens": "标准 24-70mm", "best_time": "golden_hour"},
        {"name": "雅丹魔鬼城", "lat": 40.5300, "lng": 93.5200, "tip": "风蚀地貌", "lens": "广角 16-35mm", "best_time": "sunset"},
    ],
    "architecture": [
        {"name": "苏州博物馆", "lat": 31.3230, "lng": 120.6310, "tip": "贝聿铭几何构图", "lens": "广角 16-35mm", "best_time": "overcast"},
        {"name": "北京故宫角楼", "lat": 39.9240, "lng": 116.3970, "tip": "护城河倒影", "lens": "标准 24-70mm", "best_time": "blue_hour"},
    ],
    "golden_hour": [
        {"name": "霞浦滩涂", "lat": 26.8850, "lng": 120.0050, "tip": "渔网光影", "lens": "长焦 70-200mm", "best_time": "sunrise"},
        {"name": "元阳梯田", "lat": 23.2200, "lng": 102.7800, "tip": "梯田反光", "lens": "广角 + 长焦", "best_time": "sunrise"},
    ],
    "grassland": [
        {"name": "呼伦贝尔草原", "lat": 49.2150, "lng": 119.7650, "tip": "草原公路延伸线", "lens": "广角 16-35mm", "best_time": "golden_hour"},
    ],
    "autumn": [
        {"name": "九寨沟", "lat": 33.2600, "lng": 103.9200, "tip": "彩林倒影", "lens": "标准 24-70mm + 偏振镜", "best_time": "morning"},
        {"name": "喀纳斯", "lat": 48.7200, "lng": 87.0200, "tip": "白桦林金黄", "lens": "广角 + 长焦", "best_time": "morning"},
    ],
}


def get_nearby_spots(lat: float, lng: float, scenes: List[str], max_dist_km: float = 500, limit: int = 8) -> List[dict]:
    """Get photography spots near the user, filtered by selected scenes."""
    results = []
    for scene in scenes:
        spots = PHOTO_SPOTS.get(scene, [])
        for spot in spots:
            dist = math.sqrt((lat - spot["lat"])**2 + (lng - spot["lng"])**2) * 111
            if dist <= max_dist_km:
                results.append({
                    **spot,
                    "scene": scene,
                    "scene_label": SCENE_CATALOG.get(scene, {}).get("label", scene),
                    "distance_km": round(dist),
                })
    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]


# ============================================================
#  Route Planner
# ============================================================

def plan_route(spots: List[dict], astro: dict) -> List[dict]:
    """
    Given spots + astronomy data, plan optimal shooting order.
    Prioritize: sunrise spots first, then daytime, then sunset/night.
    """
    TIME_ORDER = {"sunrise": 0, "morning": 1, "overcast": 2, "golden_hour": 3, "sunset": 4, "blue_hour": 5, "night": 6}

    sorted_spots = sorted(spots, key=lambda s: TIME_ORDER.get(s.get("best_time", "morning"), 2))

    route = []
    sunrise = astro.get("sunrise", "")
    sunset = astro.get("sunset", "")

    for i, spot in enumerate(sorted_spots):
        bt = spot.get("best_time", "morning")
        if bt == "sunrise" and sunrise:
            sr = datetime.fromisoformat(sunrise)
            arrive = sr - timedelta(minutes=20)
        elif bt == "sunset" and sunset:
            ss = datetime.fromisoformat(sunset)
            arrive = ss - timedelta(minutes=30)
        elif bt == "blue_hour" and sunset:
            ss = datetime.fromisoformat(sunset)
            arrive = ss + timedelta(minutes=15)
        elif bt == "night" and sunset:
            ss = datetime.fromisoformat(sunset)
            arrive = ss + timedelta(minutes=60)
        elif bt == "golden_hour" and sunset:
            ss = datetime.fromisoformat(sunset)
            arrive = ss - timedelta(minutes=40)
        else:
            # Default: spread through the day
            arrive = datetime.now().replace(hour=9 + i * 2, minute=0, second=0)

        duration = 40 if bt in ("sunrise", "sunset", "blue_hour", "golden_hour") else 30

        route.append({
            "order": i + 1,
            "name": spot["name"],
            "lat": spot["lat"],
            "lng": spot["lng"],
            "arrive_time": arrive.strftime("%H:%M"),
            "duration_min": duration,
            "activity": SCENE_CATALOG.get(spot.get("scene", ""), {}).get("label", "拍摄"),
            "tip": spot.get("tip", ""),
            "lens": spot.get("lens", ""),
        })

    return route
