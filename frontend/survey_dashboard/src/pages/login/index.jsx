import React from "react";
import { connect } from 'react-redux'
import { userLoginRequest } from "../../actions";

class Login extends React.Component {

    state = {
        login: '',
        password: ''
    };

    onFieldChange = (e) => {
        this.setState({
            [e.target.name]: e.target.value
        })
    };

    render() {
        let {login, password} = this.state;

        return <div className="container mt-5 w-25">
            <fieldset>
                <div className="form-group">
                    <label htmlFor="exampleInputEmail1">Login</label>
                    <input className="form-control"
                           onChange={this.onFieldChange}
                           name="login"
                           aria-describedby="emailHelp"
                           placeholder="Enter login"/>
                </div>
                <div className="form-group">
                    <label htmlFor="exampleInputPassword1">Password</label>
                    <input type="password"
                           name="password"
                           onChange={this.onFieldChange}
                           className="form-control"
                           placeholder="Password"/>
                </div>

                <button className="btn btn-default" onClick={() => this.props.loginUser(login, password)}>Login</button>
            </fieldset>
        </div>
    }

}

const mapStateToProps = state => ({
    user: state.user
});

const mapDispatchToProps = dispatch => ({
    loginUser: (login, password) => dispatch(userLoginRequest(login, password))
});

export default connect(mapStateToProps, mapDispatchToProps)(Login)