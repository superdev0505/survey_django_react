import React from "react";
import PagingTable from "../../components/PagingTable";
import Utils from "../../Utils";
import Badge from "react-bootstrap/Badge";
import API from "../../API";
import Breadcrumb from "react-bootstrap/Breadcrumb";

export default class SurveyAnswerList extends React.Component {

    state = {
        data: [],
        user: {}
    };

    componentDidMount() {
        API.fetch(API.USER_SURVEY_ANSWER_LIST, {survey_id: this.props.match.params.survey_id})
            .then(r => this.setState({
                data: r.data,
                user: r.user
            }))
    }

    getChoiceField = (c, i) =>
        <div key={'c'+i}>
            <div>{c.text}</div>
            <div>
                {c.tags.map(t => <Badge  key={'ct'+i + t.id} variant="light">{t.text}</Badge>)}
            </div>
        </div>;

    render() {
        let {data, user} = this.state;

        return <div className="m-3">

            <Breadcrumb>
                <Breadcrumb.Item href="/users">Users</Breadcrumb.Item>
                <Breadcrumb.Item href={"/users/" + user.id}>
                    {user.first_name} {user.last_name} - {user.ref_id}
                </Breadcrumb.Item>
                <Breadcrumb.Item active>
                    {this.props.match.params.survey_id}
                </Breadcrumb.Item>
            </Breadcrumb>

            <PagingTable
                data={data.reverse()}
                toolbarText="Surveylist"
                serverPaging
                onRowClick={(d) => {}}
                config={[
                    {name: '#', field: (f,i) => i+1},
                    {name: 'Created', sortField: 'created', field: f => Utils.formatDateT(f.created), style: {width: '350px'} },
                    {name: 'Question', sortField: 'tags', field: f =>
                        <div>
                            <div>{f.question.text}</div>
                            <div>
                                {f.question.tags.map(t => <Badge key={'q'+f.question.id + t.id} variant="light">{t.text}</Badge>)}
                            </div>
                        </div>
                    },
                    {name: 'Answers', sortField: 'tags', field: f => f.choice.map(this.getChoiceField) },
                ]}
            />

        </div>
    }

}