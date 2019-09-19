import React from "react";
import {Nav} from "react-bootstrap";
import connect from "react-redux/es/connect/connect";
import {withRouter} from "react-router-dom";


class Header extends React.Component {

    render () {
        let {user} = this.props;

        console.log('[USER]', user);
        if (user.is_anonymous) {
            return false
        }

        return <Nav
            activeKey="/admin/home"
            className="p-3 navbar-expand-lg bg-primary navbar-dark"
            onSelect={selectedKey => this.props.history.push(selectedKey)}>

            {user.is_superuser && <Nav.Item>
                <Nav.Link href="/users">Users</Nav.Link>
            </Nav.Item>}
            {user.is_superuser && <Nav.Item>
                <Nav.Link href="/metrics">Providers</Nav.Link>
            </Nav.Item>}
            {user.is_superuser && <Nav.Item>
                <Nav.Link href="/metrics/chart">System</Nav.Link>
            </Nav.Item>}
            {user.is_superuser && <Nav.Item>
                <Nav.Link href="/reports">Reports</Nav.Link>
            </Nav.Item>}
            {user.is_superuser && <Nav.Item>
                <Nav.Link href="/feedback">Feedbacks</Nav.Link>
            </Nav.Item>}
            <Nav.Item>
                <Nav.Link href="/tags">Questions</Nav.Link>
            </Nav.Item>
            <div className="flex-grow-1"/>
            <Nav.Item>
                <Nav.Link>{user.username}</Nav.Link>
            </Nav.Item>

        </Nav>
    }

}

const mapStateToProps = state => {
    return {
        user: state.user
    }
};

export default connect(mapStateToProps)(withRouter(Header))