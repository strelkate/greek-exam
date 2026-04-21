import enum


class LevelEnum(str, enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"


class ExerciseTypeEnum(str, enum.Enum):
    TRUE_FALSE = "true_false"
    MATCHING = "matching"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    FLASHCARD = "flashcard"
    IMAGE_DESCRIPTION = "image_description"
    DIALOGUE = "dialogue"


class CardStatusEnum(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    LEARNED = "learned"
