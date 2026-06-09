from enum import Enum


class RaceStatusEnum(str,Enum):
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class DifficultyScoreEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"