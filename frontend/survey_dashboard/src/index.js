import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

import 'react-bootstrap-typeahead/css/Typeahead.css';
import './bootstrap.min.css';
import './index.css';
import Provider from "react-redux/es/components/Provider";
import configureStore from "./reducers/configureStore";

ReactDOM.render((
    <Provider store={configureStore()}>
        <App/>
    </Provider>
), document.getElementById('root'));

