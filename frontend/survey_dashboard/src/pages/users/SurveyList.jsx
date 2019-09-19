import React from "react";
import PagingTable from "../../components/PagingTable";
import Utils from "../../Utils";
import API from "../../API";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import Badge from "react-bootstrap/Badge";

export default class SurveyList extends React.Component {

    state = {
        data: [],
        user: {},
        status: {}
    };

    componentDidMount() {
        API.fetch(API.USER_SURVEY_LIST, {user_id: this.props.match.params.user_id})
            .then(r =>
                this.setState({
                    data: r.data,
                    user: r.user,
                    status: r.status.reduce((a,v) => Object.assign(a, {[v[1]]: v[0]}),{})
                })
            )
    }

    render() {
        let {data, user, status} = this.state;

        return <div className="m-3">

            <Breadcrumb>
                <Breadcrumb.Item href="/users">Users</Breadcrumb.Item>
                <Breadcrumb.Item active>
                    {user.first_name} {user.last_name} - {user.ref_id}
                </Breadcrumb.Item>
            </Breadcrumb>

            <PagingTable
                data={data.reverse()}
                toolbarText="Surveylist"
                serverPaging
                onRowClick={(d) => {window.location = '/users/' + user.id + '/' + d.id}}
                config={[
                    {name: '#', field: (f,i) => data.length - i},
                    {name: 'Created', sortField: 'created', field: f => Utils.formatDateT(f.created)},
                    {name: 'Solved', sortField: 'solved', field: f => f ? Utils.formatDateT(f.solved) : ''},
                    {name: 'Status', sortField: 'status', field: f => <Badge variant="light">{status[f.status]}</Badge>},
                    {name: 'Last Question', sortField: 'current_question', field: f => f.current_question.text },
                ]}
            />

        </div>
    }

}