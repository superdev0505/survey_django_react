import React from 'react';
import {connect} from 'react-redux'

import {BrowserRouter as Router, Route} from "react-router-dom";
import Layout from "./components/Layout";
import Questions from "./pages/questions/Questions";
import UserList from "./pages/users/index";
import Metrics from "./pages/metrics/index";
import MetricsDate from "./pages/metrics/MetricsDate";
import MetricsChart from "./pages/metrics/MetricsChart";
import FeedbackList from "./pages/feedback/index";
import Reports from "./pages/reports/index";
import Login from "./pages/login";
import './App.css';
import {userRequest} from "./actions";
import SurveyList from "./pages/users/SurveyList";
import SurveyAnswerList from "./pages/users/SurveyAnswerList";

class App extends React.Component {

    componentWillMount() {
        if (window.location.pathname !== '/login') {
            this.props.loadUser()
        }
    }

    render () {
        return <Router>
            <Layout>
                <Route exact path="/" render={()=> <Login/>} />
                <Route exact path="/login" render={()=> <Login/>} />
                <Route exact path="/tags/" component={Questions} />
                <Route exact path="/metrics/" component={Metrics} />
                <Route exact path="/metrics/:date" component={MetricsDate} />
                <Route exact path="/users/" component={UserList} />
                <Route exact path="/users/:user_id" component={SurveyList} />
                <Route exact path="/users/:user_id/:survey_id" component={SurveyAnswerList} />
                <Route exact path="/reports/" component={Reports} />
                <Route exact path="/feedback/" component={FeedbackList} />
            </Layout>
        </Router>
    }

}

const mapStateToProps = state => {
    return {
        user: state.user
    }
};

const mapDispatchToProps = dispatch => ({
    loadUser: () => dispatch(userRequest())
});

export default connect(mapStateToProps,mapDispatchToProps)(App)