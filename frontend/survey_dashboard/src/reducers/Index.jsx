import { combineReducers } from 'redux'
import { user } from './user'
import { metrics } from './metrics'
import { userList } from "./userlist";
import { feedbackList } from "./feedback";
import { questions } from "./questions";


const AppReducers = combineReducers({
    user,
    metrics,
    userList,
    feedbackList,
    questions
});

export default AppReducers