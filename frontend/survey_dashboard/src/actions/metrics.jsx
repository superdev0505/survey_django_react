import {METRICS, METRICS_LOADING} from './types'
import API from "../API";


export const metricsRequest = (date, provider) => {
    return dispatch => {
        dispatch(metricsLoading());
        return API.fetch(API.METRICS, {date, provider})
            .then(metrics => dispatch(metricsResults(metrics || {})))
    }
};

export const metricsLoading = () => {
    return {
        type: METRICS_LOADING
    }
};

export const metricsResults = (metrics) => {
    return {
        type: METRICS,
        metrics
    }
};

