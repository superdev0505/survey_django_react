import React from "react";
import {connect} from 'react-redux'
import {metricsRequest} from "../../actions";
import PagingTable from "../../components/PagingTable";
import API from "../../API";
import Form from "react-bootstrap/Form";
import Spinner from "react-bootstrap/Spinner";
import DatePicker from "react-datepicker";
import moment from 'moment/moment'

import "react-datepicker/dist/react-datepicker.css";

class Metrics extends React.Component {

    state = {
        date: '',
        provider: '',
        providers: []
    };

    componentDidMount = () => {
        this.loadProviders();
        this.loadMetrics();
    };

    loadProviders = () => {
        API.fetch(API.PROVIDERS)
            .then(providers => this.setState({providers}))
    };

    loadMetrics = () => {
        let {provider, date} = this.state;
        this.props.loadMetrics(
            date && moment(date).format('DD/MM/YYYY'),
            provider
        )
    };

    handleProviderChange = (e) => {
        this.setState({
            provider: e.target.value
        }, this.loadMetrics)
    };

    handleDateChange = (date) => {
        this.setState({date}, this.loadMetrics)
    };

    render() {
        let {metrics, metricsLoading} = this.props;
        let {date, provider, providers} = this.state;

        return <div className="m-3">

            <Form noValidate>
                <Form.Row>
                    <Form.Group className="ml-1 mr-5">
                        <Form.Label>Date</Form.Label>
                        <div>
                            <DatePicker
                                selected={date}
                                className="form-control"
                                placeholderText="Click to select a date" onChange={this.handleDateChange}/>
                        </div>
                    </Form.Group>

                    <Form.Group controlId="metrics.providerSelect">
                        <Form.Label>Provider</Form.Label>
                        <Form.Control as="select" onChange={this.handleProviderChange}>
                            <option value=''>All</option>
                            {providers.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                        </Form.Control>
                    </Form.Group>
                    {metricsLoading && <Form.Group>
                        <Spinner animation="border" role="status" className="ml-5 mt-4">
                            <span className="sr-only">Loading...</span>
                        </Spinner>
                    </Form.Group>}
                </Form.Row>
            </Form>

            <div className="card border-primary mb-3">
                <div className="card-header">Aggregation by day</div>
                <div className="card-body">
                    <PagingTable
                        data={metrics}
                        config={[
                            {name: 'Date', field: 'trdate'},
                            {name: 'Provider', field: f => f.provider_name || 'All', sortField: 'provider_name'},
                            {name: 'All survey', field: 'all'},
                            {name: 'Started survey', field: 'started'},
                            {name: 'Success survey', field: 'success'},
                            {name: 'Success %', field: f => Math.round(f.success * 100 / f.all) + '%', sortField: 'failed' },

                            {name: 'Contradicting', field: 'is_contradicting'},
                            {name: 'Bot', field: 'is_bot'},
                            {name: 'Changin IP', field: 'is_changing_ip'},
                            {name: 'Zombie', field: 'is_zombie'},

                            {name: 'Revenue', field: 'sum'}
                        ]}
                    />
                </div>
            </div>

        </div>
    }

}

const mapStateToProps = state => ({
    metrics: state.metrics.metrics || [],
    metricsLoading: state.metrics.metricsLoading,
});

const mapDispatchToProps = dispatch => ({
    loadMetrics: (date, provider) => dispatch(metricsRequest(date, provider)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Metrics)