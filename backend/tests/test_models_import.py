def test_models_importable():
    from app.models.enums import LevelEnum, ExerciseTypeEnum, CardStatusEnum
    from app.models.user import User
    from app.models.curriculum import CurriculumUnit
    from app.models.exercise import Exercise
    from app.models.vocabulary import VocabularyCard, UserCardState
    from app.models.progress import UserProgress
    from app.models.xp_log import XpLog
    assert LevelEnum.A1 == "A1"
    assert ExerciseTypeEnum.TRUE_FALSE == "true_false"
