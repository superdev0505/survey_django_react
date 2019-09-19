import {USER_LIST_RESULTS, USER_REQUEST, USER_LIST_LOADING} from '../actions/types'

const initialSource = {
    count: 0,
    next: null,
    previous: null,
    results: [],
    dataLoading: false
};

export const userList = (state = initialSource, action) => {
    const {type, userList} = action;

    switch (type) {
        case USER_LIST_LOADING:
            return {...state, dataLoading: true };
        case USER_LIST_RESULTS:
            return {
                ...state, 
                ...userList,
                userListCount: action.userList.count,
                userListNext: action.userList.next,
                userListPrevious: action.userList.previous,
                userListOffset: action.userList.offset,
                userList: action.userList.results || [],
                userListLoading: false,
                dataLoading: false
            };
        default:
            return state
    }
};