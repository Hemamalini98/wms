import enum


class ProjectStatus(str, enum.Enum):
    active    = "Active"
    planning  = "Planning"
    completed = "Completed"


class ProjectPriority(str, enum.Enum):
    normal     = "Normal"
    fast_track = "Fast Track"


class ComplexityLevel(str, enum.Enum):
    low    = "Low"
    medium = "Medium"
    high   = "High"


class ChapterStatus(str, enum.Enum):
    in_progress = "In-progress"
    complete    = "complete"
    hold        = "Hold"
    in_query    = "In-query"


class PublishedStatus(str, enum.Enum):
    draft             = "Draft"
    ready_for_publish = "Ready for Publish"
    published         = "Published"
    archived          = "Archived"
