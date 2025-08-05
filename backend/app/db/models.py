from sqlalchemy import Column, Float, String, DateTime, JSON, Boolean
from db.session import Base

class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    agent_id = Column(String, index=True)
    latency = Column(Float)
    download = Column(Float)  # Mbps
    upload = Column(Float)    # Mbps
    packet_loss = Column(Float)
    jitter = Column(Float)
    metainfo = Column(JSON)   # Доп. параметры

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime)
