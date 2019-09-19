import Cookies from 'js-cookie';
import Utils from './Utils'
import {withRouter} from "react-router-dom";


const DEFAULT_HEADERS = {
    "Content-Type": 'application/json'
};

class API {

    static THROTTLE_TIMEOUT = 300;

    /**
     * Send fetch
     * @param request
     * @param requestBody
     * @param {Boolean} rawResponse do not automatically convert response data to JSON
     * @param {String} requestUrl Custom request URL (in case of server sends pagination url by itself)
     * @returns {*|Promise.<*>}
     */
    static fetch(request, requestBody, rawResponse, requestUrl) {
        let url = requestUrl || request.url;
        let params = {
            credentials: 'same-origin',
            method: request.method || 'get',
            headers: Object.assign(DEFAULT_HEADERS, {"X-CSRFToken": Cookies.get("csrftoken")})
        };

        if ((params.method === 'post') || (params.method === 'delete')) {
            params['body'] = JSON.stringify(requestBody)
        } else if (requestBody) {
            url = API.getUrlWithParams(requestUrl || request.url, requestBody)
        }

        return fetch(url, params)
            .then(response => {
                switch (response.status) {
                    case 401:
                        return window.location = '/login';
                    // case 403:
                    //     return window.location = '/login';
                    case 404:
                        throw new Error('Not found');
                    case 500:
                        throw new Error('Server Error');
                    default:
                }
                return rawResponse ? response.text() : response.json()
            })
            .catch(error => console.error(error));
    }

    /**
     * Send only after throttled timeout
     */
    static fetchThrottled = Utils.throttled(API.fetch, API.THROTTLE_TIMEOUT);

    /**
     * Builds query string from object
     * @param url
     * @param params
     * @returns {string}
     */
    static getUrlWithParams(url, params) {
        return url + '?' + Object.keys(params)
            .reduce((a, k) => {
                a.push(k + '=' + encodeURIComponent(params[k]));
                return a
            }, []).join('&');
    }
}

API.TAGS = {
    method: 'get',
    url: '/api/tags'
};
API.TAGS_ADD = {
    method: 'post',
    url: '/api/tags/add'
};
API.QUESTIONS = {
    method: 'get',
    url: '/api/questions'
};
API.QUESTIONS_SAVE = {
    method: 'post',
    url: '/api/questions/save'
};
API.QUESTIONS_DELETE = {
    method: 'delete',
    url: '/api/questions/delete'
};
API.ANSWER_TYPES = {
    method: 'get',
    url: '/api/answer_types'
};


API.USER_PROFILE = {
    method: 'get',
    url: '/api/user/profile'
};
API.USER_LOGIN = {
    method: 'post',
    url: '/api/user/login'
};

API.USER_LIST = {
    method: 'get',
    url: '/api/users/'
};
API.USER_LIST_BLOCK_USER = {
    method: 'post',
    url: '/api/user/block/'
};

API.USER_SURVEY_LIST = {
    method: 'get',
    url: '/api/user/survey'
};

API.USER_SURVEY_ANSWER_LIST = {
    method: 'get',
    url: '/api/user/survey/answers'
};


API.PROVIDERS = {
    method: 'get',
    url: '/api/providers'
};
API.METRICS = {
    method: 'post',
    url: '/api/metrics'
};
API.METRICS_DATE = {
    method: 'get',
    url: '/api/metrics/date'
};
API.METRICS_CHART = {
    method: 'get',
    url: '/api/metrics/chart'
};


API.USER_BLOCKS = {
    method: 'get',
    url: '/api/userblock'
};


API.USER_FEEDBACK = {
    method: 'get',
    url: '/api/user/feedback_list'
};
API.USER_FEEDBACK_AGGREGATED = {
    method: 'get',
    url: '/api/user/feedback_list_aggregated'
};

API.REPORT_COUNTRIES = {
    method: 'post',
    url: '/api/report/countries'
};

API.REPORT_COUNTRY_AMOUNTS = {
    method: 'get',
    url: '/api/report/country_amounts'
};


export default withRouter(API)