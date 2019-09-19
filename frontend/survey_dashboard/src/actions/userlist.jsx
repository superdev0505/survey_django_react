import {USER_LIST_RESULTS, USER_LIST_LOADING} from './types'
import API from "../API";


export const userListRequest = (search, next, prev, filters, ordering) => {
    return (dispatch, getState) => {
        dispatch(userListLoading());

        let {userListNext, userListPrevious, userListOffset} = getState().userList;
        let url = null;
        let params = null;
        if (next) {
            url = userListNext
        } else if (prev) {
            url = userListPrevious
        } else if (search || filters || ordering) {
            params = Object.assign({search}, filters, {ordering})
        } else {
            params = { offset: userListOffset || 0 }
        }

        return API.fetch(API.USER_LIST, params, false, url)
            .then(userList => dispatch(userListResults(userList || {})))
    }
};

export const userListLoading = (userList) => {
    return {
        type: USER_LIST_LOADING,
        userList
    }
};

export const userListResults = (userList) => {
    return {
        type: USER_LIST_RESULTS,
        userList
    }
};