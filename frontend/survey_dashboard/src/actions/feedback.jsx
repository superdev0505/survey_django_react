import {USER_FEEDBACK, USER_FEEDBACK_AGGREGATED} from './types'
import API from "../API";


export const userFeedbackRequest = () => {
    return dispatch => {
        return API.fetch(API.USER_FEEDBACK)
            .then(feedbackList => dispatch(userFeedbackResults(feedbackList || {})))
    }
};

export const userFeedbackResults = (feedbackList) => {
    return {
        type: USER_FEEDBACK,
        feedbackList
    }
};


export const userFeedbackAggregatedRequest = () => {
    return dispatch => {
        return API.fetch(API.USER_FEEDBACK_AGGREGATED)
            .then(feedbackList => dispatch(userFeedbackAggregatedResults(feedbackList || [])))
    }
};

export const userFeedbackAggregatedResults = (feedbackAggregatedList) => {
    return {
        type: USER_FEEDBACK_AGGREGATED,
        feedbackAggregatedList
    }
};