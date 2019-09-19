import {USER_FEEDBACK, USER_FEEDBACK_AGGREGATED} from '../actions/types'

const initialSource = {
    dataLoading: false,
    feedbackAggregatedList: []
};

export const feedbackList = (state = initialSource, action) => {
    const {type, feedbackList, feedbackAggregatedList} = action;

    switch (type) {
        case USER_FEEDBACK:
            return {...state, ...feedbackList };
        case USER_FEEDBACK_AGGREGATED:
            return {...state, feedbackAggregatedList };
        default:
            return state
    }
};