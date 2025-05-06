from sqlalchemy import Column, Integer, String, Boolean, JSON
from database.db_manager import Base


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), index=True)
    profileUrl = Column(String)
    nickName = Column(String)
    verified = Column(Boolean, default=False)
    signature = Column(String)
    bioLink = Column(String, nullable=True)
    originalAvatarUrl = Column(String)
    avatar = Column(String)
    commerceUserInfo = Column(JSON, nullable=True)
    privateAccount = Column(Boolean, default=False)
    region = Column(String)
    roomId = Column(String, nullable=True)
    ttSeller = Column(Boolean, default=False)
    following = Column(Integer, default=0)
    friends = Column(Integer, default=0)
    fans = Column(Integer, default=0)
    heart = Column(Integer, default=0)
    video = Column(Integer, default=0)
    digg = Column(Integer, default=0)


class TwitterPost(Base):
    __tablename__ = 'twitter_posts'

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String)
    description = Column(String)
    likes_count = Column(Integer)
    retweets_count = Column(Integer)
    media_url = Column(String)
    favorite_count = Column(Integer)
    followers_count = Column(Integer)


class InstaPost(Base):
    __tablename__ = 'instagram_post'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    posts_count = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    posts = Column(String, nullable=True)  # e.g., "72.38 M"
    posts_per_day = Column(String, nullable=True)  # e.g., "13.04 K"


class FacebookPost(Base):
    __tablename__ = 'facebook_posts'

    id = Column(Integer, primary_key=True, index=True)
    facebook_url = Column(String, nullable=False)
    reaction = Column(String, nullable=True)
    name = Column(String, nullable=False)
    profile_url = Column(String, nullable=False)
    facebook_id = Column(String, nullable=False)
