import {USER_RESULTS} from './types'
import fetch from 'isomorphic-fetch'
import API from "../API";


export const userRequest = () => {
    return dispatch => {
        return API.fetch(API.USER_PROFILE).then(json => dispatch(userResults(json)))
    }
};

export const userLoginRequest = (login, password) => {
    return dispatch => {
        return API.fetch(API.USER_LOGIN, {login, password})
            .then(json => window.location = '/tags')
    }
};

export const userResults = (user) => {
    return {
        type: USER_RESULTS,
        user
    }
};