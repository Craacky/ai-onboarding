import enum

class PlanEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"

class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"

class DocumentStatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class MessageRoleEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"