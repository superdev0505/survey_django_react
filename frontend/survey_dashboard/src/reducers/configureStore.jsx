import { createStore, applyMiddleware } from 'redux'
import thunkMiddleware from 'redux-thunk'
import { createLogger } from 'redux-logger'
import AppReducers from './Index'

const loggerMiddleware = createLogger();

export default function configureStore(preloadedState) {
    return createStore(
        AppReducers,
        preloadedState,
        applyMiddleware(
            thunkMiddleware,
            loggerMiddleware
        )
    )
}