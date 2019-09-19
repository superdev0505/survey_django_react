###Votes - 2019-05-27

#### delete previous
```python
from survey.submodels.survey import ANSWER_TYPES, Question, Choice, Survey, QuestionAnswer, SURVEY_STATUS, ANSWER_VOTE
Question.objects.filter(answer_type='vote').delete()
```


#### fill data
```bash
python3 manage.py restore_questions
python3 manage.py move_bot_questions
```


#### finally reset all
```sql
update survey_question set enabled=TRUE where answer_type = 'vote';
update survey_question set enabled=FALSE where answer_type != 'vote';
```
