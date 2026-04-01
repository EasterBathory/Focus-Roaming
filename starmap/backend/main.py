from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, Query
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

from database import engine, get_db, Base
from models import User, EmailCode, SavedPoint, UserPhoto, CommunityPhoto, PhotoLike, PhotoSave
from auth import hash_password, verify_password, create_token, decode_token
from email_code import send_email_code, gen_code
from vision import analyze_image, update_user_tags, get_top_preferences
from scenes import (
    SCENE_CATALOG, resolve_required_apis, fetch_scene_data,
    score_scene, generate_timeline, recommend_stargazing_areas,
    get_nearby_spots, plan_route,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="焦点漫游 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth helpers ──
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "未登录")
    uid = decode_token(authorization.split(" ", 1)[1])
    if not uid:
        raise HTTPException(401, "Token 无效或已过期")
    user = db.get(User, uid)
    if not user or not user.is_active:
        raise HTTPException(401, "账号不存在或已禁用")
    return user

# ── Schemas ──
class SendCodeReq(BaseModel):
    email: EmailStr
    purpose: str = "register"

class RegisterReq(BaseModel):
    email: EmailStr
    code: str
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_len(cls, v):
        if not 2 <= len(v) <= 20:
            raise ValueError("用户名长度 2-20 位")
        return v

    @field_validator("password")
    @classmethod
    def password_len(cls, v):
        if len(v) < 6:
            raise ValueError("密码至少 6 位")
        return v

class LoginReq(BaseModel):
    email: EmailStr
    code: str = ""
    password: str = ""

