from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    variant_number: int = Field()
    student_name: str = Field()
    student_github_username: str = Field()
    comment: str | None = Field()
    attempt_number: int | None = Field()
    attempt_time: str | None = Field()
    last_pr_link: str | None = Field()
    prompt: str | None = Field()
    summary: str | None = Field()
    retry_button: str | None = Field()

    def to_pd_dict(self) -> dict:
        data = {
            "Номер варіанту": [self.variant_number],
            "ПІБ": [self.student_name],
            "github nickname": [self.student_github_username],
            "Коментар бота": [self.comment],
            "№ Спроби": [self.attempt_number],
            "Час здачі": [self.attempt_time],
            "Лінк на останній PR": [self.last_pr_link],
            "Промт": [self.prompt],
            "Підсумок": [self.summary],
            "Кнопка перевірки ще раз": [self.retry_button]
        }
        return data
