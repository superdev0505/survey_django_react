import React from "react";
import PagingTable from "../../components/PagingTable";
import API from "../../API";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import Badge from "react-bootstrap/Badge";
import Utils from "../../Utils";

export default class MetricsChart extends React.Component {

    state = {
        data: []
    };

    componentDidMount() {
        API.fetch(API.METRICS_CHART)
            .then(data => this.setState({data}))
    }

    render() {
        let {data, date} = this.state;

        return <div className="m-3">

            <PagingTable
                data={data}
                toolbarText="Metrics list"
                onRowClick={(d) => {}}
                config={[
                    {name: 'Date', field: f => Utils.formatDateTmills('date')},
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