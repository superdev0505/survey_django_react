import {QUESTION_SELECT_EDIT, QUESTIONS_LIST_REQUEST, QUESTIONS_LIST_RESULT} from '../actions/types'

const initialSource = {
    questionsLoading: false,
    questionList: [],
    questionCount: 0,
    questionOffset: 0,
    questionNext: null,
    questionPrevious: null,
    questionActiveItem: null
};

export const questions = (state = initialSource, action) => {
    const {type} = action;

    switch (type) {
        case QUESTION_SELECT_EDIT:
            return {...state, questionActiveItem: action.questionActiveItem};
        case QUESTIONS_LIST_REQUEST:
            return {...state, questionsLoading: true };
        case QUESTIONS_LIST_RESULT:
            return {
                ...state,
                questionCount: action.questionList.count,
                questionNext: action.questionList.next,
                questionPrevious: action.questionList.previous,
                questionOffset: action.questionList.offset,
                questionList: action.questionList.results || [],
                questionsLoading: false
            };
        default:
            return state
    }
};