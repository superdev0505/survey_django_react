import {USER_REQUEST, USER_RESULTS} from '../actions/types'

const initialSource = {
    dataLoading: false
};

export const user = (state = initialSource, action) => {
    const {type, user} = action;

    switch (type) {
        case USER_REQUEST:
            return {...state, dataLoading: true };
        case USER_RESULTS:
            return {...state, ...user };
        default:
            return state
    }
};