class UpdateProfileReq(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    lang: Optional[str] = None

class ChangePasswordReq(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class SavePointReq(BaseModel):
    name: str
    lat: float
    lng: float
    note: str = ""

# ════════════════════════════════════════
#  Email Code
# ════════════════════════════════════════
@app.post("/api/email/send")
async def api_send_code(req: SendCodeReq, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == req.email).first()
    if req.purpose == "register" and exists:
        raise HTTPException(400, "该邮箱已注册")
    if req.purpose in ("login", "reset") and not exists:
        raise HTTPException(400, "该邮箱未注册")

    code = gen_code()

    # 暂时跳过邮件发送，直接存验证码（前端随便填即可注册）
    db.query(EmailCode).filter(
        EmailCode.email == req.email,
        EmailCode.purpose == req.purpose,
        EmailCode.used == False
    ).update({"used": True})
    db.add(EmailCode(email=req.email, code=code, purpose=req.purpose))
    db.commit()
    print(f"[DEV] 验证码: {req.email} -> {code}")
    return {"ok": True}

def verify_code(db: Session, email: str, code: str, purpose: str):
    # 暂时跳过验证码校验
    pass

# ════════════════════════════════════════
#  Auth
# ════════════════════════════════════════
@app.post("/api/auth/register")
def api_register(req: RegisterReq, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "该邮箱已注册")
    verify_code(db, req.email, req.code, "register")
    user = User(email=req.email, username=req.username, hashed_pw=hash_password(req.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"token": create_token(user.id), "user": _user_dict(user)}

@app.post("/api/auth/login")
def api_login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(400, "邮箱未注册")
    if req.code:
        verify_code(db, req.email, req.code, "login")
    elif req.password:
        if not verify_password(req.password, user.hashed_pw):
            raise HTTPException(400, "密码错误")
    else:
        raise HTTPException(400, "请提供验证码或密码")
    return {"token": create_token(user.id), "user": _user_dict(user)}

@app.post("/api/auth/reset-password")
def api_reset_pw(req: ChangePasswordReq, db: Session = Depends(get_db)):
    if len(req.new_password) < 6:
        raise HTTPException(400, "密码至少 6 位")
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(400, "邮箱未注册")
    verify_code(db, req.email, req.code, "reset")
    user.hashed_pw = hash_password(req.new_password)
    db.commit()
    return {"ok": True}

# ════════════════════════════════════════
#  Profile
# ════════════════════════════════════════
def _user_dict(u: User):
    import json
    email = u.email
    masked = email[0] + "***" + email[email.index("@"):]
    prefs = get_top_preferences(u.photo_tags or "{}")
    return {"id": u.id, "email": masked, "username": u.username,
            "bio": u.bio, "lang": u.lang, "avatar": u.avatar,
            "preferences": prefs,
            "created_at": str(u.created_at)}

@app.get("/api/me")
def api_me(user: User = Depends(get_current_user)):
    return _user_dict(user)

@app.patch("/api/me")
def api_update_me(req: UpdateProfileReq, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.username is not None:
        if not 2 <= len(req.username) <= 20:
            raise HTTPException(400, "用户名长度 2-20 位")
        user.username = req.username
    if req.bio is not None:
        if len(req.bio) > 200:
            raise HTTPException(400, "简介最多 200 字")
        user.bio = req.bio
    if req.lang is not None:
        user.lang = req.lang
    db.commit(); db.refresh(user)
    return _user_dict(user)

@app.post("/api/me/avatar")
async def api_upload_avatar(file: UploadFile, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(400, "仅支持 jpg/png/webp/gif")
    data = await file.read()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(400, "图片不能超过 2MB")
    import base64
    b64 = base64.b64encode(data).decode()
    user.avatar = f"data:{file.content_type};base64,{b64}"
    db.commit(); db.refresh(user)
    return _user_dict(user)

# ════════════════════════════════════════
#  Saved Points
# ════════════════════════════════════════
@app.get("/api/points")
def api_get_points(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pts = db.query(SavedPoint).filter(SavedPoint.user_id == user.id).order_by(SavedPoint.created_at.desc()).all()
    return [{"id": p.id, "name": p.name, "lat": p.lat, "lng": p.lng,
             "note": p.note, "created_at": str(p.created_at)} for p in pts]

@app.post("/api/points")
def api_save_point(req: SavePointReq, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pt = SavedPoint(user_id=user.id, name=req.name, lat=req.lat, lng=req.lng, note=req.note)
    db.add(pt); db.commit(); db.refresh(pt)
    return {"id": pt.id, "name": pt.name, "lat": pt.lat, "lng": pt.lng}

@app.delete("/api/points/{point_id}")
def api_delete_point(point_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pt = db.query(SavedPoint).filter(SavedPoint.id == point_id, SavedPoint.user_id == user.id).first()
    if not pt:
        raise HTTPException(404, "地点不存在")
    db.delete(pt); db.commit()
    return {"ok": True}

# ════════════════════════════════════════
#  Photo Analysis & Preferences
# ════════════════════════════════════════
@app.post("/api/me/analyze-photo")
async def api_analyze_photo(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传照片，分析拍摄偏好并更新用户标签"""
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "仅支持 jpg/png/webp")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "图片不能超过 10MB")

    # 调用阿里云分析
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        tags = await loop.run_in_executor(pool, analyze_image, data, file.content_type)

    if not tags:
        return {"ok": True, "tags": [], "message": "未识别到明确场景"}

    # 存照片记录
    import json
    photo = UserPhoto(user_id=user.id, tags=json.dumps(tags, ensure_ascii=False))
    db.add(photo)

    # 更新用户偏好权重
    user.photo_tags = update_user_tags(user.photo_tags or "{}", tags)
    db.commit()

    return {
        "ok": True,
        "tags": tags,
        "preferences": get_top_preferences(user.photo_tags)
    }

@app.get("/api/me/preferences")
def api_get_preferences(user: User = Depends(get_current_user)):
    """获取用户拍摄偏好标签（按权重排序）"""
    import json
    try:
        all_tags = json.loads(user.photo_tags or "{}")
    except Exception:
        all_tags = {}
    sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
    return {
        "preferences": [{"tag": t, "count": c} for t, c in sorted_tags],
        "top": get_top_preferences(user.photo_tags or "{}")
    }

@app.get("/api/recommend")
def api_recommend(
    lat: float, lng: float,
    user: User = Depends(get_current_user)
):
    """
    根据用户偏好推荐拍摄类型和参数建议
    前端传入当前查看地点的经纬度，返回个性化建议
    """
    prefs = get_top_preferences(user.photo_tags or "{}")
    if not prefs:
        return {"preferences": [], "tips": ["暂无偏好数据，上传你的照片来获取个性化推荐"]}

    # 根据偏好生成拍摄建议
    tips_map = {
        "星空":    ["选择 Bortle ≤ 3 的暗天区域", "建议新月前后3天拍摄", "推荐 ISO 3200+，快门 15-25s，广角镜头"],
        "城市夜景": ["选择制高点或对岸拍摄", "蓝调时段（日落后20-40分钟）最佳", "推荐三脚架 + 慢门 5-30s"],
        "自然风光": ["黄金时段（日出日落前后30分钟）光线最柔", "注意云量 ≤ 30% 能见度 ≥ 10km", "偏振镜减少反光"],
        "海景":    ["涨潮时段礁石有水流感", "日出方向迎光拍摄剪影", "ND 滤镜拍丝滑海面"],
        "人像":    ["避免正午顶光，选择阴天或黄金时段", "背景选择简洁，光污染低的区域更干净", "85mm+ 焦段压缩背景"],
        "日出日落": ["提前15分钟到位等待光线变化", "云层 20-50% 时色彩最丰富", "注意风向，顺风拍摄减少镜头起雾"],
        "雪景":    ["曝光补偿 +1 至 +2 防止雪变灰", "蓝调时段雪地反光最美", "注意低温电池保暖"],
    }

    tips = []
    for pref in prefs:
        if pref in tips_map:
            tips.extend(tips_map[pref])

    return {"preferences": prefs, "tips": tips[:6]}  # 最多返回6条

# ════════════════════════════════════════
#  Community Photos
# ════════════════════════════════════════

@app.post("/api/community/photos")
async def api_upload_community_photo(
    file: UploadFile,
    spot_name: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    caption: str = Query(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "仅支持 jpg/png/webp")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(400, "图片不能超过 5MB")
    import base64
    b64 = f"data:{file.content_type};base64,{base64.b64encode(data).decode()}"
    photo = CommunityPhoto(
        user_id=user.id, spot_name=spot_name,
        lat=lat, lng=lng, image_data=b64, caption=caption
    )
    db.add(photo); db.commit(); db.refresh(photo)
    return {"id": photo.id, "ok": True}


@app.get("/api/community/photos")
def api_get_community_photos(
    spot_name: str = Query(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    photos = (db.query(CommunityPhoto)
              .filter(CommunityPhoto.spot_name == spot_name)
              .order_by(CommunityPhoto.likes.desc(), CommunityPhoto.created_at.desc())
              .limit(20).all())
    # Check current user likes/saves
    uid = None
    if authorization and authorization.startswith("Bearer "):
        uid = decode_token(authorization.split(" ", 1)[1])
    user_likes = set()
    user_saves = set()
    if uid:
        user_likes = {r.photo_id for r in db.query(PhotoLike).filter(PhotoLike.user_id == uid).all()}
        user_saves = {r.photo_id for r in db.query(PhotoSave).filter(PhotoSave.user_id == uid).all()}
    result = []
    for p in photos:
        u = db.get(User, p.user_id)
        result.append({
            "id": p.id,
            "image": p.image_data,
            "caption": p.caption,
            "likes": p.likes,
            "liked": p.id in user_likes,
            "saved": p.id in user_saves,
            "user": {"username": u.username if u else "匿名", "avatar": u.avatar if u else ""},
            "created_at": str(p.created_at),
        })
    return {"photos": result}


@app.post("/api/community/photos/{photo_id}/like")
def api_toggle_like(
    photo_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.get(CommunityPhoto, photo_id)
    if not photo:
        raise HTTPException(404, "照片不存在")
    existing = db.query(PhotoLike).filter(
        PhotoLike.user_id == user.id, PhotoLike.photo_id == photo_id
    ).first()
    if existing:
        db.delete(existing)
        photo.likes = max(0, photo.likes - 1)
        db.commit()
        return {"liked": False, "likes": photo.likes}
    else:
        db.add(PhotoLike(user_id=user.id, photo_id=photo_id))
        photo.likes += 1
        db.commit()
        return {"liked": True, "likes": photo.likes}


@app.post("/api/community/photos/{photo_id}/save")
def api_toggle_save(
    photo_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.get(CommunityPhoto, photo_id)
    if not photo:
        raise HTTPException(404, "照片不存在")
    existing = db.query(PhotoSave).filter(
        PhotoSave.user_id == user.id, PhotoSave.photo_id == photo_id
    ).first()
    if existing:
        db.delete(existing); db.commit()
        return {"saved": False}
    else:
        db.add(PhotoSave(user_id=user.id, photo_id=photo_id))
        db.commit()
        return {"saved": True}


# ════════════════════════════════════════
#  Scene Recommendation Engine
# ════════════════════════════════════════

@app.get("/api/scenes")
def api_list_scenes():
    """Return all available scenes with metadata."""
    return {
        "scenes": [
            {"id": k, "label": v["label"], "group": v["group"], "apis": v["apis"]}
            for k, v in SCENE_CATALOG.items()
        ]
    }


@app.get("/api/scene/evaluate")
async def api_evaluate_scenes(
    lat: float,
    lng: float,
    scenes: str = Query(..., description="Comma-separated scene IDs"),
    mode: str = Query("light", description="light or deep"),
):
    """
    Core endpoint: evaluate selected scenes at a location.
    - Light mode: current conditions + score + one-line advice
    - Deep mode: 24h timeline + best window + hourly scores
    """
    scene_list = [s.strip() for s in scenes.split(",") if s.strip() in SCENE_CATALOG]
    if not scene_list:
        raise HTTPException(400, "No valid scenes provided")

    # Fetch only required APIs
    raw = await fetch_scene_data(lat, lng, scene_list, mode)
    data = raw["data"]

    # Score each scene
    results = []
    for s in scene_list:
        scored = score_scene(s, data)

        # Deep mode: add timeline
        if mode == "deep" and "weather_hourly" in data:
            tl = generate_timeline(s, data["weather_hourly"], data.get("astronomy", {}))
            scored["timeline"] = tl

        results.append(scored)

    # Star scene: return areas instead of points
    star_areas = None
    if "star" in scene_list:
        cloud = data.get("weather_current", {}).get("cloud_cover", 50)
        star_areas = recommend_stargazing_areas(lat, lng, cloud)

    # Get nearby photo spots for non-star scenes
    non_star = [s for s in scene_list if s != "star"]
    spots = get_nearby_spots(lat, lng, non_star) if non_star else []

    # Plan route if we have spots
    route = []
    if spots and "astronomy" in data:
        route = plan_route(spots, data.get("astronomy", {}))

    return {
        "location": {"lat": lat, "lng": lng},
        "apis_called": raw["apis_called"],
        "mode": mode,
        "scores": results,
        "star_areas": star_areas,
        "spots": spots,
        "route": route,
    }


# ════════════════════════════════════════
#  Health
# ════════════════════════════════════════
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/test-email")
async def test_email():
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    def _test():
        import yagmail
        yag = yagmail.SMTP(smtp_user, smtp_pass)
        yag.send(to=smtp_user, subject="test", contents="test email")
        return "ok"
    with ThreadPoolExecutor() as pool:
        result = await asyncio.wait_for(loop.run_in_executor(pool, _test), timeout=20)
    return {"result": result}
