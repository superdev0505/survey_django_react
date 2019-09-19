import {QUESTIONS_LIST_REQUEST, QUESTIONS_LIST_RESULT, QUESTION_SELECT_EDIT} from './types'
import API from "../API";


export const questionSelectEdit = (questionActiveItem) => {
    return {
        type: QUESTION_SELECT_EDIT,
        questionActiveItem
    }
};

export const questionListRequest = (search, next, prev) => {
    return (dispatch, getState) => {
        let {questionNext, questionPrevious, questionOffset} = getState().questions;
        let url = null;
        let params = null;
        if (next) {
            url = questionNext
        } else if (prev) {
            url = questionPrevious
        } else if (search) {
            params = { search: search }
        } else {
            params = { offset: questionOffset }
        }

        dispatch({type: QUESTIONS_LIST_REQUEST});
        return API.fetch(API.QUESTIONS, params, false, url)
            .then(questionList => dispatch(questionListResults(questionList || {})))
    }
};

export const questionListResults = (questionList) => {
    return {
        type: QUESTIONS_LIST_RESULT,
        questionList
    }
};