import {METRICS, METRICS_LOADING} from '../actions/types'

const initialSource = {
    metrics: [],
    metricsLoading: false
};

export const metrics = (state = initialSource, action) => {
    const {type, metrics} = action;

    switch (type) {
        case METRICS_LOADING:
            return {...state, metricsLoading: true };
        case METRICS:
            return {...state, metrics: metrics, metricsLoading: false };
        default:
            return state
    }
};