import React from "react";
import PagingTable from "../../components/PagingTable";
import API from "../../API";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import Badge from "react-bootstrap/Badge";
import Utils from "../../Utils";

const statuses = [
    'NEW',
    'SUCCESS'
];

export default class MetricsDate extends React.Component {

    state = {
        data: [],
        date: null
    };

    componentDidMount() {
        this.loadSystemMetrics()
    }

    loadSystemMetrics = () => {
        let {date} = this.props.match.params;
        API.fetch(API.METRICS_CHART, {date})
            .then(data => this.setState({
                data, date
            }))
    };

    loadBlocks = () => {
        let {date} = this.props.match.params;
        API.fetch(API.METRICS, {date})
            .then(data => this.setState({
                data, date
            }))
    };

    render() {
        let {data, date} = this.state;

        return <div className="m-3">

            <PagingTable
                data={data}
                toolbarText="Metrics list"
                onRowClick={(d) => {}}
                config={[
                    {name: 'Date', field: f => Utils.formatDateTmills(f.date)},
                    {name: 'Survey', field: 'survey'},
                    {name: 'Questions', field: 'questions'},
                    {name: 'Survey Success', field: 'survey_success'},
                    {name: 'Survey Unsuccess', field: 'survey_unsuccess'},
                    {name: 'Transaction', field: 'transaction'},
                    {name: 'Users_registered', field: 'users_registered'},
                ]}
            />





        </div>
    }

}