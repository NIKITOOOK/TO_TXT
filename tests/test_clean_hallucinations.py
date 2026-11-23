
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline"))
from clean_hallucinations import is_hallucination  # noqa: E402


class CleanTest(unittest.TestCase):
    def test_known_phrases_removed(self):
        for t in ["Продолжение следует...", "Субтитры сделал DimaTorzok", "Субтитры создавал DimaTorzok",
                  "Спасибо за просмотр!", "Thank you for watching", "Subtitles by the Amara.org community",
                  "Субтитры добавил и чей-то ник", "Редактор субтитров А.Семкин Корректор А.Егорова"]:
            self.assertTrue(is_hallucination(t, []), t)

    def test_real_speech_kept(self):
        for t in ["Продолжение следует в следующей лекции, где мы разберём JOIN", "Давайте посмотрим на слайд",
                  "Спасибо за вопрос, сейчас отвечу", "Субтитры в этом видео отключены, поэтому читайте слайды и следите за ходом лекции внимательно"]:
            self.assertFalse(is_hallucination(t, []), t)

    def test_extra(self):
        self.assertTrue(is_hallucination("Моя фраза", ["моя фраза"]))


if __name__ == "__main__":
    unittest.main()
